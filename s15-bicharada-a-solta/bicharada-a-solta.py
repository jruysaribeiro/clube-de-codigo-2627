# S15 — BICHARADA A SOLTA
# A Bicharada (s12) com um mapa por onde se anda. Na erva alta saltam
# bichos a solta, os treinadores estao espalhados pelo mapa, e a casa da avo
# cura a equipa.
#
# ESTE FICHEIRO E UMA BASE, NAO UM JOGO ACABADO.
# O mapa, os tipos, os ataques, os bichos e os treinadores sao todos DADOS,
# aqui em cima. Para mudares o mapa mudas letras no MAPA; para inventares um
# bicho novo escreves mais um dicionario em BICHOS. O resto do ficheiro sabe
# ler o que la puseres.
#
#   Setas            andar pelo mapa, e mexer nos menus
#   Enter / Espaco   escolher, e passar o texto a frente
#   Esc / Backspace  voltar atras (e, no ecra de escolha, tirar o ultimo)
#
# Para desafiares um treinador, anda contra ele. Para descansares, anda
# contra a casa da avo.
#
# Zero assets: os bichos sao formas com olhos. Se puseres um PNG com o nome
# que esta em "imagem" na pasta comum/assets/imagens/, aparece a imagem.
# Com os sons e igual: um WAV com o nome que esta em "som", na pasta
# comum/assets/sons/, passa a ouvir-se.

import math
import random
from pathlib import Path

import pygame

# --- Constantes: e aqui que se mexe primeiro ---
LARGURA = 800
ALTURA = 600
FPS = 60

TAMANHO_EQUIPA = 3       # quantos bichos levas contigo
NIVEL_INICIAL = 5        # o nivel com que os teus bichos comecam
SOPAS_NA_MOCHILA = 3     # a sopa da avo cura metade da vida. So ha mais em casa dela
QUADRADO = 40            # o tamanho de um quadrado do mapa, em pixeis
SORTE_NA_ERVA = 15       # em cada 100 passos na erva alta, em quantos salta um bicho

RELVA = (120, 190, 100)
ERVA_ALTA = (60, 140, 70)
AGUA = (70, 140, 230)
TRONCO = (110, 75, 45)
COPA = (40, 110, 60)
PAREDE = (235, 220, 190)
TELHADO = (200, 80, 60)

PRETO = (18, 18, 28)
BRANCO = (240, 240, 240)
CINZA = (130, 130, 145)
AMARELO = (240, 200, 70)
VERDE = (80, 200, 100)
VERMELHO = (220, 70, 60)
PAINEL = (30, 30, 48)

PASTA_ASSETS = Path(__file__).parent.parent / "comum" / "assets"


# =====================================================================
#                              OS DADOS
# =====================================================================

# --- O mapa ---
# Cada letra e um quadrado. Cabem 20 letras em cada linha, e 14 linhas.
#   .   relva: anda-se a vontade
#   e   erva alta: anda-se, e de vez em quando salta de la um bicho a solta
#   A   arvore: nao se passa
#   ~   agua: nao se passa
#   H   a casa da avo: anda contra ela para curar a equipa e encher as sopas
#   P   a partida: onde comecas (so um)
#   1 a 9   um treinador: o 1 e o primeiro da lista TREINADORES, o 2 e o
#           segundo, e por ai fora. Anda contra ele para o desafiares.
# Uma letra que o jogo nao conheca fica relva. Fora do mapa e tudo arvores.
MAPA = [
    "AAAAAAAAAAAAAAAAAAAA",
    "A....eeee....A...4.A",
    "A.H..eeee....A.....A",
    "A.P...ee...........A",
    "A..........AAA..eeeA",
    "A...1......A~A..eeeA",
    "AAAA..AAA..~~~..eeeA",
    "A.....A.....~~.....A",
    "A.eee.A..2.........A",
    "A.eee.....AAAA..AA.A",
    "A.eee.........eee..A",
    "A......~~~....eee3.A",
    "A.....~~~~~...eee..A",
    "AAAAAAAAAAAAAAAAAAAA",
]

# --- Os tipos ---
# Cada tipo tem uma cor, que aparece nos menus e nos bichos.
CORES_TIPO = {
    "normal": (170, 165, 150),
    "fogo": (235, 110, 50),
    "agua": (70, 140, 230),
    "planta": (90, 180, 80),
}

# Le-se: "um ataque de FOGO contra um bicho de PLANTA faz o dobro".
# O que nao estiver aqui faz o normal (1.0). Para acrescentar um tipo novo
# (eletrico? pedra? fantasma?) poe-lhe uma cor em CORES_TIPO e uma linha
# aqui a dizer contra quem e forte e contra quem e fraco.
EFICACIA = {
    "fogo": {"planta": 2.0, "agua": 0.5, "fogo": 0.5},
    "agua": {"fogo": 2.0, "planta": 0.5, "agua": 0.5},
    "planta": {"agua": 2.0, "fogo": 0.5, "planta": 0.5},
}

# --- Os ataques ---
# poder:    quanto magoa (0 nos ataques que nao fazem dano)
# precisao: de 0 a 100, a probabilidade de acertar
# efeito:   "dano", "cura", "sobe_ataque", "sobe_defesa",
#           "baixa_ataque" ou "baixa_defesa"
# som:      (so se quiseres) o nome de um WAV, assim: "som": "bicada.wav".
#           Se ele existir em comum/assets/sons/, ouve-se quando o ataque
#           e usado.
ATAQUES = {
    "Investida": {"tipo": "normal", "poder": 40, "precisao": 100, "efeito": "dano"},
    "Arranhão": {"tipo": "normal", "poder": 40, "precisao": 100, "efeito": "dano"},
    "Bicada": {"tipo": "normal", "poder": 35, "precisao": 100, "efeito": "dano"},
    "Patada": {"tipo": "normal", "poder": 50, "precisao": 95, "efeito": "dano"},
    "Salto Felino": {"tipo": "normal", "poder": 65, "precisao": 85, "efeito": "dano"},
    "Rugido": {"tipo": "normal", "poder": 0, "precisao": 100, "efeito": "baixa_ataque"},
    "Cocoricó": {"tipo": "normal", "poder": 0, "precisao": 100, "efeito": "sobe_ataque"},
    "Casca Dura": {"tipo": "normal", "poder": 0, "precisao": 100, "efeito": "sobe_defesa"},
    "Escamas": {"tipo": "normal", "poder": 0, "precisao": 100, "efeito": "sobe_defesa"},
    "Crista em Brasa": {"tipo": "fogo", "poder": 55, "precisao": 95, "efeito": "dano"},
    "Fumarada": {"tipo": "fogo", "poder": 45, "precisao": 100, "efeito": "dano"},
    "Estalido": {"tipo": "fogo", "poder": 75, "precisao": 80, "efeito": "dano"},
    "Esguicho": {"tipo": "agua", "poder": 40, "precisao": 100, "efeito": "dano"},
    "Tentáculo": {"tipo": "agua", "poder": 55, "precisao": 95, "efeito": "dano"},
    "Onda da Nazaré": {"tipo": "agua", "poder": 85, "precisao": 70, "efeito": "dano"},
    "Tinta de Choco": {"tipo": "agua", "poder": 0, "precisao": 100, "efeito": "baixa_defesa"},
    "Chicote de Cortiça": {"tipo": "planta", "poder": 45, "precisao": 100, "efeito": "dano"},
    "Folha de Couve": {"tipo": "planta", "poder": 55, "precisao": 95, "efeito": "dano"},
    "Bolotada": {"tipo": "planta", "poder": 70, "precisao": 85, "efeito": "dano"},
    "Seiva": {"tipo": "planta", "poder": 0, "precisao": 100, "efeito": "cura"},
}

# --- Os bichos ---
# Os numeros sao os valores BASE, ao nivel 1. Cada nivel acima soma 10%.
# forma: "circulo", "quadrado", "triangulo" ou "gota"
# som:   o nome de um WAV. Se ele existir em comum/assets/sons/, ouve-se
#        quando o bicho entra em campo.
# Para inventares um bicho: copia um destes, muda-lhe o nome e os numeros.
# Regra de equilibrio: vida + ataque + defesa + velocidade da a volta de 85.
BICHOS = {
    "Galo de Barcelos": {
        "tipo": "fogo", "vida": 45, "ataque": 15, "defesa": 10, "velocidade": 14,
        "ataques": ["Bicada", "Crista em Brasa", "Cocoricó", "Estalido"],
        "cor": (200, 45, 45), "forma": "triangulo", "imagem": "galo.png", "som": "galo.wav",
    },
    "Castanha Assada": {
        "tipo": "fogo", "vida": 55, "ataque": 12, "defesa": 13, "velocidade": 7,
        "ataques": ["Investida", "Fumarada", "Estalido", "Casca Dura"],
        "cor": (130, 70, 35), "forma": "gota", "imagem": "castanha.png", "som": "castanha.wav",
    },
    "Sardinhão": {
        "tipo": "agua", "vida": 48, "ataque": 13, "defesa": 10, "velocidade": 15,
        "ataques": ["Investida", "Esguicho", "Onda da Nazaré", "Escamas"],
        "cor": (120, 160, 200), "forma": "gota", "imagem": "sardinhao.png", "som": "sardinhao.wav",
    },
    "Polvo Lagareiro": {
        "tipo": "agua", "vida": 60, "ataque": 11, "defesa": 13, "velocidade": 6,
        "ataques": ["Tentáculo", "Tinta de Choco", "Esguicho", "Patada"],
        "cor": (170, 80, 150), "forma": "circulo", "imagem": "polvo.png", "som": "polvo.wav",
    },
    "Sobreirinho": {
        "tipo": "planta", "vida": 58, "ataque": 11, "defesa": 15, "velocidade": 5,
        "ataques": ["Chicote de Cortiça", "Bolotada", "Seiva", "Casca Dura"],
        "cor": (120, 100, 50), "forma": "quadrado", "imagem": "sobreirinho.png", "som": "sobreirinho.wav",
    },
    "Couve Galega": {
        "tipo": "planta", "vida": 50, "ataque": 13, "defesa": 11, "velocidade": 11,
        "ataques": ["Folha de Couve", "Seiva", "Investida", "Bolotada"],
        "cor": (60, 150, 70), "forma": "circulo", "imagem": "couve.png", "som": "couve.wav",
    },
    "Lince Ibérico": {
        "tipo": "normal", "vida": 46, "ataque": 15, "defesa": 9, "velocidade": 16,
        "ataques": ["Arranhão", "Salto Felino", "Rugido", "Patada"],
        "cor": (205, 155, 85), "forma": "quadrado", "imagem": "lince.png", "som": "lince.wav",
    },
}

# --- Os treinadores ---
# Estao no mapa: o primeiro desta lista e o 1, o segundo e o 2... Podes
# desafia-los pela ordem que quiseres, mas os ultimos sao mais fortes.
# Ganhas a todos os que estao no mapa, ganhas a feira.
# cor_fundo: a cor do campo de batalha, e da camisola dele no mapa.
TREINADORES = [
    {
        "nome": "Tia da Mercearia",
        "frase": "Os meus bichos comem melhor do que tu!",
        "cor_fundo": (150, 200, 230),
        "equipa": [
            {"bicho": "Couve Galega", "nivel": 3},
            {"bicho": "Castanha Assada", "nivel": 4},
        ],
    },
    {
        "nome": "Pescador da Póvoa",
        "frase": "Cheira a maresia... e a vitória!",
        "cor_fundo": (110, 170, 210),
        "equipa": [
            {"bicho": "Sardinhão", "nivel": 5},
            {"bicho": "Polvo Lagareiro", "nivel": 6},
        ],
    },
    {
        "nome": "Guarda Florestal",
        "frase": "Ninguém passa pelo meu montado.",
        "cor_fundo": (170, 200, 150),
        "equipa": [
            {"bicho": "Sobreirinho", "nivel": 6},
            {"bicho": "Lince Ibérico", "nivel": 6},
            {"bicho": "Couve Galega", "nivel": 7},
        ],
    },
    {
        "nome": "Campeã da Feira",
        "frase": "Três anos invicta. Hoje não vai ser diferente.",
        "cor_fundo": (230, 170, 140),
        "equipa": [
            {"bicho": "Galo de Barcelos", "nivel": 7},
            {"bicho": "Sardinhão", "nivel": 8},
            {"bicho": "Sobreirinho", "nivel": 8},
        ],
    },
]

# Quando o adversario e um bicho a solta, e este o "treinador" dele: assim
# treinador()["nome"] funciona em todas as batalhas.
BICHO_A_SOLTA = {
    "nome": "Bicho à solta",
    "frase": "",
    "cor_fundo": (165, 210, 150),
    "equipa": [],
}


# =====================================================================
#                          PYGAME E UTILITARIOS
# =====================================================================

pygame.init()
ecra = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Bicharada à Solta")
clock = pygame.time.Clock()
fonte_pequena = pygame.font.SysFont(None, 24)
fonte = pygame.font.SysFont(None, 32)
fonte_grande = pygame.font.SysFont(None, 80)

# Guardamos aqui as imagens ja carregadas, para nao ler o disco 60 vezes
# por segundo. None quer dizer "procurei e nao ha".
imagens_carregadas = {}


def obter_imagem(nome_ficheiro, tamanho):
    chave = nome_ficheiro + str(tamanho)
    if chave not in imagens_carregadas:
        caminho = PASTA_ASSETS / "imagens" / nome_ficheiro
        if caminho.exists():
            imagem = pygame.image.load(caminho).convert_alpha()
            imagens_carregadas[chave] = pygame.transform.scale(imagem, (tamanho, tamanho))
        else:
            imagens_carregadas[chave] = None
    return imagens_carregadas[chave]


# Com os sons e igual: ficam aqui depois de lidos, e None quer dizer "nao ha".
sons_carregados = {}


def tocar_som(nome_ficheiro):
    # Toca o som com esse nome, se ele existir em comum/assets/sons/.
    if nome_ficheiro not in sons_carregados:
        caminho = PASTA_ASSETS / "sons" / nome_ficheiro
        som = None
        if caminho.is_file() and pygame.mixer.get_init():
            try:
                som = pygame.mixer.Sound(str(caminho))
            except pygame.error:
                som = None       # o ficheiro existe mas nao e um som que se perceba
        sons_carregados[nome_ficheiro] = som
    if sons_carregados[nome_ficheiro] is not None:
        sons_carregados[nome_ficheiro].play()


def som_do_bicho(bicho):
    # A "voz" do bicho: ouve-se quando ele entra em campo.
    dados = BICHOS[bicho["nome"]]
    if "som" in dados:
        tocar_som(dados["som"])


def mostrar_texto(texto, x, y, cor, letra):
    desenho = letra.render(texto, True, cor)
    ecra.blit(desenho, (x, y))


def escurecer(cor, quanto):
    return (int(cor[0] * quanto), int(cor[1] * quanto), int(cor[2] * quanto))


# =====================================================================
#                          AS REGRAS DO JOGO
# =====================================================================

# --- As regras do jogo ---
# Ha oito funcoes neste ficheiro que sao as REGRAS. Cinco sao da batalha:
# quanto magoa um ataque (calcular_dano), quando sai um golpe critico
# (golpe_critico), quanta experiencia e precisa para subir de nivel
# (xp_para_subir), quem ataca primeiro (quem_ataca_primeiro) e que ataque o
# inimigo escolhe (escolher_ataque_inimigo). Tres sao do mapa: onde se pode
# andar (pode_andar), quando salta um bicho da erva (ha_batalha_na_erva) e
# que bicho salta (escolher_bicho_selvagem). Mudar uma delas muda a maneira
# como o jogo se comporta.
#
# Dentro delas podes usar tudo o que o jogo tem. Um bicho em batalha e um
# dicionario:
#   bicho["nome"], bicho["tipo"], bicho["nivel"], bicho["xp"]
#   bicho["vida"], bicho["vida_max"]    a vida que lhe resta, e a maxima
#   bicho["ataque"], bicho["defesa"], bicho["velocidade"]    ja com o nivel
#   bicho["mod_ataque"], bicho["mod_defesa"]    comecam em 1.0; o Cocorico,
#                                       o Rugido e outros fazem-nos mudar
# E ha mais:
#   minha_equipa[ativo_meu]             o teu bicho que esta em campo
#   equipa_inimiga[ativo_inimigo]       o bicho inimigo que esta em campo
#   BICHOS[bicho["nome"]]               a ficha dele, la em cima ("ataques"...)
#   ATAQUES[nome]                       a ficha de um ataque ("tipo", "poder",
#                                       "precisao", "efeito")
#   eficacia(tipo_do_ataque, tipo_do_alvo)    2.0, 0.5 ou 1.0, pela tabela EFICACIA
#   random.randint(1, 6)                um numero inteiro ao calhas, de 1 a 6
#   random.uniform(0.5, 1.5)            um numero com virgula ao calhas
#   dizer("ola")                        poe um texto no painel de baixo (na
#                                       batalha) ou numa caixa (no mapa)
# E do mapa:
#   jogador["coluna"], jogador["linha"]    onde estas (0, 0 e o canto de cima,
#                                       a esquerda)
#   jogador["passos"]                   quantos passos ja deste
#   letra_do_mapa(coluna, linha)        a letra que esta nesse quadrado do MAPA
#   minha_equipa                        a lista dos teus bichos
#   batalha_selvagem                    True se a batalha e contra um bicho a
#                                       solta, False se e contra um treinador
#   treinadores_vencidos                a lista dos que ja venceste (0 e o
#                                       primeiro treinador, 1 o segundo...)
# Para mudar as sopas dentro de uma funcao, a primeira linha dela tem de ser
# "global sopas".

def valor_no_nivel(base, nivel):
    # Cada nivel acima do 1 soma 10% do valor base.
    return int(base * (1 + (nivel - 1) * 0.1))


def calcular_valores(bicho):
    base = BICHOS[bicho["nome"]]
    bicho["vida_max"] = valor_no_nivel(base["vida"], bicho["nivel"]) + 10
    bicho["ataque"] = valor_no_nivel(base["ataque"], bicho["nivel"])
    bicho["defesa"] = valor_no_nivel(base["defesa"], bicho["nivel"])
    bicho["velocidade"] = valor_no_nivel(base["velocidade"], bicho["nivel"])


def criar_bicho(nome, nivel):
    # Os dados em BICHOS sao o "molde". Na batalha usamos uma copia, com a
    # vida que lhe resta, o nivel, a experiencia, etc.
    bicho = {
        "nome": nome,
        "tipo": BICHOS[nome]["tipo"],
        "nivel": nivel,
        "xp": 0,
        "mod_ataque": 1.0,
        "mod_defesa": 1.0,
        "anunciado": False,   # ja dissemos "desmaiou"?
        "tremor": 0,          # quantos frames ainda treme depois de levar
    }
    calcular_valores(bicho)
    bicho["vida"] = bicho["vida_max"]
    bicho["vida_mostrada"] = bicho["vida"]
    return bicho


def curar_tudo(equipa):
    for bicho in equipa:
        bicho["vida"] = bicho["vida_max"]
        bicho["mod_ataque"] = 1.0
        bicho["mod_defesa"] = 1.0
        bicho["anunciado"] = False


def nivel_mais_alto(equipa):
    # O nivel do bicho mais forte de uma equipa.
    maior = 1
    for bicho in equipa:
        if bicho["nivel"] > maior:
            maior = bicho["nivel"]
    return maior


def eficacia(tipo_ataque, tipo_alvo):
    if tipo_ataque in EFICACIA:
        if tipo_alvo in EFICACIA[tipo_ataque]:
            return EFICACIA[tipo_ataque][tipo_alvo]
    return 1.0


# QUANTO MAGOA UM ATAQUE
# Recebe quem ataca, quem leva e o NOME do ataque. Devolve quanta vida o
# golpe tira (um numero inteiro). Como esta: o poder do ataque, vezes o
# ataque de um a dividir pela defesa do outro, e depois o nivel, o tipo e
# um bocadinho de sorte.
#   dados["poder"], dados["tipo"]    vem da ficha do ataque, em ATAQUES
# Ideias: um bicho com pouca vida bater mais forte (furia); tirar a sorte,
# para o mesmo ataque tirar sempre o mesmo; bater mais em bichos mais lentos.
def calcular_dano(atacante, alvo, ataque):
    dados = ATAQUES[ataque]
    ataque_real = atacante["ataque"] * atacante["mod_ataque"]
    defesa_real = alvo["defesa"] * alvo["mod_defesa"]
    dano = dados["poder"] * ataque_real / defesa_real * 0.35
    # Quem esta em nivel mais alto bate mais forte.
    dano = dano * (atacante["nivel"] + 5) / 10
    dano = dano * eficacia(dados["tipo"], alvo["tipo"])
    # Um bicho que usa um ataque do seu proprio tipo bate 25% mais.
    if dados["tipo"] == atacante["tipo"]:
        dano = dano * 1.25
    # Um bocadinho de sorte, para nenhuma batalha ser igual a outra.
    dano = dano * random.uniform(0.85, 1.0)
    return int(dano) + 1


# QUANDO SAI UM GOLPE CRITICO
# Corre cada vez que um ataque acerta. Recebe quem ataca e quem leva, e
# devolve True se o golpe for critico (tira mais metade do dano) ou False se
# nao for. Como esta: e sorte, 1 vez em cada 16.
# Ideias: sair mais vezes (1 em cada 4); os bichos mais rapidos do que o alvo
# terem mais sorte; critico garantido quando quem ataca tem pouca vida.
def golpe_critico(atacante, alvo):
    return random.randint(1, 16) == 1


def proximo_vivo(equipa):
    # Devolve a posicao do primeiro bicho com vida, ou -1 se nao houver.
    indice = 0
    while indice < len(equipa):
        if equipa[indice]["vida"] > 0:
            return indice
        indice = indice + 1
    return -1


# QUANTA EXPERIENCIA E PRECISA PARA SUBIR DE NIVEL
# Recebe um bicho e devolve quantos pontos de experiencia (XP) ele precisa
# de juntar para passar ao nivel seguinte. Como esta: 10 por cada nivel que
# ja tem (ao nivel 5 precisa de 50). Vencer um bicho da 12 de XP por cada
# nivel dele. Tem de devolver sempre mais que zero, senao o bicho nunca mais
# parava de subir.
# Ideias: subir mais depressa (5 por nivel); os primeiros niveis faceis e os
# ultimos dificeis; os bichos de planta crescerem mais depressa.
def xp_para_subir(bicho):
    return bicho["nivel"] * 10


# =====================================================================
#                          O ESTADO DO JOGO
# =====================================================================

estado = "menu"          # menu, escolha, mundo, batalha, vitoria, derrota
fase = "texto"           # dentro da batalha: texto, menu, ataques, equipa
cursor = 0               # qual opcao do menu esta escolhida

nomes_dos_bichos = list(BICHOS.keys())
escolhidos = []          # nomes escolhidos no ecra de escolha
cursor_escolha = 0

minha_equipa = []
equipa_inimiga = []
ativo_meu = 0
ativo_inimigo = 0
indice_treinador = 0
sopas = SOPAS_NA_MOCHILA
troca_obrigatoria = False

# No mapa: onde estas, para onde olhas e quantos passos ja deste.
jogador = {"coluna": 1, "linha": 1, "olha": "baixo", "passos": 0}
# Onde acordas se a equipa toda desmaiar: o ultimo sitio onde descansaste.
descanso = {"coluna": 1, "linha": 1}
treinadores_vencidos = []    # 0 e o primeiro treinador, 1 o segundo...
batalha_selvagem = False     # a batalha e contra um bicho a solta?
bicho_a_solta = None         # o bicho que saltou da erva
a_fugir = False
aviso = ""                   # o texto da caixa que aparece no mapa
espera_do_passo = 0          # frames ate ao proximo passo com a seta carregada

# Os textos que aparecem no painel de baixo, um de cada vez.
mensagens = []
# As acoes que ainda faltam neste turno, pela ordem em que acontecem.
# Cada acao e um dicionario, por exemplo:
#   {"quem": "jogador", "tipo": "atacar", "ataque": "Bicada"}
fila_acoes = []

OPCOES_MENU = ["Lutar", "Equipa", "Sopa", "Fugir"]


def dizer(texto):
    # Numa batalha: poe um texto no painel de baixo, a seguir aos que la
    # estiverem, e o jogador passa-o com Enter. No mapa: mostra o texto numa
    # caixa, ate ao passo seguinte.
    global fase, aviso
    if estado == "batalha":
        mensagens.append(texto)
        fase = "texto"
    else:
        aviso = texto


def treinador():
    # Contra quem e a batalha.
    if batalha_selvagem:
        return BICHO_A_SOLTA
    return TREINADORES[indice_treinador]


def comecar_escolha():
    global estado, escolhidos, cursor_escolha, indice_treinador
    estado = "escolha"
    escolhidos = []
    cursor_escolha = 0
    indice_treinador = 0
    memoria.clear()


def comecar_batalha():
    # Contra o treinador que esta em indice_treinador ou, se batalha_selvagem
    # for True, contra o bicho_a_solta.
    global estado, fase, equipa_inimiga, ativo_meu, ativo_inimigo
    global mensagens, fila_acoes, troca_obrigatoria, a_fugir
    estado = "batalha"
    equipa_inimiga = []
    if batalha_selvagem:
        equipa_inimiga.append(bicho_a_solta)
    else:
        for membro in treinador()["equipa"]:
            equipa_inimiga.append(criar_bicho(membro["bicho"], membro["nivel"]))
    # A vida fica como estava: so a casa da avo cura. O ataque e a defesa,
    # que alguns ataques fazem subir e descer, voltam ao normal.
    for bicho in minha_equipa:
        bicho["mod_ataque"] = 1.0
        bicho["mod_defesa"] = 1.0
    ativo_meu = max(0, proximo_vivo(minha_equipa))
    ativo_inimigo = 0
    troca_obrigatoria = False
    a_fugir = False
    fila_acoes = []
    eu = minha_equipa[ativo_meu]
    if batalha_selvagem:
        mensagens = [
            "Salta da erva um " + equipa_inimiga[0]["nome"] + " à solta!",
            "Vai, " + eu["nome"] + "!",
        ]
    else:
        mensagens = [
            treinador()["nome"] + " desafia-te!",
            "«" + treinador()["frase"] + "»",
            treinador()["nome"] + " manda " + equipa_inimiga[0]["nome"] + "!",
            "Vai, " + eu["nome"] + "!",
        ]
    fase = "texto"
    som_do_bicho(equipa_inimiga[0])
    som_do_bicho(eu)
    ao_comecar_batalha()


def voltar_ao_mundo():
    # Acaba a batalha, de qualquer maneira, e volta ao mapa.
    global estado, batalha_selvagem, a_fugir
    estado = "mundo"
    batalha_selvagem = False
    a_fugir = False


def ganhar_batalha():
    global estado
    era_selvagem = batalha_selvagem
    nome = treinador()["nome"]
    voltar_ao_mundo()
    if era_selvagem:
        return
    if indice_treinador not in treinadores_vencidos:
        treinadores_vencidos.append(indice_treinador)
    faltam = treinadores_por_vencer()
    if faltam == 0:
        estado = "vitoria"
    elif faltam == 1:
        dizer("Ganhaste a " + nome + "! Só falta um treinador.")
    else:
        dizer("Ganhaste a " + nome + "! Faltam " + str(faltam) + " treinadores.")


def acordar_em_casa():
    # A equipa toda desmaiou: acordas onde descansaste pela ultima vez, com
    # os bichos curados. Os treinadores que ja venceste continuam vencidos.
    global sopas
    voltar_ao_mundo()
    curar_tudo(minha_equipa)
    sopas = SOPAS_NA_MOCHILA
    jogador["coluna"] = descanso["coluna"]
    jogador["linha"] = descanso["linha"]
    jogador["olha"] = "baixo"
    dizer("A avó foi buscar-te. A equipa está curada: tenta outra vez!")


# =====================================================================
#                              O MAPA
# =====================================================================

def letra_do_mapa(coluna, linha):
    # A letra de um quadrado do MAPA. Fora do mapa e tudo arvores.
    if linha < 0 or linha >= len(MAPA):
        return "A"
    if coluna < 0 or coluna >= len(MAPA[linha]):
        return "A"
    return MAPA[linha][coluna]


def treinador_do_quadrado(letra):
    # Que treinador esta num quadrado: 0 para o "1", 1 para o "2"... ou -1
    # se a letra nao e de nenhum treinador que exista.
    if letra in "123456789" and int(letra) <= len(TREINADORES):
        return int(letra) - 1
    return -1


def encontrar_partida():
    # Onde esta o P no MAPA: (coluna, linha). Sem P, o primeiro bocado de relva.
    for procurada in ["P", "."]:
        for linha in range(len(MAPA)):
            for coluna in range(len(MAPA[linha])):
                if MAPA[linha][coluna] == procurada:
                    return coluna, linha
    return 0, 0


def treinadores_por_vencer():
    # Quantos treinadores do mapa ainda nao venceste.
    faltam = []
    for texto in MAPA:
        for letra in texto:
            numero = treinador_do_quadrado(letra)
            if numero != -1 and numero not in treinadores_vencidos and numero not in faltam:
                faltam.append(numero)
    return len(faltam)


def comecar_mundo():
    # Poe-te na partida, com as sopas todas e nenhum treinador vencido.
    global sopas
    voltar_ao_mundo()
    coluna, linha = encontrar_partida()
    jogador["coluna"] = coluna
    jogador["linha"] = linha
    jogador["olha"] = "baixo"
    jogador["passos"] = 0
    descanso["coluna"] = coluna
    descanso["linha"] = linha
    treinadores_vencidos.clear()
    sopas = SOPAS_NA_MOCHILA
    dizer("Anda com as setas. Vai contra um treinador para o desafiares.")


# ONDE SE PODE ANDAR
# Recebe a letra de um quadrado do MAPA e devolve True se da para andar para
# la, ou False se nao da. Como esta: so nao se passa nas arvores (A) nem na
# agua (~). (A casa da avo e os treinadores nao passam por aqui: contra eles
# vai-se sempre de encontro.)
# Ideias: nadar, isto e, passar na agua se levares na equipa um bicho do tipo
# "agua"; uma letra nova para um muro; uma ponte "=" por cima da agua.
def pode_andar(letra):
    if letra == "A" or letra == "~":
        return False
    return True


# QUANDO SALTA UM BICHO DA ERVA
# Corre a cada passo que das na erva alta (a letra e). Devolve True se desse
# passo salta um bicho a solta, ou False se nao salta nada. Como esta: e
# sorte, SORTE_NA_ERVA vezes em cada 100.
# Ideias: saltar sempre; nunca saltar dois bichos seguidos (guarda na memoria
# o passo do ultimo); quanto mais passos ja deste, mais bichos saltam.
def ha_batalha_na_erva():
    return random.randint(1, 100) <= SORTE_NA_ERVA


# QUE BICHO SALTA DA ERVA
# Devolve o bicho a solta, feito com criar_bicho(nome, nivel). Como esta: um
# bicho qualquer de BICHOS, um a tres niveis abaixo do teu bicho mais forte.
# Ideias: so bichos de planta; bichos mais fortes do lado direito do mapa
# (quando jogador["coluna"] e maior que 10); um bicho raro, que so salta 1 vez
# em cada 20.
def escolher_bicho_selvagem():
    nome = random.choice(list(BICHOS.keys()))
    nivel = nivel_mais_alto(minha_equipa) - random.randint(1, 3)
    if nivel < 1:
        nivel = 1
    return criar_bicho(nome, nivel)


def descansar():
    # Em casa da avo: cura a equipa, enche as sopas, e passa a ser aqui que
    # acordas se a equipa desmaiar.
    global sopas
    curar_tudo(minha_equipa)
    sopas = SOPAS_NA_MOCHILA
    descanso["coluna"] = jogador["coluna"]
    descanso["linha"] = jogador["linha"]
    dizer("A avó deu sopa a todos. A equipa está curada!")
    ao_descansar()


def desafiar(numero):
    # Foste contra um treinador: comeca a batalha, se ainda nao o venceste.
    global indice_treinador, batalha_selvagem
    if numero in treinadores_vencidos:
        dizer(TREINADORES[numero]["nome"] + ": «Já me ganhaste. Boa sorte!»")
        return
    indice_treinador = numero
    batalha_selvagem = False
    comecar_batalha()


def encontrar_bicho():
    # Saltou um bicho da erva: comeca uma batalha contra ele.
    global batalha_selvagem, bicho_a_solta
    bicho_a_solta = escolher_bicho_selvagem()
    batalha_selvagem = True
    comecar_batalha()


def andar(passo_coluna, passo_linha):
    # Tenta dar um passo: andar(1, 0) e para a direita, andar(0, -1) e para
    # cima. O que acontece depende da letra do quadrado para onde vais.
    global aviso
    if passo_coluna == 1:
        jogador["olha"] = "direita"
    elif passo_coluna == -1:
        jogador["olha"] = "esquerda"
    elif passo_linha == 1:
        jogador["olha"] = "baixo"
    else:
        jogador["olha"] = "cima"
    coluna = jogador["coluna"] + passo_coluna
    linha = jogador["linha"] + passo_linha
    letra = letra_do_mapa(coluna, linha)

    if treinador_do_quadrado(letra) != -1:
        desafiar(treinador_do_quadrado(letra))
        return
    if letra == "H":
        descansar()
        return
    if not pode_andar(letra):
        return

    jogador["coluna"] = coluna
    jogador["linha"] = linha
    jogador["passos"] = jogador["passos"] + 1
    aviso = ""
    ao_dar_passo(letra)
    if estado == "mundo" and letra == "e" and ha_batalha_na_erva():
        encontrar_bicho()


def tecla_no_mundo(tecla):
    # Um passo logo que se carrega na seta. Com a seta carregada, os passos
    # seguintes sao dados pelo andar_com_as_setas.
    global espera_do_passo
    if tecla == pygame.K_LEFT:
        andar(-1, 0)
    elif tecla == pygame.K_RIGHT:
        andar(1, 0)
    elif tecla == pygame.K_UP:
        andar(0, -1)
    elif tecla == pygame.K_DOWN:
        andar(0, 1)
    else:
        return
    espera_do_passo = 12


def andar_com_as_setas():
    # Corre a cada frame, no mapa: com uma seta carregada, da um passo de 9
    # em 9 frames.
    global espera_do_passo
    if espera_do_passo > 0:
        espera_do_passo = espera_do_passo - 1
        return
    teclas = pygame.key.get_pressed()
    if teclas[pygame.K_LEFT]:
        andar(-1, 0)
    elif teclas[pygame.K_RIGHT]:
        andar(1, 0)
    elif teclas[pygame.K_UP]:
        andar(0, -1)
    elif teclas[pygame.K_DOWN]:
        andar(0, 1)
    else:
        return
    espera_do_passo = 9


# =====================================================================
#                          ACONTECIMENTOS
# =====================================================================

# --- Os acontecimentos ---
# O jogo chama cada uma destas funcoes quando acontece o que o nome diz.
# Estao vazias (so tem "pass"): o que la escreveres passa a acontecer nesse
# momento. E aqui que se INVENTA: um bicho vampiro, um premio, um truque.
#
# Alem do que as regras do jogo podem usar (ver mais acima), tens:
#   memoria                 um dicionario so teu, para guardares o que
#                           quiseres de um turno para o outro:
#                           memoria["vitorias"] = 3
#                           (fica vazio cada vez que o jogo recomeca)
#   dizer("Boa!")           numa batalha, poe um texto no painel de baixo, a
#                           seguir aos que la estiverem; passa-se com Enter.
#                           No mapa, mostra o texto numa caixa
#   voltar_ao_mundo()       acaba a batalha ali mesmo e volta ao mapa
#   bicho in minha_equipa   e verdade se o bicho e teu, e nao do inimigo
#   bicho["vida"] = min(bicho["vida_max"], bicho["vida"] + 10)
#                           cura 10 de vida, sem passar da vida maxima
#   ganhar_xp(bicho, 20)    da 20 de experiencia a um bicho teu
#   sopas                   quantas sopas te restam. Para as MUDAR, a
#                           primeira linha da funcao tem de ser "global sopas"
memoria = {}


# QUANDO COMECA UMA BATALHA
# Corre no inicio de cada batalha, com as duas equipas ja prontas.
# batalha_selvagem e True se e contra um bicho a solta. Se e contra um
# treinador, treinador()["nome"] diz contra quem, e indice_treinador diz qual
# deles e: 0 no primeiro, 1 no segundo, e por ai fora.
# Ideias: dizer uma frase tua antes da luta; levar uma sopa a mais contra o
# segundo treinador; o teu bicho entrar com o ataque mais forte (mod_ataque
# a 1.25) contra os bichos a solta.
def ao_comecar_batalha():
    pass


# QUANDO UM ATAQUE ACERTA
# atacante: quem atacou. alvo: quem levou. dano: quanta vida o golpe tirou
# (a vida do alvo ja desceu). So corre nos ataques que fazem dano.
# Ideias: um bicho vampiro, que recupera metade do dano que faz; dizer
# "Que pancada!" quando o golpe tira mais de 20; o alvo ficar um bocadinho
# mais fraco de cada vez que leva (mod_defesa a descer).
def ao_acertar(atacante, alvo, dano):
    pass


# QUANDO UM BICHO DESMAIA
# desmaiado: o bicho que ficou sem vida. vencedor: o que o deitou abaixo
# (o que estava em campo do outro lado). Corre para os teus e para os do
# inimigo.
# Ideias: o vencedor recuperar 10 de vida; contar na memoria quantos bichos
# ja deitaste abaixo, e dizer o numero; o desmaiado despedir-se com uma frase.
def ao_desmaiar(desmaiado, vencedor):
    pass


# QUANDO UM BICHO TEU SOBE DE NIVEL
# bicho: o que acabou de subir. bicho["nivel"] ja e o nivel novo.
# Ideias: ficar com a vida toda (bicho["vida"] = bicho["vida_max"]); ganhar
# uma sopa; dizer uma frase de festa quando chega ao nivel 10.
def ao_subir_de_nivel(bicho):
    pass


# QUANDO GANHAS UMA BATALHA
# Corre quando o ultimo bicho do adversario desmaia (o de um treinador, ou o
# bicho a solta), antes de voltares ao mapa.
# Ideias: um premio (o teu bicho em campo ganha 30 de experiencia a mais);
# contar as vitorias na memoria e dizer quantas ja vao; o treinador dizer uma
# frase de mau perdedor.
def ao_ganhar_batalha():
    pass


# QUANDO SE CARREGA NUMA TECLA
# tecla: a tecla em que se carregou. pygame.K_s e a tecla S, pygame.K_c a C.
# Corre no mapa e nas batalhas: estado diz onde estas ("mundo" ou "batalha").
# (As setas, Enter, Espaco, Esc e Backspace ja fazem coisas no jogo.)
# Ideias: a tecla S da mais uma sopa (batota!); a tecla C cura o teu bicho,
# mas so uma vez por jogo (usa a memoria para te lembrares se ja foi usada).
# Mais dificil: APANHAR um bicho a solta. Se a batalha e selvagem e o bicho
# inimigo tem menos de um quarto da vida, a tecla C poe-no no lugar do teu
# ultimo bicho (minha_equipa[-1] = equipa_inimiga[ativo_inimigo]) e depois
# chama voltar_ao_mundo().
def ao_carregar_tecla(tecla):
    pass


# QUANDO DAS UM PASSO
# Corre a cada passo no mapa, ja no quadrado novo. letra: a letra desse
# quadrado no MAPA ("." e relva, "e" e erva alta...). jogador["passos"] diz
# quantos ja deste.
# Ideias: uma letra nova no mapa, por exemplo "s" para uma sopa perdida no
# chao (if letra == "s"); os bichos cansarem-se, e perderem 1 de vida a cada
# 20 passos; dizer "Cheira a maresia..." quando chegas perto da agua.
def ao_dar_passo(letra):
    pass


# QUANDO DESCANSAS EM CASA DA AVO
# Corre depois de a avo curar a equipa e encher as sopas.
# Ideias: a avo dar uma sopa a mais; a avo dizer outra coisa; o teu primeiro
# bicho ganhar 10 de experiencia por cada visita.
def ao_descansar():
    pass


# A CADA FRAME
# Corre 60 vezes por segundo enquanto andas pelo mapa (nas batalhas nao).
# Ideias: um relogio (soma 1 a memoria["frames"] e, de 60 em 60, passou um
# segundo); os bichos irem recuperando vida devagarinho enquanto andas.
def a_cada_frame():
    pass


# =====================================================================
#                          O TURNO, PASSO A PASSO
#
# Um turno e uma fila de acoes. Executamos uma, mostramos as mensagens
# que ela deixou, e so depois de o jogador carregar em Enter passamos a
# seguinte. Quando a fila acaba, vemos quem desmaiou.
# =====================================================================

# QUE ATAQUE O INIMIGO ESCOLHE
# Nao recebe nada, e devolve o NOME de um dos ataques do bicho inimigo que
# esta em campo. Como esta: da pontos a cada ataque (os que magoam mais
# valem mais, e curar vale muito quando ele tem pouca vida), junta-lhes
# alguma sorte e escolhe o que ficou com mais pontos.
# Ideias: escolher ao calhas, com random.choice(BICHOS[inimigo["nome"]]["ataques"]);
# escolher sempre o que magoa mais, sem sorte nenhuma; curar-se mais cedo.
def escolher_ataque_inimigo():
    inimigo = equipa_inimiga[ativo_inimigo]
    eu = minha_equipa[ativo_meu]
    melhor = ""
    melhor_pontos = -1
    for nome in BICHOS[inimigo["nome"]]["ataques"]:
        dados = ATAQUES[nome]
        if dados["efeito"] == "dano":
            pontos = dados["poder"] * eficacia(dados["tipo"], eu["tipo"])
            pontos = pontos * dados["precisao"] / 100
        elif dados["efeito"] == "cura":
            pontos = 10
            if inimigo["vida"] < inimigo["vida_max"] * 0.4:
                pontos = 50
        else:
            pontos = 25
        # A sorte faz o inimigo nao ser previsivel de mais.
        pontos = pontos * random.uniform(0.6, 1.4)
        if pontos > melhor_pontos:
            melhor_pontos = pontos
            melhor = nome
    return melhor


# QUEM ATACA PRIMEIRO
# Corre quando os dois bichos vao atacar no mesmo turno. Recebe o teu bicho
# e o do inimigo, e devolve "jogador" (o teu vai primeiro) ou "inimigo".
# Como esta: vai primeiro o mais rapido; se forem iguais, e a sorte.
# (Trocar de bicho e comer sopa vem sempre antes dos ataques.)
# Ideias: ir primeiro o que tem menos vida; ser sempre ao calhas; o teu bicho
# ir sempre primeiro no primeiro turno (conta os turnos na memoria).
def quem_ataca_primeiro(eu, inimigo):
    if eu["velocidade"] > inimigo["velocidade"]:
        return "jogador"
    if eu["velocidade"] < inimigo["velocidade"]:
        return "inimigo"
    if random.randint(0, 1) == 0:
        return "jogador"
    return "inimigo"


def jogador_escolheu(acao_jogador):
    global fila_acoes
    acao_inimigo = {"quem": "inimigo", "tipo": "atacar", "ataque": escolher_ataque_inimigo()}
    eu = minha_equipa[ativo_meu]
    inimigo = equipa_inimiga[ativo_inimigo]
    # Trocar de bicho e comer sopa vem sempre antes dos ataques.
    # Entre dois ataques, decide a regra quem_ataca_primeiro.
    if acao_jogador["tipo"] != "atacar":
        fila_acoes = [acao_jogador, acao_inimigo]
    elif quem_ataca_primeiro(eu, inimigo) == "jogador":
        fila_acoes = [acao_jogador, acao_inimigo]
    else:
        fila_acoes = [acao_inimigo, acao_jogador]
    continuar()


def mudar_modificador(bicho, chave, fator, nome_do_valor):
    novo = bicho[chave] * fator
    if novo > 2.01 or novo < 0.49:
        mensagens.append("O " + nome_do_valor + " de " + bicho["nome"] + " já não muda mais!")
        return
    bicho[chave] = novo
    if fator > 1:
        mensagens.append("O " + nome_do_valor + " de " + bicho["nome"] + " subiu!")
    else:
        mensagens.append("O " + nome_do_valor + " de " + bicho["nome"] + " desceu!")


def usar_ataque(atacante, alvo, nome):
    dados = ATAQUES[nome]
    mensagens.append(atacante["nome"] + " usa " + nome + "!")
    if "som" in dados:
        tocar_som(dados["som"])
    if random.randint(1, 100) > dados["precisao"]:
        mensagens.append("Mas falhou!")
        return
    efeito = dados["efeito"]
    if efeito == "dano":
        dano = calcular_dano(atacante, alvo, nome)
        if golpe_critico(atacante, alvo):
            dano = int(dano * 1.5)
            mensagens.append("Golpe crítico!")
        alvo["vida"] = max(0, alvo["vida"] - dano)
        alvo["tremor"] = 24
        multiplicador = eficacia(dados["tipo"], alvo["tipo"])
        if multiplicador > 1:
            mensagens.append("É super eficaz!")
        if multiplicador < 1:
            mensagens.append("Não é muito eficaz...")
        ao_acertar(atacante, alvo, dano)
    elif efeito == "cura":
        cura = atacante["vida_max"] * 40 // 100
        atacante["vida"] = min(atacante["vida_max"], atacante["vida"] + cura)
        mensagens.append(atacante["nome"] + " recuperou vida.")
    elif efeito == "sobe_ataque":
        mudar_modificador(atacante, "mod_ataque", 1.25, "ataque")
    elif efeito == "sobe_defesa":
        mudar_modificador(atacante, "mod_defesa", 1.25, "defesa")
    elif efeito == "baixa_ataque":
        mudar_modificador(alvo, "mod_ataque", 0.8, "ataque")
    elif efeito == "baixa_defesa":
        mudar_modificador(alvo, "mod_defesa", 0.8, "defesa")


def executar(acao):
    global ativo_meu, ativo_inimigo, sopas
    if acao["quem"] == "jogador":
        atacante = minha_equipa[ativo_meu]
        alvo = equipa_inimiga[ativo_inimigo]
    else:
        atacante = equipa_inimiga[ativo_inimigo]
        alvo = minha_equipa[ativo_meu]

    if acao["tipo"] == "atacar":
        # Quem desmaiou antes de chegar a sua vez ja nao ataca.
        if atacante["vida"] > 0 and alvo["vida"] > 0:
            usar_ataque(atacante, alvo, acao["ataque"])
    elif acao["tipo"] == "trocar":
        mensagens.append("Volta, " + atacante["nome"] + "!")
        atacante["mod_ataque"] = 1.0
        atacante["mod_defesa"] = 1.0
        ativo_meu = acao["indice"]
        mensagens.append("Vai, " + minha_equipa[ativo_meu]["nome"] + "!")
        som_do_bicho(minha_equipa[ativo_meu])
    elif acao["tipo"] == "entrar_inimigo":
        ativo_inimigo = acao["indice"]
        mensagens.append(treinador()["nome"] + " manda " + equipa_inimiga[ativo_inimigo]["nome"] + "!")
        som_do_bicho(equipa_inimiga[ativo_inimigo])
    elif acao["tipo"] == "sopa":
        sopas = sopas - 1
        cura = atacante["vida_max"] // 2
        atacante["vida"] = min(atacante["vida_max"], atacante["vida"] + cura)
        mensagens.append(atacante["nome"] + " comeu a sopa da avó. Que conforto.")


def ganhar_xp(bicho, quanto):
    bicho["xp"] = bicho["xp"] + quanto
    mensagens.append(bicho["nome"] + " ganhou " + str(quanto) + " de experiência.")
    while bicho["xp"] >= xp_para_subir(bicho):
        bicho["xp"] = bicho["xp"] - xp_para_subir(bicho)
        # Subir de nivel aumenta tudo, mas mantem a vida que ja se perdeu.
        perdida = bicho["vida_max"] - bicho["vida"]
        bicho["nivel"] = bicho["nivel"] + 1
        calcular_valores(bicho)
        bicho["vida"] = max(1, bicho["vida_max"] - perdida)
        mensagens.append(bicho["nome"] + " subiu para o nível " + str(bicho["nivel"]) + "!")
        ao_subir_de_nivel(bicho)


def fim_do_turno():
    global fase, estado, troca_obrigatoria, cursor
    if a_fugir:
        voltar_ao_mundo()
        return
    inimigo = equipa_inimiga[ativo_inimigo]
    eu = minha_equipa[ativo_meu]

    if inimigo["vida"] <= 0:
        if not inimigo["anunciado"]:
            inimigo["anunciado"] = True
            mensagens.append(inimigo["nome"] + " desmaiou!")
            ao_desmaiar(inimigo, eu)
            ganhar_xp(eu, inimigo["nivel"] * 12)
            if proximo_vivo(equipa_inimiga) == -1:
                ao_ganhar_batalha()
            fase = "texto"
            return
        seguinte = proximo_vivo(equipa_inimiga)
        if seguinte == -1:
            ganhar_batalha()
            return
        fila_acoes.append({"quem": "inimigo", "tipo": "entrar_inimigo", "indice": seguinte})
        continuar()
        return

    if eu["vida"] <= 0:
        if not eu["anunciado"]:
            eu["anunciado"] = True
            mensagens.append(eu["nome"] + " desmaiou!")
            ao_desmaiar(eu, inimigo)
            fase = "texto"
            return
        if proximo_vivo(minha_equipa) == -1:
            estado = "derrota"
            return
        troca_obrigatoria = True
        fase = "equipa"
        cursor = proximo_vivo(minha_equipa)
        return

    fase = "menu"
    cursor = 0


def continuar():
    global fase
    while len(fila_acoes) > 0:
        executar(fila_acoes.pop(0))
        if len(mensagens) > 0:
            fase = "texto"
            return
    fim_do_turno()


def barras_paradas():
    # Enquanto alguma barra de vida esta a descer, nao passamos o texto.
    for bicho in minha_equipa + equipa_inimiga:
        if abs(bicho["vida_mostrada"] - bicho["vida"]) > 0.5:
            return False
    return True


# =====================================================================
#                          AS TECLAS DA BATALHA
# =====================================================================

def tecla_na_batalha(tecla):
    global fase, cursor, troca_obrigatoria, ativo_meu, a_fugir
    confirmar = tecla == pygame.K_RETURN or tecla == pygame.K_SPACE
    voltar = tecla == pygame.K_ESCAPE or tecla == pygame.K_BACKSPACE
    eu = minha_equipa[ativo_meu]

    if fase == "texto":
        if confirmar and barras_paradas():
            mensagens.pop(0)
            if len(mensagens) == 0:
                continuar()
        return

    if fase == "menu":
        quantas = len(OPCOES_MENU)
    elif fase == "ataques":
        quantas = len(BICHOS[eu["nome"]]["ataques"])
    else:
        quantas = len(minha_equipa)
    if tecla == pygame.K_UP:
        cursor = (cursor - 1) % quantas
    if tecla == pygame.K_DOWN:
        cursor = (cursor + 1) % quantas

    if fase == "menu" and confirmar:
        escolha = OPCOES_MENU[cursor]
        if escolha == "Lutar":
            fase = "ataques"
            cursor = 0
        elif escolha == "Equipa":
            fase = "equipa"
            cursor = ativo_meu
        elif escolha == "Sopa":
            if sopas == 0:
                mensagens.append("Já não há sopa. A avó vai ficar triste.")
                fase = "texto"
            elif eu["vida"] == eu["vida_max"]:
                mensagens.append(eu["nome"] + " já está de barriga cheia.")
                fase = "texto"
            else:
                jogador_escolheu({"quem": "jogador", "tipo": "sopa"})
        elif escolha == "Fugir":
            # So se foge de um bicho a solta. Depois de lido o texto, o
            # fim_do_turno ve o a_fugir e volta ao mapa.
            if batalha_selvagem:
                mensagens.append("Fugiste a sete pés!")
                a_fugir = True
            else:
                mensagens.append("De um treinador não se foge!")
            fase = "texto"

    elif fase == "ataques":
        if voltar:
            fase = "menu"
            cursor = 0
        elif confirmar:
            nome = BICHOS[eu["nome"]]["ataques"][cursor]
            jogador_escolheu({"quem": "jogador", "tipo": "atacar", "ataque": nome})

    elif fase == "equipa":
        if voltar and not troca_obrigatoria:
            fase = "menu"
            cursor = 1
        elif confirmar:
            escolhido = minha_equipa[cursor]
            if escolhido["vida"] <= 0 or cursor == ativo_meu:
                return
            if troca_obrigatoria:
                # O anterior desmaiou: trocar nao gasta o turno.
                troca_obrigatoria = False
                ativo_meu = cursor
                mensagens.append("Vai, " + escolhido["nome"] + "!")
                som_do_bicho(escolhido)
                fase = "texto"
            else:
                jogador_escolheu({"quem": "jogador", "tipo": "trocar", "indice": cursor})


# =====================================================================
#                          DESENHAR
# =====================================================================

# --- Os desenhos ---
# As funcoes que se seguem desenham um bicho (o corpo e os olhos) e a barra
# de vida. Desenha-se com formas do pygame, sempre no "ecra":
#   pygame.draw.circle(ecra, cor, (x, y), raio)
#   pygame.draw.ellipse(ecra, cor, (x, y, largura, altura))
#   pygame.draw.rect(ecra, cor, (x, y, largura, altura))
#   pygame.draw.line(ecra, cor, (x1, y1), (x2, y2), grossura)
#   pygame.draw.polygon(ecra, cor, [(x1, y1), (x2, y2), (x3, y3)])
# O x cresce para a direita e o y cresce para BAIXO. Uma cor sao tres
# numeros (vermelho, verde, azul), de 0 a 255. O que se desenha depois fica
# por cima do que se desenhou antes. escurecer(cor, 0.5) da a mesma cor, mais
# escura.
#   cx, cy       o centro do bicho, em pixeis
#   tamanho      a largura (e a altura) do bicho. O mesmo bicho e desenhado
#                grande na batalha e pequeno nos menus, por isso faz as
#                contas com o tamanho (tamanho // 4) em vez de numeros fixos
#   bicho["nome"], bicho["tipo"], bicho["vida"], bicho["vida_max"]
#   BICHOS[bicho["nome"]]    a ficha dele, la em cima ("forma", "cor"...)
# Nos desenhos do mapa (um quadrado, tu, um treinador):
#   x, y         o canto de cima, a esquerda, do quadrado onde se desenha
#   QUADRADO     o lado do quadrado, em pixeis. O meio dele e
#                (x + QUADRADO // 2, y + QUADRADO // 2)

# O BICHO INTEIRO
# Faz o bicho respirar e tremer, e depois mostra a imagem dele ou, se nao
# houver imagem, manda desenhar o corpo e os olhos.
#   olha_para         1 se o bicho olha para a direita, -1 para a esquerda
#   bicho["tremor"]   os frames que ainda treme depois de levar um golpe
# Ideias: respirar mais depressa; saltar em vez de tremer; ficar mais
# pequeno quando tem pouca vida.
def desenhar_bicho(bicho, cx, cy, tamanho, olha_para):
    if bicho["vida_mostrada"] <= 0.5:
        return
    dados = BICHOS[bicho["nome"]]
    # Respira: sobe e desce devagar.
    cy = cy + int(math.sin(pygame.time.get_ticks() / 300 + cx) * 3)
    if bicho["tremor"] > 0:
        cx = cx + random.randint(-6, 6)

    imagem = obter_imagem(dados["imagem"], tamanho)
    if imagem is not None:
        if olha_para == -1:
            imagem = pygame.transform.flip(imagem, True, False)
        ecra.blit(imagem, (cx - tamanho // 2, cy - tamanho // 2))
        return

    cor = dados["cor"]
    # Pisca a branco nos primeiros frames depois de levar um golpe.
    if bicho["tremor"] > 0 and bicho["tremor"] % 6 < 3:
        cor = BRANCO
    desenhar_corpo(bicho, cor, cx, cy, tamanho)
    desenhar_olhos(bicho, cx, cy, tamanho, olha_para)


# O CORPO DE UM BICHO
# Desenha a forma que esta na ficha do bicho ("circulo", "quadrado",
# "triangulo" ou "gota"), com um contorno mais escuro.
#   cor      a cor com que se pinta (a do bicho, ou branco quando leva um golpe)
#   corpo    um retangulo do tamanho do bicho: corpo.top e o cimo,
#            corpo.bottom o fundo, corpo.left e corpo.right os lados
# Ideias: uma forma nova (um "losango", para usares na ficha de um bicho);
# uma crista ou um chapeu por cima do corpo; uma boca; riscas.
def desenhar_corpo(bicho, cor, cx, cy, tamanho):
    dados = BICHOS[bicho["nome"]]
    contorno = escurecer(dados["cor"], 0.55)
    corpo = pygame.Rect(0, 0, tamanho, tamanho)
    corpo.center = (cx, cy)

    if dados["forma"] == "circulo":
        pygame.draw.ellipse(ecra, cor, corpo)
        pygame.draw.ellipse(ecra, contorno, corpo, 4)
    elif dados["forma"] == "quadrado":
        pygame.draw.rect(ecra, cor, corpo, border_radius=tamanho // 5)
        pygame.draw.rect(ecra, contorno, corpo, 4, border_radius=tamanho // 5)
    elif dados["forma"] == "triangulo":
        pontos = [(cx, corpo.top), (corpo.right, corpo.bottom), (corpo.left, corpo.bottom)]
        pygame.draw.polygon(ecra, cor, pontos)
        pygame.draw.polygon(ecra, contorno, pontos, 4)
    elif dados["forma"] == "gota":
        raio = tamanho * 2 // 5
        centro_baixo = (cx, corpo.bottom - raio)
        bico = [(cx, corpo.top), (cx + raio, centro_baixo[1]), (cx - raio, centro_baixo[1])]
        pygame.draw.circle(ecra, cor, centro_baixo, raio)
        pygame.draw.polygon(ecra, cor, bico)
        pygame.draw.circle(ecra, contorno, centro_baixo, raio, 4)


# OS OLHOS DE UM BICHO
# Dois circulos brancos, cada um com a pupila virada para o outro bicho.
#   olha_para    1 se o bicho olha para a direita, -1 para a esquerda
# Ideias: olhos maiores; olhos zangados quando tem pouca vida (uma linha por
# cima de cada olho); um olho so, ao meio, como um ciclope.
def desenhar_olhos(bicho, cx, cy, tamanho, olha_para):
    olho_y = cy + tamanho // 10
    raio_olho = tamanho // 9
    for lado in [-1, 1]:
        olho_x = cx + lado * tamanho // 5
        pygame.draw.circle(ecra, BRANCO, (olho_x, olho_y), raio_olho)
        pygame.draw.circle(ecra, PRETO, (olho_x + olha_para * raio_olho // 2, olho_y), raio_olho // 2)


# A BARRA DE VIDA
# x, y: o canto de cima, a esquerda. largura: o comprimento da barra cheia.
# fracao vai de 0 (sem vida) a 1 (vida toda). A barra e verde, passa a
# amarela abaixo de metade e a vermelha quando esta quase no fim.
# Ideias: outras cores; uma barra mais grossa; piscar quando esta vermelha.
def desenhar_barra_vida(bicho, x, y, largura):
    fracao = bicho["vida_mostrada"] / bicho["vida_max"]
    cor = VERDE
    if fracao < 0.5:
        cor = AMARELO
    if fracao < 0.2:
        cor = VERMELHO
    pygame.draw.rect(ecra, PRETO, (x, y, largura, 12), border_radius=6)
    pygame.draw.rect(ecra, cor, (x, y, int(largura * fracao), 12), border_radius=6)


# UM QUADRADO DO MAPA
# letra: a letra desse quadrado no MAPA. Primeiro pinta-se relva em todos, e
# depois, por cima, o que a letra disser: erva alta, uma arvore, agua ou a
# casa da avo. (Tu e os treinadores sao desenhados depois, por outras funcoes.)
# Ideias: outras cores (um mapa de neve, ou de deserto); flores na relva; o
# desenho de uma letra nova que tenhas inventado (if letra == "s").
def desenhar_quadrado(letra, x, y):
    meio = x + QUADRADO // 2
    pygame.draw.rect(ecra, RELVA, (x, y, QUADRADO, QUADRADO))
    if letra == "e":
        pygame.draw.rect(ecra, ERVA_ALTA, (x, y, QUADRADO, QUADRADO))
        # Tres tufos, cada um com duas folhas.
        for tufo in [x + 8, x + 20, x + 32]:
            pygame.draw.line(ecra, RELVA, (tufo, y + 32), (tufo - 4, y + 14), 3)
            pygame.draw.line(ecra, RELVA, (tufo, y + 32), (tufo + 4, y + 10), 3)
    elif letra == "A":
        pygame.draw.rect(ecra, TRONCO, (meio - 4, y + 22, 8, 16))
        pygame.draw.circle(ecra, COPA, (meio, y + 16), 15)
        pygame.draw.circle(ecra, escurecer(COPA, 0.8), (meio, y + 16), 15, 3)
    elif letra == "~":
        pygame.draw.rect(ecra, AGUA, (x, y, QUADRADO, QUADRADO))
        # Duas ondas, que andam para a direita e voltam ao inicio.
        desvio = pygame.time.get_ticks() // 200 % 8
        pygame.draw.line(ecra, BRANCO, (x + 4 + desvio, y + 12), (x + 16 + desvio, y + 12), 2)
        pygame.draw.line(ecra, BRANCO, (x + 16 + desvio, y + 28), (x + 28 + desvio, y + 28), 2)
    elif letra == "H":
        pygame.draw.rect(ecra, PAREDE, (x + 5, y + 18, 30, 20))
        pygame.draw.polygon(ecra, TELHADO, [(x + 1, y + 20), (meio, y + 2), (x + 39, y + 20)])
        pygame.draw.rect(ecra, TRONCO, (meio - 4, y + 26, 8, 12))


# TU, NO MAPA
# olha_para: "cima", "baixo", "esquerda" ou "direita". Como esta: um corpo
# amarelo, uma cabeca, e dois olhos virados para onde vais (de costas nao se
# veem).
# Ideias: outra cor de camisola; um chapeu; o teu primeiro bicho a andar
# atras de ti, pequenino (desenhar_bicho(minha_equipa[0], x, y, 20, 1)).
def desenhar_jogador(x, y, olha_para):
    meio = x + QUADRADO // 2
    pygame.draw.rect(ecra, AMARELO, (meio - 9, y + 20, 18, 17), border_radius=5)
    pygame.draw.circle(ecra, PAREDE, (meio, y + 13), 10)
    pygame.draw.circle(ecra, PRETO, (meio, y + 13), 10, 2)
    if olha_para == "cima":
        return
    desvio = 0
    if olha_para == "esquerda":
        desvio = -4
    if olha_para == "direita":
        desvio = 4
    pygame.draw.circle(ecra, PRETO, (meio - 4 + desvio, y + 13), 2)
    pygame.draw.circle(ecra, PRETO, (meio + 4 + desvio, y + 13), 2)


# UM TREINADOR, NO MAPA
# treinador: a ficha dele, de TREINADORES. vencido: True se ja lhe ganhaste.
# Como esta: a camisola tem a cor_fundo dele, e um ponto de exclamacao por
# cima enquanto nao o venceres. Vencido, fica cinzento.
# Ideias: uma coroa na ultima treinadora (if treinador["nome"] == ...); um
# desenho diferente para cada um; os vencidos ficarem deitados.
def desenhar_treinador(treinador, x, y, vencido):
    meio = x + QUADRADO // 2
    cor = escurecer(treinador["cor_fundo"], 0.8)
    if vencido:
        cor = CINZA
    pygame.draw.rect(ecra, cor, (meio - 9, y + 20, 18, 17), border_radius=5)
    pygame.draw.circle(ecra, PAREDE, (meio, y + 13), 10)
    pygame.draw.circle(ecra, PRETO, (meio, y + 13), 10, 2)
    pygame.draw.circle(ecra, PRETO, (meio - 4, y + 13), 2)
    pygame.draw.circle(ecra, PRETO, (meio + 4, y + 13), 2)
    if not vencido:
        pygame.draw.rect(ecra, VERMELHO, (meio + 9, y, 4, 9))
        pygame.draw.rect(ecra, VERMELHO, (meio + 9, y + 11, 4, 4))


def canto_do_mapa():
    # Onde se desenha o primeiro quadrado, para o mapa ficar ao meio do ecra
    # (por cima da faixa de baixo, que tem 40 pixeis).
    largura = 0
    for texto in MAPA:
        largura = max(largura, len(texto))
    x = max(0, (LARGURA - largura * QUADRADO) // 2)
    y = max(0, (ALTURA - 40 - len(MAPA) * QUADRADO) // 2)
    return x, y


def desenhar_mundo():
    ecra.fill(PRETO)
    x0, y0 = canto_do_mapa()
    linha = 0
    for texto in MAPA:
        coluna = 0
        for letra in texto:
            x = x0 + coluna * QUADRADO
            y = y0 + linha * QUADRADO
            desenhar_quadrado(letra, x, y)
            numero = treinador_do_quadrado(letra)
            if numero != -1:
                desenhar_treinador(TREINADORES[numero], x, y, numero in treinadores_vencidos)
            coluna = coluna + 1
        linha = linha + 1
    desenhar_jogador(x0 + jogador["coluna"] * QUADRADO, y0 + jogador["linha"] * QUADRADO, jogador["olha"])

    # A caixa com o que foi dito, por cima do mapa.
    if aviso != "":
        pygame.draw.rect(ecra, PAINEL, (20, 500, LARGURA - 40, 50), border_radius=12)
        pygame.draw.rect(ecra, BRANCO, (20, 500, LARGURA - 40, 50), 3, border_radius=12)
        mostrar_texto(aviso, 38, 514, BRANCO, fonte)

    # A faixa de baixo: os treinadores que faltam, a equipa e as sopas.
    pygame.draw.rect(ecra, PAINEL, (0, ALTURA - 40, LARGURA, 40))
    faltam = treinadores_por_vencer()
    mostrar_texto("Treinadores por vencer: " + str(faltam), 14, ALTURA - 28, BRANCO, fonte_pequena)
    x = 280
    for bicho in minha_equipa[:4]:
        mostrar_texto("Nv " + str(bicho["nivel"]), x, ALTURA - 28, AMARELO, fonte_pequena)
        desenhar_barra_vida(bicho, x + 48, ALTURA - 26, 60)
        x = x + 125
    mostrar_texto("Sopas: " + str(sopas), LARGURA - 90, ALTURA - 28, BRANCO, fonte_pequena)


def desenhar_caixa_bicho(bicho, x, y, com_numeros):
    altura = 70
    if com_numeros:
        altura = 95
    pygame.draw.rect(ecra, PAINEL, (x, y, 300, altura), border_radius=10)
    pygame.draw.rect(ecra, BRANCO, (x, y, 300, altura), 2, border_radius=10)
    mostrar_texto(bicho["nome"], x + 14, y + 10, BRANCO, fonte)
    mostrar_texto("Nv " + str(bicho["nivel"]), x + 235, y + 12, AMARELO, fonte_pequena)
    cor_tipo = CORES_TIPO[bicho["tipo"]]
    pygame.draw.rect(ecra, cor_tipo, (x + 14, y + 38, 70, 18), border_radius=9)
    mostrar_texto(bicho["tipo"], x + 22, y + 40, PRETO, fonte_pequena)
    desenhar_barra_vida(bicho, x + 95, y + 42, 190)
    if com_numeros:
        vida = str(int(bicho["vida_mostrada"] + 0.5)) + " / " + str(bicho["vida_max"])
        mostrar_texto(vida, x + 180, y + 64, BRANCO, fonte_pequena)
        mostrar_texto("XP " + str(bicho["xp"]) + "/" + str(xp_para_subir(bicho)), x + 14, y + 64, CINZA, fonte_pequena)


def desenhar_painel():
    pygame.draw.rect(ecra, PAINEL, (0, 440, LARGURA, 160))
    pygame.draw.rect(ecra, BRANCO, (8, 448, LARGURA - 16, 144), 3, border_radius=12)


def desenhar_batalha():
    eu = minha_equipa[ativo_meu]
    inimigo = equipa_inimiga[ativo_inimigo]

    ecra.fill(treinador()["cor_fundo"])
    pygame.draw.rect(ecra, escurecer(treinador()["cor_fundo"], 0.75), (0, 250, LARGURA, 190))
    pygame.draw.ellipse(ecra, escurecer(treinador()["cor_fundo"], 0.55), (480, 205, 230, 55))
    pygame.draw.ellipse(ecra, escurecer(treinador()["cor_fundo"], 0.55), (70, 385, 280, 60))

    desenhar_bicho(inimigo, 595, 180, 110, -1)
    desenhar_bicho(eu, 210, 340, 150, 1)
    desenhar_caixa_bicho(inimigo, 40, 40, False)
    desenhar_caixa_bicho(eu, 460, 300, True)

    desenhar_painel()
    if fase == "texto":
        if len(mensagens) > 0:
            mostrar_texto(mensagens[0], 34, 475, BRANCO, fonte)
            if barras_paradas() and pygame.time.get_ticks() // 400 % 2 == 0:
                pygame.draw.polygon(ecra, AMARELO, [(748, 560), (768, 560), (758, 572)])

    elif fase == "menu":
        mostrar_texto("O que faz " + eu["nome"] + "?", 34, 475, BRANCO, fonte)
        y = 458
        indice = 0
        for opcao in OPCOES_MENU:
            texto = opcao
            if opcao == "Sopa":
                texto = "Sopa (" + str(sopas) + ")"
            cor = BRANCO
            if indice == cursor:
                cor = AMARELO
                mostrar_texto(">", 545, y, AMARELO, fonte)
            mostrar_texto(texto, 570, y, cor, fonte)
            y = y + 32
            indice = indice + 1

    elif fase == "ataques":
        nomes = BICHOS[eu["nome"]]["ataques"]
        y = 460
        indice = 0
        for nome in nomes:
            cor = BRANCO
            if indice == cursor:
                cor = AMARELO
                mostrar_texto(">", 22, y, AMARELO, fonte)
            pygame.draw.circle(ecra, CORES_TIPO[ATAQUES[nome]["tipo"]], (52, y + 10), 7)
            mostrar_texto(nome, 66, y, cor, fonte)
            y = y + 32
            indice = indice + 1
        # A ficha do ataque escolhido, do lado direito.
        dados = ATAQUES[nomes[cursor]]
        mostrar_texto("Tipo: " + dados["tipo"], 440, 462, BRANCO, fonte_pequena)
        if dados["efeito"] == "dano":
            mostrar_texto("Poder: " + str(dados["poder"]), 440, 488, BRANCO, fonte_pequena)
        else:
            mostrar_texto("Efeito: " + dados["efeito"].replace("_", " "), 440, 488, BRANCO, fonte_pequena)
        mostrar_texto("Precisão: " + str(dados["precisao"]), 440, 514, BRANCO, fonte_pequena)
        if dados["efeito"] == "dano":
            multiplicador = eficacia(dados["tipo"], inimigo["tipo"])
            if multiplicador > 1:
                mostrar_texto("Super eficaz contra " + inimigo["nome"] + "!", 440, 545, VERDE, fonte_pequena)
            if multiplicador < 1:
                mostrar_texto("Pouco eficaz contra " + inimigo["nome"] + ".", 440, 545, VERMELHO, fonte_pequena)
        mostrar_texto("Esc: voltar", 680, 568, CINZA, fonte_pequena)

    elif fase == "equipa":
        desenhar_lista_equipa()
        dica = "Enter: entra este · Esc: voltar (trocar gasta o turno)"
        if troca_obrigatoria:
            dica = "Enter: entra este"
        mostrar_texto(dica, 34, 500, CINZA, fonte)


def desenhar_lista_equipa():
    pygame.draw.rect(ecra, PAINEL, (100, 90, 600, 380), border_radius=14)
    pygame.draw.rect(ecra, BRANCO, (100, 90, 600, 380), 3, border_radius=14)
    titulo = "Quem entra?"
    if troca_obrigatoria:
        titulo = "Quem entra? (tens de escolher)"
    mostrar_texto(titulo, 130, 110, AMARELO, fonte)
    y = 160
    indice = 0
    for bicho in minha_equipa:
        if indice == cursor:
            pygame.draw.rect(ecra, (60, 60, 90), (115, y - 8, 570, 90), border_radius=10)
        desenhar_bicho(bicho, 170, y + 36, 60, 1)
        cor = BRANCO
        if bicho["vida"] <= 0:
            cor = CINZA
        mostrar_texto(bicho["nome"] + "  Nv " + str(bicho["nivel"]), 230, y + 6, cor, fonte)
        desenhar_barra_vida(bicho, 230, y + 42, 250)
        mostrar_texto(str(bicho["vida"]) + " / " + str(bicho["vida_max"]), 500, y + 38, cor, fonte_pequena)
        if bicho["vida"] <= 0:
            mostrar_texto("desmaiado", 590, y + 38, VERMELHO, fonte_pequena)
        elif indice == ativo_meu:
            mostrar_texto("em campo", 590, y + 38, AMARELO, fonte_pequena)
        y = y + 100
        indice = indice + 1


def desenhar_escolha():
    ecra.fill(PRETO)
    mostrar_texto("Escolhe " + str(TAMANHO_EQUIPA) + " bichos", 30, 20, AMARELO, fonte)
    mostrar_texto("Enter escolhe · Backspace tira o último · o primeiro é o que entra primeiro", 30, 52, CINZA, fonte_pequena)
    colunas = 4
    # So cabem duas filas de cartoes. Com mais bichos do que isso, mostram-se
    # as duas filas onde anda o cursor.
    filas = (len(nomes_dos_bichos) + colunas - 1) // colunas
    primeira_fila = max(0, min(cursor_escolha // colunas, filas - 2))
    if primeira_fila > 0:
        pygame.draw.polygon(ecra, AMARELO, [(770, 62), (790, 62), (780, 50)])
    if primeira_fila + 2 < filas:
        pygame.draw.polygon(ecra, AMARELO, [(770, 426), (790, 426), (780, 438)])
    indice = 0
    for nome in nomes_dos_bichos:
        fila = indice // colunas - primeira_fila
        if fila < 0 or fila > 1:
            indice = indice + 1
            continue
        x = 30 + (indice % colunas) * 188
        y = 85 + fila * 170
        cartao = pygame.Rect(x, y, 176, 158)
        cor_borda = CINZA
        if indice == cursor_escolha:
            cor_borda = AMARELO
        pygame.draw.rect(ecra, PAINEL, cartao, border_radius=12)
        pygame.draw.rect(ecra, cor_borda, cartao, 3, border_radius=12)
        modelo = criar_bicho(nome, NIVEL_INICIAL)
        desenhar_bicho(modelo, cartao.centerx, y + 60, 80, 1)
        mostrar_texto(nome, x + 10, y + 112, BRANCO, fonte_pequena)
        tipo = BICHOS[nome]["tipo"]
        pygame.draw.rect(ecra, CORES_TIPO[tipo], (x + 10, y + 134, 70, 16), border_radius=8)
        mostrar_texto(tipo, x + 16, y + 135, PRETO, fonte_pequena)
        if nome in escolhidos:
            numero = escolhidos.index(nome) + 1
            pygame.draw.circle(ecra, AMARELO, (x + 154, y + 22), 16)
            mostrar_texto(str(numero), x + 148, y + 12, PRETO, fonte)
        indice = indice + 1

    # A ficha do bicho onde esta o cursor.
    dados = BICHOS[nomes_dos_bichos[cursor_escolha]]
    y = 440
    pygame.draw.rect(ecra, PAINEL, (30, y, 740, 145), border_radius=12)
    mostrar_texto(nomes_dos_bichos[cursor_escolha], 50, y + 14, AMARELO, fonte)
    linha = "Vida " + str(dados["vida"]) + "   Ataque " + str(dados["ataque"])
    linha = linha + "   Defesa " + str(dados["defesa"]) + "   Velocidade " + str(dados["velocidade"])
    mostrar_texto(linha, 50, y + 50, BRANCO, fonte_pequena)
    x = 50
    for nome in dados["ataques"]:
        pygame.draw.circle(ecra, CORES_TIPO[ATAQUES[nome]["tipo"]], (x + 6, y + 96), 6)
        mostrar_texto(nome, x + 18, y + 88, BRANCO, fonte_pequena)
        x = x + 180


def tecla_na_escolha(tecla):
    global cursor_escolha, minha_equipa
    colunas = 4
    total = len(nomes_dos_bichos)
    if tecla == pygame.K_RIGHT:
        cursor_escolha = (cursor_escolha + 1) % total
    if tecla == pygame.K_LEFT:
        cursor_escolha = (cursor_escolha - 1) % total
    if tecla == pygame.K_DOWN and cursor_escolha + colunas < total:
        cursor_escolha = cursor_escolha + colunas
    if tecla == pygame.K_UP and cursor_escolha - colunas >= 0:
        cursor_escolha = cursor_escolha - colunas
    if tecla == pygame.K_BACKSPACE or tecla == pygame.K_ESCAPE:
        if len(escolhidos) > 0:
            escolhidos.pop()
    if tecla == pygame.K_RETURN or tecla == pygame.K_SPACE:
        nome = nomes_dos_bichos[cursor_escolha]
        if nome in escolhidos:
            escolhidos.remove(nome)
        else:
            escolhidos.append(nome)
        if len(escolhidos) == TAMANHO_EQUIPA:
            minha_equipa = []
            for escolhido in escolhidos:
                minha_equipa.append(criar_bicho(escolhido, NIVEL_INICIAL))
            comecar_mundo()


# =====================================================================
#                          O CICLO DO JOGO
# =====================================================================

a_correr = True
while a_correr:

    # ------------------------- 1. EVENTOS -------------------------
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            a_correr = False
        if evento.type == pygame.KEYDOWN:
            confirmar = evento.key == pygame.K_RETURN or evento.key == pygame.K_SPACE
            if estado == "menu" and confirmar:
                comecar_escolha()
            elif estado == "escolha":
                tecla_na_escolha(evento.key)
            elif estado == "mundo":
                tecla_no_mundo(evento.key)
                ao_carregar_tecla(evento.key)
            elif estado == "batalha":
                tecla_na_batalha(evento.key)
                ao_carregar_tecla(evento.key)
            elif estado == "derrota" and confirmar:
                acordar_em_casa()
            elif estado == "vitoria" and evento.key == pygame.K_r:
                comecar_escolha()

    # ------------------------- 2. LOGICA --------------------------
    if estado == "mundo":
        andar_com_as_setas()
    # (Outra vez o if: o passo pode ter comecado uma batalha.)
    if estado == "mundo":
        a_cada_frame()

    # As barras de vida descem devagar ate a vida verdadeira.
    for bicho in minha_equipa + equipa_inimiga:
        passo = bicho["vida_max"] / 50
        if bicho["vida_mostrada"] > bicho["vida"]:
            bicho["vida_mostrada"] = max(bicho["vida"], bicho["vida_mostrada"] - passo)
        if bicho["vida_mostrada"] < bicho["vida"]:
            bicho["vida_mostrada"] = min(bicho["vida"], bicho["vida_mostrada"] + passo)
        if bicho["tremor"] > 0:
            bicho["tremor"] = bicho["tremor"] - 1

    # ------------------------ 3. DESENHAR -------------------------
    if estado == "menu":
        ecra.fill(PRETO)
        mostrar_texto("BICHARADA À SOLTA", 120, 170, AMARELO, fonte_grande)
        mostrar_texto("Os bichos mais portugueses do mundo andam por aí", 135, 260, BRANCO, fonte)
        # Os dois primeiros bichos de BICHOS, sejam eles quais forem.
        modelo = criar_bicho(nomes_dos_bichos[0], NIVEL_INICIAL)
        desenhar_bicho(modelo, 300, 380, 90, 1)
        modelo = criar_bicho(nomes_dos_bichos[1], NIVEL_INICIAL)
        desenhar_bicho(modelo, 500, 380, 90, -1)
        mostrar_texto("Enter para começar", 290, 490, CINZA, fonte)
    elif estado == "escolha":
        desenhar_escolha()
    elif estado == "mundo":
        desenhar_mundo()
    elif estado == "batalha":
        desenhar_batalha()
    elif estado == "vitoria":
        ecra.fill(PRETO)
        mostrar_texto("CAMPEÃ(O) DA FEIRA!", 90, 200, AMARELO, fonte_grande)
        mostrar_texto("Ganhaste a todos os treinadores.", 220, 300, BRANCO, fonte)
        mostrar_texto("R para jogar outra vez", 270, 380, CINZA, fonte)
    elif estado == "derrota":
        ecra.fill(PRETO)
        mostrar_texto("A tua equipa desmaiou...", 120, 200, VERMELHO, fonte_grande)
        if batalha_selvagem:
            mostrar_texto("Perdeste contra um bicho à solta.", 220, 300, BRANCO, fonte)
        else:
            mostrar_texto("Perdeste contra " + treinador()["nome"] + ".", 230, 300, BRANCO, fonte)
        mostrar_texto("Enter para acordar em casa da avó", 215, 380, CINZA, fonte)

    # ------------------------- 4. MOSTRAR -------------------------
    pygame.display.flip()

    # ------------------------- 5. ESPERAR -------------------------
    clock.tick(FPS)

pygame.quit()
