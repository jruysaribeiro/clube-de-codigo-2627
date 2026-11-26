# As batalhas da Bicharada na Oficina: os bichos, os ataques, os treinadores
# e os tipos. Que coisas se podem escolher, onde esta o codigo de cada uma,
# e o "palco" que mostra so essa coisa a funcionar.
#
# ESTE FICHEIRO JA NAO E UM JOGO DA OFICINA. Era o da Bicharada (s12), que
# saiu do repositorio. Ficou porque a Bicharada a Solta (bicharada_a_solta.py,
# aqui ao lado) e feita em cima dele: tudo o que e da batalha vem daqui.
#
# O palco nao e um jogo a parte: e o jogo verdadeiro, ja dentro de uma
# batalha (sem menu e sem mapa), com a equipa que interessa para ver a coisa
# escolhida. Quando a batalha acaba, comeca outra igual.
#
# Nas regras, nos acontecimentos e nos desenhos (que sao funcoes do jogo) a
# batalha joga-se sozinha, turno atras de turno, para se ver logo o que a
# funcao nova faz.

import ast
import difflib
import inspect
import random
import re

import blocos


# Uma frase por grupo, para a pagina do jogo dizer o que la ha.
SOBRE_OS_GRUPOS = {
    "Bichos": "Tipo, vida, ataque, forma, cor. Podes pôr uma imagem tua.",
    "Ataques": "O poder, a precisão e o efeito de cada ataque.",
    "Treinadores": "Quem enfrentas, o que dizem e que bichos levam.",
    "Tipos": "Cada tipo e a cor dele, e quem é forte contra quem.",
    "Regras do jogo": "Aqui mudas a maneira como a batalha se comporta: é programar a sério.",
    "Acontecimentos": "Estão vazios: o que lá escreveres passa a acontecer nesse momento. É aqui que se inventa.",
    "Desenhos": "Como se desenha um bicho e a barra de vida, com círculos, retângulos e linhas.",
}

# Os grupos onde se pode criar uma coisa nova, e o que diz o botao.
CRIAVEIS = {"Bichos": "Novo bicho", "Ataques": "Novo ataque", "Treinadores": "Novo treinador", "Tipos": "Novo tipo"}

# Pedidos ja escritos para o ajudante, para se perceber o que se pode pedir.
SUGESTOES = {
    "bicho": ["Põe-no mais rápido mas com menos vida", "Muda-lhe a cor para roxo", "O que quer dizer cada número?"],
    "ataque": ["Faz este ataque mais forte, mas a falhar mais vezes", "Muda-lhe o tipo para fogo", "O que faz o efeito?"],
    "treinador": ["Põe os bichos dele dois níveis acima", "Muda-lhe a frase para uma mais assustadora",
                  "Como é que lhe dou mais um bicho?"],
    "tipo": ["Muda-lhe a cor para um tom mais escuro", "Para que serve a cor de um tipo?",
             "Como é que digo contra quem este tipo é forte?"],
    "tipos:normal": ["O que quer dizer isto?", "Que tipos é que há?", "O que muda se eu puser aqui outro tipo?"],
    "tipos:cores": ["Muda a cor do tipo agua para um azul mais escuro", "Acrescenta um tipo novo chamado pedra, cinzento",
                    "Para que servem estas cores?"],
    "tipos:eficacia": ["Faz o fogo bater o triplo na planta", "Faz a planta bater o dobro no fogo",
                       "Como é que se lê esta tabela?"],
    "calcular_dano": ["Um bicho com menos de metade da vida bate o dobro", "Tira a sorte: o mesmo ataque tira sempre o mesmo",
                      "Explica-me esta função linha a linha"],
    "golpe_critico": ["Faz sair um golpe crítico 1 vez em cada 4", "Golpe crítico garantido quando quem ataca tem pouca vida",
                      "Explica-me esta função linha a linha"],
    "xp_para_subir": ["Faz os bichos subirem de nível duas vezes mais depressa",
                      "Até ao nível 7 é fácil subir, depois é muito difícil", "Explica-me esta função linha a linha"],
    "quem_ataca_primeiro": ["Faz ir primeiro o bicho que tem menos vida", "Faz ser sempre ao calhas",
                            "Explica-me esta função linha a linha"],
    "escolher_ataque_inimigo": ["Faz o inimigo escolher um ataque completamente ao calhas",
                                "Faz o inimigo escolher sempre o ataque com mais poder",
                                "Explica-me esta função linha a linha"],
    "ao_comecar_batalha": ["Mostra uma frase minha no início de cada batalha",
                           "O meu primeiro bicho começa com o ataque mais forte", "O que posso fazer aqui?"],
    "ao_acertar": ["Faz um bicho vampiro: quem ataca recupera metade do dano que fez",
                   "Diz «Que pancada!» quando o golpe tira mais de 20", "O que posso fazer aqui?"],
    "ao_desmaiar": ["Quando um bicho desmaia, o vencedor recupera 10 de vida",
                    "Conta quantos bichos já desmaiaram e diz o número", "O que posso fazer aqui?"],
    "ao_subir_de_nivel": ["Quando sobe de nível, o bicho fica com a vida toda", "Ganha-se uma sopa ao subir de nível",
                          "O que posso fazer aqui?"],
    "ao_ganhar_batalha": ["Dá 30 de experiência de prémio ao meu bicho em campo", "Conta as vitórias e diz quantas já vão",
                          "O que posso fazer aqui?"],
    "ao_carregar_tecla": ["A tecla S dá mais uma sopa", "A tecla C cura o meu bicho, mas só uma vez por jogo",
                          "O que posso fazer aqui?"],
    "desenhar_bicho": ["Faz o bicho respirar mais depressa", "Faz o bicho ficar mais pequeno quando tem pouca vida",
                       "Explica-me este desenho linha a linha"],
    "desenhar_corpo": ["Põe um chapéu em cima do corpo", "Acrescenta uma boca por baixo dos olhos",
                       "Explica-me este desenho linha a linha"],
    "desenhar_olhos": ["Faz os olhos maiores", "Põe uma sobrancelha zangada por cima de cada olho",
                       "Explica-me este desenho linha a linha"],
    "desenhar_barra_vida": ["Faz a barra mais grossa", "Faz a barra ficar azul quando a vida está cheia",
                            "Explica-me este desenho linha a linha"],
}

# As regras: funcoes do jogo que se podem mudar. Para cada uma, o titulo que
# aparece na Oficina, e o que ela recebe (o jogo chama-a assim, por isso nao
# pode mudar).
REGRAS = {
    "calcular_dano": ("Quanto magoa um ataque", ["atacante", "alvo", "ataque"]),
    "golpe_critico": ("Quando sai um golpe crítico", ["atacante", "alvo"]),
    "quem_ataca_primeiro": ("Quem ataca primeiro", ["eu", "inimigo"]),
    "escolher_ataque_inimigo": ("Que ataque o inimigo escolhe", []),
    "xp_para_subir": ("Quanta experiência é precisa para subir de nível", ["bicho"]),
}
INICIO_DAS_REGRAS = "# --- As regras do jogo ---"

# Os acontecimentos: funcoes que o jogo chama em certos momentos, e que vem
# vazias. E os desenhos. Tudo isto sao funcoes, como as regras.
ACONTECIMENTOS = {
    "ao_comecar_batalha": ("Quando começa uma batalha", []),
    "ao_acertar": ("Quando um ataque acerta", ["atacante", "alvo", "dano"]),
    "ao_desmaiar": ("Quando um bicho desmaia", ["desmaiado", "vencedor"]),
    "ao_subir_de_nivel": ("Quando um bicho teu sobe de nível", ["bicho"]),
    "ao_ganhar_batalha": ("Quando ganhas uma batalha", []),
    "ao_carregar_tecla": ("Quando se carrega numa tecla", ["tecla"]),
}
INICIO_DOS_ACONTECIMENTOS = "# --- Os acontecimentos ---"
DESENHOS = {
    "desenhar_bicho": ("O bicho inteiro: respirar, tremer", ["bicho", "cx", "cy", "tamanho", "olha_para"]),
    "desenhar_corpo": ("O corpo de um bicho", ["bicho", "cor", "cx", "cy", "tamanho"]),
    "desenhar_olhos": ("Os olhos de um bicho", ["bicho", "cx", "cy", "tamanho", "olha_para"]),
    "desenhar_barra_vida": ("A barra de vida", ["bicho", "x", "y", "largura"]),
}
INICIO_DOS_DESENHOS = "# --- Os desenhos ---"

# tipo da escolha -> (as funcoes desse tipo, o grupo onde aparecem, as
# explicacoes gerais que se juntam a ajuda de cada uma)
FUNCOES = {
    "regra": (REGRAS, "Regras do jogo", [INICIO_DAS_REGRAS]),
    "evento": (ACONTECIMENTOS, "Acontecimentos", [INICIO_DOS_ACONTECIMENTOS, INICIO_DAS_REGRAS]),
    "desenho": (DESENHOS, "Desenhos", [INICIO_DOS_DESENHOS]),
}

# Nestes, os bichos do inimigo comecam com pouca vida, para o que interessa
# (um bicho desmaiar, o teu subir de nivel, ganhares) acontecer depressa.
COM_PRESSA = ["ao_desmaiar", "ao_subir_de_nivel", "ao_ganhar_batalha", "xp_para_subir"]

FORMAS = ["circulo", "quadrado", "triangulo", "gota"]
EFEITOS = ["dano", "cura", "sobe_ataque", "sobe_defesa", "baixa_ataque", "baixa_defesa"]

TECLAS = " Setas e Enter para jogar, Esc para voltar atrás."
SOZINHO = (" A batalha joga-se sozinha. Se clicares no jogo e carregares numa tecla,"
           " ela espera uns segundos e deixa-te jogar a ti.")

DICAS = {
    "bicho": "O teu bicho é o de baixo, e os ataques dele estão à vista."
             " Muda um número e vê a ficha lá em cima." + TECLAS,
    "ataque": "O teu bicho já tem este ataque escolhido: carrega em Enter para o usar."
              " Com precisão baixa falha muitas vezes."
              ' Para lhe dares um som, acrescenta à ficha "som": "nome.wav".' + TECLAS,
    "treinador": "A batalha é contra este treinador: lê o nome e a frase dele no início."
                 " Enter passa o texto à frente." + TECLAS,
    "tipo": "A cor deste tipo aparece nos menus e nas etiquetas lá em cima. Para lhe mudares o nome usa o"
            " botão «Mudar o nome», que acerta os bichos e os ataques que são deste tipo."
            " Contra quem ele é forte diz-se em «Quem é forte contra quem»." + TECLAS,
    "tipos": "A tabela do meio diz quem é forte contra quem: a linha ataca, a coluna leva."
             " Levas um bicho de cada tipo para experimentar." + TECLAS,
    "regra": "Isto é uma regra do jogo: muda-a e a batalha passa a comportar-se de outra maneira."
             " O quadro do meio mostra as contas que a tua regra faz agora." + SOZINHO,
    "evento": "Tira o pass e escreve o que queres que aconteça nesse momento."
              " O quadro do meio mostra o que tens na memoria." + SOZINHO,
    "desenho": "Isto é o desenho: muda-o e vês logo, na batalha e em todos os bichos lá em cima."
               " Um bicho que tenha imagem mostra a imagem, e não este desenho." + SOZINHO,
}

# id da escolha -> (nome da instrucao no ficheiro, titulo)
TIPOS = {
    "tipos:cores": ("CORES_TIPO", "As cores dos tipos"),
    "tipos:eficacia": ("EFICACIA", "Quem é forte contra quem"),
    "tipos:normal": ("TIPO_NORMAL", "O tipo que todos podem aprender"),
}
# Um bicho so sabe ataques do tipo dele, ou do tipo "de todos": o que o jogo
# disser em TIPO_NORMAL ou, se nao disser nada, o que se chama "normal".
TIPO_DE_TODOS = "normal"
# As cores para um tipo novo, por ordem: a primeira que ainda nao estiver usada.
CORES_PARA_TIPOS = [(150, 150, 165), (240, 210, 70), (110, 210, 230), (120, 90, 170), (200, 150, 100), (230, 130, 190)]


def _tipo_de_todos(arvore):
    no = blocos.instrucao(arvore, "TIPO_NORMAL")
    if no is not None and blocos.texto_constante(no.value) is not None:
        return blocos.texto_constante(no.value)
    return TIPO_DE_TODOS


# =====================================================================
#                    ONDE ESTA O CODIGO DE CADA COISA
# =====================================================================

def _fichas(no):
    # As fichas de um dicionario {"nome": {...}, ...} ou de uma lista
    # [{...}, ...] escritos no codigo: [(nome, ficha, primeira, ultima), ...].
    # O nome e None quando a ficha vem de uma lista.
    if no is None:
        return []
    partes = blocos.entradas(no)
    if not partes:
        return []
    if isinstance(no.value, ast.Dict):
        valores = no.value.values
        return [(blocos.texto_constante(chave), valor, primeira, ultima)
                for (chave, primeira, ultima), valor in zip(partes, valores)]
    return [(None, elemento, primeira, ultima) for elemento, primeira, ultima in partes]


def escolhas(fonte):
    arvore = ast.parse(fonte)
    lista = []

    numero = 0
    for nome, _, _, _ in _fichas(blocos.instrucao(arvore, "BICHOS")):
        lista.append({"id": "bicho:" + str(numero), "grupo": "Bichos",
                      "titulo": nome or "Bicho " + str(numero + 1)})
        numero = numero + 1

    numero = 0
    for nome, _, _, _ in _fichas(blocos.instrucao(arvore, "ATAQUES")):
        lista.append({"id": "ataque:" + str(numero), "grupo": "Ataques",
                      "titulo": nome or "Ataque " + str(numero + 1)})
        numero = numero + 1

    numero = 0
    for _, ficha, _, _ in _fichas(blocos.instrucao(arvore, "TREINADORES")):
        nome = blocos.valor_da_chave(ficha, "nome")
        lista.append({"id": "treinador:" + str(numero), "grupo": "Treinadores",
                      "titulo": nome or "Treinador " + str(numero + 1)})
        numero = numero + 1

    # Cada tipo abre sozinho (a linha dele em CORES_TIPO). Se as cores nao
    # estiverem escritas uma por linha, abre-se o dicionario inteiro.
    cores = _fichas(blocos.instrucao(arvore, "CORES_TIPO"))
    numero = 0
    for nome, _, _, _ in cores:
        lista.append({"id": "tipo:" + str(numero), "grupo": "Tipos", "titulo": nome or "Tipo " + str(numero + 1)})
        numero = numero + 1
    for escolha, (instrucao, titulo) in TIPOS.items():
        if escolha == "tipos:cores" and cores:
            continue
        if blocos.instrucao(arvore, instrucao) is not None:
            lista.append({"id": escolha, "grupo": "Tipos", "titulo": titulo})

    for tipo in FUNCOES:
        funcoes, grupo, _ = FUNCOES[tipo]
        for nome in funcoes:
            if blocos.funcao(arvore, nome) is not None:
                lista.append({"id": tipo + ":" + nome, "grupo": grupo, "titulo": funcoes[nome][0]})
    return lista


def regiao(fonte, escolha):
    # Devolve {"inicio", "fim", "ajuda", "titulo", "dica", "imagem", "som",
    # "sugestoes"} ou None. "imagem" e o nome do PNG escrito na ficha de um
    # bicho, e "som" o nome do WAV escrito na ficha de um bicho ou de um
    # ataque: e com eles que a Oficina sabe onde guardar o que a crianca
    # escolher. Nas outras coisas ficam None.
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
        return {"inicio": no.lineno, "fim": no.end_lineno, "ajuda": ajuda, "dica": DICAS[tipo],
                "titulo": funcoes[numero][0], "imagem": None, "som": None, "sugestoes": SUGESTOES[numero]}

    if escolha in TIPOS:
        instrucao, titulo = TIPOS[escolha]
        no = blocos.instrucao(arvore, instrucao)
        if no is None:
            return None
        return {"inicio": no.lineno, "fim": no.end_lineno, "titulo": titulo, "imagem": None, "som": None,
                "ajuda": blocos.ajuda_acima(linhas, no.lineno), "dica": DICAS["tipos"],
                "sugestoes": SUGESTOES[escolha]}

    nomes = {"bicho": "BICHOS", "ataque": "ATAQUES", "treinador": "TREINADORES", "tipo": "CORES_TIPO"}
    if tipo not in nomes:
        return None
    no = blocos.instrucao(arvore, nomes[tipo])
    partes = _fichas(no)
    if not numero.isdigit() or int(numero) >= len(partes):
        return None
    nome, ficha, inicio, fim = partes[int(numero)]
    if tipo == "tipo":
        return {"inicio": inicio, "fim": fim, "titulo": nome or escolha, "imagem": None, "som": None,
                "ajuda": blocos.ajuda_acima(linhas, no.lineno), "dica": DICAS["tipo"], "sugestoes": SUGESTOES["tipo"],
                "apagar": "Apagar este tipo", "renomear": "Mudar o nome"}
    imagem = None
    som = None
    if tipo == "bicho":
        imagem = blocos.valor_da_chave(ficha, "imagem")
    if tipo == "bicho" or tipo == "ataque":
        som = blocos.valor_da_chave(ficha, "som")
    if tipo == "treinador":
        nome = blocos.valor_da_chave(ficha, "nome")
    # Estas coisas podem ser apagadas, e os bichos de um treinador
    # escolhem-se de uma lista: o que vai aqui e o que dizem esses botoes na
    # Oficina.
    return {"inicio": inicio, "fim": fim, "titulo": nome or escolha, "imagem": imagem, "som": som,
            "ajuda": blocos.ajuda_acima(linhas, no.lineno), "dica": DICAS[tipo], "sugestoes": SUGESTOES[tipo],
            "apagar": "Apagar este " + tipo,
            # (Mudar o nome a um bicho ou a um ataque acerta quem o usava.)
            "renomear": "Mudar o nome" if tipo in ("bicho", "ataque") else None,
            "lista": {"treinador": "Escolher os bichos", "bicho": "Escolher os ataques"}.get(tipo)}


# =====================================================================
#                        CRIAR UMA COISA NOVA
# =====================================================================
# Um bicho, um ataque ou um treinador novos nascem como copia do primeiro
# que la esta, com outro nome, e ficam no fim da lista. (Um ataque novo nao
# fica com nenhum bicho.) Devolve o ficheiro
# inteiro ja com a coisa nova, a escolha a abrir, e uma frase a contar o que
# se fez.

def _nome_livre(base, existentes):
    nome = base
    numero = 2
    while nome in existentes:
        nome = base + " " + str(numero)
        numero = numero + 1
    return nome


def _ficheiro(nome):
    # "Bicho novo 2" -> "bicho-novo-2"
    return nome.lower().replace(" ", "-")


def _coluna(linha, bytes_ate_la):
    # O Python conta as colunas em bytes: com acentos nao e o mesmo que letras.
    return len(linha.encode("utf-8")[:bytes_ate_la].decode("utf-8"))


def _copiar_ficha(linhas, inicio, fim, antigo, nome, ultima):
    # As linhas de uma ficha, outra vez, com o nome, a imagem e o som novos.
    # "ultima" e a linha onde acaba a ultima ficha: a copia vai a seguir.
    texto = "\n".join(linhas[inicio - 1:fim])
    texto = texto.replace('"' + antigo + '"', '"' + nome + '"', 1)
    # (Ficheiros so dela: ve o corpo_livre, no blocos.py.)
    corpo = blocos.corpo_livre("\n".join(linhas), _ficheiro(nome), (".png", "-costas.png", ".wav"))
    texto = re.sub(r'"imagem": "[^"]*"', '"imagem": "' + corpo + '.png"', texto)
    texto = re.sub(r'"som": "[^"]*"', '"som": "' + corpo + '.wav"', texto)
    if not texto.rstrip().endswith(","):
        texto = texto.rstrip() + ","
    if not linhas[ultima - 1].rstrip().endswith(","):
        linhas[ultima - 1] = linhas[ultima - 1].rstrip() + ","
    return texto.split("\n")


def _novo_tipo(fonte):
    # Uma linha nova em CORES_TIPO e outra, ainda vazia, em EFICACIA.
    arvore = ast.parse(fonte)
    linhas = fonte.split("\n")
    cores = _fichas(blocos.instrucao(arvore, "CORES_TIPO"))
    if not cores:
        raise ValueError("não percebi como está escrito CORES_TIPO no ficheiro.")
    nome = _nome_livre("tipo novo", [parte[0] for parte in cores])
    usadas = [linhas[parte[2] - 1].replace(" ", "") for parte in cores]
    cor = CORES_PARA_TIPOS[0]
    for candidata in CORES_PARA_TIPOS:
        if not any(str(candidata).replace(" ", "") in usada for usada in usadas):
            cor = candidata
            break
    juntar = [(cores[-1][3], '    "' + nome + '": ' + str(cor) + ",")]
    tabela = _fichas(blocos.instrucao(arvore, "EFICACIA"))
    if tabela:
        juntar.append((tabela[-1][3], '    "' + nome + '": {},'))
    for ultima, linha in sorted(juntar, reverse=True):        # de baixo para cima
        if not linhas[ultima - 1].rstrip().endswith(","):
            linhas[ultima - 1] = linhas[ultima - 1].rstrip() + ","
        linhas[ultima:ultima] = [linha]
    aviso = ('Criei o tipo "' + nome + '". Muda-lhe o nome (com o botão «Mudar o nome») e a cor.'
             " Em «Quem é forte contra quem» dizes contra quem ele bate mais.")
    return "\n".join(linhas), "tipo:" + str(len(cores)), aviso


def novo(fonte, grupo):
    if grupo == "Tipos":
        return _novo_tipo(fonte)
    arvore = ast.parse(fonte)
    linhas = fonte.split("\n")
    nomes = {"Bichos": "BICHOS", "Ataques": "ATAQUES", "Treinadores": "TREINADORES"}
    if grupo not in nomes:
        raise ValueError("aqui não dá para criar isso.")
    partes = _fichas(blocos.instrucao(arvore, nomes[grupo]))
    if not partes:
        raise ValueError("não encontrei " + nomes[grupo] + " no ficheiro.")
    antigo, ficha, inicio, fim = partes[0]
    ultima = partes[-1][3]
    existentes = [parte[0] for parte in partes]
    if grupo == "Treinadores":
        antigo = blocos.valor_da_chave(ficha, "nome")
        existentes = [blocos.valor_da_chave(parte[1], "nome") for parte in partes]
    if antigo is None:
        raise ValueError("não percebi o nome do primeiro que lá está.")

    if grupo == "Bichos":
        nome = _nome_livre("Bicho novo", existentes)
        copia = _copiar_ficha(linhas, inicio, fim, antigo, nome, ultima)
        aviso = ('Criei o "' + nome + '", igual ao ' + antigo + ". Muda-lhe o nome e os números."
                 " No jogo inteiro já aparece no ecrã de escolha.")
        return "\n".join(linhas[:ultima] + copia + linhas[ultima:]), "bicho:" + str(len(partes)), aviso

    if grupo == "Treinadores":
        nome = _nome_livre("Treinador novo", existentes)
        copia = _copiar_ficha(linhas, inicio, fim, antigo, nome, ultima)
        aviso = ('Criei o "' + nome + '", igual a ' + antigo + ". Muda-lhe o nome, a frase e a equipa."
                 " No jogo inteiro é o último da feira: aparece depois de ganhares aos outros.")
        return "\n".join(linhas[:ultima] + copia + linhas[ultima:]), "treinador:" + str(len(partes)), aviso

    # Um ataque novo nao e de nenhum bicho: da-se a quem se quiser, na ficha
    # do bicho, com o botao "Escolher os ataques".
    nome = _nome_livre("Ataque novo", existentes)
    copia = _copiar_ficha(linhas, inicio, fim, antigo, nome, ultima)
    if '"som"' not in "\n".join(copia) and copia[-1].rstrip().endswith("},"):
        copia[-1] = (copia[-1].rstrip()[:-2] + ', "som": "'
                     + blocos.corpo_livre("\n".join(linhas), _ficheiro(nome), (".wav",)) + '.wav"},')
    aviso = ('Criei o "' + nome + '", igual a ' + antigo + ". Muda-lhe o nome e os números."
             " Ainda nenhum bicho o tem: abre um bicho e carrega em «Escolher os ataques».")
    return "\n".join(linhas[:ultima] + copia + linhas[ultima:]), "ataque:" + str(len(partes)), aviso


# =====================================================================
#                          APAGAR UMA COISA
# =====================================================================
# Um bicho, um ataque ou um treinador saem do jogo e dos sitios onde eram
# usados: o bicho sai das equipas dos treinadores, o ataque sai dos ataques
# dos bichos. Quem ficaria sem nada (um treinador sem bichos, um bicho sem
# ataques) fica com outro, para o jogo nao parar. Devolve o ficheiro inteiro
# ja sem a coisa, e uma frase a contar o que se fez.

def _lista_da_chave(ficha, chave):
    # Dentro de um {...} escrito no codigo, a lista [...] guardada em "chave".
    if isinstance(ficha, ast.Dict):
        for k, v in zip(ficha.keys, ficha.values):
            if blocos.texto_constante(k) == chave and isinstance(v, ast.List):
                return v
    return None


def _no_da_chave(ficha, chave):
    for k, v in zip(ficha.keys, ficha.values):
        if blocos.texto_constante(k) == chave:
            return v
    return None


# As mudancas ao ficheiro juntam-se em duas listas e fazem-se todas no fim,
# de baixo para cima, para os numeros das linhas nao mudarem a meio:
#   cortes   linhas inteiras que saem: (primeira, ultima)
#   trocas   bocados de uma linha: (linha, de, ate, texto novo)

def _trocar_no(linhas, no, texto, trocas):
    # O que esta escrito num no (de uma linha so) passa a ser "texto".
    linha = linhas[no.lineno - 1]
    trocas.append((no.lineno, _coluna(linha, no.col_offset), _coluna(linha, no.end_col_offset), texto))


def _tirar_da_lista(linhas, elemento, cortes, trocas):
    # Tira um elemento de uma lista [...] escrita no codigo, com a virgula
    # dele. Diz se conseguiu (nao consegue se estiver escrito em varias
    # linhas misturado com outros).
    primeira = linhas[elemento.lineno - 1]
    de = _coluna(primeira, elemento.col_offset)
    ate = _coluna(linhas[elemento.end_lineno - 1], elemento.end_col_offset)
    antes = primeira[:de].strip()
    depois = linhas[elemento.end_lineno - 1][ate:].strip()
    if antes == "" and depois in ("", ","):
        cortes.append((elemento.lineno, elemento.end_lineno))      # esta sozinho nas linhas dele
        return True
    if elemento.lineno != elemento.end_lineno:
        return False
    virgula = re.match(r"\s*,\s*", primeira[ate:])
    if virgula:
        ate = ate + virgula.end()
    else:
        virgula = re.search(r",\s*$", primeira[:de])
        if virgula:
            de = virgula.start()
    trocas.append((elemento.lineno, de, ate, ""))
    return True


def _aplicar(linhas, cortes, trocas):
    for linha, de, ate, texto in sorted(trocas, reverse=True):
        linhas[linha - 1] = linhas[linha - 1][:de] + texto + linhas[linha - 1][ate:]
    for primeira, ultima in sorted(cortes, reverse=True):
        del linhas[primeira - 1:ultima]
    return "\n".join(linhas)


def _e_de(nomes):
    # ["A", "B", "C"] -> "A, de B e de C"
    if len(nomes) == 1:
        return nomes[0]
    return ", de ".join(nomes[:-1]) + " e de " + nomes[-1]


class _Bocado:
    # Um bocado de uma linha do codigo, do inicio de uma coisa ao fim de outra
    # (uma chave de um dicionario e o valor dela, por exemplo).
    def __init__(self, inicio, fim):
        self.lineno, self.col_offset = inicio.lineno, inicio.col_offset
        self.end_lineno, self.end_col_offset = fim.end_lineno, fim.end_col_offset


def _usos_do_tipo(arvore, nome):
    # Onde um tipo esta escrito, fora de CORES_TIPO:
    #   fichas    os nos do "tipo" dos bichos e dos ataques que sao desse tipo
    #   linha     as linhas da fila dele em EFICACIA, ou None
    #   chave     o no do nome dele nessa fila
    #   alvos     [(a chave, o valor)] onde ele aparece nas filas dos outros
    #   de_todos  o no do valor de TIPO_NORMAL, se for ele
    usos = {"fichas": [], "quantos": {"BICHOS": 0, "ATAQUES": 0}, "linha": None, "chave": None, "alvos": [],
            "de_todos": None}
    for instrucao in ("BICHOS", "ATAQUES"):
        for _, ficha, _, _ in _fichas(blocos.instrucao(arvore, instrucao)):
            no = _no_da_chave(ficha, "tipo") if isinstance(ficha, ast.Dict) else None
            if no is not None and blocos.texto_constante(no) == nome and no.lineno == no.end_lineno:
                usos["fichas"].append(no)
                usos["quantos"][instrucao] += 1
    tabela = blocos.instrucao(arvore, "EFICACIA")
    for atacante, fila, primeira, ultima in _fichas(tabela):
        chave = [k for k in tabela.value.keys if blocos.texto_constante(k) == atacante][0]
        if atacante == nome:
            usos["linha"], usos["chave"] = (primeira, ultima), chave
        for alvo, valor in zip(fila.keys, fila.values) if isinstance(fila, ast.Dict) else []:
            if blocos.texto_constante(alvo) == nome:
                usos["alvos"].append((alvo, valor))
    no = blocos.instrucao(arvore, "TIPO_NORMAL")
    if no is not None and blocos.texto_constante(no.value) == nome:
        usos["de_todos"] = no.value
    return usos


def _apagar_tipo(fonte, numero):
    arvore = ast.parse(fonte)
    linhas = fonte.split("\n")
    cores = _fichas(blocos.instrucao(arvore, "CORES_TIPO"))
    if not numero.isdigit() or int(numero) >= len(cores):
        raise ValueError("isso não se pode apagar.")
    nome, _, inicio, fim = cores[int(numero)]
    de_todos = _tipo_de_todos(arvore)
    if nome == de_todos:
        raise ValueError('o tipo "' + str(nome) + '" é o que todos podem aprender: é para ele que vão os bichos e '
                         "os ataques dos tipos que se apagam. Não se pode apagar.")
    if len(cores) < 2:
        raise ValueError("tem de haver pelo menos um tipo.")
    usos = _usos_do_tipo(arvore, nome)
    cortes = [(inicio, fim)]
    trocas = []
    for no in usos["fichas"]:                       # os bichos e os ataques dele passam para o tipo de todos
        _trocar_no(linhas, no, '"' + de_todos + '"', trocas)
    if usos["linha"] is not None:
        cortes.append(usos["linha"])
    for alvo, valor in usos["alvos"]:
        dentro = usos["linha"] is not None and usos["linha"][0] <= alvo.lineno <= usos["linha"][1]
        if not dentro:
            _tirar_da_lista(linhas, _Bocado(alvo, valor), cortes, trocas)
    aviso = 'Apaguei o tipo "' + str(nome) + '".'
    bichos, ataques = usos["quantos"]["BICHOS"], usos["quantos"]["ATAQUES"]
    if bichos or ataques:
        aviso = (aviso + " Os bichos e os ataques que eram desse tipo (" + str(bichos) + " e " + str(ataques)
                 + ') passaram a ser do tipo "' + de_todos + '".')
    return _aplicar(linhas, cortes, trocas), aviso


# =====================================================================
#                          MUDAR UM NOME
# =====================================================================
# Os dados falam uns dos outros pelo nome: mudar o nome a um ataque so no
# sitio dele deixava os bichos a chamar pelo antigo. Aqui muda-se o nome em
# todos os sitios de uma vez. Devolve o ficheiro inteiro e uma frase.

def _nome_escrito(nome):
    # O nome novo, tal como vai para o codigo, entre aspas.
    nome = " ".join(str(nome or "").split())
    if nome == "":
        raise ValueError("escreve um nome.")
    if len(nome) > 40:
        raise ValueError("esse nome é comprido demais: no máximo 40 letras.")
    if '"' in nome or "\\" in nome:
        raise ValueError("o nome não pode ter aspas nem barras.")
    return nome


def renomear(fonte, escolha, nome):
    tipo, _, numero = escolha.partition(":")
    arvore = ast.parse(fonte)
    linhas = fonte.split("\n")
    instrucoes = {"bicho": "BICHOS", "ataque": "ATAQUES", "tipo": "CORES_TIPO"}
    no = blocos.instrucao(arvore, instrucoes[tipo]) if tipo in instrucoes else None
    partes = _fichas(no)
    if not numero.isdigit() or int(numero) >= len(partes):
        raise ValueError("a isso não se pode mudar o nome.")
    antigo = partes[int(numero)][0]
    nome = _nome_escrito(nome)
    if nome == antigo:
        raise ValueError("esse já é o nome dele.")
    if nome in [parte[0] for parte in partes]:
        raise ValueError('já há outro com o nome "' + nome + '".')
    novo_nome = '"' + nome + '"'
    trocas = []
    _trocar_no(linhas, no.value.keys[int(numero)], novo_nome, trocas)
    onde = []

    if tipo == "tipo":
        usos = _usos_do_tipo(arvore, antigo)
        if antigo == _tipo_de_todos(arvore) and usos["de_todos"] is None:
            # (Um jogo sem TIPO_NORMAL procura o tipo de todos por este nome.)
            raise ValueError('o tipo "' + str(antigo) + '" é o que todos podem aprender, e neste jogo tem de se '
                             "chamar assim.")
        for uso in usos["fichas"] + [alvo for alvo, _ in usos["alvos"]]:
            _trocar_no(linhas, uso, novo_nome, trocas)
        for uso in (usos["chave"], usos["de_todos"]):
            if uso is not None:
                _trocar_no(linhas, uso, novo_nome, trocas)
        if usos["fichas"]:
            onde.append("nos " + str(usos["quantos"]["BICHOS"]) + " bichos e " + str(usos["quantos"]["ATAQUES"])
                        + " ataques desse tipo")
        if usos["chave"] is not None or usos["alvos"]:
            onde.append("em «Quem é forte contra quem»")
    elif tipo == "ataque":
        donos = []
        for bicho, ficha, _, _ in _fichas(blocos.instrucao(arvore, "BICHOS")):
            usa = False
            ataques = _lista_da_chave(ficha, "ataques")
            for uso in ataques.elts if ataques is not None else []:
                if blocos.texto_constante(uso) == antigo and uso.lineno == uso.end_lineno:
                    _trocar_no(linhas, uso, novo_nome, trocas)
                    usa = True
            aprende = _no_da_chave(ficha, "aprende") if isinstance(ficha, ast.Dict) else None
            for uso in aprende.keys if isinstance(aprende, ast.Dict) else []:
                if blocos.texto_constante(uso) == antigo and uso.lineno == uso.end_lineno:
                    _trocar_no(linhas, uso, novo_nome, trocas)
                    usa = True
            if usa:
                donos.append(str(bicho))
        if donos:
            onde.append("na ficha de " + _e_de(donos))
    else:
        donos = []
        for _, ficha, _, _ in _fichas(blocos.instrucao(arvore, "TREINADORES")):
            equipa = _lista_da_chave(ficha, "equipa")
            usa = False
            for membro in equipa.elts if equipa is not None else []:
                uso = _no_da_chave(membro, "bicho") if isinstance(membro, ast.Dict) else None
                if uso is not None and blocos.texto_constante(uso) == antigo and uso.lineno == uso.end_lineno:
                    _trocar_no(linhas, uso, novo_nome, trocas)
                    usa = True
            if usa:
                donos.append(blocos.valor_da_chave(ficha, "nome") or "um treinador")
        if donos:
            onde.append("na equipa de " + _e_de(donos))

    aviso = '"' + str(antigo) + '" passou a chamar-se "' + nome + '".'
    if onde:
        aviso = aviso + " Mudei o nome também " + " e ".join(onde) + "."
    return _aplicar(linhas, [], trocas), escolha, aviso


def apagar(fonte, escolha):
    tipo, _, numero = escolha.partition(":")
    if tipo == "tipo":
        return _apagar_tipo(fonte, numero)
    arvore = ast.parse(fonte)
    linhas = fonte.split("\n")
    nomes = {"bicho": "BICHOS", "ataque": "ATAQUES", "treinador": "TREINADORES"}
    partes = _fichas(blocos.instrucao(arvore, nomes[tipo])) if tipo in nomes else []
    if not numero.isdigit() or int(numero) >= len(partes):
        raise ValueError("isso não se pode apagar.")
    nome, ficha, inicio, fim = partes[int(numero)]
    cortes = [(inicio, fim)]
    trocas = []

    if tipo == "treinador":
        if len(partes) < 2:
            raise ValueError("tem de haver pelo menos um treinador.")
        nome = blocos.valor_da_chave(ficha, "nome") or "o treinador"
        return _aplicar(linhas, cortes, trocas), 'Apaguei "' + nome + '".'

    outro = [parte[0] for parte in partes if parte[0] != nome]
    if tipo == "ataque":
        if len(outro) == 0:
            raise ValueError("tem de haver pelo menos um ataque.")
        # Sai tambem dos ataques dos bichos. Um bicho que so tinha este fica
        # com outro, para nao ficar sem ataques.
        donos = []
        for bicho, dados, _, _ in _fichas(blocos.instrucao(arvore, "BICHOS")):
            ataques = _lista_da_chave(dados, "ataques")
            dele = [no for no in ataques.elts if blocos.texto_constante(no) == nome] if ataques is not None else []
            if len(dele) == 0:
                continue
            donos.append(str(bicho))
            ficam = len(ataques.elts) - len(dele)
            for no in dele:
                if (ficam == 0 and no is dele[0]) or not _tirar_da_lista(linhas, no, cortes, trocas):
                    _trocar_no(linhas, no, '"' + outro[0] + '"', trocas)
        aviso = 'Apaguei o ataque "' + str(nome) + '".'
        if donos:
            aviso = aviso + " Saiu também dos ataques de " + _e_de(donos) + "."
        return _aplicar(linhas, cortes, trocas), aviso

    # (Num jogo em que se escolhe uma equipa a entrada, com TAMANHO_EQUIPA,
    # tem de haver bichos que cheguem. Sem isso basta ficar um.)
    minimo = 1
    no = blocos.instrucao(arvore, "TAMANHO_EQUIPA")
    if no is not None and isinstance(no.value, ast.Constant) and isinstance(no.value.value, int):
        minimo = no.value.value
    if len(partes) - 1 < minimo:
        if minimo == 1:
            raise ValueError("tem de haver pelo menos um bicho.")
        raise ValueError("tem de haver pelo menos " + str(minimo) + " bichos, para dar para fazer uma equipa. "
                         "Cria outro primeiro.")
    # Sai tambem das equipas dos treinadores. Um treinador que so tinha este
    # fica com outro bicho, para nao ficar sem equipa.
    donos = []
    for _, dados, _, _ in _fichas(blocos.instrucao(arvore, "TREINADORES")):
        equipa = _lista_da_chave(dados, "equipa")
        dele = [m for m in equipa.elts if blocos.valor_da_chave(m, "bicho") == nome] if equipa is not None else []
        if len(dele) == 0:
            continue
        donos.append(blocos.valor_da_chave(dados, "nome") or "um treinador")
        ficam = len(equipa.elts) - len(dele)
        for membro in dele:
            if (ficam == 0 and membro is dele[0]) or not _tirar_da_lista(linhas, membro, cortes, trocas):
                _trocar_no(linhas, _no_da_chave(membro, "bicho"), '"' + outro[0] + '"', trocas)
    aviso = 'Apaguei o "' + str(nome) + '".'
    if donos:
        aviso = aviso + " Saiu também da equipa de " + _e_de(donos) + "."
    return _aplicar(linhas, cortes, trocas), aviso + " Os ataques dele continuam em Ataques."


# =====================================================================
#     ESCOLHER DE UMA LISTA: OS BICHOS DE UM TREINADOR, OS ATAQUES DE UM BICHO
# =====================================================================
# A Oficina mostra os bichos que existem e a crianca escolhe os que o
# treinador leva (ou os ataques que existem, e escolhe os que o bicho sabe). Trabalha-se sobre o codigo que esta no editor (a ficha do
# treinador), e devolve-se esse codigo com a "equipa" nova: o resto do
# caminho e o de sempre, como se a crianca o tivesse escrito.
#   sem "escolhidos": devolve a lista e os que ele leva agora
#   com "escolhidos": devolve {"codigo": ...}

# Um bicho so sabe ataques do tipo dele, ou do tipo de todos (ve TIPO_DE_TODOS,
# la em cima): um bicho de fogo nao aprende ataques de agua.

def _tipo_serve(tipo_do_bicho, tipo_do_ataque, de_todos):
    return tipo_do_ataque == tipo_do_bicho or tipo_do_ataque == de_todos


def _ver_tipo_dos_ataques(quem, ficha, nomes, onde, ns, aberto, problemas, avisos):
    # Os ataques com esses nomes (os de "ataques", ou os de "aprende") tem de
    # ser do tipo do bicho, ou normais. aberto: e a ficha deste bicho que
    # esta aberta no editor?
    fichas = ns.get("ATAQUES") if isinstance(ns.get("ATAQUES"), dict) else {}
    tipo = ficha.get("tipo")
    de_todos = ns.get("TIPO_NORMAL") if isinstance(ns.get("TIPO_NORMAL"), str) else TIPO_DE_TODOS
    for ataque in nomes:
        do_ataque = fichas[ataque].get("tipo") if isinstance(fichas.get(ataque), dict) else None
        if not isinstance(tipo, str) or not isinstance(do_ataque, str) or _tipo_serve(tipo, do_ataque, de_todos):
            continue
        frase = (quem + " é do tipo " + tipo + ": não pode " + ("aprender" if onde else "saber") + ' "' + str(ataque)
                 + '", que é do tipo ' + do_ataque + ". Só ataques do tipo " + tipo
                 + (" ou do tipo " + de_todos if tipo != de_todos else "") + ".")
        if aberto:
            problemas.append(frase)
        else:
            avisos.append(frase + " Acerta a ficha desse bicho.")


def _resumir_avisos_de_tipo(avisos):
    # Mudar o tipo de todos (ou o tipo de um ataque muito usado) deixa muitos
    # bichos com ataques que ja nao podem saber: em vez de um aviso por cada
    # um, fica um so, a dizer quantos sao e como se resolve.
    deles = [aviso for aviso in avisos if ": não pode saber " in aviso or ": não pode aprender " in aviso]
    if len(deles) <= 3:
        return
    bichos = []
    for aviso in deles:
        avisos.remove(aviso)
        nome = aviso.split(" é do tipo ")[0]
        if nome not in bichos:
            bichos.append(nome)
    avisos.append("Há " + str(len(deles)) + " ataques que os bichos já não podem saber, por não serem do tipo deles "
                  "nem do tipo de todos (" + ", ".join(bichos[:8]) + ("..." if len(bichos) > 8 else "")
                  + "). Abre cada um desses bichos e usa «Escolher os ataques».")


def _lista_de_ataques(fonte, codigo, escolhidos):
    # Os ataques de um bicho. O codigo do editor e uma entrada de BICHOS
    # ("Nome": {...},): para o Python a ler, mete-se entre chavetas.
    arvore = ast.parse(fonte)
    de_todos = _tipo_de_todos(arvore)
    fichas = [(nome, blocos.valor_da_chave(ficha, "tipo"))
              for nome, ficha, _, _ in _fichas(blocos.instrucao(arvore, "ATAQUES")) if nome]
    texto = codigo.rstrip()
    if texto.endswith(","):
        texto = texto[:-1]
    try:
        dicionario = ast.parse("{" + texto + "}", mode="eval").body
    except SyntaxError:
        raise ValueError("o código tem um erro: corrige-o primeiro, ou carrega em Repor o original.")
    if not isinstance(dicionario, ast.Dict) or len(dicionario.values) != 1:
        raise ValueError("não percebi a ficha deste bicho.")
    ataques = _lista_da_chave(dicionario.values[0], "ataques")
    if ataques is None:
        raise ValueError('não encontrei os "ataques" deste bicho no código.')
    atuais = [blocos.texto_constante(no) for no in ataques.elts]
    # So se mostram os ataques que este bicho pode saber: os do tipo dele e
    # os normais.
    tipo = blocos.valor_da_chave(dicionario.values[0], "tipo")
    nomes = [nome for nome, do_ataque in fichas
             if tipo is None or do_ataque is None or _tipo_serve(tipo, do_ataque, de_todos)]
    if escolhidos is None:
        quem = blocos.texto_constante(dicionario.keys[0]) or "este bicho"
        nota = "Carrega nos ataques pela ordem em que aparecem no menu da batalha. Cabem 4."
        if tipo is not None and len(nomes) < len(fichas):
            nota = nota + (" Só aparecem os ataques do tipo dele (" + tipo + ")"
                           + (" e os do tipo " + de_todos if tipo != de_todos else "") + ".")
        return {"titulo": "Que ataques sabe " + quem + "?", "opcoes": nomes,
                "escolhidos": [ataque for ataque in atuais if ataque in nomes], "nota": nota}
    escolha_feita = []
    for ataque in escolhidos if isinstance(escolhidos, list) else []:
        if ataque in nomes and ataque not in escolha_feita:
            escolha_feita.append(ataque)
    if len(escolha_feita) == 0:
        raise ValueError("um bicho tem de saber pelo menos um ataque.")
    if len(escolha_feita) > 4:
        raise ValueError("só cabem 4 ataques no menu da batalha: tira um primeiro.")
    # (A chaveta que se pos antes do codigo empurra uma letra as colunas da
    # primeira linha.)
    linhas = texto.split("\n")
    desvio = 1 if ataques.lineno == 1 else 0
    desvio_do_fim = 1 if ataques.end_lineno == 1 else 0
    antes = linhas[ataques.lineno - 1][:_coluna("{" * desvio + linhas[ataques.lineno - 1], ataques.col_offset) - desvio]
    depois = linhas[ataques.end_lineno - 1][_coluna("{" * desvio_do_fim + linhas[ataques.end_lineno - 1],
                                                    ataques.end_col_offset) - desvio_do_fim:]
    nova = antes + "[" + ", ".join('"' + ataque + '"' for ataque in escolha_feita) + "]" + depois
    linhas[ataques.lineno - 1:ataques.end_lineno] = [nova]
    return {"codigo": "\n".join(linhas) + codigo[len(codigo.rstrip()) - (1 if codigo.rstrip().endswith(",") else 0):]}


def lista(fonte, escolha, codigo, escolhidos=None):
    if escolha.partition(":")[0] == "bicho":
        return _lista_de_ataques(fonte, codigo, escolhidos)
    if escolha.partition(":")[0] != "treinador":
        raise ValueError("aqui não há nada para escolher de uma lista.")
    nomes = [nome for nome, _, _, _ in _fichas(blocos.instrucao(ast.parse(fonte), "BICHOS")) if nome]
    texto = codigo.rstrip()
    if texto.endswith(","):
        texto = texto[:-1]
    try:
        ficha = ast.parse(texto, mode="eval").body
    except SyntaxError:
        raise ValueError("o código tem um erro: corrige-o primeiro, ou carrega em Repor o original.")
    equipa = _lista_da_chave(ficha, "equipa")
    if equipa is None:
        raise ValueError('não encontrei a "equipa" deste treinador no código.')
    niveis = {}
    atuais = []
    for membro in equipa.elts:
        bicho = blocos.valor_da_chave(membro, "bicho")
        nivel = _no_da_chave(membro, "nivel") if isinstance(membro, ast.Dict) else None
        if bicho is not None:
            atuais.append(bicho)
            if isinstance(nivel, ast.Constant) and isinstance(nivel.value, int):
                niveis.setdefault(bicho, nivel.value)
    if escolhidos is None:
        quem = blocos.valor_da_chave(ficha, "nome") or "este treinador"
        return {"titulo": "Que bichos leva " + quem + "?", "opcoes": nomes,
                "escolhidos": [bicho for bicho in atuais if bicho in nomes],
                "nota": "Carrega nos bichos pela ordem em que entram na batalha. "
                        "Os níveis mudam-se depois, no código."}

    escolha_feita = []
    for bicho in escolhidos if isinstance(escolhidos, list) else []:
        if bicho in nomes and bicho not in escolha_feita:
            escolha_feita.append(bicho)
    if len(escolha_feita) == 0:
        raise ValueError("um treinador tem de levar pelo menos um bicho.")
    # Quem ja la estava fica com o nivel que tinha; os novos, com o do primeiro.
    nivel_novo = list(niveis.values())[0] if niveis else 5
    linhas = texto.split("\n")
    chave = [k for k, v in zip(ficha.keys, ficha.values) if v is equipa][0]
    primeira = linhas[chave.lineno - 1]
    inicio = primeira[:_coluna(primeira, chave.col_offset)]
    margem = inicio[:len(inicio) - len(inicio.lstrip())]
    resto = linhas[equipa.end_lineno - 1][_coluna(linhas[equipa.end_lineno - 1], equipa.end_col_offset):]
    novas = [inicio + '"equipa": [']
    for bicho in escolha_feita:
        novas.append(margem + '    {"bicho": "' + bicho + '", "nivel": ' + str(niveis.get(bicho, nivel_novo)) + "},")
    novas.append(margem + "]" + (resto if resto.strip() not in ("", ",") else ","))
    linhas[chave.lineno - 1:equipa.end_lineno] = novas
    return {"codigo": "\n".join(linhas) + codigo[len(codigo.rstrip()) - (1 if codigo.rstrip().endswith(",") else 0):]}


# =====================================================================
#                 VER SE O QUE FOI ESCRITO FAZ SENTIDO
# =====================================================================
# Antes de uma mudanca entrar no jogo, passa por aqui. Devolve duas listas
# de frases: problemas (a mudanca nao entra) e avisos (entra, mas atencao).
#
# Os dados falam uns dos outros pelo nome: um bicho diz que ataques tem, um
# treinador diz que bichos leva. Quando um nome deixa de existir:
#   - se o engano esta no bocado aberto (um bicho com um ataque que nao
#     ha), e um problema;
#   - se e o bocado aberto que mudou de nome e ha outros a chamar pelo nome
#     antigo, e um aviso que diz onde falta mudar. Assim da para mudar o
#     nome a um ataque ou a um bicho, e o palco aguenta-se ate la.

def _numero(valor):
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


def _cor(valor):
    if not isinstance(valor, (tuple, list)) or len(valor) != 3:
        return False
    for parte in valor:
        if not isinstance(parte, int) or isinstance(parte, bool) or parte < 0 or parte > 255:
            return False
    return True


def _ver_numero(ficha, quem, chave, minimo, maximo, problemas):
    # Numeros gigantes ou negativos nao fazem sentido numa batalha, e
    # alguns (defesa 0) fazem o jogo parar com uma divisao por zero.
    if chave not in ficha:
        problemas.append(quem + ': falta "' + chave + '".')
    elif not _numero(ficha[chave]):
        problemas.append(quem + ': "' + chave + '" tem de ser um número, sem aspas.')
    elif ficha[chave] < minimo:
        problemas.append(quem + ': "' + chave + '" não pode ser menos que ' + str(minimo) + ".")
    elif ficha[chave] > maximo:
        problemas.append(quem + ': "' + chave + '" é grande demais. O máximo é ' + str(maximo) + ".")


def _ver_texto(ficha, quem, chave, problemas):
    if chave not in ficha:
        problemas.append(quem + ': falta "' + chave + '".')
        return False
    if not isinstance(ficha[chave], str):
        problemas.append(quem + ': "' + chave + '" tem de ser um texto entre aspas.')
        return False
    return True


def _ver_cor(ficha, quem, chave, problemas):
    if chave not in ficha:
        problemas.append(quem + ': falta "' + chave + '".')
    elif not _cor(ficha[chave]):
        problemas.append(quem + ': "' + chave + '" são três números de 0 a 255, como (200, 60, 60).')


def _ver_tipo(ficha, quem, tipos, problemas):
    if not _ver_texto(ficha, quem, "tipo", problemas):
        return
    if tipos is not None and ficha["tipo"] not in tipos:
        problemas.append(quem + ': o tipo "' + ficha["tipo"] + '" não tem cor em CORES_TIPO. '
                         "Os tipos que há: " + ", ".join(tipos) + ".")


def _parecido(nome, nomes):
    # Para quem se enganou numa letra: ' Querias dizer "Bicada"?'
    parecidos = difflib.get_close_matches(nome, nomes, 1)
    if parecidos:
        return ' Querias dizer "' + parecidos[0] + '"?'
    return ""


def _ver_tipos(ns, problemas, avisos):
    # Devolve os nomes dos tipos, ou None se nem der para os ler.
    cores = ns.get("CORES_TIPO")
    if not isinstance(cores, dict) or len(cores) == 0:
        problemas.append("CORES_TIPO tem de ter pelo menos um tipo, entre { }.")
        return None
    for tipo, cor in cores.items():
        if not isinstance(tipo, str):
            problemas.append("O nome de um tipo tem de estar entre aspas.")
        elif not _cor(cor):
            problemas.append('A cor do tipo "' + tipo + '" são três números de 0 a 255, como (200, 60, 60).')
    tipos = [tipo for tipo in cores if isinstance(tipo, str)]

    # Um tipo que desapareceu daqui mas ainda e o de bichos ou de ataques:
    # diz-se uma vez so (e nao uma vez por cada bicho e por cada ataque), e
    # como se resolve.
    usados = {}
    for instrucao in ("BICHOS", "ATAQUES"):
        fichas = ns.get(instrucao)
        for ficha in fichas.values() if isinstance(fichas, dict) else []:
            tipo = ficha.get("tipo") if isinstance(ficha, dict) else None
            if isinstance(tipo, str) and tipo not in tipos:
                usados[tipo] = usados.get(tipo, 0) + 1
    for tipo, quantos in usados.items():
        problemas.append('O tipo "' + tipo + '" não está em CORES_TIPO, e ainda é o tipo de ' + str(quantos)
                         + " bichos e ataques. Para lhe mudares o nome usa o botão «Mudar o nome»; para o tirares, "
                           "o «Apagar este tipo»: os dois acertam os bichos e os ataques.")
    de_todos = ns.get("TIPO_NORMAL")
    if de_todos is not None and de_todos not in tipos:
        problemas.append("TIPO_NORMAL tem de ser o nome de um dos tipos, entre aspas: " + ", ".join(tipos) + ".")
    tipos = tipos + list(usados)

    tabela = ns.get("EFICACIA")
    if not isinstance(tabela, dict):
        problemas.append("EFICACIA tem de estar entre { }.")
        return tipos
    sem_cor = []
    for atacante, linha in tabela.items():
        if not isinstance(linha, dict):
            problemas.append('EFICACIA: à frente de "' + str(atacante) + '" vem outro { }, '
                             'como {"planta": 2.0}.')
            continue
        for alvo, vezes in linha.items():
            quem = str(atacante) + " contra " + str(alvo)
            if not _numero(vezes):
                problemas.append("EFICACIA, " + quem + ": tem de ser um número, como 2.0 ou 0.5.")
            elif vezes < 0:
                problemas.append("EFICACIA, " + quem + ": não pode ser menos que zero.")
            elif vezes > 100:
                problemas.append("EFICACIA, " + quem + ": é grande demais. O máximo é 100.")
            for tipo in (atacante, alvo):
                if tipo not in tipos and tipo not in sem_cor:
                    sem_cor.append(tipo)
    for tipo in sem_cor:
        avisos.append('EFICACIA fala do tipo "' + str(tipo) + '", que não tem cor em CORES_TIPO. '
                      "Enquanto não tiver, nenhum bicho pode ser desse tipo.")
    return tipos


def _ver_ataques(ns, tipos, problemas, avisos):
    # Devolve os nomes dos ataques, ou None se nem der para os ler.
    ataques = ns.get("ATAQUES")
    if not isinstance(ataques, dict) or len(ataques) == 0:
        problemas.append("Tem de haver pelo menos um ataque.")
        return None
    for nome, ficha in ataques.items():
        quem = str(nome)
        if not isinstance(nome, str):
            problemas.append("O nome de um ataque tem de estar entre aspas.")
            continue
        if not isinstance(ficha, dict):
            problemas.append(quem + ": a ficha tem de estar entre { }.")
            continue
        _ver_tipo(ficha, quem, tipos, problemas)
        _ver_numero(ficha, quem, "poder", 0, 999, problemas)
        _ver_numero(ficha, quem, "precisao", 0, 999, problemas)
        if _numero(ficha.get("precisao")) and 100 < ficha["precisao"] <= 999:
            avisos.append(quem + ': a "precisao" vai de 0 a 100. Com mais de 100 acerta sempre.')
        if ficha.get("efeito") not in EFEITOS:
            problemas.append(quem + ': o "efeito" tem de ser um destes: ' + ", ".join(EFEITOS) + ".")
        _ver_som(ficha, quem, problemas)
    return [nome for nome in ataques if isinstance(nome, str)]


def _ver_som(ficha, quem, problemas):
    if "som" in ficha and not isinstance(ficha["som"], str):
        problemas.append(quem + ': o "som" é o nome de um ficheiro, entre aspas, como "bicho.wav".')


def _ver_imagem(ficha, quem, ns, problemas):
    if not _ver_texto(ficha, quem, "imagem", problemas):
        return
    nome = ficha["imagem"]
    if nome.strip() == "":
        problemas.append(quem + ': a "imagem" não pode ficar vazia. Escreve um nome, como "bicho.png".')
        return
    # Se o ficheiro existe mas nao e uma imagem, o jogo para ao desenhar.
    try:
        caminho = ns["PASTA_ASSETS"] / "imagens" / nome
        if caminho.exists():
            ns["pygame"].image.load(caminho)
    except Exception:
        problemas.append(quem + ': não consegui abrir a imagem "' + nome + '". É mesmo uma imagem (PNG)?')


def _ver_bichos(bichos, ns, tipos, ataques, aberto, problemas, avisos):
    # aberto: e a ficha de um bicho que esta aberta no editor?
    # Devolve os nomes dos bichos, ou None se nem der para os ler.
    if not isinstance(bichos, dict) or len(bichos) == 0:
        problemas.append("Tem de haver pelo menos um bicho.")
        return None
    for nome, ficha in bichos.items():
        quem = str(nome)
        if not isinstance(nome, str):
            problemas.append("O nome de um bicho tem de estar entre aspas.")
            continue
        if not isinstance(ficha, dict):
            problemas.append(quem + ": a ficha tem de estar entre { }.")
            continue
        _ver_tipo(ficha, quem, tipos, problemas)
        _ver_numero(ficha, quem, "vida", 1, 999, problemas)
        _ver_numero(ficha, quem, "ataque", 0, 999, problemas)
        _ver_numero(ficha, quem, "defesa", 1, 999, problemas)
        _ver_numero(ficha, quem, "velocidade", 0, 999, problemas)
        _ver_cor(ficha, quem, "cor", problemas)
        _ver_imagem(ficha, quem, ns, problemas)
        _ver_som(ficha, quem, problemas)
        if ficha.get("forma") not in FORMAS:
            avisos.append(quem + ': a "forma" só pode ser ' + ", ".join(FORMAS) + ". Assim fica só com os olhos.")

        lista = ficha.get("ataques")
        if not isinstance(lista, list) or len(lista) == 0:
            problemas.append(quem + ': os "ataques" são uma lista com pelo menos um nome, entre [ ].')
            continue
        if len(lista) > 4:
            avisos.append(quem + ": só cabem 4 ataques no menu da batalha. Os outros ficam fora do ecrã.")
        for ataque in lista:
            if not isinstance(ataque, str):
                problemas.append(quem + ": o nome de um ataque tem de estar entre aspas.")
            elif ataques is not None and ataque not in ataques:
                if aberto:
                    problemas.append(quem + ': o ataque "' + ataque + '" não existe em ATAQUES.'
                                     + _parecido(ataque, ataques))
                else:
                    avisos.append(quem + ' ainda usa o ataque "' + ataque + '", que já não existe. '
                                  "Muda o nome também na ficha desse bicho, senão o jogo pára.")
        _ver_tipo_dos_ataques(quem, ficha, [ataque for ataque in lista if isinstance(ataque, str)], "",
                              ns, aberto, problemas, avisos)

    minimo = ns.get("TAMANHO_EQUIPA")
    if isinstance(minimo, int) and len(bichos) < minimo:
        problemas.append("Tem de haver pelo menos " + str(minimo) + " bichos, para dar para fazer uma equipa.")
    return [nome for nome in bichos if isinstance(nome, str)]


def _ver_treinadores(treinadores, bichos, aberto, problemas, avisos):
    # aberto: e um treinador que esta aberto no editor?
    if not isinstance(treinadores, list) or len(treinadores) == 0:
        problemas.append("Tem de haver pelo menos um treinador.")
        return
    numero = 0
    for ficha in treinadores:
        numero = numero + 1
        quem = "Treinador " + str(numero)
        if not isinstance(ficha, dict):
            problemas.append(quem + ": tem de estar entre { }.")
            continue
        if _ver_texto(ficha, quem, "nome", problemas):
            quem = ficha["nome"]
        _ver_texto(ficha, quem, "frase", problemas)
        _ver_cor(ficha, quem, "cor_fundo", problemas)
        equipa = ficha.get("equipa")
        if not isinstance(equipa, list) or len(equipa) == 0:
            problemas.append(quem + ': a "equipa" é uma lista com pelo menos um bicho, entre [ ].')
            continue
        for membro in equipa:
            if not isinstance(membro, dict):
                problemas.append(quem + ': cada bicho da equipa é assim: {"bicho": "Sardinhão", "nivel": 5}.')
                continue
            _ver_numero(membro, quem, "nivel", 1, 99, problemas)
            if _numero(membro.get("nivel")) and not isinstance(membro["nivel"], int):
                problemas.append(quem + ': o "nivel" tem de ser um número inteiro, sem vírgula.')
            if not _ver_texto(membro, quem, "bicho", problemas):
                continue
            bicho = membro["bicho"]
            if bichos is not None and bicho not in bichos:
                if aberto:
                    problemas.append(quem + ': o bicho "' + bicho + '" não existe em BICHOS.'
                                     + _parecido(bicho, bichos))
                else:
                    avisos.append(quem + ' ainda chama por "' + bicho + '", que já não existe. '
                                  "Muda o nome também na equipa desse treinador, senão o jogo pára.")


def _ver_funcoes(ns, problemas, avisos):
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
    if not isinstance(ns.get("memoria"), dict):
        problemas.append("A memoria tem de ser um dicionário: memoria = {}")


def _experimentar(ns, regra, problemas):
    # Uma regra tem de devolver uma resposta que o jogo perceba. Experimenta-se
    # com os dois bichos que estao em campo (com copias, para nao os estragar),
    # e o que a regra disser no painel de baixo nao fica la.
    if not ns.get("minha_equipa") or not ns.get("equipa_inimiga"):
        return
    eu = dict(ns["minha_equipa"][ns["ativo_meu"]])
    inimigo = dict(ns["equipa_inimiga"][ns["ativo_inimigo"]])
    funcao = ns[regra]
    antes = list(ns["mensagens"])
    try:
        if regra == "calcular_dano":
            ataque = _ataques_de(ns, eu)[0]
            if not _numero(funcao(eu, inimigo, ataque)):
                problemas.append("calcular_dano tem de devolver um número: falta um return no fim, ou devolve outra coisa?")
        elif regra == "xp_para_subir":
            for nivel in (1, 5, 50):
                eu["nivel"] = nivel
                valor = funcao(eu)
                if not _numero(valor) or valor <= 0:
                    problemas.append("xp_para_subir tem de devolver um número maior que zero (ao nível "
                                     + str(nivel) + " devolveu " + repr(valor) + "). Senão o bicho nunca parava de subir.")
                    break
        elif regra == "quem_ataca_primeiro":
            valor = funcao(eu, inimigo)
            if valor != "jogador" and valor != "inimigo":
                problemas.append('quem_ataca_primeiro tem de devolver "jogador" ou "inimigo", com aspas. Devolveu '
                                 + repr(valor) + ".")
        elif regra == "escolher_ataque_inimigo":
            valor = funcao()
            if not isinstance(valor, str) or valor not in ns["ATAQUES"]:
                problemas.append("escolher_ataque_inimigo tem de devolver o nome de um ataque que exista. Devolveu "
                                 + repr(valor) + ".")
        elif regra == "golpe_critico":
            funcao(eu, inimigo)
    finally:
        ns["mensagens"][:] = antes


def _ataques_de(ns, bicho):
    # Os nomes dos ataques de um bicho que esta em batalha: os que aparecem
    # no menu dele. (Ha jogos em que os ataques se aprendem com o nivel: esses
    # tem uma funcao ataques_de, e e ela que diz.)
    if "ataques_de" in ns:
        return ns["ataques_de"](bicho)
    return ns["BICHOS"][bicho["nome"]]["ataques"]


# =====================================================================
#                              O PALCO
# =====================================================================

class Palco:

    # Quando se ganha uma batalha, a seguinte e com os mesmos bichos, tal
    # como ficaram (magoados, com a experiencia que ganharam), como no jogo?
    # Senao, cada batalha comeca com bichos novos.
    mesma_equipa = False

    def __init__(self, escolha):
        tipo, _, numero = escolha.partition(":")
        self.tipo = tipo             # bicho, ataque, treinador, tipos, regra, evento ou desenho
        if tipo == "tipo":
            self.tipo = "tipos"      # um tipo sozinho abre no palco dos tipos
        self.numero = int(numero) if numero.isdigit() else 0
        # Uma regra, um acontecimento ou um desenho: o nome da funcao. Com
        # eles a batalha joga-se sozinha.
        self.regra = numero if tipo in FUNCOES else None
        self.espera = 30             # frames ate a batalha dar o passo seguinte
        self.maos = 0                # frames em que a crianca joga, e nos esperamos
        self.vez = 0                 # qual o ataque que se usa a seguir
        self.fase_antes = None
        self.quadro_de_contas = []   # as linhas do quadro do meio
        self.montra = []             # um bicho de cada, para os desenhos
        self.som_visto = None
        if tipo in FUNCOES:
            # Uma funcao nova so mostra o que vale quando chega a vez de ser
            # usada (um ataque acertar, um bicho desmaiar): prova-se mais tempo.
            self.quadros_de_prova = 150
            if tipo == "evento" and numero in COM_PRESSA:
                self.quadros_de_prova = 240      # ate um bicho desmaiar ainda demora
        self.preparado = False
        self.redesenhar = False      # a batalha mudou depois de o jogo desenhar
        self.letra = None
        self.letra_pequena = None
        self.meu = None              # o nome do bicho que vai a frente
        self.ataque = None           # o nome do ataque escolhido (se for um ataque)
        self.equipa = []             # os nomes dos bichos que levo
        self.nivel = 5
        # O palco poe no jogo uma versao "segura" de BICHOS e de TREINADORES
        # (ve arrumar). Aqui fica o que o ficheiro diz mesmo, e o que la pus.
        self.escrito = {}
        self.do_palco = {}

    def ler(self, ns, nome):
        # O que o ficheiro diz, mesmo que no jogo esteja a versao do palco.
        valor = ns.get(nome)
        if nome in self.do_palco and valor is self.do_palco[nome]:
            return self.escrito[nome]
        return valor

    def por(self, ns, nome, valor):
        self.escrito[nome] = self.ler(ns, nome)
        self.do_palco[nome] = valor
        ns[nome] = valor

    def verificar(self, ns):
        problemas = []
        avisos = []
        tipos = _ver_tipos(ns, problemas, avisos)
        ataques = _ver_ataques(ns, tipos, problemas, avisos)
        bichos = _ver_bichos(self.ler(ns, "BICHOS"), ns, tipos, ataques,
                             self.tipo == "bicho", problemas, avisos)
        _ver_treinadores(self.ler(ns, "TREINADORES"), bichos,
                         self.tipo == "treinador", problemas, avisos)
        _ver_funcoes(ns, problemas, avisos)
        if self.tipo == "regra" and self.preparado and not problemas:
            _experimentar(ns, self.regra, problemas)
        _resumir_avisos_de_tipo(avisos)
        return problemas, avisos

    # --- Preparar e voltar a preparar ---

    def preparar(self, ns, pygame):
        self.letra = pygame.font.SysFont(None, 22)
        self.letra_pequena = pygame.font.SysFont(None, 18)
        self.preparado = True
        self.arrumar(ns)
        self.batalha(ns, None)

    def ao_mudar(self, ns):
        # O codigo mudou. Os bichos que estavam em campo foram feitos com
        # os numeros antigos (criar_bicho copia-os), por isso fazem-se
        # outros e a batalha comeca de novo.
        if not self.preparado:
            return
        if self.regra is not None:
            ns["memoria"].clear()      # como se o jogo recomecasse
            self.vez = 0
        self.arrumar(ns)
        self.batalha(ns, None)

    def ao_mudar_imagens(self, ns):
        # Chegou (ou saiu) uma imagem ou um som. Se foi o som da coisa que
        # esta aberta, toca-se logo, para se ouvir como ficou.
        if not self.preparado:
            return
        nome = None
        if self.tipo == "bicho":
            nome = ns["BICHOS"][self.meu].get("som")
        if self.tipo == "ataque":
            nome = ns["ATAQUES"][self.ataque].get("som")
        if not isinstance(nome, str):
            return
        try:
            visto = (nome, (ns["PASTA_ASSETS"] / "sons" / nome).stat().st_mtime_ns)
        except (OSError, ValueError):
            visto = None
        if visto is not None and visto != self.som_visto:
            ns["tocar_som"](nome)
        self.som_visto = visto

    def arrumar(self, ns):
        # Decide quem levo e contra quem, e deixa os dados de maneira que a
        # batalha nao pare: tira os nomes que ja nao existem (um ataque ou
        # um bicho a quem acabaram de mudar o nome).
        ataques = ns["ATAQUES"]
        escritos = self.ler(ns, "BICHOS")
        nomes = list(escritos)

        self.meu = nomes[0]
        self.ataque = None
        if self.tipo == "bicho":
            self.meu = nomes[min(self.numero, len(nomes) - 1)]
        if self.tipo == "ataque":
            self.ataque = list(ataques)[min(self.numero, len(ataques) - 1)]
            self.meu = self.dono(escritos, ataques)

        seguros = {}
        for nome in nomes:
            lista = [ataque for ataque in escritos[nome]["ataques"] if ataque in ataques]
            if nome == self.meu and self.ataque is not None and self.ataque not in lista:
                lista.insert(0, self.ataque)      # ninguem o tinha: fica emprestado
            if len(lista) == 0:
                lista = [list(ataques)[0]]
            seguros[nome] = dict(escritos[nome])
            seguros[nome]["ataques"] = lista
        self.por(ns, "BICHOS", seguros)
        ns["nomes_dos_bichos"] = nomes

        # A minha equipa: o bicho que interessa a frente, e mais dois.
        self.equipa = [self.meu]
        if self.tipo == "tipos" or self.tipo == "regra":
            vistos = [seguros[self.meu]["tipo"]]
            for nome in nomes:
                if len(self.equipa) < 3 and seguros[nome]["tipo"] not in vistos:
                    self.equipa.append(nome)
                    vistos.append(seguros[nome]["tipo"])
        for nome in nomes:
            if len(self.equipa) < 3 and nome not in self.equipa:
                self.equipa.append(nome)

        # O adversario: o treinador escolhido, ou o primeiro.
        treinadores = self.ler(ns, "TREINADORES")
        adversario = treinadores[0]
        if self.tipo == "treinador":
            adversario = treinadores[min(self.numero, len(treinadores) - 1)]
        membros = [membro for membro in adversario["equipa"] if membro["bicho"] in seguros]
        self.nivel = ns["NIVEL_INICIAL"]
        if self.tipo == "treinador":
            # Para a batalha ser renhida, vou ao nivel do bicho mais forte dele.
            for membro in membros:
                self.nivel = max(self.nivel, membro["nivel"])
        if len(membros) == 0:
            membros = [{"bicho": nomes[0], "nivel": self.nivel}]
        if self.regra == "ao_ganhar_batalha":
            membros = membros[:1]        # um so, para se ganhar depressa
        adversario = dict(adversario)
        adversario["equipa"] = membros
        self.por(ns, "TREINADORES", [adversario])
        ns["indice_treinador"] = 0

    def dono(self, bichos, ataques):
        # Que bicho leva o ataque escolhido? O primeiro que o tiver. Se
        # ninguem o tem (e novo, ou mudou de nome agora mesmo), empresta-se
        # a um bicho que ficou com um ataque em falta, ou a um do mesmo tipo.
        for nome, ficha in bichos.items():
            if self.ataque in ficha["ataques"]:
                return nome
        for nome, ficha in bichos.items():
            for ataque in ficha["ataques"]:
                if ataque not in ataques:
                    return nome
        for nome, ficha in bichos.items():
            if ficha["tipo"] == ataques[self.ataque]["tipo"]:
                return nome
        return list(bichos)[0]

    def batalha(self, ns, noticia, ganhou=False):
        # Comeca uma batalha com as funcoes do proprio jogo. ("ganhou": a
        # anterior acabou de ser ganha. Ve "mesma_equipa", la em cima.)
        if not (ganhou and self.mesma_equipa and ns.get("minha_equipa")):
            equipa = []
            for nome in self.equipa:
                equipa.append(ns["criar_bicho"](nome, self.nivel))
            ns["minha_equipa"] = equipa
        ns["comecar_batalha"]()
        if self.regra is not None:
            self.sem_conversa(ns)
        elif self.tipo != "treinador":
            # Sem conversa: direto ao menu dos ataques. Com um treinador
            # fica a conversa, que e onde aparecem o nome e a frase dele.
            ns["mensagens"] = []
            ns["fase"] = "ataques"
            ns["cursor"] = 0
            if self.ataque is not None:
                sabe = _ataques_de(ns, ns["minha_equipa"][0])
                ns["cursor"] = sabe.index(self.ataque) if self.ataque in sabe else 0
        if noticia is not None:
            ns["mensagens"].insert(0, noticia)
            ns["fase"] = "texto"
        self.redesenhar = True

    def sem_conversa(self, ns):
        # Numa regra, num acontecimento ou num desenho: tira a conversa do
        # treinador (as 4 primeiras frases) mas deixa o que o codigo da
        # crianca tiver dito em "quando comeca uma batalha".
        del ns["mensagens"][:4]
        if len(ns["mensagens"]) == 0:
            ns["fase"] = "menu"
            ns["cursor"] = 0
        # (Nao se mexe na vida nem na experiencia de ninguem: a batalha e
        # como no jogo, para o que se experimenta aqui valer la.)
        self.montra = [ns["criar_bicho"](nome, self.nivel) for nome in ns["nomes_dos_bichos"]]
        self.espera = 10
        self.fase_antes = None

    # --- A batalha que se joga sozinha ---

    def jogar_sozinho(self, ns, pygame):
        # Carrega nas teclas pelo jogador, devagar, com a funcao do proprio
        # jogo. Se a crianca carregar numa tecla, espera uns segundos por ela.
        teclas = pygame.key.get_pressed()
        for tecla in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_UP, pygame.K_DOWN,
                      pygame.K_ESCAPE, pygame.K_BACKSPACE):
            if teclas[tecla]:
                self.maos = 480
        if self.maos > 0:
            self.maos = self.maos - 1
            return
        self.espera = self.espera - 1
        if self.espera > 0:
            return
        carregar = ns["tecla_na_batalha"]
        fase = ns["fase"]
        if fase == "texto":
            if ns["barras_paradas"]():
                carregar(pygame.K_RETURN)
                self.espera = 50
        elif fase == "menu":
            ns["cursor"] = 0             # Lutar
            carregar(pygame.K_RETURN)
            self.espera = 10
        elif fase == "ataques":
            # Um ataque de cada vez, a comecar pelos que fazem dano.
            eu = ns["minha_equipa"][ns["ativo_meu"]]
            ataques = _ataques_de(ns, eu)
            ordem = [i for i in range(len(ataques)) if ns["ATAQUES"][ataques[i]]["efeito"] == "dano"]
            ordem = ordem + [i for i in range(len(ataques)) if i not in ordem]
            ns["cursor"] = ordem[self.vez % len(ordem)]
            self.vez = self.vez + 1
            carregar(pygame.K_RETURN)
            self.espera = 50
        elif fase == "equipa":
            if ns["troca_obrigatoria"]:
                ns["cursor"] = ns["proximo_vivo"](ns["minha_equipa"])
                carregar(pygame.K_RETURN)
            else:
                carregar(pygame.K_ESCAPE)
            self.espera = 50

    def fazer_contas(self, ns):
        # As linhas do quadro do meio: o que a regra aberta responde agora,
        # com os dois bichos que estao em campo. Cada linha e (texto, cor).
        # O que a regra disser no painel de baixo durante as contas nao fica la.
        eu = ns["minha_equipa"][ns["ativo_meu"]]
        inimigo = ns["equipa_inimiga"][ns["ativo_inimigo"]]
        antes = list(ns["mensagens"])
        fase = ns["fase"]
        linhas = []
        try:
            if self.regra == "calcular_dano":
                linhas.append(("Quanto tira cada ataque, agora:", ns["AMARELO"]))
                for atacante, alvo, cor in ((eu, inimigo, ns["BRANCO"]), (inimigo, eu, ns["CINZA"])):
                    for ataque in _ataques_de(ns, atacante):
                        if ns["ATAQUES"][ataque]["efeito"] == "dano" and len(linhas) < 8:
                            danos = [ns["calcular_dano"](dict(atacante), dict(alvo), ataque) for _ in range(8)]
                            texto = str(danos[0])
                            if _numero(danos[0]) and min(danos) != max(danos):
                                texto = str(min(danos)) + " a " + str(max(danos))
                            linhas.append((ataque + " em " + alvo["nome"] + ": " + texto, cor))
            elif self.regra == "golpe_critico":
                criticos = len([1 for _ in range(320) if ns["golpe_critico"](dict(eu), dict(inimigo))])
                linhas.append(("Em 320 golpes de " + eu["nome"] + ",", ns["AMARELO"]))
                linhas.append((str(criticos) + " eram críticos.", ns["BRANCO"]))
                if criticos > 0:
                    linhas.append(("(mais ou menos 1 em cada " + str(max(1, round(320 / criticos))) + ")", ns["CINZA"]))
            elif self.regra == "quem_ataca_primeiro":
                vezes = len([1 for _ in range(20) if ns["quem_ataca_primeiro"](dict(eu), dict(inimigo)) == "jogador"])
                linhas.append(("Quem ataca primeiro, agora:", ns["AMARELO"]))
                linhas.append((eu["nome"] + ": velocidade " + str(eu["velocidade"]), ns["BRANCO"]))
                linhas.append((inimigo["nome"] + ": velocidade " + str(inimigo["velocidade"]), ns["CINZA"]))
                if vezes == 20:
                    linhas.append(("Vai primeiro o teu bicho.", ns["VERDE"]))
                elif vezes == 0:
                    linhas.append(("Vai primeiro o bicho inimigo.", ns["VERMELHO"]))
                else:
                    linhas.append(("Ora um, ora outro (o teu, " + str(vezes) + " vezes em 20).", ns["BRANCO"]))
            elif self.regra == "escolher_ataque_inimigo":
                contagem = {}
                for _ in range(60):
                    ataque = str(ns["escolher_ataque_inimigo"]())
                    contagem[ataque] = contagem.get(ataque, 0) + 1
                linhas.append(("Em 60 vezes, " + inimigo["nome"] + " escolhia:", ns["AMARELO"]))
                for ataque in sorted(contagem, key=contagem.get, reverse=True)[:6]:
                    linhas.append((ataque + ": " + str(contagem[ataque]) + " vezes", ns["BRANCO"]))
            elif self.regra == "xp_para_subir":
                linhas.append(("Experiência para subir de nível:", ns["AMARELO"]))
                for nivel in range(eu["nivel"], eu["nivel"] + 4):
                    modelo = dict(eu)
                    modelo["nivel"] = nivel
                    linhas.append(("do nível " + str(nivel) + " para o " + str(nivel + 1) + ": "
                                   + str(ns["xp_para_subir"](modelo)) + " XP", ns["BRANCO"]))
                linhas.append(("Vencer " + inimigo["nome"] + " dá " + str(inimigo["nivel"] * 12) + " XP.", ns["CINZA"]))
            elif self.tipo == "evento":
                linhas.append(("O que está na memoria:", ns["AMARELO"]))
                for chave in list(ns["memoria"])[:6]:
                    linhas.append((str(chave) + ": " + str(ns["memoria"][chave])[:30], ns["BRANCO"]))
                if len(ns["memoria"]) == 0:
                    linhas.append(("(nada, por enquanto)", ns["CINZA"]))
        finally:
            ns["mensagens"][:] = antes
            ns["fase"] = fase
        self.quadro_de_contas = linhas

    # --- Todos os frames ---

    def quadro(self, ns, pygame):
        if not self.preparado:
            self.preparar(ns, pygame)

        # A batalha acabou? Comeca outra igual.
        if ns["estado"] == "derrota":
            self.batalha(ns, "A tua equipa desmaiou... Vamos outra vez!")
        elif ns["estado"] != "batalha":
            self.batalha(ns, "Ganhaste! Vamos outra vez.", True)

        if self.regra is not None:
            self.jogar_sozinho(ns, pygame)
            # As contas fazem-se de novo no inicio de cada turno (e os
            # acontecimentos mexem na memoria a qualquer altura).
            if ns["estado"] == "batalha" and (self.tipo == "evento" or ns["fase"] != self.fase_antes):
                if self.tipo == "evento" or ns["fase"] == "menu" or self.fase_antes is None:
                    self.fazer_contas(ns)
                self.fase_antes = ns["fase"]

        if self.redesenhar:
            # O jogo ja tinha desenhado este frame com o que havia antes.
            if ns["estado"] == "batalha":
                ns["desenhar_batalha"]()
            self.redesenhar = False
        self.desenhar(ns, pygame)

    def desenhar(self, ns, pygame):
        ecra = ns["ecra"]
        pygame.draw.rect(ecra, ns["PAINEL"], (0, 0, ns["LARGURA"], 32))
        pygame.draw.rect(ecra, ns["AMARELO"], (0, 0, 6, 32))

        texto = ""
        if self.tipo == "bicho":
            ficha = ns["BICHOS"][self.meu]
            soma = ficha["vida"] + ficha["ataque"] + ficha["defesa"] + ficha["velocidade"]
            texto = self.meu + " (" + ficha["tipo"] + "):   vida " + str(ficha["vida"])
            texto = texto + "   ataque " + str(ficha["ataque"]) + "   defesa " + str(ficha["defesa"])
            texto = texto + "   velocidade " + str(ficha["velocidade"]) + "   soma " + str(soma)
        elif self.tipo == "ataque":
            ficha = ns["ATAQUES"][self.ataque]
            texto = self.ataque + ":   tipo " + ficha["tipo"] + "   poder " + str(ficha["poder"])
            texto = texto + "   precisão " + str(ficha["precisao"]) + "   efeito " + ficha["efeito"]
            if self.ataque not in self.escrito["BICHOS"][self.meu]["ataques"]:
                texto = texto + "   (emprestado: nenhum bicho o tem)"
        elif self.tipo == "treinador":
            ficha = ns["TREINADORES"][0]
            partes = []
            for membro in ficha["equipa"]:
                partes.append(membro["bicho"] + " nv " + str(membro["nivel"]))
            texto = ficha["nome"] + ":   " + ",  ".join(partes)
        elif self.tipo == "tipos":
            self.etiquetas(ns, pygame)
            if ns["fase"] != "equipa":       # a lista da equipa ocupa o meio do ecra
                self.tabela(ns, pygame)
        elif self.regra is not None:
            funcoes = FUNCOES[self.tipo][0]
            genero = {"regra": "Regra", "evento": "Acontecimento", "desenho": "Desenho"}[self.tipo]
            texto = genero + ":   " + funcoes[self.regra][0] + "   (a função " + self.regra + ")"
            if ns["fase"] != "equipa" and ns["estado"] == "batalha":
                if self.tipo == "desenho":
                    self.mostrar_montra(ns, pygame)
                else:
                    self.mostrar_contas(ns, pygame)

        desenho = self.letra.render(texto, True, ns["BRANCO"])
        ecra.blit(desenho, (18, 9))

    def mostrar_contas(self, ns, pygame):
        # O quadro do meio, por baixo da caixa do bicho inimigo.
        ecra = ns["ecra"]
        linhas = self.quadro_de_contas
        if len(linhas) == 0:
            return
        desenhos = [self.letra_pequena.render(texto, True, cor) for texto, cor in linhas]
        largura = max(300, min(420, 20 + max(desenho.get_width() for desenho in desenhos)))
        caixa = pygame.Rect(40, 118, largura, 10 + 17 * len(linhas))
        pygame.draw.rect(ecra, ns["PAINEL"], caixa, border_radius=6)
        pygame.draw.rect(ecra, ns["AMARELO"], caixa, 2, border_radius=6)
        y = caixa.y + 6
        for desenho in desenhos:
            ecra.blit(desenho, (caixa.x + 10, y), (0, 0, caixa.width - 20, 17))
            y = y + 17

    def mostrar_montra(self, ns, pygame):
        # Todos os bichos, pequenos, la em cima, desenhados com as funcoes
        # do jogo: assim ve-se o desenho novo em todas as formas de uma vez.
        ecra = ns["ecra"]
        caixa = pygame.Rect(352, 40, 436, 66)
        pygame.draw.rect(ecra, ns["PAINEL"], caixa, border_radius=6)
        pygame.draw.rect(ecra, ns["AMARELO"], caixa, 2, border_radius=6)
        if self.regra == "desenhar_barra_vida":
            # A mesma barra com a vida cheia, a meio e quase no fim.
            x = caixa.x + 16
            for fracao in (1.0, 0.45, 0.12):
                modelo = dict(self.montra[0])
                modelo["vida"] = int(modelo["vida_max"] * fracao)
                modelo["vida_mostrada"] = modelo["vida_max"] * fracao
                ns["desenhar_barra_vida"](modelo, x, caixa.y + 27, 120)
                x = x + 140
            return
        passo = min(60, (caixa.width - 16) // max(1, len(self.montra)))
        x = caixa.x + 8 + passo // 2
        for modelo in self.montra:
            if modelo["nome"] not in ns["BICHOS"]:
                continue
            if self.regra == "desenhar_bicho":
                ns["desenhar_bicho"](modelo, x, caixa.centery, 40, 1)
            else:
                # (Sem passar pela imagem: aqui e o desenho que interessa.)
                ns["desenhar_corpo"](modelo, ns["BICHOS"][modelo["nome"]]["cor"], x, caixa.centery, 40)
                ns["desenhar_olhos"](modelo, x, caixa.centery, 40, 1)
            x = x + passo

    def etiquetas(self, ns, pygame):
        # Todos os tipos, cada um com a sua cor, na barra de cima.
        ecra = ns["ecra"]
        x = 18
        for tipo, cor in ns["CORES_TIPO"].items():
            desenho = self.letra.render(tipo, True, ns["PRETO"])
            largura = desenho.get_width() + 18
            pygame.draw.rect(ecra, cor, (x, 7, largura, 19), border_radius=9)
            ecra.blit(desenho, (x + 9, 9))
            x = x + largura + 8

    def tabela(self, ns, pygame):
        # A EFICACIA em quadradinhos, no espaco livre ao meio: a linha e o
        # tipo do ataque, a coluna e o tipo de quem leva. Os numeros vem da
        # funcao do jogo: verde bate mais, vermelho bate menos.
        ecra = ns["ecra"]
        tipos = list(ns["CORES_TIPO"])
        lado = max(18, min(30, 176 // (len(tipos) + 1)))
        largura = lado * (len(tipos) + 1)
        caixa = pygame.Rect(352, 46, largura, largura)
        pygame.draw.rect(ecra, ns["PAINEL"], caixa.inflate(8, 8), border_radius=6)
        pygame.draw.rect(ecra, ns["AMARELO"], caixa.inflate(8, 8), 2, border_radius=6)

        numero = 0
        for tipo in tipos:
            numero = numero + 1
            cor = ns["CORES_TIPO"][tipo]
            meio = numero * lado + lado // 2
            pygame.draw.circle(ecra, cor, (caixa.x + meio, caixa.y + lado // 2), lado // 3)
            pygame.draw.circle(ecra, cor, (caixa.x + lado // 2, caixa.y + meio), lado // 3)

        linha = 0
        for atacante in tipos:
            linha = linha + 1
            coluna = 0
            for alvo in tipos:
                coluna = coluna + 1
                vezes = ns["eficacia"](atacante, alvo)
                texto = "%g" % vezes          # 2.0 fica "2", 0.5 fica "0.5"
                cor = ns["CINZA"]
                if vezes > 1:
                    cor = ns["VERDE"]
                if vezes < 1:
                    cor = ns["VERMELHO"]
                if vezes == 1:
                    texto = "·"
                desenho = self.letra_pequena.render(texto, True, cor)
                centro = (caixa.x + coluna * lado + lado // 2, caixa.y + linha * lado + lado // 2)
                ecra.blit(desenho, desenho.get_rect(center=centro))


def criar_palco(escolha):
    return Palco(escolha)
