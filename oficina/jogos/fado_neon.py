# O FADO//NEON na Oficina: que coisas se podem escolher, onde esta o codigo
# de cada uma, e o "palco" que mostra so essa coisa a funcionar.
#
# O palco nao e um jogo a parte: e o FADO//NEON verdadeiro a correr, sem
# menu e sem perder, e nos a mandarmos vir o que interessa (um inimigo, o
# chefe, as cartas...). Tudo o que se ve e desenhado pelo proprio jogo.
#
# Este jogo guarda tudo num objeto (o Jogo) que e feito dentro do main(),
# e copia os numeros quando cria as coisas: um inimigo fica com a vida que
# estava em PERFIS quando nasceu. Por isso, quando o codigo muda, o palco
# volta a criar o que foi feito com os numeros antigos (ver ao_mudar).
#
# As regras, os acontecimentos e os desenhos sao funcoes encostadas a margem,
# que as classes do jogo chamam pelo nome: essas trocam-se sem refazer nada.

import ast
import inspect
import json
import math
import re
import sys

import blocos

NOME = "FADO//NEON"
FICHEIRO = "s10-jogo-do-ano/fado-neon.py"
DESCRICAO = "Um roguelite de saudade e neon. Jogo do Ano 2026."

# Uma frase por grupo, para a pagina do jogo dizer o que la ha.
SOBRE_OS_GRUPOS = {
    "Inimigos": "Tamanho, vida, velocidade, cor. Podes pôr uma imagem e um som teus.",
    "Tu": "As tuas vidas, os tiros, a investida e o laser.",
    "Ondas": "Quantas ondas há e como vão ficando mais difíceis.",
    "Cartas": "As melhorias que aparecem entre as ondas.",
    "Textos": "As frases que o jogo diz.",
    "Regras do jogo": "Aqui mudas a maneira como o jogo se comporta: é programar a sério.",
    "Acontecimentos": "Estão vazios: o que lá escreveres passa a acontecer nesse momento. É aqui que se inventa.",
    "Desenhos": "Como se desenha um inimigo, a tua nave e uma bala, com polígonos, círculos e linhas.",
}

# Os grupos onde se pode criar uma coisa nova, e o que diz o botao.
CRIAVEIS = {"Inimigos": "Novo inimigo", "Cartas": "Nova carta"}

# Pedidos ja escritos para o ajudante, para se perceber o que se pode pedir.
EXPLICA = "Explica-me esta função linha a linha"
QUE_FAZER = "O que posso fazer aqui?"
SUGESTOES = {
    "inimigo": ["Põe-no mais rápido mas com menos vida", "Muda-lhe a cor para amarelo e dá-lhe 5 lados",
                "O que quer dizer cada número?"],
    "chefe": ["Põe o Saudosista com metade da vida", "Faz o Saudosista aguentar o dobro", "O que muda este número?"],
    "vidas": ["Dá-me 8 corações", "Põe-me a andar mais depressa", "O que quer dizer cada número?"],
    "tiros": ["Faz-me disparar muito mais depressa", "Faz metade dos meus tiros serem críticos",
              "O que quer dizer cada número?"],
    "dash": ["Quero investir sem ter de esperar", "Faz-me piscar mais tempo depois de levar dano",
             "O que quer dizer cada número?"],
    "laser": ["Faz o laser durar 4 segundos", "Faz o laser encher com 5 mortes", "O que quer dizer cada número?"],
    "jogo": ["Faz um jogo rápido, só com 3 ondas", "Põe o Saudosista a aparecer logo na onda 2",
             "O que quer dizer cada número?"],
    "ondas": ["Põe o dobro dos inimigos em cada onda", "Faz os inimigos não ficarem mais fortes de onda para onda",
              "Como é que o jogo decide quantos inimigos vêm?"],
    "carta": ["Muda o nome e a descrição desta carta para ficarem mais engraçados", "Faz esta carta ser lendária",
              "O que quer dizer cada coisa desta linha?"],
    "frases": ["Junta três frases novas sobre Lisboa", "Põe as frases mais assustadoras", "Onde aparecem estas frases?"],
    "criticas": ["Junta uma crítica nova que dá 0/10 ao jogo", "Junta uma crítica da minha avó",
                 "Onde aparecem estas críticas?"],
    "creditos": ["Junta uma linha a agradecer à minha turma", "Junta uma linha a dizer quem fez os inimigos",
                 "Quando é que os créditos aparecem?"],
    "conquistas": ["Muda os textos para ficarem mais engraçados", "Muda o título da conquista \"morte\" para \"Ups\"",
                   "Porque é que o nome da esquerda não se pode mudar?"],
    "mover_inimigo": ["Faz os inimigos fugirem de mim quando têm menos de metade da vida",
                      "Faz os corredores virem aos ziguezagues", EXPLICA],
    "magoar_inimigo": ["O divisor tem um escudo: só leva metade do dano", "Dá-me 1 ponto por cada golpe que acerta",
                       EXPLICA],
    "disparar_balas": ["Faz-me disparar também para trás", "Faz todas as balas baterem uma vez nas paredes", EXPLICA],
    "rebentar_inimigo": ["Faz o divisor partir-se em quatro", "Faz o atirador deixar sempre um coração", EXPLICA],
    "aplicar_carta": ["Faz a Guitarra dar +2 projéteis de cada vez", "Faz o Café Duplo também me pôr a andar mais rápido",
                      "Explica-me o que faz cada carta"],
    "ao_comecar_onda": ["Dá-me um coração de 2 em 2 ondas", "Mostra um texto por cima de mim com o número da onda", QUE_FAZER],
    "ao_morrer_inimigo": ["Quando um inimigo morre, rebenta e magoa os que estão perto",
                          "De 10 em 10 mortes ganho um coração", QUE_FAZER],
    "ao_perder_coracao": ["Quando perco um coração, todos os inimigos levam 30 de dano",
                          "Quando perco um coração, o laser fica cheio", QUE_FAZER],
    "ao_disparar": ["Cada tiro meu sai também para trás", "De 10 em 10 tiros, disparo para os quatro lados", QUE_FAZER],
    "ao_carregar_tecla": ["A tecla X magoa todos os inimigos, mas só uma vez por onda", "A tecla G dá-me um coração", QUE_FAZER],
    "a_cada_frame": ["Dá-me 10 pontos por cada segundo que passa", "Os inimigos perdem vida aos poucos", QUE_FAZER],
    "desenhar_inimigo": ["Dá um olho ao inimigo", "Põe uma barra de vida por cima do inimigo",
                         "Explica-me este desenho linha a linha"],
    "desenhar_jogador": ["Faz a minha nave maior", "Põe a nave vermelha quando só me resta um coração",
                         "Explica-me este desenho linha a linha"],
    "desenhar_bala": ["Faz as balas redondas e maiores", "Dá uma cauda mais comprida às balas",
                      "Explica-me este desenho linha a linha"],
}

# As regras: funcoes do jogo que se podem mudar. Para cada uma, o titulo que
# aparece na Oficina, e o que ela recebe (o jogo chama-a assim, por isso nao
# pode mudar).
REGRAS = {
    "mover_inimigo": ("Como anda cada inimigo", ["inimigo", "direcao", "distancia", "dt"]),
    "magoar_inimigo": ("O que acontece a um inimigo atingido", ["inimigo", "dano", "direcao", "critico"]),
    "disparar_balas": ("Como saem os teus tiros", ["angulo"]),
    "rebentar_inimigo": ("O que um inimigo deixa ao rebentar", ["inimigo"]),
    "aplicar_carta": ("O que cada carta faz", ["carta", "jogador"]),
}
INICIO_DAS_REGRAS = "# --- As regras do jogo ---"

# Os acontecimentos: funcoes que o jogo chama em certos momentos, e que vem
# vazias. E os desenhos. Tudo isto sao funcoes, como as regras.
ACONTECIMENTOS = {
    "ao_comecar_onda": ("Quando começa uma onda", ["numero"]),
    "ao_morrer_inimigo": ("Quando um inimigo morre", ["inimigo"]),
    "ao_perder_coracao": ("Quando perdes um coração", []),
    "ao_disparar": ("Quando disparas", ["angulo"]),
    "ao_carregar_tecla": ("Quando se carrega numa tecla", ["tecla"]),
    "a_cada_frame": ("A cada frame", ["dt"]),
}
INICIO_DOS_ACONTECIMENTOS = "# --- Os acontecimentos ---"
DESENHOS = {
    "desenhar_inimigo": ("O desenho de um inimigo", ["cena", "inimigo", "p"]),
    "desenhar_jogador": ("O desenho da tua nave", ["cena", "jogador", "p"]),
    "desenhar_bala": ("O desenho de uma bala tua", ["cena", "bala", "p"]),
}
INICIO_DOS_DESENHOS = "# --- Os desenhos ---"

# tipo da escolha -> (as funcoes desse tipo, o grupo onde aparecem, as
# explicacoes gerais que se juntam a ajuda de cada uma)
FUNCOES = {
    "regra": (REGRAS, "Regras do jogo", [INICIO_DAS_REGRAS]),
    "evento": (ACONTECIMENTOS, "Acontecimentos", [INICIO_DOS_ACONTECIMENTOS, INICIO_DAS_REGRAS]),
    "desenho": (DESENHOS, "Desenhos", [INICIO_DOS_DESENHOS]),
}

# Os bocados que sao so numeros: cada escolha mostra umas quantas linhas
# "NOME = numero" seguidas, com a explicacao que o ficheiro ja traz por
# baixo de cada uma.
BLOCOS = {
    "vidas": ["VIDAS_JOGADOR", "VELOCIDADE_JOGADOR"],
    "tiros": ["DANO_BALA", "TEMPO_ENTRE_TIROS", "VELOCIDADE_BALA", "CHANCE_CRITICO", "DANO_CRITICO"],
    "dash": ["RECARGA_INVESTIDA", "INVULNERAVEL_DEPOIS_DE_DANO"],
    "laser": ["DURACAO_LASER", "CARGA_LASER_POR_MORTE", "CHANCE_CORACAO"],
    "jogo": ["ONDAS_TOTAIS", "ONDA_DO_CHEFE"],
    "ondas": ["ORCAMENTO_BASE", "ORCAMENTO_POR_ONDA", "VIDA_EXTRA_POR_ONDA",
              "VELOCIDADE_EXTRA_POR_ONDA", "VELOCIDADE_EXTRA_MAXIMA"],
    "chefe": ["VIDA_CHEFE"],
}

# Os bocados que sao uma lista (ou um dicionario) de textos.
TEXTOS = {
    "frases": "FRASES_ONDA",
    "criticas": "CRITICAS",
    "creditos": "CREDITOS",
    "conquistas": "CONQUISTAS",
}

# O que aparece na lista de escolhas, pela ordem em que aparece.
TITULOS = [
    ("chefe", "Inimigos", "O Saudosista (o chefe)"),
    ("vidas", "Tu", "Vidas e velocidade"),
    ("tiros", "Tu", "Os teus tiros"),
    ("dash", "Tu", "Investida e dano"),
    ("laser", "Tu", "Laser e corações"),
    ("jogo", "Ondas", "Quantas ondas"),
    ("ondas", "Ondas", "Quantos inimigos"),
    ("frases", "Textos", "Frases das ondas"),
    ("criticas", "Textos", "Críticas do menu"),
    ("creditos", "Textos", "Créditos"),
    ("conquistas", "Textos", "Conquistas"),
]

# Cada numero: (o mais pequeno que pode ser, o maior, tem de ser inteiro?).
# Os maximos nao sao para estragar a brincadeira: acima deles o jogo fica
# preso a fazer contas ou a desenhar.
NUMEROS = {
    "ONDAS_TOTAIS": (1, 999, True),
    "ONDA_DO_CHEFE": (1, 999, True),
    "VIDAS_JOGADOR": (1, 30, True),
    "VELOCIDADE_JOGADOR": (0, 5000, False),
    "DANO_BALA": (0, 100000, False),
    "TEMPO_ENTRE_TIROS": (0, 60, False),
    "VELOCIDADE_BALA": (1, 20000, False),
    "CHANCE_CRITICO": (0, 1, False),
    "DANO_CRITICO": (0, 1000, False),
    "RECARGA_INVESTIDA": (0, 60, False),
    "INVULNERAVEL_DEPOIS_DE_DANO": (0, 60, False),
    "DURACAO_LASER": (0, 60, False),
    "CARGA_LASER_POR_MORTE": (0, 1, False),
    "CHANCE_CORACAO": (0, 1, False),
    "ORCAMENTO_BASE": (0, 300, False),
    "ORCAMENTO_POR_ONDA": (0, 100, False),
    "VIDA_EXTRA_POR_ONDA": (0, 100, False),
    "VELOCIDADE_EXTRA_POR_ONDA": (0, 100, False),
    "VELOCIDADE_EXTRA_MAXIMA": (0, 100, False),
    "VIDA_CHEFE": (1, 1000000, False),
}

# Os nomes de inimigo de que o resto do jogo precisa, e porque.
INIMIGOS_PRECISOS = {
    "corredor": "o chefe é feito a partir dele",
    "investida": "o chefe chama por ele",
    "pequeno": "é o que sai de um divisor quando rebenta",
}

# As cartas a que a funcao aplicar_carta() do jogo sabe dar um efeito, tal
# como ela vem. (Se a funcao la estiver, pergunta-se a ela: ver _ids_com_efeito.)
CARTAS_COM_EFEITO = ["guitarra", "cafe", "calcada", "eletrico", "nata", "saudade", "gaivota",
                     "bacalhau", "vira", "azulejo", "sardinha", "ginjinha", "fado", "bugio"]

# As conquistas por que o jogo chama, pelo nome.
CONQUISTAS_PRECISAS = ["abrir", "sangue", "combo10", "combo25", "dash", "chefe", "morte",
                       "auto", "nata", "onda10", "raspao", "laser", "vitoria"]

# Que inimigos vem ao palco quando a coisa escolhida nao e um inimigo.
ELENCO = {
    "vidas": ["corredor"],
    "dash": ["corredor", "investida"],
    "tiros": ["divisor", "corredor", "atirador"],
    "laser": ["corredor", "corredor", "atirador"],
    "carta": ["corredor", "atirador", "corredor", "divisor"],
}
# Onde o tiro automatico comeca ligado (a tecla T liga e desliga).
COM_TIRO_AUTOMATICO = ["inimigo", "chefe", "tiros", "laser", "jogo", "ondas", "carta"]
# Onde o jogador pode perder coracoes (quando ficam a zero, volta a nascer).
PODE_LEVAR_DANO = ["vidas", "dash", "tiros", "laser"]

JOGAR = "Clica no jogo para jogares: WASD anda, as setas disparam, Espaço investe, E é o laser."

DICAS = {
    "inimigo": "Estão sempre a chegar mais destes, e tu disparas sozinho (a tecla T desliga isso). "
               "No palco não perdes vidas. " + JOGAR,
    "chefe": "O Saudosista está sempre na arena: quando cai, vem outro. Disparas sozinho e "
             "não perdes vidas. A barra lá em cima é a vida dele.",
    "vidas": "Os corredores vêm bater-te para veres os corações a ir; quando acabam, nasces "
             "outra vez. " + JOGAR,
    "tiros": "Disparas sozinho contra o que vier (a tecla T desliga isso). Os números "
             "amarelos com ! são os tiros críticos.",
    "dash": "Clica no jogo e carrega em Espaço para investir: o anel à tua volta é a "
            "recarga. Deixa que te batam para veres quanto tempo ficas a piscar.",
    "laser": "A barra do laser começa cheia e o laser dispara sozinho. Depois repara em "
             "quantos inimigos é preciso para ela voltar a encher.",
    "jogo": "É o jogo inteiro a jogar-se sozinho, desde a onda 1, e tu não perdes vidas. "
            "Quando mudas um número, recomeça. " + JOGAR,
    "ondas": "É o jogo inteiro a jogar-se sozinho, desde a onda 1: conta os inimigos que "
             "chegam. Quando mudas um número, recomeça.",
    "carta": "A tua carta é a do meio. Escolhe-a (tecla 2, ou um clique) para a "
             "experimentares uns segundos; depois as cartas voltam.",
    "frases": "As frases aparecem uma a uma, por baixo do número da onda. "
              "No jogo a sério sai uma ao calhas.",
    "criticas": "É o menu do jogo: as críticas passam lá em baixo. "
                "A que mudares aparece logo.",
    "creditos": "É o ecrã de quem ganha o jogo, com os créditos a subir. "
                "A linha que mudares vem logo para o meio.",
    "conquistas": "As conquistas aparecem uma a uma, à direita. No jogo a sério cada uma "
                  "aparece quando a ganhas.",
    "regra": "Isto é uma regra do jogo: muda-a e o jogo passa a comportar-se de outra maneira. "
             "Há inimigos de todos sempre a chegar e tu disparas sozinho, para veres logo a diferença. " + JOGAR,
    "evento": "O jogo joga-se sozinho, onda atrás de onda, para veres o teu acontecimento a acontecer. "
              "Tira o pass e escreve o que queres que aconteça. A faixa lá em baixo mostra a tua memoria.",
    "desenho": "Isto é o desenho: muda-o e vês logo, no jogo e aumentado no canto. "
               "Experimenta mudar um número, ou acrescentar um círculo.",
}
# As funcoes cujo palco e diferente do das outras do mesmo genero.
DICAS_DAS_FUNCOES = {
    "aplicar_carta": "Escolhe uma carta (teclas 1 2 3, ou um clique) para veres o que ela te faz: os teus "
                     "números estão na faixa lá em baixo. Passados uns segundos vêm outras três cartas.",
    "ao_comecar_onda": "O jogo joga-se sozinho. Cada vez que mudas o código a onda começa outra vez, "
                       "para veres logo o teu acontecimento. A faixa lá em baixo mostra a tua memoria.",
    "ao_perder_coracao": "Aqui não disparas sozinho (a tecla T liga isso), para os inimigos te acertarem. "
                         "Cada vez que mudas o código levas um golpe, para veres logo o que acontece.",
    "ao_carregar_tecla": "O jogo joga-se sozinho. Clica no jogo e carrega na tua tecla para experimentares. "
                         "A faixa lá em baixo mostra a tua memoria.",
}

# A explicacao ao lado do codigo, para os bocados em que o ficheiro do jogo
# nao traz nenhuma por cima.
AJUDA_NUMEROS = ("A explicação de cada número está por baixo dele.\n"
                 "MAIS  -> o que acontece se o número subir\n"
                 "MENOS -> o que acontece se o número descer\n"
                 "Os tempos estão em segundos (0.5 = meio segundo), as velocidades em\n"
                 "píxeis por segundo (o ecrã tem 960 de largura) e as percentagens\n"
                 "escrevem-se de 0 a 1 (0.05 = 5%).\n"
                 "Muda só o número: o nome e o = ficam como estão.")
AJUDAS = {
    "frases": "Uma frase por linha, entre aspas e com uma vírgula no fim.\n"
              "Podes mudar as que há, apagar ou juntar mais.",
    "criticas": "Uma crítica por linha, entre aspas e com uma vírgula no fim.\n"
                "Passam no menu do jogo, uma de cada vez.",
    "creditos": "Uma linha dos créditos por cada linha, entre aspas e com vírgula.\n"
                'Uma linha vazia ("") deixa um espaço.',
    "conquistas": 'Cada conquista é   "nome": ("título", "texto"),\n'
                  "Muda o título e o texto à vontade. O nome fica como está: é por ele\n"
                  "que o jogo chama a conquista.",
}


# =====================================================================
#                    ONDE ESTA O CODIGO DE CADA COISA
# =====================================================================

def _nome_da_carta(elemento):
    # Uma carta e ("id", "nome", "descricao", raridade, unica).
    if isinstance(elemento, ast.Tuple) and len(elemento.elts) > 1:
        return blocos.texto_constante(elemento.elts[1])
    return None


def _linhas_do_bloco(arvore, linhas, nomes):
    # Da primeira instrucao "NOME = ..." do bloco ate a ultima, mais os
    # comentarios colados por baixo dela (neste jogo a explicacao de cada
    # numero vem depois dele). Devolve (inicio, fim), ou None se nao houver.
    nos = [blocos.instrucao(arvore, nome) for nome in nomes]
    nos = [no for no in nos if no is not None]
    if len(nos) == 0:
        return None
    inicio = min(no.lineno for no in nos)
    fim = max(no.end_lineno for no in nos)
    while fim < len(linhas) and linhas[fim].lstrip().startswith("#"):
        fim = fim + 1
    return (inicio, fim)


def escolhas(fonte):
    arvore = ast.parse(fonte)
    lista = []

    no = blocos.instrucao(arvore, "PERFIS")
    partes = blocos.entradas(no) if no is not None else None
    if partes:
        for i, (chave, _, _) in enumerate(partes):
            nome = blocos.texto_constante(chave) or "Inimigo " + str(i + 1)
            lista.append({"id": "inimigo:" + str(i), "grupo": "Inimigos", "titulo": nome})

    for tipo, grupo, titulo in TITULOS:
        if tipo in BLOCOS:
            existe = any(blocos.instrucao(arvore, nome) is not None for nome in BLOCOS[tipo])
        else:
            existe = blocos.instrucao(arvore, TEXTOS[tipo]) is not None
        if existe:
            lista.append({"id": tipo, "grupo": grupo, "titulo": titulo})

    no = blocos.instrucao(arvore, "MELHORIAS")
    partes = blocos.entradas(no) if no is not None else None
    if partes:
        for i, (elemento, _, _) in enumerate(partes):
            nome = _nome_da_carta(elemento) or "Carta " + str(i + 1)
            lista.append({"id": "carta:" + str(i), "grupo": "Cartas", "titulo": nome})

    for tipo in FUNCOES:
        funcoes, grupo, _ = FUNCOES[tipo]
        for nome in funcoes:
            if blocos.funcao(arvore, nome) is not None:
                lista.append({"id": tipo + ":" + nome, "grupo": grupo, "titulo": funcoes[nome][0]})

    # Os grupos ficam juntos, pela ordem em que apareceram pela primeira vez.
    ordem = []
    for escolha in lista:
        if escolha["grupo"] not in ordem:
            ordem.append(escolha["grupo"])
    lista.sort(key=lambda escolha: ordem.index(escolha["grupo"]))
    return lista


def regiao(fonte, escolha):
    # Devolve {"inicio", "fim", "ajuda", "titulo", "dica", "imagem", "som",
    # "sugestoes"} ou None. "imagem" e o nome do PNG que essa coisa usa (None
    # se nao usa nenhum), e "som" o do WAV: neste jogo so os inimigos de
    # PERFIS e que os tem.
    arvore = ast.parse(fonte)
    linhas = fonte.split("\n")
    tipo, _, numero = escolha.partition(":")
    if tipo not in DICAS:
        return None
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
                "dica": DICAS_DAS_FUNCOES.get(numero, DICAS[tipo]), "titulo": funcoes[numero][0],
                "imagem": None, "som": None, "sugestoes": SUGESTOES[numero]}
    resposta = {"dica": DICAS[tipo], "imagem": None, "som": None, "sugestoes": SUGESTOES[tipo]}

    if tipo in BLOCOS:
        limites = _linhas_do_bloco(arvore, linhas, BLOCOS[tipo])
        if limites is None:
            return None
        titulo = [t for t in TITULOS if t[0] == tipo][0][2]
        resposta.update(inicio=limites[0], fim=limites[1], titulo=titulo, ajuda=AJUDA_NUMEROS)
        return resposta

    if tipo in TEXTOS:
        no = blocos.instrucao(arvore, TEXTOS[tipo])
        if no is None:
            return None
        titulo = [t for t in TITULOS if t[0] == tipo][0][2]
        ajuda = blocos.ajuda_acima(linhas, no.lineno) or AJUDAS[tipo]
        resposta.update(inicio=no.lineno, fim=no.end_lineno, titulo=titulo, ajuda=ajuda)
        return resposta

    # Um inimigo ou uma carta: uma entrada so, dentro de PERFIS ou MELHORIAS.
    no = blocos.instrucao(arvore, "PERFIS" if tipo == "inimigo" else "MELHORIAS")
    if no is None:
        return None
    partes = blocos.entradas(no)
    if not partes or not numero.isdigit() or int(numero) >= len(partes):
        return None
    parte, inicio, fim = partes[int(numero)]
    if tipo == "inimigo":
        titulo = blocos.texto_constante(parte)
        ficha = blocos.valor_da_entrada(no, int(numero))
        resposta["imagem"] = blocos.valor_da_chave(ficha, "imagem")
        resposta["som"] = blocos.valor_da_chave(ficha, "som")
    else:
        titulo = _nome_da_carta(parte)
    resposta.update(inicio=inicio, fim=fim, titulo=titulo or escolha,
                    ajuda=blocos.ajuda_acima(linhas, no.lineno))
    return resposta


# =====================================================================
#                        CRIAR UMA COISA NOVA
# =====================================================================
# Um inimigo novo ou uma carta nova nascem como copia do mais simples que
# la esta (o corredor, o Cafe Duplo), com outro nome, e ficam no fim da
# lista. Devolve o ficheiro inteiro ja com a coisa nova, a escolha a abrir,
# e uma frase a contar o que se fez.

def _nome_livre(base, existentes, espaco=""):
    nome = base
    numero = 2
    while nome in existentes:
        nome = base + espaco + str(numero)
        numero = numero + 1
    return nome


def _por_virgula(linhas, ultima):
    # A linha onde acaba a ultima entrada tem de acabar numa virgula, para
    # se poder escrever outra entrada a seguir.
    if not linhas[ultima - 1].rstrip().endswith(","):
        linhas[ultima - 1] = linhas[ultima - 1].rstrip() + ","


def _novo_inimigo(fonte):
    arvore = ast.parse(fonte)
    linhas = fonte.split("\n")
    no = blocos.instrucao(arvore, "PERFIS")
    partes = blocos.entradas(no) if no is not None else None
    if not partes:
        raise ValueError("não encontrei os PERFIS no ficheiro.")
    nomes = [blocos.texto_constante(chave) for chave, _, _ in partes]
    # Copia-se o corredor, que e o mais simples. Se ja nao houver, o primeiro.
    qual = nomes.index("corredor") if "corredor" in nomes else 0
    antigo = nomes[qual]
    if antigo is None:
        raise ValueError("não percebi o nome do primeiro inimigo.")
    _, inicio, fim = partes[qual]
    ultima = partes[-1][2]
    nome = _nome_livre("novo", nomes)

    texto = "\n".join(linhas[inicio - 1:fim])
    texto = texto.replace('"' + antigo + '"', '"' + nome + '"', 1)
    texto = re.sub(r'"imagem": "[^"]*"', '"imagem": "' + nome + '.png"', texto)
    texto = re.sub(r'"som": "[^"]*"', '"som": "' + nome + '.wav"', texto)
    # Para aparecer logo na onda 1 do jogo, e para nao se confundir com o
    # outro: fica amarelo.
    texto = re.sub(r'"desde_onda": \w+', '"desde_onda": 1', texto)
    texto = re.sub(r'"custo": 0\b', '"custo": 1', texto)
    texto = re.sub(r'"cor": (\([^)]*\)|\w+)', '"cor": AMARELO', texto)
    if not texto.rstrip().endswith(","):
        texto = texto.rstrip() + ","
    # As linhas de baixo da ficha vinham alinhadas pelo nome antigo.
    copia = texto.split("\n")
    for i in range(1, len(copia)):
        if len(nome) >= len(antigo):
            copia[i] = " " * (len(nome) - len(antigo)) + copia[i]
        elif copia[i].startswith(" " * (len(antigo) - len(nome) + 4)):
            copia[i] = copia[i][len(antigo) - len(nome):]
    _por_virgula(linhas, ultima)
    nova = "\n".join(linhas[:ultima] + copia + linhas[ultima:])
    aviso = ('Criei o "' + nome + '", igual ao ' + antigo + " mas amarelo. Aparece logo na onda 1. "
             'Muda-lhe o nome e os números. Ele corre para ti: para andar de outra maneira, vê "Como anda '
             'cada inimigo" nas Regras do jogo.')
    return nova, "inimigo:" + str(len(partes)), aviso


def _ramo_da_carta(funcao, ident):
    # Dentro de aplicar_carta(), a cadeia de if / elif. Devolve (as linhas
    # onde esta o que a carta "ident" faz, a linha onde acaba a cadeia, a
    # margem do if), ou None se a funcao ja nao for uma cadeia dessas.
    if funcao is None or len(funcao.body) == 0 or not isinstance(funcao.body[-1], ast.If):
        return None
    no = funcao.body[-1]
    margem = no.col_offset
    corpo = None
    while True:
        teste = no.test
        if (isinstance(teste, ast.Compare) and len(teste.comparators) == 1
                and blocos.texto_constante(teste.comparators[0]) == ident):
            corpo = (no.body[0].lineno, no.body[-1].end_lineno)
        if len(no.orelse) == 1 and isinstance(no.orelse[0], ast.If):
            no = no.orelse[0]
        elif len(no.orelse) == 0:
            break
        else:
            return None         # acaba num "else": nao se pode por um elif depois
    if corpo is None:
        return None
    return corpo, no.end_lineno, margem


def _nova_carta(fonte):
    arvore = ast.parse(fonte)
    linhas = fonte.split("\n")
    no = blocos.instrucao(arvore, "MELHORIAS")
    partes = blocos.entradas(no) if no is not None else None
    if not partes:
        raise ValueError("não encontrei as MELHORIAS no ficheiro.")
    cartas = []
    for elemento, _, _ in partes:
        try:
            carta = ast.literal_eval(elemento)
        except ValueError:
            carta = None
        if not isinstance(carta, tuple) or len(carta) != 5 or not isinstance(carta[0], str):
            raise ValueError("há uma carta em MELHORIAS que não percebi. Arranja-a primeiro.")
        cartas.append(carta)
    ids = [carta[0] for carta in cartas]
    # Copia-se o Cafe Duplo, que so muda um numero. Se ja nao houver, a primeira.
    qual = ids.index("cafe") if "cafe" in ids else 0
    antiga = cartas[qual]
    ident = _nome_livre("carta_nova", ids)
    nome = _nome_livre("Carta nova", [carta[1] for carta in cartas], " ")
    ultima = partes[-1][2]
    primeira = linhas[partes[0][1] - 1]
    margem = primeira[:len(primeira) - len(primeira.lstrip())]
    linha = (margem + "(" + json.dumps(ident) + ", " + json.dumps(nome, ensure_ascii=False) + ", "
             + json.dumps(antiga[2], ensure_ascii=False) + ", " + repr(antiga[3]) + ", " + repr(antiga[4]) + "),")

    # O que a carta faz: mais um "elif" no fim de aplicar_carta(), igual ao
    # da carta copiada. (Primeiro este, que fica mais abaixo no ficheiro:
    # assim as linhas das MELHORIAS ainda sao as mesmas.)
    ramo = _ramo_da_carta(blocos.funcao(arvore, "aplicar_carta"), antiga[0])
    if ramo is not None and ramo[1] > ultima:
        corpo, fim, espacos = ramo
        elif_novo = [" " * espacos + "elif carta == " + json.dumps(ident) + ":"] + linhas[corpo[0] - 1:corpo[1]]
        linhas = linhas[:fim] + elif_novo + linhas[fim:]
    else:
        ramo = None
    _por_virgula(linhas, ultima)
    linhas = linhas[:ultima] + [linha] + linhas[ultima:]

    aviso = 'Criei a carta "' + nome + '", igual à "' + str(antiga[1]) + '". Muda-lhe o nome e a descrição. '
    if ramo is not None:
        aviso = aviso + 'O que ela faz está nas Regras do jogo, em "O que cada carta faz": é o último elif.'
    else:
        aviso = aviso + ('Ainda não faz nada: escreve o que ela faz nas Regras do jogo, em "O que cada '
                         'carta faz", com um elif carta == "' + ident + '":')
    return "\n".join(linhas), "carta:" + str(len(partes)), aviso


def novo(fonte, grupo):
    if grupo == "Inimigos":
        return _novo_inimigo(fonte)
    if grupo == "Cartas":
        return _nova_carta(fonte)
    raise ValueError("aqui não dá para criar isso.")


# =====================================================================
#                 VER SE O QUE FOI ESCRITO FAZ SENTIDO
# =====================================================================
# Antes de uma mudanca entrar no jogo, passa por aqui. Devolve duas listas
# de frases: problemas (a mudanca nao entra) e avisos (entra, mas atencao).

def _numero(valor):
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


def _inteiro(valor):
    return isinstance(valor, int) and not isinstance(valor, bool)


def _cor(valor):
    if not isinstance(valor, (tuple, list)) or len(valor) != 3:
        return False
    for parte in valor:
        if not _inteiro(parte) or parte < 0 or parte > 255:
            return False
    return True


def _ver_valor(valor, quem, limites, problemas):
    # quem e como se fala do numero: VIDAS_JOGADOR, ou corredor: "vida".
    minimo, maximo, inteiro = limites
    if not _numero(valor) or valor != valor:
        problemas.append(quem + " tem de ser um número, sem aspas.")
    elif inteiro and not _inteiro(valor):
        problemas.append(quem + " tem de ser um número inteiro, como 3 (e não 3.5).")
    elif valor < minimo:
        problemas.append(quem + " não pode ser menos que " + str(minimo) + ".")
    elif valor > maximo and maximo == 1:
        problemas.append(quem + " vai de 0 a 1: é uma percentagem (0.5 = 50%, 1 = 100%).")
    elif valor > maximo:
        problemas.append(quem + " é grande demais para o jogo. O máximo é " + str(maximo) + ".")


def _ver_numeros(ns, problemas, avisos):
    for nome, limites in NUMEROS.items():
        if nome not in ns:
            problemas.append("Falta " + nome + ".")
        else:
            _ver_valor(ns[nome], nome, limites, problemas)


# O que cada ficha de PERFIS tem de ter: (minimo, maximo, inteiro?).
FICHA_DE_INIMIGO = {
    "raio": (1, 200, False),
    "vida": (1, 1000000, False),
    "velocidade": (0, 3000, False),
    "lados": (3, 40, True),
    "pontos": (0, 1000000, False),
    "custo": (0, 1000, True),
}


def _ver_perfis(ns, problemas, avisos):
    perfis = ns.get("PERFIS")
    if not isinstance(perfis, dict) or len(perfis) == 0:
        problemas.append("Tem de haver pelo menos um inimigo em PERFIS.")
        return
    na_onda_1 = False
    for nome, ficha in perfis.items():
        quem = str(nome)
        if not isinstance(nome, str):
            problemas.append("O nome de um inimigo tem de estar entre aspas.")
            continue
        if not isinstance(ficha, dict):
            problemas.append(quem + ": a ficha tem de estar entre { }.")
            continue
        for chave, limites in FICHA_DE_INIMIGO.items():
            if chave not in ficha:
                problemas.append(quem + ': falta "' + chave + '".')
            else:
                _ver_valor(ficha[chave], quem + ': "' + chave + '"', limites, problemas)
        if "cor" not in ficha:
            problemas.append(quem + ': falta a "cor".')
        elif not _cor(ficha["cor"]):
            problemas.append(quem + ': a "cor" é uma das cores lá de cima (ROSA, VERDE...) '
                             "ou três números de 0 a 255, como (200, 60, 60).")
        if "desde_onda" not in ficha:
            problemas.append(quem + ': falta "desde_onda".')
        elif ficha["desde_onda"] is not None:
            _ver_valor(ficha["desde_onda"], quem + ': "desde_onda"', (1, 999, True), problemas)
            if ficha["desde_onda"] == 1 and _numero(ficha.get("custo")) and ficha["custo"] > 0:
                na_onda_1 = True
        if "imagem" in ficha and not isinstance(ficha["imagem"], str):
            problemas.append(quem + ': a "imagem" é o nome de um ficheiro, entre aspas, como "corredor.png".')
        if "som" in ficha and not isinstance(ficha["som"], str):
            problemas.append(quem + ': o "som" é o nome de um ficheiro, entre aspas, como "corredor.wav".')
    for nome, razao in INIMIGOS_PRECISOS.items():
        if nome not in perfis:
            problemas.append('Tem de haver um inimigo chamado "' + nome + '": ' + razao + ".")
    if not problemas and not na_onda_1:
        avisos.append('Nenhum inimigo tem "desde_onda": 1 e custo acima de 0: a onda 1 fica vazia.')


def _ids_com_efeito(ns):
    # Os ids de carta que a funcao aplicar_carta() conhece: sao os textos
    # que la estao escritos (carta == "guitarra"...). Assim uma carta nova
    # passa a contar logo que a crianca lhe escreve o "elif".
    funcao = ns.get("aplicar_carta")
    if not inspect.isfunction(funcao):
        return CARTAS_COM_EFEITO
    ids = []
    for coisa in funcao.__code__.co_consts:
        for parte in coisa if isinstance(coisa, (tuple, frozenset)) else [coisa]:
            if isinstance(parte, str):
                ids.append(parte)
    return ids


def _ver_cartas(ns, problemas, avisos):
    com_efeito = _ids_com_efeito(ns)
    cartas = ns.get("MELHORIAS")
    if not isinstance(cartas, list) or len(cartas) == 0:
        problemas.append("Tem de haver pelo menos uma carta em MELHORIAS.")
        return
    vistos = []
    numero = 0
    for carta in cartas:
        numero = numero + 1
        quem = "A carta " + str(numero)
        if not isinstance(carta, tuple) or len(carta) != 5:
            problemas.append(quem + " tem de ter 5 coisas entre ( ), separadas por vírgulas: "
                             "id, nome, descrição, raridade e única.")
            continue
        ident, nome, descricao, raridade, unica = carta
        if isinstance(nome, str) and nome != "":
            quem = nome
        if not isinstance(ident, str) or not isinstance(nome, str) or not isinstance(descricao, str):
            problemas.append(quem + ": o id, o nome e a descrição são textos, entre aspas.")
            continue
        if not _inteiro(raridade) or raridade not in (1, 2, 3):
            problemas.append(quem + ": a raridade é 1 (comum), 2 (rara) ou 3 (lendária).")
        if not isinstance(unica, bool):
            problemas.append(quem + ": a última coisa é True (só se apanha uma vez) ou False.")
        if ident in vistos:
            avisos.append(quem + ': já há outra carta com o id "' + ident + '". Contam como a mesma.')
        elif ident not in com_efeito:
            avisos.append(quem + ': o jogo não conhece o id "' + ident + '", por isso a carta não faz nada. '
                          'O que cada carta faz está nas Regras do jogo, em "O que cada carta faz".')
        vistos.append(ident)


def _ver_textos(ns, problemas, avisos):
    for nome in ("FRASES_ONDA", "CRITICAS", "CREDITOS"):
        lista = ns.get(nome)
        if not isinstance(lista, list) or len(lista) == 0:
            problemas.append(nome + " tem de ser uma lista entre [ ], com pelo menos um texto.")
            continue
        for texto in lista:
            if not isinstance(texto, str):
                problemas.append(nome + ": cada linha é um texto entre aspas, com uma vírgula no fim.")
                break

    conquistas = ns.get("CONQUISTAS")
    if not isinstance(conquistas, dict):
        problemas.append("CONQUISTAS tem de estar entre { }.")
        return
    for nome in CONQUISTAS_PRECISAS:
        if nome not in conquistas:
            problemas.append('Falta a conquista "' + nome + '": o jogo chama por ela com esse nome.')
    for nome, par in conquistas.items():
        certo = isinstance(par, (tuple, list)) and len(par) == 2
        if not certo or not isinstance(par[0], str) or not isinstance(par[1], str):
            problemas.append('A conquista "' + str(nome) + '" tem de ser ("título", "texto"): '
                             "dois textos entre aspas, dentro de ( ).")


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


def _primeira_diferenca(antes, agora):
    # Em que posicao e que duas listas deixam de ser iguais (0 se sao iguais).
    for i in range(len(agora)):
        if i >= len(antes) or antes[i] != agora[i]:
            return i
    return 0


# =====================================================================
#                              O PALCO
# =====================================================================

class Palco:

    def __init__(self, escolha):
        tipo, _, numero = escolha.partition(":")
        self.tipo = tipo
        self.numero = int(numero) if numero.isdigit() else 0
        self.jogo = None         # o objeto Jogo, quando acabar de carregar
        self.espera = 0          # frames ate a proxima coisa acontecer
        self.vez = 0             # qual o proximo (inimigo, frase, conquista...)
        self.antes = []          # os textos como estavam, para ver qual mudou
        self.funcao = numero if tipo in FUNCOES else None
        # Nos acontecimentos o jogo joga-se sozinho, onda atras de onda; nas
        # regras e nos desenhos ha sempre inimigos de todos na arena. A regra
        # das cartas mostra as cartas, como o palco de uma carta.
        self.sozinho = tipo == "evento"
        self.com_cartas = tipo == "carta" or self.funcao == "aplicar_carta"
        self.volta = 0           # quantas vezes ja se deram cartas
        self.vez_da_lupa = 0
        if tipo in FUNCOES:
            # Uma regra nova so mostra o que vale quando chega a vez de ser
            # usada (um tiro acertar, um inimigo rebentar): prova-se mais tempo.
            self.quadros_de_prova = 150

    def verificar(self, ns):
        problemas = []
        avisos = []
        _ver_numeros(ns, problemas, avisos)
        _ver_perfis(ns, problemas, avisos)
        _ver_cartas(ns, problemas, avisos)
        _ver_textos(ns, problemas, avisos)
        _ver_funcoes(ns, problemas, avisos)
        return problemas, avisos

    # --- Encontrar o jogo e prepara-lo ---

    def procurar_jogo(self, ns):
        # O jogo nao tem um nome a que se possa chegar: e feito dentro do
        # main(). Mas quem nos chamou foi o pygame.display.flip() que esta
        # no ciclo dele (Jogo.correr), por isso andamos para tras, de funcao
        # em funcao, ate dar com ele. Enquanto o jogo esta no ecra de
        # carregamento ainda nao ha ciclo, e nao se encontra nada.
        quadro = sys._getframe()
        while quadro is not None:
            if quadro.f_code.co_name == "correr" and isinstance(quadro.f_locals.get("self"), ns["Jogo"]):
                return quadro.f_locals["self"]
            quadro = quadro.f_back
        return None

    def preparar(self, ns, pygame):
        jogo = self.jogo
        # Sem janela nao ha ecra inteiro: a tecla F rebentava o jogo.
        pygame.display.toggle_fullscreen = lambda: None
        # A musica comeca calada (numa sala cheia de computadores agradece-se).
        # A tecla M liga-a.
        jogo.musica_ligada = False
        jogo.ajustar_musica()
        jogo.auto = self.tipo in COM_TIRO_AUTOMATICO
        if self.tipo in FUNCOES:
            # (Para se ver o que acontece ao perder um coracao, e preciso
            # que os inimigos cheguem ao jogador.)
            jogo.auto = self.funcao != "ao_perder_coracao"
        self.guardar_textos(ns)
        self.comecar(ns)

    def guardar_textos(self, ns):
        if self.tipo in TEXTOS:
            textos = ns[TEXTOS[self.tipo]]
            self.antes = list(textos.values()) if isinstance(textos, dict) else list(textos)

    def comecar(self, ns):
        # Poe o jogo a mostrar a coisa escolhida, desde o inicio.
        jogo = self.jogo
        self.espera = 0
        if self.tipo in ("jogo", "ondas") or self.sozinho:
            jogo.novo_jogo()
            return
        jogo.limpar_mundo()
        jogo.estado = "jogo"
        jogo.onda = 1
        jogo.fase = "combate"
        if self.tipo == "chefe":
            self.novo_chefe(ns)
        elif self.tipo == "laser":
            jogo.farol = 1.0
        elif self.com_cartas:
            self.dar_cartas(ns, False)
        elif self.tipo == "criticas":
            jogo.estado = "titulo"
            self.mostrar_critica(ns, 0)
        elif self.tipo == "creditos":
            jogo.estado = "vitoria"
            self.mostrar_credito(0)

    def ao_mudar(self, ns):
        # O codigo mudou. O que andava no ecra foi feito com os numeros
        # antigos, por isso faz-se de novo com os que la estao agora.
        jogo = self.jogo
        if jogo is None:
            return
        if self.tipo in ("jogo", "ondas"):
            self.comecar(ns)
            return
        if self.tipo in FUNCOES:
            self.ao_mudar_funcao(ns)
            return

        novos = []
        for inimigo in jogo.inimigos:
            if inimigo.chefe:
                novo = ns["Chefe"](inimigo.onda)
                novo.pos = inimigo.pos
                jogo.chefe = novo
                novos.append(novo)
            elif inimigo.tipo in ns["PERFIS"]:
                novos.append(ns["Inimigo"](inimigo.tipo, inimigo.pos, inimigo.onda))
        jogo.inimigos = novos
        jogo.avisos = [aviso for aviso in jogo.avisos if aviso.tipo in ns["PERFIS"]]
        jogo.fila = []

        velho = jogo.jogador
        jogo.jogador = ns["Jogador"]()
        jogo.jogador.pos = velho.pos
        jogo.jogador.ang = velho.ang
        jogo.laser_t = 0.0

        if self.tipo == "laser":
            jogo.farol = 1.0
        elif self.tipo == "carta":
            self.dar_cartas(ns, True)
        elif self.tipo in TEXTOS:
            textos = ns[TEXTOS[self.tipo]]
            agora = list(textos.values()) if isinstance(textos, dict) else list(textos)
            mudou = _primeira_diferenca(self.antes, agora)
            self.antes = agora
            self.vez = mudou
            self.espera = 0
            if self.tipo == "frases":
                jogo.fase = "combate"      # tira a frase que la estava
            elif self.tipo == "criticas":
                self.mostrar_critica(ns, mudou)
            elif self.tipo == "creditos":
                self.mostrar_credito(mudou)
            elif self.tipo == "conquistas":
                jogo.notificacoes = []

    def ao_mudar_funcao(self, ns):
        # Uma funcao nova nao precisa que se refaca nada: o jogo vai busca-la
        # pelo nome da proxima vez que a chamar, e a accao continua como ia.
        # So se mexe no que e preciso para a mudanca se ver ja.
        jogo = self.jogo
        if self.funcao == "ao_comecar_onda" and jogo.estado == "jogo":
            # A onda comeca outra vez, para o acontecimento acontecer agora.
            if jogo.chefe in jogo.inimigos:
                jogo.inimigos.remove(jogo.chefe)
            jogo.chefe = None
            jogo.inimigos = []
            jogo.avisos = []
            jogo.balas_inimigas = []
            jogo.fila = []
            jogo.onda = max(0, jogo.onda - 1)
            jogo.proxima_onda()
        elif self.funcao == "ao_perder_coracao" and jogo.estado == "jogo" and jogo.fase != "morte":
            # Um golpe ja, vindo de cima, para o acontecimento acontecer agora.
            jogador = jogo.jogador
            jogador.vida = max(jogador.vida, 2)
            jogador.invulneravel = 0.0
            jogador.dash_t = 0.0
            jogo.ferir_jogador(jogador.pos + ns["Vector2"](0, -30))
        elif self.funcao == "aplicar_carta":
            # Experimenta-se ja cada carta num jogador a fingir: se a regra
            # rebentar numa delas, sabe-se agora (e o jogo volta a regra
            # anterior), e nao so no dia em que essa carta for escolhida.
            for carta in ns["MELHORIAS"]:
                ns["aplicar_carta"](carta[0], ns["Jogador"]())
            # As cartas voltam, e o jogador volta aos numeros do inicio.
            velho = jogo.jogador
            jogo.jogador = ns["Jogador"]()
            jogo.jogador.pos = velho.pos
            jogo.jogador.ang = velho.ang
            self.dar_cartas(ns, True)

    # --- As pecas com que se montam os palcos ---

    def sem_dano(self):
        # Coracoes sempre cheios, e sempre um bocadinho de "invulneravel":
        # tao pouco que o jogador nao chega a piscar.
        jogador = self.jogo.jogador
        jogador.vida = jogador.vida_max
        jogador.invulneravel = 0.12

    def a_meio_do_combate(self, ns):
        # Sem menu, sem fim e sem ondas: o jogo fica sempre a meio de um combate.
        jogo = self.jogo
        if jogo.estado == "fim" or jogo.estado == "titulo":
            self.comecar(ns)           # ficou sem coracoes: nasce outra vez
        jogo.estado = "jogo"
        jogo.onda = 1
        jogo.infinito = False
        if jogo.fase in ("limpo", "chefe_intro"):
            jogo.fase = "combate"

    def segurar_fila(self, ns):
        # O jogo da a onda por acabada quando nao ha inimigos nem ninguem na
        # fila para entrar. Deixamos sempre um na fila, e seguramo-lo la:
        # enquanto spawn_cd nao chegar a zero, ele nao entra.
        jogo = self.jogo
        if not jogo.fila:
            jogo.fila.append(list(ns["PERFIS"])[0])
        jogo.spawn_cd = 0.5

    def mandar_vir(self, ns, elenco, quantos):
        # Mantem "quantos" inimigos do elenco na arena. Quem os faz entrar e
        # o jogo, com o aviso de sempre: nos so pomos o proximo na fila.
        jogo = self.jogo
        elenco = [nome for nome in elenco if nome in ns["PERFIS"]]
        if len(elenco) == 0:
            elenco = [list(ns["PERFIS"])[0]]
        if not jogo.fila:
            jogo.fila.append(elenco[self.vez % len(elenco)])
            self.vez = self.vez + 1
        ca_estao = len([inimigo for inimigo in jogo.inimigos if inimigo.tipo in elenco])
        ca_estao = ca_estao + len([aviso for aviso in jogo.avisos if aviso.tipo in elenco])
        if ca_estao >= quantos or len(jogo.inimigos) >= 30:
            jogo.spawn_cd = 0.5
        else:
            # Faltam inimigos: o proximo entra ja, sem a espera entre dois
            # que o jogo faz nas ondas (senao morriam mais depressa do que
            # chegavam, e a arena ficava vazia).
            jogo.spawn_cd = min(jogo.spawn_cd, 0.15)

    def o_inimigo(self, ns):
        nomes = list(ns["PERFIS"])
        return nomes[min(self.numero, len(nomes) - 1)]

    def a_carta(self, ns):
        if self.funcao is not None:
            # Na regra das cartas vem tres de cada vez, sempre outras.
            return (self.volta * 3 + 1) % len(ns["MELHORIAS"])
        return min(self.numero, len(ns["MELHORIAS"]) - 1)

    def novo_chefe(self, ns):
        jogo = self.jogo
        jogo.chefe = ns["Chefe"](1)
        jogo.inimigos.append(jogo.chefe)
        self.espera = 150

    def dar_cartas(self, ns, ja):
        # Poe o ecra das cartas, com a carta escolhida no meio e as duas
        # vizinhas dela ao lado. "ja" e para aparecerem logo no sitio, sem
        # a animacao de entrada (quando o codigo acabou de mudar).
        jogo = self.jogo
        cartas = ns["MELHORIAS"]
        minha = self.a_carta(ns)
        mostrar = [minha]
        if len(cartas) > 1:
            mostrar.insert(0, (minha - 1) % len(cartas))
        if len(cartas) > 2:
            mostrar.append((minha + 1) % len(cartas))
        jogo.cartas = [[cartas[i], 1.0 if ja else 0.0] for i in mostrar]
        jogo.carta_rato = mostrar.index(minha)
        jogo.estado = "melhoria"
        jogo.estado_t = 1.0 if ja else 0.0
        jogo.inimigos = []
        jogo.avisos = []
        jogo.balas_inimigas = []
        jogo.chefe = None
        jogo.fila = []
        jogo.onda = 1
        jogo.fase = "combate"
        self.espera = 0
        if not ja:
            self.volta = self.volta + 1

    def mostrar_critica(self, ns, qual):
        jogo = self.jogo
        jogo.critica_i = min(qual, len(ns["CRITICAS"]) - 1)
        jogo.critica_x = 380          # ja a meio do ecra, para se ler logo

    def mostrar_credito(self, qual):
        # Os creditos sobem 32 pixeis por segundo, com 26 entre linhas. Isto
        # poe o relogio do ecra na altura em que a linha "qual" vai a meio.
        self.jogo.estado_t = (qual * 26 + 90) / 32

    # --- Todos os frames ---

    def quadro(self, ns, pygame):
        if self.jogo is None:
            self.jogo = self.procurar_jogo(ns)
            if self.jogo is None:
                return                  # ainda esta a carregar
            self.preparar(ns, pygame)
        jogo = self.jogo
        jogo.sair = False               # no palco, o Esc do menu nao fecha o jogo
        if jogo.estado != "pausa":      # na pausa fica tudo parado, e o palco tambem
            self.encenar(ns)
            self.desenhar(ns, pygame)

    def encenar(self, ns):
        jogo = self.jogo
        tipo = self.tipo

        if tipo in ("jogo", "ondas") or self.sozinho:
            # O jogo verdadeiro, a jogar-se sozinho: escolhe uma carta se
            # ninguem escolher, e quando ganha comeca outra vez.
            if not self.sozinho:
                self.sem_dano()
            elif jogo.jogador.vida <= 1 and jogo.fase != "morte":
                # Nos acontecimentos perdem-se coracoes a serio (ha um
                # acontecimento para isso), mas antes do ultimo voltam todos.
                jogo.jogador.vida = jogo.jogador.vida_max
            if jogo.estado in ("titulo", "fim"):
                jogo.novo_jogo()
            elif jogo.estado == "vitoria" and jogo.estado_t > 4:
                jogo.novo_jogo()
            elif jogo.estado == "melhoria" and jogo.estado_t > 2.5:
                if jogo.cartas:
                    jogo.escolher(max(0, jogo.carta_rato))
                else:
                    jogo.estado = "jogo"
                    jogo.proxima_onda()
            return

        if tipo == "criticas":
            jogo.estado = "titulo"
            jogo.critica_i = min(jogo.critica_i, len(ns["CRITICAS"]) - 1)
            return

        if tipo == "creditos":
            jogo.estado = "vitoria"
            jogo.infinito = False
            return

        if self.com_cartas:
            if jogo.estado == "melhoria":
                self.sem_dano()
                return
            if jogo.estado != "jogo":
                self.dar_cartas(ns, False)
                return
            # Escolheram uma carta: uns segundos de arena para a experimentar.
            if self.espera <= 0:
                self.espera = 540
                if jogo.chefe in jogo.inimigos:
                    jogo.inimigos.remove(jogo.chefe)
                jogo.chefe = None
                jogo.fila = []
                jogo.fase = "combate"
            self.espera = self.espera - 1
            if self.espera <= 0:
                self.dar_cartas(ns, False)
                return

        self.a_meio_do_combate(ns)
        if tipo not in PODE_LEVAR_DANO:
            self.sem_dano()

        if tipo == "inimigo":
            self.mandar_vir(ns, [self.o_inimigo(ns)], 4)
        elif self.com_cartas:
            self.mandar_vir(ns, ELENCO["carta"], 4)
        elif tipo in FUNCOES:
            self.mandar_vir(ns, list(ns["PERFIS"]), 5)     # um de cada, a vez
        elif tipo in ELENCO:
            self.mandar_vir(ns, ELENCO[tipo], 6 if tipo == "laser" else 4)
        else:
            self.segurar_fila(ns)

        if tipo == "chefe" and jogo.chefe is None:
            # Caiu. Passado um bocadinho vem outro.
            self.espera = self.espera - 1
            if self.espera <= 0:
                self.novo_chefe(ns)
        elif tipo == "frases":
            if jogo.fase == "banner":
                self.espera = 40
            else:
                self.espera = self.espera - 1
                if self.espera <= 0:
                    frases = ns["FRASES_ONDA"]
                    jogo.frase = frases[self.vez % len(frases)]
                    self.vez = self.vez + 1
                    jogo.fase = "banner"
                    jogo.fase_t = 1.8
        elif tipo == "conquistas":
            self.espera = self.espera - 1
            if self.espera <= 0 and len(jogo.notificacoes) < 3:
                pares = list(ns["CONQUISTAS"].values())
                titulo, texto = pares[self.vez % len(pares)]
                jogo.notificacoes.append([titulo, texto, 0.0])
                self.vez = self.vez + 1
                self.espera = 80

    # --- O que o palco desenha por cima do jogo ---

    def desenhar(self, ns, pygame):
        jogo = self.jogo
        tipo = self.tipo
        texto = ""
        if tipo == "inimigo":
            nome = self.o_inimigo(ns)
            ficha = ns["PERFIS"][nome]
            texto = nome + ":   vida " + str(ficha["vida"]) + "   velocidade " + str(ficha["velocidade"])
            texto = texto + "   raio " + str(ficha["raio"]) + "   pontos " + str(ficha["pontos"])
            texto = texto + "   custo " + str(ficha["custo"])
            if ficha["desde_onda"] is None:
                texto = texto + "   não aparece nas ondas"
            else:
                texto = texto + "   desde a onda " + str(ficha["desde_onda"])
            self.lupa(ns, pygame, nome)
        elif tipo == "chefe":
            texto = "O Saudosista:   VIDA_CHEFE " + str(ns["VIDA_CHEFE"])
            if jogo.chefe is not None:
                texto = texto + "   (ainda tem " + str(max(0, int(jogo.chefe.vida))) + ")"
            else:
                texto = texto + "   (caiu: já vem outro)"
        elif tipo == "jogo":
            texto = "Onda " + str(jogo.onda) + " de " + str(ns["ONDAS_TOTAIS"])
            if ns["ONDA_DO_CHEFE"] == 1:
                texto = texto + "   ·   o Saudosista aparece em todas as ondas"
            else:
                texto = texto + "   ·   o Saudosista aparece de " + str(ns["ONDA_DO_CHEFE"]) + " em "
                texto = texto + str(ns["ONDA_DO_CHEFE"]) + " ondas"
        elif tipo == "ondas":
            onda = max(1, jogo.onda)
            pontos = ns["ORCAMENTO_BASE"] + onda * ns["ORCAMENTO_POR_ONDA"]
            vida = 1 + ns["VIDA_EXTRA_POR_ONDA"] * (onda - 1)
            pressa = min(ns["VELOCIDADE_EXTRA_MAXIMA"], 1 + ns["VELOCIDADE_EXTRA_POR_ONDA"] * (onda - 1))
            texto = "Onda " + str(onda) + ":   " + str(round(pontos, 2)) + " pontos para gastar em inimigos"
            texto = texto + "   ·   vida x" + str(round(vida, 2)) + "   ·   velocidade x" + str(round(pressa, 2))
            texto = texto + "   ·   faltam entrar " + str(len(jogo.fila) + len(jogo.avisos))
        elif tipo in BLOCOS:
            texto = "      ".join(nome + " " + str(ns[nome]) for nome in BLOCOS[tipo])
        elif tipo == "carta":
            carta = ns["MELHORIAS"][self.a_carta(ns)]
            texto = "Carta: " + carta[1] + '   (id "' + carta[0] + '")'
            if jogo.estado == "melhoria":
                texto = texto + "   ·   escolhe-a para a experimentares"
            else:
                texto = texto + "   ·   as cartas voltam daqui a " + str(self.espera // 60 + 1) + " s"
        elif tipo == "frases":
            total = len(ns["FRASES_ONDA"])
            texto = "Frase " + str((self.vez - 1) % total + 1) + " de " + str(total)
        elif tipo == "criticas":
            texto = "Crítica " + str(jogo.critica_i + 1) + " de " + str(len(ns["CRITICAS"]))
        elif tipo == "creditos":
            texto = "Créditos: " + str(len(ns["CREDITOS"])) + " linhas, a subir sem parar"
        elif tipo == "conquistas":
            texto = "Conquistas: " + str(len(ns["CONQUISTAS"])) + ", uma de cada vez"
        elif tipo in FUNCOES:
            texto = self.desenhar_funcao(ns, pygame)
        self.faixa(ns, pygame, texto)

    def desenhar_funcao(self, ns, pygame):
        # O que a faixa diz no palco de uma regra, de um acontecimento ou de
        # um desenho (e, nos desenhos, a lupa no canto). Devolve o texto.
        jogo = self.jogo
        funcoes = FUNCOES[self.tipo][0]
        if self.tipo == "evento":
            # A memoria a vista: e a maneira de ver o codigo a contar coisas.
            memoria = str(ns["memoria"])
            if len(memoria) > 70:
                memoria = memoria[:67] + "..."
            return funcoes[self.funcao][0] + "   (" + self.funcao + ")   ·   memoria = " + memoria
        if self.funcao == "aplicar_carta":
            j = jogo.jogador
            texto = "Tu:   balas " + str(j.multi) + "   espera " + str(round(j.intervalo, 3))
            texto = texto + "   dano " + str(round(j.dano, 1)) + "   crítico " + str(round(j.critico, 2))
            texto = texto + "   corações " + str(j.vida_max) + "   velocidade " + str(round(j.velocidade))
            return texto + "   perfura " + str(j.perfura) + "   ricochete " + str(j.ricochete)
        if self.tipo == "regra":
            return "Regra:   " + funcoes[self.funcao][0] + "   (a função " + self.funcao + ")"
        # Um desenho. No canto, aumentado: um de cada, a vez.
        self.vez_da_lupa = self.vez_da_lupa + 1
        vetor = ns["Vector2"]
        if self.funcao == "desenhar_inimigo":
            nomes = list(ns["PERFIS"])
            self.lupa(ns, pygame, nomes[(self.vez_da_lupa // 120) % len(nomes)])
        elif self.funcao == "desenhar_jogador":
            self.aumentar(ns, pygame, 48, lambda folha: ns["desenhar_jogador"](folha, jogo.jogador, vetor(24, 24)))
        elif self.funcao == "desenhar_bala":
            # Uma bala normal e, de vez em quando, uma critica.
            bala = ns["Bala"]((0, 0), vetor(ns["VELOCIDADE_BALA"], 0), 10, 4.0, ns["CIANO"])
            if (self.vez_da_lupa // 90) % 2 == 1:
                bala.critica = True
                bala.cor = ns["AMARELO"]
                bala.raio = bala.raio * 1.4
            self.aumentar(ns, pygame, 40, lambda folha: ns["desenhar_bala"](folha, bala, vetor(29, 20)))
        return "Desenho:   " + funcoes[self.funcao][0] + "   (a função " + self.funcao + ")"

    def faixa(self, ns, pygame, texto):
        # Uma faixa escura, meio transparente, no unico sitio onde o jogo
        # nunca escreve nada: por baixo das cartas e por cima das ultimas
        # linhas do ecra (a onda, as teclas do menu, as criticas).
        ecra = self.jogo.ecra
        topo = ns["ALTURA"] - 88
        fundo = pygame.Surface((ns["LARGURA"], 26), pygame.SRCALPHA)
        fundo.fill((10, 8, 24, 215))
        ecra.blit(fundo, (0, topo))
        pygame.draw.rect(ecra, ns["AMARELO"], (0, topo, 5, 26))
        ns["escrever"](ecra, texto, 20, (16, topo + 13), ns["BRANCO"], "midleft")

    def lupa(self, ns, pygame, nome):
        # Desenha o inimigo numa folha pequena, com o desenhar() do proprio
        # jogo, e mostra essa folha aumentada no canto.
        modelo = ns["Inimigo"](nome, (0, 0), 1)
        lado = int(max(24, min(modelo.raio * 3.6 + 8, 420)))
        modelo.pos = ns["Vector2"](lado / 2, lado / 2)
        modelo.ang = -math.pi / 2       # de bico para cima
        modelo.cd_tiro = 9              # sem o anel de "vou disparar"
        self.aumentar(ns, pygame, lado, lambda folha: modelo.desenhar(folha, ns["Vector2"](0, 0)))

    def aumentar(self, ns, pygame, lado, desenhar):
        # Uma folha pequena, com "lado" pixeis de lado, onde o desenhar(folha)
        # desenha a coisa. Mostra-se aumentada no canto.
        folha = pygame.Surface((lado, lado))
        folha.fill(ns["FUNDO"])
        desenhar(folha)
        grande = pygame.transform.smoothscale(folha, (104, 104))
        ecra = self.jogo.ecra
        caixa = pygame.Rect(ns["LARGURA"] - 122, ns["ALTURA"] - 208, 108, 108)
        ecra.blit(grande, (caixa.x + 2, caixa.y + 2))
        pygame.draw.rect(ecra, ns["AMARELO"], caixa, 2, border_radius=6)


def criar_palco(escolha):
    return Palco(escolha)
