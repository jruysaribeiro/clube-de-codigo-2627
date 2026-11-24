# O Cerco na Oficina: que coisas se podem escolher, onde esta o codigo de
# cada uma, e o "palco" que mostra so essa coisa a funcionar.
#
# O palco nao e um jogo a parte: e O Cerco verdadeiro a correr, com ouro
# sem fim e sem ondas, e nos a mandarmos vir os inimigos que interessam.
# Por isso tudo o que se ve e desenhado pelo codigo do proprio jogo.

import ast
import inspect
import re

import blocos
# (Tirar uma coisa de uma lista escrita no codigo, com a virgula dela, ja
# esta feito no bicharada.py: usa-se o de la.)
from jogos import bicharada as base

NOME = "O Cerco"
FICHEIRO = "s13-o-cerco/o-cerco.py"
DESCRICAO = "Um tower defense. Guimarães, 1128."

# Uma frase por grupo, para a pagina do jogo dizer o que la ha.
SOBRE_OS_GRUPOS = {
    "Inimigos": "Vida, velocidade, cor, tamanho. Podes pôr uma imagem tua.",
    "Torres": "Custo, alcance, dano, efeito. Podes pôr uma imagem tua.",
    "Mapa": "O caminho, desenhado com letras.",
    "Ondas": "Que inimigos vêm em cada onda, e quantos. Cada onda abre sozinha, e há a lista de todas.",
    "Regras do jogo": "Aqui mudas a maneira como o jogo se comporta, no combate e nas contas: é programar a sério.",
    "Acontecimentos": "Estão vazios: o que lá escreveres passa a acontecer nesse momento. É aqui que se inventa.",
    "Desenhos": "Como se desenha uma torre, um inimigo, o mapa, o castelo e um projétil.",
}

# Os grupos onde se pode criar uma coisa nova, e o que diz o botao.
CRIAVEIS = {"Inimigos": "Novo inimigo", "Torres": "Nova torre", "Ondas": "Nova onda"}

LINHA_A_LINHA = "Explica-me esta função linha a linha"
QUE_FAZER = "O que posso fazer aqui?"

# Pedidos ja escritos para o ajudante, para se perceber o que se pode pedir.
SUGESTOES = {
    "inimigo": ["Põe-no mais rápido mas com menos vida", "Muda-lhe a cor para verde", "O que quer dizer cada número?"],
    "torre": ["Faz esta torre disparar mais depressa", "Dá-lhe mais alcance, mas mais cara", "O que faz o efeito?"],
    "mapa": ["Como é que desenho um caminho novo?", "O que quer dizer cada letra?"],
    "escolher_alvo": ["Faz as torres atacarem o inimigo com menos vida", "Faz as torres atacarem o que está mais perto",
                      "Explica-me esta função linha a linha"],
    "disparar": ["Faz o Besteiro disparar duas setas de cada vez", "Faz a pedra do Trabuco voar mais depressa",
                 "Explica-me esta função linha a linha"],
    "magoar": ["Quero golpes críticos: às vezes o dano conta a dobrar", "Dá 1 de ouro por cada golpe que acerta",
               "Explica-me esta função linha a linha"],
    "mover_inimigo": ["Faz os inimigos acelerarem quando têm pouca vida", "Faz os inimigos pararem um bocadinho de vez em quando",
                      "Explica-me esta função linha a linha"],
    "ondas": ["Acrescenta uma onda só de Cavaleiros", "Faz a primeira onda mais fácil", "Como é que se lê uma onda?"],
    "onda": ["Põe mais inimigos nesta onda", "Faz os inimigos saírem mais juntos", "Como é que se lê uma onda?"],
    "vida_do_inimigo": ["Faz os inimigos terem sempre a mesma vida, em todas as ondas",
                        "A vida dobra de 5 em 5 ondas", LINHA_A_LINHA],
    "valor_da_torre": ["No último nível o dano fica a triplicar", "O alcance não cresce com o nível", LINHA_A_LINHA],
    "custo_melhoria": ["Faz melhorar custar sempre 40 de ouro", "A primeira melhoria de cada torre é de borla",
                       LINHA_A_LINHA],
    "valor_de_venda": ["Ao vender recebe-se o ouro todo de volta", "As torres no nível máximo valem o dobro",
                       LINHA_A_LINHA],
    "premio_da_onda": ["Cada onda dá mais 10 de ouro do que a anterior", "De 5 em 5 ondas o prémio é de 200",
                       LINHA_A_LINHA],
    "pode_construir": ["Deixa construir também por cima das árvores", "Só se pode construir colado ao caminho",
                       LINHA_A_LINHA],
    "ao_acabar_onda": ["Recupero uma vida por cada onda vencida", "Mostra um texto a dizer quantas ondas faltam",
                       QUE_FAZER],
    "ao_melhorar": ["A torre dispara logo a seguir a ser melhorada", "Mostra um texto a festejar com o nível novo",
                    QUE_FAZER],
    "ao_vender": ["Ao ser vendida, a torre rebenta e magoa os inimigos que estão perto",
                  "Conta na memoria quantas torres já vendi", QUE_FAZER],
    "desenhar_quadrado": ["Põe flores na relva", "Dá um tronco às árvores", "Explica-me este desenho linha a linha"],
    "desenhar_castelo": ["Muda a bandeira para vermelha", "Põe uma torre de cada lado do castelo",
                         "Explica-me este desenho linha a linha"],
    "desenhar_projetil": ["Faz as setas compridas em vez de bolinhas", "Faz a pedra do Trabuco cinzenta",
                          "Explica-me este desenho linha a linha"],
    "ao_comecar_onda": ["Dá 50 de ouro de 3 em 3 ondas", "Mostra um texto a dizer o número da onda", "O que posso fazer aqui?"],
    "ao_cair_inimigo": ["Quando um inimigo cai, rebenta e magoa os que estão perto",
                        "Um Aríete que ao cair larga dois Soldados", "O que posso fazer aqui?"],
    "ao_chegar_ao_castelo": ["Quando um inimigo chega ao castelo, os outros perdem 20 de vida",
                             "Dá 10 de ouro de consolação", "O que posso fazer aqui?"],
    "ao_construir": ["Mostra um círculo a crescer onde a torre aparece", "A primeira torre de cada jogo nasce no nível 2",
                     "O que posso fazer aqui?"],
    "ao_carregar_tecla": ["A tecla B magoa todos os inimigos, mas só uma vez por onda", "A tecla G dá 100 de ouro",
                          "O que posso fazer aqui?"],
    "a_cada_frame": ["Dá 1 de ouro a cada segundo", "Os inimigos perdem vida aos poucos", "O que posso fazer aqui?"],
    "desenhar_torre": ["Põe uma bandeira no topo da torre", "Faz a torre mudar de cor com o nível", "Explica-me este desenho linha a linha"],
    "desenhar_inimigo": ["Dá olhos ao inimigo", "Faz o inimigo ficar vermelho quando tem pouca vida",
                         "Explica-me este desenho linha a linha"],
}

EFEITOS = ["tiro", "explosao", "area", "golpe"]

# As regras: funcoes do jogo que se podem mudar. Para cada uma, o titulo que
# aparece na Oficina, e o que ela recebe (o jogo chama-a assim, por isso nao
# pode mudar).
REGRAS = {
    "escolher_alvo": ("Quem a torre ataca", ["torre"]),
    "disparar": ("O que a torre faz ao disparar", ["torre", "alvo"]),
    "magoar": ("O que acontece a um inimigo atingido", ["inimigo", "dano"]),
    "mover_inimigo": ("Como anda um inimigo", ["inimigo"]),
    "vida_do_inimigo": ("Quanta vida tem um inimigo", ["nome", "onda"]),
    "valor_da_torre": ("O que vale uma torre em cada nível", ["torre", "chave"]),
    "custo_melhoria": ("Quanto custa melhorar uma torre", ["torre"]),
    "valor_de_venda": ("Quanto se recebe ao vender uma torre", ["torre"]),
    "premio_da_onda": ("Quanto ouro dá acabar uma onda", ["numero"]),
    "pode_construir": ("Onde se pode construir", ["coluna", "linha"]),
}
# As regras que sao das torres: no palco ha uma torre escolhida, que vai
# mudando de nivel, para se ver o que a regra da em cada um.
DAS_TORRES = ["valor_da_torre", "custo_melhoria", "valor_de_venda"]
# As funcoes que so se veem com as ondas a passar: o jogo joga-se sozinho.
COM_ONDAS = ["premio_da_onda"]
# Nestas as ondas andam a dobrar, para chegar depressa ao fim de cada uma.
DEPRESSA = ["premio_da_onda", "ao_acabar_onda"]
INICIO_DAS_REGRAS = "# --- As regras do jogo ---"

# Os acontecimentos: funcoes que o jogo chama em certos momentos, e que vem
# vazias. E os desenhos. Tudo isto sao funcoes, como as regras.
ACONTECIMENTOS = {
    "ao_comecar_onda": ("Quando começa uma onda", ["numero"]),
    "ao_cair_inimigo": ("Quando um inimigo cai", ["inimigo"]),
    "ao_chegar_ao_castelo": ("Quando um inimigo chega ao castelo", ["inimigo"]),
    "ao_construir": ("Quando se constrói uma torre", ["torre"]),
    "ao_carregar_tecla": ("Quando se carrega numa tecla", ["tecla"]),
    "a_cada_frame": ("A cada frame", []),
    "ao_acabar_onda": ("Quando acaba uma onda", ["numero"]),
    "ao_melhorar": ("Quando se melhora uma torre", ["torre"]),
    "ao_vender": ("Quando se vende uma torre", ["torre"]),
}
INICIO_DOS_ACONTECIMENTOS = "# --- Os acontecimentos ---"
DESENHOS = {
    "desenhar_torre": ("O desenho de uma torre", ["torre"]),
    "desenhar_inimigo": ("O desenho de um inimigo", ["inimigo"]),
    "desenhar_quadrado": ("Um quadrado do mapa", ["letra", "coluna", "linha"]),
    "desenhar_castelo": ("O castelo", ["x", "y"]),
    "desenhar_projetil": ("Um projétil", ["projetil"]),
}
INICIO_DOS_DESENHOS = "# --- Os desenhos ---"

# tipo da escolha -> (as funcoes desse tipo, o grupo onde aparecem, as
# explicacoes gerais que se juntam a ajuda de cada uma)
FUNCOES = {
    "regra": (REGRAS, "Regras do jogo", [INICIO_DAS_REGRAS]),
    "evento": (ACONTECIMENTOS, "Acontecimentos", [INICIO_DOS_ACONTECIMENTOS, INICIO_DAS_REGRAS]),
    "desenho": (DESENHOS, "Desenhos", [INICIO_DOS_DESENHOS]),
}

DICAS = {
    "inimigo": "O inimigo anda sozinho pelo caminho. "
               "Clica na relva para pôr mais torres e ver quanto ele aguenta.",
    "torre": "A tua torre já está posta, com o alcance à vista. "
             "Clica na relva para pôr mais; as teclas 1 2 3 4 escolhem outra torre.",
    "mapa": "Cada letra é um quadrado. Muda uma letra e vê o mapa mudar. "
            "Os inimigos andam pelo caminho para veres por onde ele vai.",
    "regra": "Isto é uma regra do jogo: muda-a e o jogo passa a comportar-se de outra maneira. "
             "Há uma torre de cada e inimigos de todos, para veres logo a diferença. "
             "O círculo amarelo marca quem cada torre escolheu.",
    "evento": "O jogo joga-se sozinho, onda atrás de onda, para veres o teu acontecimento a acontecer. "
              "Tira o pass e escreve o que queres que aconteça. Clica no jogo para carregares em teclas.",
    "desenho": "Isto é o desenho: muda-o e vês logo, no jogo e aumentado no canto. "
               "Experimenta mudar um número, ou acrescentar um círculo.",
    "ondas": "O jogo joga-se sozinho desde a primeira onda, para veres as ondas como as escreveste.",
    "onda": "O jogo joga esta onda sozinho, e quando ela acaba começa-a outra vez. "
            "«Escolher os inimigos» mostra os inimigos que existem, para não teres de escrever os nomes.",
}

# As funcoes cujo palco nao e o habitual do genero delas: o que la se ve.
DICAS_DAS_FUNCOES = {
    "vida_do_inimigo": "Isto é uma regra do jogo. O quadro do canto mostra a vida com que cada inimigo nasce na "
                       "primeira onda, a meio e na última. Os inimigos que passam são da primeira.",
    "valor_da_torre": "Isto é uma regra do jogo. A primeira torre está escolhida e vai mudando de nível sozinha: "
                      "vê o dano na barra de baixo, o círculo do alcance, e as contas no quadro do canto.",
    "custo_melhoria": "Isto é uma regra do jogo. A primeira torre está escolhida e vai mudando de nível sozinha: "
                      "a barra de baixo diz quanto custa melhorá-la, e o quadro do canto diz o de todas.",
    "valor_de_venda": "Isto é uma regra do jogo. A primeira torre está escolhida e vai mudando de nível sozinha: "
                      "a barra de baixo diz por quanto se vende, e o quadro do canto diz o de todas.",
    "premio_da_onda": "Isto é uma regra do jogo. O jogo joga-se sozinho, a dobrar, onda atrás de onda: "
                      "o prémio aparece quando uma onda acaba, e o quadro do canto diz o de cada onda.",
    "pode_construir": "Isto é uma regra do jogo. Os pontos verdes marcam os quadrados onde, com a tua regra, "
                      "dá para construir. Clica num para experimentar.",
    "ao_acabar_onda": "O jogo joga-se sozinho, a dobrar, onda atrás de onda, para veres o que acontece quando "
                      "cada uma acaba. Tira o pass e escreve o que queres que aconteça.",
    "ao_melhorar": "O jogo joga-se sozinho e, de dois em dois segundos, melhora uma torre por ti, para veres o teu "
                   "acontecimento a acontecer. Tira o pass e escreve o que queres que aconteça.",
    "ao_vender": "O jogo joga-se sozinho e, de vez em quando, vende uma torre por ti (e põe outra no lugar), para "
                 "veres o teu acontecimento a acontecer. Tira o pass e escreve o que queres que aconteça.",
    "desenhar_quadrado": "Isto é o desenho de cada quadrado do mapa: muda-o e vês logo, no mapa todo e aumentado "
                         "no canto, uma letra de cada vez.",
    "desenhar_castelo": "Isto é o desenho do castelo: muda-o e vês logo, no fim do caminho e aumentado no canto.",
    "desenhar_projetil": "Isto é o desenho das setas e das pedras: muda-o e vês logo, no jogo e aumentado no canto "
                         "(ora uma seta, ora uma pedra).",
}


# =====================================================================
#                    ONDE ESTA O CODIGO DE CADA COISA
# =====================================================================

def escolhas(fonte):
    arvore = ast.parse(fonte)
    lista = []

    no = blocos.instrucao(arvore, "INIMIGOS")
    partes = blocos.entradas(no) if no is not None else None
    if partes:
        for i, (chave, _, _) in enumerate(partes):
            nome = blocos.texto_constante(chave) or "Inimigo " + str(i + 1)
            lista.append({"id": "inimigo:" + str(i), "grupo": "Inimigos", "titulo": nome})

    no = blocos.instrucao(arvore, "TORRES")
    partes = blocos.entradas(no) if no is not None else None
    if partes:
        for i, (elemento, _, _) in enumerate(partes):
            nome = blocos.valor_da_chave(elemento, "nome") or "Torre " + str(i + 1)
            lista.append({"id": "torre:" + str(i), "grupo": "Torres", "titulo": nome})

    if blocos.instrucao(arvore, "MAPA") is not None:
        lista.append({"id": "mapa", "grupo": "Mapa", "titulo": "O mapa"})

    no = blocos.instrucao(arvore, "ONDAS")
    if no is not None:
        lista.append({"id": "ondas", "grupo": "Ondas", "titulo": "As ondas todas"})
        # Cada onda sozinha, se estiverem escritas uma por linha.
        for i in range(len(blocos.entradas(no) or [])):
            lista.append({"id": "onda:" + str(i), "grupo": "Ondas", "titulo": "Onda " + str(i + 1)})

    for tipo in FUNCOES:
        funcoes, grupo, _ = FUNCOES[tipo]
        for nome in funcoes:
            if blocos.funcao(arvore, nome) is not None:
                lista.append({"id": tipo + ":" + nome, "grupo": grupo, "titulo": funcoes[nome][0]})
    return lista


def regiao(fonte, escolha):
    # Devolve {"inicio", "fim", "ajuda", "titulo", "dica", "imagem", "som"} ou None.
    # "imagem" e o nome do PNG que essa coisa usa (None se nao usa nenhum):
    # e com ele que a Oficina sabe onde guardar a imagem que a crianca
    # escolher. "som" e o mesmo, para o WAV.
    arvore = ast.parse(fonte)
    linhas = fonte.split("\n")
    tipo, _, numero = escolha.partition(":")
    if tipo in FUNCOES:
        # Uma regra, um acontecimento ou um desenho: e uma funcao inteira. A
        # ajuda junta o que o ficheiro diz sobre ela ao que se pode usar
        # dentro de qualquer funcao desse genero.
        funcoes, _, gerais = FUNCOES[tipo]
        no = blocos.funcao(arvore, numero) if numero in funcoes else None
        if no is None:
            return None
        ajuda = blocos.ajuda_acima(linhas, no.lineno)
        for inicio in gerais:
            geral = blocos.comentarios_a_partir_de(linhas, inicio)
            if geral and geral != ajuda:
                ajuda = ajuda + "\n\n" + geral
        return {"inicio": no.lineno, "fim": no.end_lineno, "ajuda": ajuda,
                "dica": DICAS_DAS_FUNCOES.get(numero, DICAS[tipo]),
                "titulo": funcoes[numero][0], "imagem": None, "som": None, "sugestoes": SUGESTOES[numero]}
    nomes = {"inimigo": "INIMIGOS", "torre": "TORRES", "mapa": "MAPA", "ondas": "ONDAS", "onda": "ONDAS"}
    if tipo not in nomes:
        return None
    no = blocos.instrucao(arvore, nomes[tipo])
    if no is None:
        return None
    resposta = {"ajuda": blocos.ajuda_acima(linhas, no.lineno), "dica": DICAS[tipo], "imagem": None, "som": None,
                "sugestoes": SUGESTOES[tipo]}

    if tipo == "mapa" or tipo == "ondas":
        resposta.update(inicio=no.lineno, fim=no.end_lineno, titulo="O mapa" if tipo == "mapa" else "As ondas")
        return resposta

    partes = blocos.entradas(no)
    if not partes or not numero.isdigit() or int(numero) >= len(partes):
        return None
    parte, inicio, fim = partes[int(numero)]
    # O que dizem os botoes de apagar e de escolher de uma lista (ve apagar e
    # lista, mais abaixo).
    if tipo == "onda":
        resposta.update(inicio=inicio, fim=fim, titulo="Onda " + str(int(numero) + 1),
                        apagar="Apagar esta onda", lista="Escolher os inimigos")
        return resposta
    resposta["apagar"] = "Apagar este inimigo" if tipo == "inimigo" else "Apagar esta torre"
    if tipo == "inimigo":
        titulo = blocos.texto_constante(parte)
    else:
        titulo = blocos.valor_da_chave(parte, "nome")
    ficha = blocos.valor_da_entrada(no, int(numero))
    resposta.update(inicio=inicio, fim=fim, titulo=titulo or escolha,
                    imagem=blocos.valor_da_chave(ficha, "imagem"), som=blocos.valor_da_chave(ficha, "som"))
    return resposta


# =====================================================================
#                        CRIAR UMA COISA NOVA
# =====================================================================
# Um inimigo novo ou uma torre nova nascem como copia do primeiro que la
# esta (o mais simples), com outro nome, e ficam no fim da lista. Devolve o ficheiro inteiro ja com a coisa nova, a
# escolha a abrir, e uma frase a contar o que se fez.

def _nome_livre(base, existentes):
    nome = base
    numero = 2
    while nome in existentes:
        nome = base + " " + str(numero)
        numero = numero + 1
    return nome


def _ficheiro(nome):
    # "Inimigo novo 2" -> "inimigo-novo-2"
    return nome.lower().replace(" ", "-")


def _copiar_entrada(linhas, inicio, fim, antigo, nome, ultima):
    # As linhas de uma entrada, outra vez, com o nome, a imagem e o som
    # novos. "ultima" e a linha onde acaba a ultima entrada: a copia vai a seguir.
    texto = "\n".join(linhas[inicio - 1:fim])
    texto = texto.replace('"' + antigo + '"', '"' + nome + '"', 1)
    texto = re.sub(r'"imagem": "[^"]*"', '"imagem": "' + _ficheiro(nome) + '.png"', texto)
    texto = re.sub(r'"som": "[^"]*"', '"som": "' + _ficheiro(nome) + '.wav"', texto)
    if not texto.rstrip().endswith(","):
        texto = texto.rstrip() + ","
    if not linhas[ultima - 1].rstrip().endswith(","):
        linhas[ultima - 1] = linhas[ultima - 1].rstrip() + ","
    return texto.split("\n")


def _por_na_primeira_onda(fonte, nome):
    # Sem isto o inimigo novo existia mas nunca aparecia no jogo.
    no = blocos.instrucao(ast.parse(fonte), "ONDAS")
    if no is None or not isinstance(no.value, ast.List) or len(no.value.elts) == 0:
        return fonte, False
    onda = no.value.elts[0]
    if not isinstance(onda, ast.List):
        return fonte, False
    linhas = fonte.split("\n")
    linha = linhas[onda.end_lineno - 1]
    # (O Python conta as colunas em bytes: com acentos nao e o mesmo que letras.)
    corte = len(linha.encode("utf-8")[:onda.end_col_offset - 1].decode("utf-8"))
    antes = linha[:corte].rstrip()
    grupo = '{"inimigo": "' + nome + '", "quantos": 3, "intervalo": 60}'
    if len(onda.elts) > 0 and not antes.endswith(","):
        grupo = ", " + grupo
    linhas[onda.end_lineno - 1] = antes + grupo + linha[corte:]
    return "\n".join(linhas), True


def novo(fonte, grupo):
    arvore = ast.parse(fonte)
    linhas = fonte.split("\n")
    if grupo == "Inimigos":
        no = blocos.instrucao(arvore, "INIMIGOS")
        partes = blocos.entradas(no) if no is not None else None
        if not partes:
            raise ValueError("não encontrei os INIMIGOS no ficheiro.")
        chave, inicio, fim = partes[0]
        ultima = partes[-1][2]
        antigo = blocos.texto_constante(chave)
        nome = _nome_livre("Inimigo novo", [blocos.texto_constante(c) for c, _, _ in partes])
        copia = _copiar_entrada(linhas, inicio, fim, antigo, nome, ultima)
        nova = "\n".join(linhas[:ultima] + copia + linhas[ultima:])
        nova, posto = _por_na_primeira_onda(nova, nome)
        aviso = 'Criei o "' + nome + '", igual ao ' + str(antigo) + ". Muda-lhe o nome e os números."
        if posto:
            aviso = aviso + " Pus 3 na primeira onda: em Ondas podes mudar isso."
        return nova, "inimigo:" + str(len(partes)), aviso
    if grupo == "Torres":
        no = blocos.instrucao(arvore, "TORRES")
        partes = blocos.entradas(no) if no is not None else None
        if not partes:
            raise ValueError("não encontrei as TORRES no ficheiro.")
        if len(partes) >= 9:
            raise ValueError("já há 9 torres, e só há 9 teclas com números.")
        elemento, inicio, fim = partes[0]
        ultima = partes[-1][2]
        antigo = blocos.valor_da_chave(elemento, "nome")
        nome = _nome_livre("Torre nova", [blocos.valor_da_chave(e, "nome") for e, _, _ in partes])
        copia = _copiar_entrada(linhas, inicio, fim, antigo, nome, ultima)
        tecla = str(len(partes) + 1)
        copia = [re.sub(r"pygame\.K_\w+", "pygame.K_" + tecla, linha) for linha in copia]
        nova = "\n".join(linhas[:ultima] + copia + linhas[ultima:])
        aviso = ('Criei a "' + nome + '", igual ao ' + str(antigo) + ". Escolhe-se com a tecla " + tecla
                 + ". Muda-lhe o nome e os números.")
        return nova, "torre:" + str(len(partes)), aviso
    if grupo == "Ondas":
        # Uma copia da primeira onda (a mais facil), no fim: passa a ser a
        # ultima do jogo.
        no = blocos.instrucao(arvore, "ONDAS")
        partes = blocos.entradas(no) if no is not None else None
        if not partes:
            raise ValueError("não percebi como estão escritas as ONDAS: cada onda tem de começar numa linha nova.")
        _, inicio, fim = partes[0]
        ultima = partes[-1][2]
        copia = linhas[inicio - 1:fim]
        if not copia[-1].rstrip().endswith(","):
            copia[-1] = copia[-1].rstrip() + ","
        if not linhas[ultima - 1].rstrip().endswith(","):
            linhas[ultima - 1] = linhas[ultima - 1].rstrip() + ","
        nova = "\n".join(linhas[:ultima] + copia + linhas[ultima:])
        numero = len(partes) + 1
        aviso = ("Criei a onda " + str(numero) + ", igual à primeira. É a última do jogo: "
                 "escolhe os inimigos dela, e quantos vêm.")
        return nova, "onda:" + str(len(partes)), aviso
    raise ValueError("aqui não dá para criar isso.")


# =====================================================================
#                          APAGAR UMA COISA
# =====================================================================
# Um inimigo, uma torre ou uma onda saem do jogo, e acerta-se o que falava
# deles: o inimigo sai das ondas (uma onda que so o tinha a ele fica com
# outro, para nao ficar vazia), e as torres que vinham a seguir a apagada
# passam para a tecla anterior. Devolve o ficheiro inteiro ja sem a coisa, e
# uma frase a contar o que se fez.

def _arrumar_ondas(fonte):
    # Depois de tirar grupos das ondas podem ficar um "[" ou um "]," sozinhos
    # numa linha. Juntam-se a linha do lado, so dentro das ONDAS.
    no = blocos.instrucao(ast.parse(fonte), "ONDAS")
    if no is None:
        return fonte
    linhas = fonte.split("\n")
    texto = "\n".join(linhas[no.lineno - 1:no.end_lineno])
    texto = re.sub(r'\[[ \t]*\n[ \t]*(\{"inimigo")', r"[\1", texto)
    texto = re.sub(r"\},[ \t]*\n[ \t]*\]", "}]", texto)
    return "\n".join(linhas[:no.lineno - 1] + texto.split("\n") + linhas[no.end_lineno:])


def apagar(fonte, escolha):
    tipo, _, numero = escolha.partition(":")
    arvore = ast.parse(fonte)
    linhas = fonte.split("\n")
    nomes = {"inimigo": "INIMIGOS", "torre": "TORRES", "onda": "ONDAS"}
    no = blocos.instrucao(arvore, nomes[tipo]) if tipo in nomes else None
    partes = (blocos.entradas(no) if no is not None else None) or []
    if not numero.isdigit() or int(numero) >= len(partes):
        raise ValueError("isso não se pode apagar.")
    qual = int(numero)
    parte, inicio, fim = partes[qual]
    cortes = [(inicio, fim)]     # linhas inteiras que saem (ve o _aplicar do bicharada.py)
    trocas = []                  # bocados de uma linha que mudam

    if tipo == "onda":
        if len(partes) < 2:
            raise ValueError("tem de haver pelo menos uma onda.")
        aviso = "Apaguei a onda " + str(qual + 1) + ". Agora o jogo tem " + str(len(partes) - 1) + "."
        if qual + 1 < len(partes):
            aviso = aviso + " As que vinham a seguir passaram a ter o número anterior."
        return base._aplicar(linhas, cortes, trocas), aviso

    if tipo == "torre":
        if len(partes) < 2:
            raise ValueError("tem de haver pelo menos uma torre.")
        nome = blocos.valor_da_chave(parte, "nome") or "a torre"
        # As que vinham a seguir passam para a tecla anterior, para a tecla
        # continuar a ser o numero que aparece na barra de baixo.
        mudaram = False
        for lugar in range(qual + 1, len(partes)):
            tecla = base._no_da_chave(partes[lugar][0], "tecla") if isinstance(partes[lugar][0], ast.Dict) else None
            if isinstance(tecla, ast.Attribute) and tecla.attr == "K_" + str(lugar + 1) and tecla.lineno == tecla.end_lineno:
                base._trocar_no(linhas, tecla, "pygame.K_" + str(lugar), trocas)
                mudaram = True
        aviso = 'Apaguei a "' + str(nome) + '".'
        if mudaram:
            aviso = aviso + " As torres que vinham a seguir passaram para a tecla anterior."
        return base._aplicar(linhas, cortes, trocas), aviso

    if len(partes) < 2:
        raise ValueError("tem de haver pelo menos um inimigo.")
    nome = blocos.texto_constante(parte)
    outro = [blocos.texto_constante(chave) for chave, _, _ in partes if blocos.texto_constante(chave) != nome][0]
    ondas = blocos.instrucao(arvore, "ONDAS")
    quantas = 0
    trocado = False
    for onda in ondas.value.elts if ondas is not None and isinstance(ondas.value, ast.List) else []:
        grupos = onda.elts if isinstance(onda, ast.List) else []
        dele = [grupo for grupo in grupos if blocos.valor_da_chave(grupo, "inimigo") == nome]
        if len(dele) == 0:
            continue
        quantas = quantas + 1
        ficam = len(grupos) - len(dele)
        for grupo in dele:
            if (ficam == 0 and grupo is dele[0]) or not base._tirar_da_lista(linhas, grupo, cortes, trocas):
                # A onda so o tinha a ele: em vez de ficar vazia, fica com outro.
                base._trocar_no(linhas, base._no_da_chave(grupo, "inimigo"), '"' + str(outro) + '"', trocas)
                trocado = True
    aviso = 'Apaguei o "' + str(nome) + '".'
    if quantas == 1:
        aviso = aviso + " Saiu também de uma onda."
    elif quantas > 1:
        aviso = aviso + " Saiu também de " + str(quantas) + " ondas."
    if trocado:
        aviso = aviso + ' Nas ondas que só o tinham a ele ficou o "' + str(outro) + '".'
    return _arrumar_ondas(base._aplicar(linhas, cortes, trocas)), aviso


# =====================================================================
#              ESCOLHER DE UMA LISTA OS INIMIGOS DE UMA ONDA
# =====================================================================
# A Oficina mostra os inimigos que existem e a crianca carrega nos que vem
# nessa onda. Trabalha-se sobre o codigo que esta no editor (a onda), e
# devolve-se esse codigo com os grupos novos: o resto do caminho e o de
# sempre, como se a crianca o tivesse escrito.
#   sem "escolhidos": devolve a lista e os que vem agora
#   com "escolhidos": devolve {"codigo": ...}

def lista(fonte, escolha, codigo, escolhidos=None):
    tipo, _, numero = escolha.partition(":")
    if tipo != "onda":
        raise ValueError("aqui não há nada para escolher de uma lista.")
    no = blocos.instrucao(ast.parse(fonte), "INIMIGOS")
    nomes = [blocos.texto_constante(chave) for chave, _, _ in (blocos.entradas(no) if no is not None else None) or []]
    nomes = [nome for nome in nomes if nome]
    texto = codigo.rstrip()
    virgula = texto.endswith(",")
    if virgula:
        texto = texto[:-1]
    try:
        onda = ast.parse(texto.strip(), mode="eval").body
    except SyntaxError:
        raise ValueError("o código tem um erro: corrige-o primeiro, ou carrega em Repor o original.")
    if not isinstance(onda, ast.List):
        raise ValueError("não percebi esta onda: tem de estar entre [ ].")
    # O que cada grupo diz agora: (inimigo, quantos, intervalo).
    grupos = []
    for grupo in onda.elts:
        if not isinstance(grupo, ast.Dict):
            continue
        valores = []
        for chave in ("quantos", "intervalo"):
            valor = base._no_da_chave(grupo, chave)
            valores.append(valor.value if isinstance(valor, ast.Constant) and isinstance(valor.value, int) else None)
        grupos.append((blocos.valor_da_chave(grupo, "inimigo"), valores[0], valores[1]))
    if escolhidos is None:
        atuais = []
        for nome, _, _ in grupos:
            if nome in nomes and nome not in atuais:
                atuais.append(nome)
        quem = "na onda " + str(int(numero) + 1) if numero.isdigit() else "nesta onda"
        return {"titulo": "Que inimigos vêm " + quem + "?", "opcoes": nomes, "escolhidos": atuais,
                "nota": "Carrega nos inimigos pela ordem em que saem. Quantos vêm de cada um, e de quanto em "
                        "quanto tempo, muda-se depois no código."}

    feita = []
    for nome in escolhidos if isinstance(escolhidos, list) else []:
        if nome in nomes and nome not in feita:
            feita.append(nome)
    if len(feita) == 0:
        raise ValueError("uma onda tem de ter pelo menos um inimigo.")
    # Quem ja la estava fica com os numeros que tinha; os novos, com os do primeiro grupo.
    quantos = [grupo[1] for grupo in grupos if grupo[1] is not None]
    intervalos = [grupo[2] for grupo in grupos if grupo[2] is not None]
    antigos = {}
    for nome, quantos_dele, intervalo_dele in grupos:
        antigos.setdefault(nome, (quantos_dele, intervalo_dele))
    escritos = []
    for nome in feita:
        quantos_dele, intervalo_dele = antigos.get(nome, (None, None))
        if quantos_dele is None:
            quantos_dele = quantos[0] if quantos else 5
        if intervalo_dele is None:
            intervalo_dele = intervalos[0] if intervalos else 40
        escritos.append('{"inimigo": "' + nome + '", "quantos": ' + str(quantos_dele)
                        + ', "intervalo": ' + str(intervalo_dele) + "}")
    margem = texto[:len(texto) - len(texto.lstrip())]
    novo_texto = margem + "[" + (",\n" + margem + " ").join(escritos) + "]" + ("," if virgula else "")
    return {"codigo": novo_texto + codigo[len(codigo.rstrip()):]}


# =====================================================================
#                 VER SE O QUE FOI ESCRITO FAZ SENTIDO
# =====================================================================
# Antes de uma mudanca entrar no jogo, passa por aqui. Devolve duas listas
# de frases: problemas (a mudanca nao entra) e avisos (entra, mas atencao).

def _numero(valor):
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


def _cor(valor):
    if not isinstance(valor, (tuple, list)) or len(valor) != 3:
        return False
    for parte in valor:
        if not isinstance(parte, int) or isinstance(parte, bool) or parte < 0 or parte > 255:
            return False
    return True


def _ver_numeros(ficha, quem, chaves, problemas):
    for chave in chaves:
        if chave not in ficha:
            problemas.append(quem + ': falta "' + chave + '".')
        elif not _numero(ficha[chave]):
            problemas.append(quem + ': "' + chave + '" tem de ser um número, sem aspas.')
        elif ficha[chave] < 0:
            problemas.append(quem + ': "' + chave + '" não pode ser menos que zero.')


def _ver_maximo(ficha, quem, chave, maximo, problemas):
    # Numeros gigantes nao rebentam o jogo: deixam-no preso a desenhar.
    if _numero(ficha.get(chave)) and ficha[chave] > maximo:
        problemas.append(quem + ': "' + chave + '" é grande demais para o ecrã. O máximo é ' + str(maximo) + ".")


def _ver_cor(ficha, quem, problemas):
    if "cor" not in ficha:
        problemas.append(quem + ': falta a "cor".')
    elif not _cor(ficha["cor"]):
        problemas.append(quem + ': a "cor" são três números de 0 a 255, como (200, 60, 60).')


def _ver_imagem(ficha, quem, problemas):
    if "imagem" in ficha and not isinstance(ficha["imagem"], str):
        problemas.append(quem + ': a "imagem" é o nome de um ficheiro, entre aspas, como "soldado.png".')
    if "som" in ficha and not isinstance(ficha["som"], str):
        problemas.append(quem + ': o "som" é o nome de um ficheiro, entre aspas, como "soldado.wav".')


def _ver_ondas(ns, problemas, avisos, aberta=False):
    # aberta: e uma onda (ou as ondas todas) que esta aberta no editor? Entao
    # um inimigo que nao existe e um engano de quem a escreveu, e nao entra.
    inimigos = ns.get("INIMIGOS")
    ondas = ns.get("ONDAS")
    if not isinstance(ondas, list) or len(ondas) == 0:
        problemas.append("Tem de haver pelo menos uma onda: uma linha [ ... ] dentro de ONDAS.")
        return
    numero = 0
    for onda in ondas:
        numero = numero + 1
        quem = "Onda " + str(numero)
        if not isinstance(onda, list) or len(onda) == 0:
            problemas.append(quem + ": tem de ser uma lista [ ... ] com pelo menos um grupo { ... }.")
            continue
        for grupo in onda:
            if not isinstance(grupo, dict):
                problemas.append(quem + ": cada grupo tem de estar entre { }.")
                continue
            if not isinstance(grupo.get("inimigo"), str):
                problemas.append(quem + ': falta o "inimigo", com o nome entre aspas.')
            elif aberta and isinstance(inimigos, dict) and grupo["inimigo"] not in inimigos:
                problemas.append(quem + ': o inimigo "' + grupo["inimigo"] + '" não existe em INIMIGOS.'
                                 + base._parecido(grupo["inimigo"], [nome for nome in inimigos if isinstance(nome, str)]))
            for chave, maximo in (("quantos", 300), ("intervalo", 6000)):
                valor = grupo.get(chave)
                if not isinstance(valor, int) or isinstance(valor, bool):
                    problemas.append(quem + ': "' + chave + '" tem de ser um número inteiro, sem aspas.')
                elif valor < 1:
                    problemas.append(quem + ': "' + chave + '" tem de ser pelo menos 1.')
                elif valor > maximo:
                    problemas.append(quem + ': "' + chave + '" é grande demais. O máximo é ' + str(maximo) + ".")


def _ver_inimigos(ns, problemas, avisos):
    inimigos = ns.get("INIMIGOS")
    if not isinstance(inimigos, dict) or len(inimigos) == 0:
        problemas.append("Tem de haver pelo menos um inimigo.")
        return
    for nome, ficha in inimigos.items():
        quem = str(nome)
        if not isinstance(nome, str):
            problemas.append("O nome de um inimigo tem de estar entre aspas.")
            continue
        if not isinstance(ficha, dict):
            problemas.append(quem + ": a ficha tem de estar entre { }.")
            continue
        _ver_numeros(ficha, quem, ["vida", "velocidade", "recompensa", "estrago", "tamanho"], problemas)
        _ver_maximo(ficha, quem, "tamanho", 300, problemas)
        _ver_maximo(ficha, quem, "velocidade", 100, problemas)
        if _numero(ficha.get("vida")) and 0 <= ficha["vida"] < 1:
            problemas.append(quem + ': a "vida" tem de ser pelo menos 1.')
        _ver_cor(ficha, quem, problemas)
        _ver_imagem(ficha, quem, problemas)
        forma = ficha.get("forma")
        if forma not in ("circulo", "quadrado"):
            avisos.append(quem + ': a "forma" só pode ser "circulo" ou "quadrado". Fica círculo.')

    ondas = ns.get("ONDAS")
    em_falta = []
    if isinstance(ondas, list):
        for onda in ondas:
            for grupo in onda if isinstance(onda, list) else []:
                nome = grupo.get("inimigo") if isinstance(grupo, dict) else None
                if nome not in inimigos and nome not in em_falta:
                    em_falta.append(nome)
    for nome in em_falta:
        avisos.append('As ONDAS ainda chamam por "' + str(nome) + '", que já não existe. '
                      "O jogo inteiro vai parar quando essa onda chegar.")


def _ver_torres(ns, problemas, avisos):
    torres = ns.get("TORRES")
    if not isinstance(torres, list) or len(torres) == 0:
        problemas.append("Tem de haver pelo menos uma torre.")
        return
    numero = 0
    for ficha in torres:
        numero = numero + 1
        if not isinstance(ficha, dict):
            problemas.append("A torre " + str(numero) + " tem de estar entre { }.")
            continue
        quem = ficha.get("nome")
        if not isinstance(quem, str):
            problemas.append("A torre " + str(numero) + ': o "nome" tem de ser um texto entre aspas.')
            quem = "Torre " + str(numero)
        if not isinstance(ficha.get("tecla"), int):
            problemas.append(quem + ': falta a "tecla", como pygame.K_1.')
        _ver_numeros(ficha, quem, ["custo", "alcance", "dano", "cadencia"], problemas)
        _ver_maximo(ficha, quem, "alcance", 2000, problemas)
        _ver_maximo(ficha, quem, "raio_explosao", 2000, problemas)
        _ver_cor(ficha, quem, problemas)
        _ver_imagem(ficha, quem, problemas)
        efeito = ficha.get("efeito")
        if efeito not in EFEITOS:
            problemas.append(quem + ': o "efeito" tem de ser "tiro", "explosao", "area" ou "golpe".')
        if efeito == "explosao":
            _ver_numeros(ficha, quem, ["raio_explosao"], problemas)
        if efeito == "area":
            _ver_numeros(ficha, quem, ["lentidao"], problemas)
    if len(torres) > 4:
        avisos.append("Só cabem 4 botões na barra de baixo: as outras torres escolhem-se só pela tecla.")


def _andar_pelo_mapa(mapa):
    # O mesmo passeio que o jogo faz em encontrar_caminho(): do E ate ao C.
    # Devolve quantos quadrados andou e se chegou.
    def letra(coluna, linha):
        if 0 <= linha < len(mapa) and 0 <= coluna < len(mapa[linha]):
            return mapa[linha][coluna]
        return " "

    atual = None
    for linha in range(len(mapa)):
        for coluna in range(len(mapa[linha])):
            if mapa[linha][coluna] == "E":
                atual = (coluna, linha)
    visitados = [atual]
    while letra(atual[0], atual[1]) != "C":
        andou = False
        for passo in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            vizinho = (atual[0] + passo[0], atual[1] + passo[1])
            if not andou and letra(vizinho[0], vizinho[1]) in ("#", "E", "C") and vizinho not in visitados:
                atual = vizinho
                visitados.append(atual)
                andou = True
        if not andou:
            return (len(visitados), False)
    return (len(visitados), True)


def _ver_mapa(ns, problemas, avisos):
    mapa = ns.get("MAPA")
    if not isinstance(mapa, list) or len(mapa) == 0:
        problemas.append("O MAPA tem de ser uma lista de linhas, entre [ ].")
        return
    for linha in mapa:
        if not isinstance(linha, str):
            problemas.append("Cada linha do MAPA tem de estar entre aspas e acabar com uma vírgula.")
            return
    tudo = "".join(mapa)
    if tudo.count("E") == 0:
        problemas.append("Falta o E: a entrada por onde os inimigos chegam.")
    if tudo.count("E") > 1:
        problemas.append("Só pode haver um E (uma entrada).")
    if tudo.count("C") == 0:
        problemas.append("Falta o C: o castelo, no fim do caminho.")
    if problemas:
        return
    passos, chegou = _andar_pelo_mapa(mapa)
    if not chegou:
        problemas.append("O caminho não chega ao C. Parou ao fim de " + str(passos) + " quadrados: "
                         "vê se há um buraco, ou se o caminho toca nele próprio.")
    estranhas = sorted(set(tudo) - set(".#ECT"))
    if estranhas:
        avisos.append("Letras que o mapa não conhece (ficam relva onde não se constrói): " + " ".join(estranhas))
    if len(mapa) > 13 or max(len(linha) for linha in mapa) > 20:
        avisos.append("O ecrã só mostra 20 letras de largura e 13 linhas. O resto fica de fora.")


def _ver_regras(ns, problemas, avisos):
    # O jogo chama cada funcao pelo nome e da-lhe sempre as mesmas coisas.
    todas = {}
    for tipo in FUNCOES:
        todas.update(FUNCOES[tipo][0])
    for nome in todas:
        esperado = todas[nome][1]
        funcao = ns.get(nome)
        como = "def " + nome + "(" + ", ".join(esperado) + "):"
        if not inspect.isfunction(funcao):
            problemas.append('"' + nome + '" tem de ser uma função. A primeira linha é: ' + como)
            continue
        recebe = list(inspect.signature(funcao).parameters)
        if len(recebe) != len(esperado):
            problemas.append("A função " + nome + " tem de receber "
                             + (", ".join(esperado) if esperado else "nada, só ( )") + ", nem mais nem menos. "
                             "A primeira linha tem de ser: " + como)


def _torre_de_exemplo(ns, tipo, nivel):
    # Uma torre como as que o jogo faz, para perguntar as regras o que dao.
    custo = ns["TORRES"][tipo]["custo"]
    gasto = custo
    for subida in range(1, nivel):
        gasto = gasto + custo * subida
    return {"tipo": tipo, "coluna": 0, "linha": 0, "x": 100, "y": 100, "nivel": nivel, "gasto": gasto,
            "recarga": 0, "mira": (101, 100)}


def _experimentar(ns, regra, problemas):
    # Uma regra das contas tem de devolver um numero que o jogo perceba.
    def ver(valor, nome, minimo, quando):
        if not _numero(valor):
            problemas.append(nome + " tem de devolver um número: falta um return no fim, ou devolve outra coisa? "
                             "(" + quando + " devolveu " + repr(valor)[:40] + ")")
            return False
        if valor < minimo:
            problemas.append(nome + " não pode devolver menos que " + str(minimo) + " (" + quando + " devolveu "
                             + repr(valor)[:40] + ").")
            return False
        return True

    torre = _torre_de_exemplo(ns, 0, 1)
    quem = ns["TORRES"][0]["nome"]
    if regra == "vida_do_inimigo":
        for nome in ns["INIMIGOS"]:
            for onda in (1, len(ns["ONDAS"])):
                if not ver(ns["vida_do_inimigo"](nome, onda), "vida_do_inimigo", 1, nome + " na onda " + str(onda)):
                    return
    elif regra == "valor_da_torre":
        for chave in ("dano", "alcance"):
            if not ver(ns["valor_da_torre"](torre, chave), "valor_da_torre", 0, 'o "' + chave + '" de ' + quem):
                return
            if chave == "alcance" and ns["valor_da_torre"](_torre_de_exemplo(ns, 0, ns["NIVEL_MAXIMO"]), chave) > 2000:
                problemas.append("valor_da_torre: o alcance é grande demais para o ecrã. O máximo é 2000.")
    elif regra == "custo_melhoria":
        ver(ns["custo_melhoria"](torre), "custo_melhoria", 0, quem)
    elif regra == "valor_de_venda":
        ver(ns["valor_de_venda"](torre), "valor_de_venda", 0, quem)
    elif regra == "premio_da_onda":
        for onda in (1, len(ns["ONDAS"])):
            if not ver(ns["premio_da_onda"](onda), "premio_da_onda", 0, "a onda " + str(onda)):
                return
    elif regra == "pode_construir":
        ns["pode_construir"](0, 0)


# =====================================================================
#                              O PALCO
# =====================================================================

class Palco:

    def __init__(self, escolha):
        tipo, _, numero = escolha.partition(":")
        self.tipo = tipo
        self.numero = int(numero) if numero.isdigit() else 0
        self.preparado = False
        self.espera = 0          # frames ate ao proximo inimigo
        self.vez = 0             # qual o proximo inimigo, quando vem todos
        self.letra = None
        self.regra = numero if tipo in FUNCOES else None
        # Nos acontecimentos e nas ondas o jogo joga-se sozinho, onda atras
        # de onda; nas regras e nos desenhos ha inimigos sempre a passar.
        self.sozinho = tipo in ("evento", "ondas", "onda") or self.regra in COM_ONDAS
        self.passeio = tipo in ("regra", "desenho") and not self.sozinho
        self.pausa_entre_ondas = 0
        self.relogio = 0
        self.contas = []         # as linhas do quadro do canto: (texto, cor)
        if tipo in FUNCOES:
            # Uma regra nova so mostra o que vale quando chega a vez de ser
            # usada (a torre disparar, o golpe acertar): prova-se mais tempo.
            self.quadros_de_prova = 150

    def verificar(self, ns):
        problemas = []
        avisos = []
        _ver_inimigos(ns, problemas, avisos)
        _ver_torres(ns, problemas, avisos)
        _ver_mapa(ns, problemas, avisos)
        _ver_ondas(ns, problemas, avisos, self.tipo in ("onda", "ondas"))
        _ver_regras(ns, problemas, avisos)
        if self.tipo == "regra" and self.preparado and not problemas:
            _experimentar(ns, self.regra, problemas)
        return problemas, avisos

    # --- Preparar e voltar a preparar ---

    def preparar(self, ns, pygame):
        ns["comecar_jogo"]()
        self.letra = pygame.font.SysFont(None, 22)
        self.preparado = True
        self.arrumar(ns)
        if self.passeio:
            self.espalhar_inimigos(ns)
        if self.sozinho:
            ns["ouro"] = 300
        if self.regra in DEPRESSA:
            ns["velocidade_jogo"] = 2

    def ao_mudar(self, ns):
        # O codigo mudou. Os inimigos que andavam no ecra foram feitos com
        # os numeros antigos, por isso saem e vem outros novos.
        if not self.preparado:
            return
        if self.tipo == "mapa":
            ns["CAMINHO_PONTOS"] = ns["encontrar_caminho"]()
        if self.sozinho:
            # O jogo continua como ia. So recomeca a onda quando isso e
            # preciso para se ver a mudanca: as ondas novas desde a primeira,
            # e "quando comeca uma onda" a acontecer outra vez, ja.
            if self.tipo in ("ondas", "onda") or self.regra == "ao_comecar_onda":
                ns["inimigos"] = []
                ns["projeteis"] = []
                ns["a_por_sair"] = []
                ns["onda_a_decorrer"] = False
                ns["numero_onda"] = 0 if self.tipo in ("ondas", "onda") else max(0, ns["numero_onda"] - 1)
                self.pausa_entre_ondas = 0
            self.arrumar(ns)
            return
        ns["inimigos"] = []
        ns["projeteis"] = []
        ns["efeitos"] = []
        self.espera = 0
        self.arrumar(ns)
        if self.passeio:
            self.espalhar_inimigos(ns)

    def espalhar_inimigos(self, ns):
        # Para a regra nova ter logo trabalho: inimigos ja a meio do caminho,
        # ao pe das torres, em vez de esperar que eles la cheguem.
        pontos = ns["CAMINHO_PONTOS"]
        nomes = list(ns["INIMIGOS"])
        for i in range(6):
            indice = min(len(pontos) - 2, int(len(pontos) * (0.08 + 0.13 * i)))
            inimigo = ns["criar_inimigo"](nomes[i % len(nomes)])
            inimigo["x"] = pontos[indice][0]
            inimigo["y"] = pontos[indice][1]
            inimigo["ponto"] = indice + 1
            inimigo["andado"] = indice * ns["TILE"]
            ns["inimigos"].append(inimigo)

    def arrumar(self, ns):
        # Tira as torres que ja nao fazem sentido e garante que ha uma.
        boas = []
        for torre in ns["torres"]:
            if torre["tipo"] < len(ns["TORRES"]) and ns["letra_do_mapa"](torre["coluna"], torre["linha"]) == ".":
                boas.append(torre)
        ns["torres"] = boas
        ns["torre_escolhida"] = None
        if ns["torre_para_construir"] >= len(ns["TORRES"]):
            ns["torre_para_construir"] = 0

        if self.tipo == "mapa":
            return
        if self.passeio or self.sozinho:
            # Uma torre de cada, espalhadas pelo caminho, prontas a disparar.
            for tipo in range(min(4, len(ns["TORRES"]))):
                if len([torre for torre in ns["torres"] if torre["tipo"] == tipo]) == 0:
                    self.construir(ns, tipo, 0.12 + 0.2 * tipo)
            for torre in ns["torres"]:
                torre["recarga"] = min(torre["recarga"], 20)
            return
        minha = 0
        if self.tipo == "torre":
            minha = min(self.numero, len(ns["TORRES"]) - 1)
            ns["torre_para_construir"] = minha
        da_minha = [torre for torre in ns["torres"] if torre["tipo"] == minha]
        if len(da_minha) == 0:
            self.construir(ns, minha)
            da_minha = [torre for torre in ns["torres"] if torre["tipo"] == minha]
        if self.tipo == "torre" and len(da_minha) > 0:
            ns["torre_escolhida"] = da_minha[0]   # fica com o alcance a vista

    def construir(self, ns, tipo, onde=0.25):
        # Procura um quadrado de relva colado ao caminho, mais ou menos a
        # um quarto do percurso (ou "onde", de 0 a 1), e constroi la com a
        # funcao do jogo.
        pontos = ns["CAMINHO_PONTOS"]
        ocupados = [(torre["coluna"], torre["linha"]) for torre in ns["torres"]]
        primeiro = int(len(pontos) * onde)
        for i in range(len(pontos)):
            ponto = pontos[(primeiro + i) % len(pontos)]
            coluna = ponto[0] // ns["TILE"]
            linha = (ponto[1] - ns["TOPO"]) // ns["TILE"]
            for passo in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                c = coluna + passo[0]
                l = linha + passo[1]
                if 0 <= c < 20 and 0 <= l < 13 and ns["letra_do_mapa"](c, l) == "." and (c, l) not in ocupados:
                    antes = ns["torre_para_construir"]
                    ouro = ns["ouro"]
                    ns["torre_para_construir"] = tipo
                    ns["ouro"] = 99999
                    ns["construir"](c, l)
                    ns["torre_para_construir"] = antes
                    if self.sozinho:
                        ns["ouro"] = ouro      # estas torres sao oferta: o ouro fica como estava
                    return

    # --- Todos os frames ---

    def quadro(self, ns, pygame):
        if not self.preparado:
            self.preparar(ns, pygame)

        self.relogio = self.relogio + 1
        if self.sozinho:
            self.jogar_sozinho(ns)
            if self.regra in COM_ONDAS:
                if self.relogio % 30 == 1:
                    self.fazer_contas(ns)
                self.mostrar_contas(ns, pygame)
            return

        # O jogo fica sempre "a meio": sem menu, sem ondas, sem perder.
        ns["estado"] = "jogo"
        ns["ouro"] = 99999
        ns["vidas"] = 99
        ns["numero_onda"] = 1
        ns["onda_a_decorrer"] = False
        ns["a_por_sair"] = []

        if self.regra in DAS_TORRES and len(ns["torres"]) > 0:
            # A primeira torre fica escolhida (com a ficha na barra de baixo)
            # e vai mudando de nivel, para se ver a regra em todos.
            torre = ns["torres"][0]
            nivel = 1 + (self.relogio // 100) % max(1, ns["NIVEL_MAXIMO"])
            if torre["nivel"] != nivel:
                torre["nivel"] = nivel
                torre["gasto"] = _torre_de_exemplo(ns, torre["tipo"], nivel)["gasto"]
            ns["torre_escolhida"] = torre
        if self.tipo == "regra" and self.relogio % 30 == 1:
            self.fazer_contas(ns)

        nomes = list(ns["INIMIGOS"])
        if not ns["pausa"]:
            self.espera = self.espera - ns["velocidade_jogo"]
        if self.espera <= 0:
            if self.tipo == "inimigo":
                nome = nomes[min(self.numero, len(nomes) - 1)]
                iguais = [inimigo for inimigo in ns["inimigos"] if inimigo["nome"] == nome]
                if len(iguais) < 4:
                    ns["inimigos"].append(ns["criar_inimigo"](nome))
                self.espera = 150
            else:
                if len(ns["inimigos"]) < 25:
                    ns["inimigos"].append(ns["criar_inimigo"](nomes[self.vez % len(nomes)]))
                    self.vez = self.vez + 1
                self.espera = 55

        self.desenhar(ns, pygame, nomes)

    def jogar_sozinho(self, ns):
        # O jogo verdadeiro, com as ondas a comecarem sozinhas e sem se
        # perder. O ouro e as vidas ficam como o jogo (e o codigo da
        # crianca) os deixar, e a barra de cima do jogo fica a vista.
        ns["estado"] = "jogo"
        if ns["vidas"] < 5:
            ns["vidas"] = ns["VIDAS_INICIAIS"]
        # Nestes dois acontecimentos faz-se pela crianca o que os faz
        # acontecer: de vez em quando melhora-se, ou vende-se, uma torre.
        if self.regra == "ao_melhorar" and self.relogio % 120 == 0:
            self.melhorar_uma(ns)
        if self.regra == "ao_vender" and self.relogio % 200 == 0:
            self.vender_uma(ns)
        if ns["onda_a_decorrer"]:
            self.pausa_entre_ondas = 0
            return
        self.pausa_entre_ondas = self.pausa_entre_ondas + 1
        if self.pausa_entre_ondas > 50:
            if self.tipo == "onda":
                # Sempre a mesma onda: a que esta aberta.
                ns["numero_onda"] = min(self.numero, len(ns["ONDAS"]) - 1)
            elif ns["numero_onda"] >= len(ns["ONDAS"]):
                ns["numero_onda"] = 0          # acabaram: volta a primeira
            ns["comecar_onda"]()
            self.pausa_entre_ondas = 0

    def melhorar_uma(self, ns):
        # Melhora a primeira torre que ainda nao esta no nivel maximo, com a
        # funcao do jogo (e com ouro que chegue). Quando estao todas, voltam
        # ao nivel 1.
        por_melhorar = [torre for torre in ns["torres"] if torre["nivel"] < ns["NIVEL_MAXIMO"]]
        if len(por_melhorar) == 0:
            for torre in ns["torres"]:
                torre["nivel"] = 1
                torre["gasto"] = ns["TORRES"][torre["tipo"]]["custo"]
            return
        ns["torre_escolhida"] = por_melhorar[0]
        custo = ns["custo_melhoria"](por_melhorar[0])
        if _numero(custo) and custo > 0:
            ns["ouro"] = ns["ouro"] + custo        # a melhoria e oferta: o ouro fica como estava
        ns["melhorar"]()
        ns["torre_escolhida"] = None

    def vender_uma(self, ns):
        # Vende uma torre com a funcao do jogo, e poe outra igual no lugar.
        if len(ns["torres"]) == 0:
            return
        ns["torre_escolhida"] = ns["torres"][(self.relogio // 200) % len(ns["torres"])]
        ns["vender"]()
        self.arrumar(ns)

    def fazer_contas(self, ns):
        # As linhas do quadro do canto: o que a regra aberta responde agora.
        linhas = []
        torres = ns["TORRES"]
        niveis = range(1, min(ns["NIVEL_MAXIMO"], 4) + 1)
        if self.regra == "vida_do_inimigo":
            ultima = len(ns["ONDAS"])
            ondas = sorted({1, max(1, (ultima + 1) // 2), ultima})
            linhas.append(("A vida com que nascem, na onda " + ", ".join(str(onda) for onda in ondas) + ":", ns["AMARELO"]))
            for nome in list(ns["INIMIGOS"])[:6]:
                vidas = [str(ns["vida_do_inimigo"](nome, onda)) for onda in ondas]
                linhas.append((nome + ":  " + "  ·  ".join(vidas), ns["BRANCO"]))
        elif self.regra == "valor_da_torre":
            linhas.append(("O dano e o alcance, em cada nível:", ns["AMARELO"]))
            for tipo in range(min(4, len(torres))):
                partes = []
                for nivel in niveis:
                    torre = _torre_de_exemplo(ns, tipo, nivel)
                    partes.append(_arredondar(ns["valor_da_torre"](torre, "dano")) + "/"
                                  + _arredondar(ns["valor_da_torre"](torre, "alcance")))
                linhas.append((torres[tipo]["nome"] + ":  " + "  ·  ".join(partes), ns["BRANCO"]))
        elif self.regra == "custo_melhoria":
            linhas.append(("Quanto custa subir de nível:", ns["AMARELO"]))
            for tipo in range(min(4, len(torres))):
                partes = [str(nivel) + "→" + str(nivel + 1) + ": "
                          + _arredondar(ns["custo_melhoria"](_torre_de_exemplo(ns, tipo, nivel))) for nivel in list(niveis)[:-1]]
                linhas.append((torres[tipo]["nome"] + ":  " + "  ·  ".join(partes), ns["BRANCO"]))
        elif self.regra == "valor_de_venda":
            linhas.append(("Por quanto se vende, em cada nível:", ns["AMARELO"]))
            for tipo in range(min(4, len(torres))):
                partes = [_arredondar(ns["valor_de_venda"](_torre_de_exemplo(ns, tipo, nivel))) for nivel in niveis]
                linhas.append((torres[tipo]["nome"] + ":  " + "  ·  ".join(partes), ns["BRANCO"]))
        elif self.regra == "premio_da_onda":
            linhas.append(("O ouro de prémio, no fim de cada onda:", ns["AMARELO"]))
            premios = [_arredondar(ns["premio_da_onda"](onda)) for onda in range(1, min(len(ns["ONDAS"]), 12))]
            for inicio in range(0, len(premios), 6):
                linhas.append(("ondas " + str(inicio + 1) + " a " + str(inicio + len(premios[inicio:inicio + 6])) + ":  "
                               + "  ·  ".join(premios[inicio:inicio + 6]), ns["BRANCO"]))
            linhas.append(("(a última não dá prémio: ganha-se o jogo)", ns["CINZA"]))
        elif self.regra == "pode_construir":
            quantos = 0
            for linha in range(len(ns["MAPA"])):
                for coluna in range(len(ns["MAPA"][linha])):
                    if ns["pode_construir"](coluna, linha):
                        quantos = quantos + 1
            linhas.append(("Dá para construir em " + str(quantos) + " quadrados", ns["AMARELO"]))
            linhas.append(("(os que têm um ponto verde)", ns["BRANCO"]))
        self.contas = linhas

    def mostrar_contas(self, ns, pygame):
        # O quadro do canto, por baixo da barra de cima, a direita.
        if len(self.contas) == 0:
            return
        ecra = ns["ecra"]
        desenhos = [self.letra.render(texto, True, cor) for texto, cor in self.contas]
        largura = min(ns["LARGURA"] - 20, 20 + max(desenho.get_width() for desenho in desenhos))
        caixa = pygame.Rect(ns["LARGURA"] - largura - 8, ns["TOPO"] + 8, largura, 10 + 19 * len(desenhos))
        pygame.draw.rect(ecra, ns["PAINEL"], caixa, border_radius=6)
        pygame.draw.rect(ecra, ns["AMARELO"], caixa, 2, border_radius=6)
        y = caixa.y + 6
        for desenho in desenhos:
            ecra.blit(desenho, (caixa.x + 10, y), (0, 0, caixa.width - 20, 19))
            y = y + 19

    def desenhar(self, ns, pygame, nomes):
        ecra = ns["ecra"]
        pygame.draw.rect(ecra, ns["PAINEL"], (0, 0, ns["LARGURA"], ns["TOPO"]))
        pygame.draw.rect(ecra, ns["AMARELO"], (0, 0, 6, ns["TOPO"]))

        texto = ""
        if self.tipo == "inimigo":
            nome = nomes[min(self.numero, len(nomes) - 1)]
            ficha = ns["INIMIGOS"][nome]
            texto = nome + ":   vida " + str(ficha["vida"]) + "   velocidade " + str(ficha["velocidade"])
            texto = texto + "   recompensa " + str(ficha["recompensa"]) + "   estrago " + str(ficha["estrago"])
            modelo = ns["criar_inimigo"](nome)
            self.lupa(ns, pygame, ns["desenhar_inimigo"], modelo, ficha["tamanho"] + 16)
        elif self.tipo == "torre":
            tipo = min(self.numero, len(ns["TORRES"]) - 1)
            ficha = ns["TORRES"][tipo]
            texto = ficha["nome"] + ":   custo " + str(ficha["custo"]) + "   alcance " + str(ficha["alcance"])
            texto = texto + "   dano " + str(ficha["dano"]) + "   cadência " + str(ficha["cadencia"])
            texto = texto + "   efeito " + str(ficha["efeito"])
            modelo = {"tipo": tipo, "nivel": 1, "x": 0, "y": 0, "mira": (1, 0)}
            self.lupa(ns, pygame, ns["desenhar_torre"], modelo, ns["TILE"] + 8)
        elif self.tipo == "desenho":
            texto = "Desenho:   " + DESENHOS[self.regra][0] + "   (a função " + self.regra + ")"
            # No canto, aumentado: um de cada, a vez.
            self.vez_da_lupa = getattr(self, "vez_da_lupa", 0) + 1
            if self.regra == "desenhar_inimigo":
                nome = nomes[(self.vez_da_lupa // 120) % len(nomes)]
                self.lupa(ns, pygame, ns["desenhar_inimigo"], ns["criar_inimigo"](nome), ns["INIMIGOS"][nome]["tamanho"] + 16)
            elif self.regra == "desenhar_projetil":
                # Ora uma seta, ora uma pedra das que rebentam, com a cor de cada torre.
                vez = self.vez_da_lupa // 90
                cor = ns["TORRES"][vez % len(ns["TORRES"])]["cor"]
                modelo = {"x": 0, "y": 0, "alvo": None, "destino_x": 0, "destino_y": 0, "dano": 1,
                          "raio": 55 if vez % 2 == 1 else 0, "velocidade": 5, "cor": cor}
                self.lupa(ns, pygame, ns["desenhar_projetil"], modelo, 28)
            elif self.regra == "desenhar_quadrado":
                # Uma letra do mapa de cada vez, as que o jogo conhece e as que la estiverem.
                letras = []
                for letra in ".#TEC" + "".join(ns["MAPA"]):
                    if letra not in letras:
                        letras.append(letra)
                letra = letras[(self.vez_da_lupa // 90) % len(letras)]
                texto = texto + '      agora: "' + letra + '"'
                self.lupa_livre(ns, pygame, ns["TILE"], lambda: ns["desenhar_quadrado"](letra, 0, 0), sem_topo=True)
            elif self.regra == "desenhar_castelo":
                self.lupa_livre(ns, pygame, 96, lambda: ns["desenhar_castelo"](48, 68))
            else:
                tipo = (self.vez_da_lupa // 120) % len(ns["TORRES"])
                modelo = {"tipo": tipo, "nivel": 1 + (self.vez_da_lupa // 40) % 3, "x": 0, "y": 0, "mira": (1, 0)}
                self.lupa(ns, pygame, ns["desenhar_torre"], modelo, ns["TILE"] + 8)
        elif self.tipo == "regra":
            texto = "Regra:   " + REGRAS[self.regra][0] + "   (a função " + self.regra + ")"
            # Um circulo a volta de quem cada torre escolheu agora.
            for torre in ns["torres"]:
                alvo = ns["escolher_alvo"](torre)
                if isinstance(alvo, dict) and "x" in alvo and "y" in alvo:
                    pygame.draw.circle(ecra, ns["AMARELO"], (int(alvo["x"]), int(alvo["y"])), 16, 2)
            if self.regra == "pode_construir":
                # Um ponto verde em cada quadrado onde a regra deixa construir.
                for linha in range(len(ns["MAPA"])):
                    for coluna in range(len(ns["MAPA"][linha])):
                        if ns["pode_construir"](coluna, linha):
                            centro = (coluna * ns["TILE"] + ns["TILE"] // 2, ns["TOPO"] + linha * ns["TILE"] + ns["TILE"] // 2)
                            pygame.draw.circle(ecra, ns["PRETO"], centro, 5)
                            pygame.draw.circle(ecra, ns["VERDE"], centro, 4)
            self.mostrar_contas(ns, pygame)
        elif self.tipo == "mapa":
            mapa = ns["MAPA"]
            texto = "Mapa:   " + str(max(len(linha) for linha in mapa)) + " letras de largura   "
            texto = texto + str(len(mapa)) + " linhas   caminho com " + str(len(ns["CAMINHO_PONTOS"])) + " quadrados"

        desenho = self.letra.render(texto, True, ns["BRANCO"])
        ecra.blit(desenho, (18, 12))

    def lupa(self, ns, pygame, desenhar, modelo, lado):
        # Desenha a coisa numa folha pequena, com a funcao do proprio jogo,
        # e mostra essa folha aumentada no canto.
        lado = int(max(24, min(lado, 110)))
        folha = pygame.Surface((lado, lado))
        folha.fill(ns["RELVA"])
        modelo["x"] = lado // 2
        modelo["y"] = lado // 2
        if "mira" in modelo:
            modelo["mira"] = (lado, lado // 2)
        ecra = ns["ecra"]
        ns["ecra"] = folha
        try:
            desenhar(modelo)
        finally:
            ns["ecra"] = ecra
        grande = pygame.transform.scale(folha, (110, 110))
        caixa = pygame.Rect(ns["LARGURA"] - 122, ns["TOPO"] + 8, 114, 114)
        pygame.draw.rect(ecra, ns["PAINEL"], caixa.inflate(6, 6), border_radius=6)
        ecra.blit(grande, (caixa.x + 2, caixa.y + 2))
        pygame.draw.rect(ecra, ns["AMARELO"], caixa.inflate(6, 6), 2, border_radius=6)


    def lupa_livre(self, ns, pygame, lado, desenhar, sem_topo=False):
        # Como a lupa, para os desenhos que nao recebem uma coisa com x e y:
        # "desenhar" desenha numa folha com esse lado, e mostra-se aumentada.
        # sem_topo: o desenho conta a partir da barra de cima (um quadrado do
        # mapa), por isso a barra tira-se enquanto ele se faz.
        folha = pygame.Surface((lado, lado))
        folha.fill(ns["RELVA"])
        ecra = ns["ecra"]
        topo = ns["TOPO"]
        ns["ecra"] = folha
        if sem_topo:
            ns["TOPO"] = 0
        try:
            desenhar()
        finally:
            ns["ecra"] = ecra
            ns["TOPO"] = topo
        grande = pygame.transform.scale(folha, (110, 110))
        caixa = pygame.Rect(ns["LARGURA"] - 122, ns["TOPO"] + 8, 114, 114)
        pygame.draw.rect(ecra, ns["PAINEL"], caixa.inflate(6, 6), border_radius=6)
        ecra.blit(grande, (caixa.x + 2, caixa.y + 2))
        pygame.draw.rect(ecra, ns["AMARELO"], caixa.inflate(6, 6), 2, border_radius=6)


def _arredondar(valor):
    # 10.5 fica "10.5", 14.0 fica "14": para o quadro das contas.
    if _numero(valor):
        return "%g" % round(valor, 1)
    return str(valor)[:12]


def criar_palco(escolha):
    return Palco(escolha)
