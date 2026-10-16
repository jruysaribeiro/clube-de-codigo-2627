# S12 — BICHARADA
# Batalhas por turnos, a moda do Pokemon, com bichos muito portugueses.
#
# ESTE FICHEIRO E UMA BASE, NAO UM JOGO ACABADO.
# Os tipos, os ataques, os bichos e os treinadores sao todos DADOS, aqui
# em cima. Para inventares um bicho novo escreves mais um dicionario em
# BICHOS e nao mexes em mais nada. O resto do ficheiro sabe ler qualquer
# bicho que la puseres.
#
#   Setas            mexer nos menus
#   Enter / Espaco   escolher, e passar o texto a frente
#   Esc / Backspace  voltar atras (e, no ecra de escolha, tirar o ultimo)
#
# Zero assets: os bichos sao formas com olhos. Se puseres um PNG com o nome
# que esta em "imagem" na pasta comum/assets/imagens/, aparece a imagem.

import math
import random
from pathlib import Path

import pygame

# --- Constantes: e aqui que se mexe primeiro ---
LARGURA = 800
ALTURA = 600
FPS = 60

TAMANHO_EQUIPA = 3       # quantos bichos levas para a feira
NIVEL_INICIAL = 5        # o nivel com que os teus bichos comecam
SOPAS_POR_BATALHA = 3    # a sopa da avo cura metade da vida

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
# Para inventares um bicho: copia um destes, muda-lhe o nome e os numeros.
# Regra de equilibrio: vida + ataque + defesa + velocidade da a volta de 85.
BICHOS = {
    "Galo de Barcelos": {
        "tipo": "fogo", "vida": 45, "ataque": 15, "defesa": 10, "velocidade": 14,
        "ataques": ["Bicada", "Crista em Brasa", "Cocoricó", "Estalido"],
        "cor": (200, 45, 45), "forma": "triangulo", "imagem": "galo.png",
    },
    "Castanha Assada": {
        "tipo": "fogo", "vida": 55, "ataque": 12, "defesa": 13, "velocidade": 7,
        "ataques": ["Investida", "Fumarada", "Estalido", "Casca Dura"],
        "cor": (130, 70, 35), "forma": "gota", "imagem": "castanha.png",
    },
    "Sardinhão": {
        "tipo": "agua", "vida": 48, "ataque": 13, "defesa": 10, "velocidade": 15,
        "ataques": ["Investida", "Esguicho", "Onda da Nazaré", "Escamas"],
        "cor": (120, 160, 200), "forma": "gota", "imagem": "sardinhao.png",
    },
    "Polvo Lagareiro": {
        "tipo": "agua", "vida": 60, "ataque": 11, "defesa": 13, "velocidade": 6,
        "ataques": ["Tentáculo", "Tinta de Choco", "Esguicho", "Patada"],
        "cor": (170, 80, 150), "forma": "circulo", "imagem": "polvo.png",
    },
    "Sobreirinho": {
        "tipo": "planta", "vida": 58, "ataque": 11, "defesa": 15, "velocidade": 5,
        "ataques": ["Chicote de Cortiça", "Bolotada", "Seiva", "Casca Dura"],
        "cor": (120, 100, 50), "forma": "quadrado", "imagem": "sobreirinho.png",
    },
    "Couve Galega": {
        "tipo": "planta", "vida": 50, "ataque": 13, "defesa": 11, "velocidade": 11,
        "ataques": ["Folha de Couve", "Seiva", "Investida", "Bolotada"],
        "cor": (60, 150, 70), "forma": "circulo", "imagem": "couve.png",
    },
    "Lince Ibérico": {
        "tipo": "normal", "vida": 46, "ataque": 15, "defesa": 9, "velocidade": 16,
        "ataques": ["Arranhão", "Salto Felino", "Rugido", "Patada"],
        "cor": (205, 155, 85), "forma": "quadrado", "imagem": "lince.png",
    },
}

# --- Os treinadores, por ordem ---
# Ganhas a um, a tua equipa e curada e passas ao seguinte.
# Ganhas ao ultimo, ganhas a feira.
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


# =====================================================================
#                          PYGAME E UTILITARIOS
# =====================================================================

pygame.init()
ecra = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Bicharada")
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


def mostrar_texto(texto, x, y, cor, letra):
    desenho = letra.render(texto, True, cor)
    ecra.blit(desenho, (x, y))


def escurecer(cor, quanto):
    return (int(cor[0] * quanto), int(cor[1] * quanto), int(cor[2] * quanto))


# =====================================================================
#                          AS REGRAS DO JOGO
# =====================================================================

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


def eficacia(tipo_ataque, tipo_alvo):
    if tipo_ataque in EFICACIA:
        if tipo_alvo in EFICACIA[tipo_ataque]:
            return EFICACIA[tipo_ataque][tipo_alvo]
    return 1.0


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


def proximo_vivo(equipa):
    # Devolve a posicao do primeiro bicho com vida, ou -1 se nao houver.
    indice = 0
    while indice < len(equipa):
        if equipa[indice]["vida"] > 0:
            return indice
        indice = indice + 1
    return -1


def xp_para_subir(bicho):
    return bicho["nivel"] * 10


# =====================================================================
#                          O ESTADO DO JOGO
# =====================================================================

estado = "menu"          # menu, escolha, batalha, intervalo, vitoria, derrota
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
sopas = SOPAS_POR_BATALHA
troca_obrigatoria = False

# Os textos que aparecem no painel de baixo, um de cada vez.
mensagens = []
# As acoes que ainda faltam neste turno, pela ordem em que acontecem.
# Cada acao e um dicionario, por exemplo:
#   {"quem": "jogador", "tipo": "atacar", "ataque": "Bicada"}
fila_acoes = []

OPCOES_MENU = ["Lutar", "Equipa", "Sopa"]


def treinador():
    return TREINADORES[indice_treinador]


def comecar_escolha():
    global estado, escolhidos, cursor_escolha, indice_treinador
    estado = "escolha"
    escolhidos = []
    cursor_escolha = 0
    indice_treinador = 0


def comecar_batalha():
    global estado, fase, equipa_inimiga, ativo_meu, ativo_inimigo
    global sopas, mensagens, fila_acoes, troca_obrigatoria
    estado = "batalha"
    equipa_inimiga = []
    for membro in treinador()["equipa"]:
        equipa_inimiga.append(criar_bicho(membro["bicho"], membro["nivel"]))
    curar_tudo(minha_equipa)
    ativo_meu = 0
    ativo_inimigo = 0
    sopas = SOPAS_POR_BATALHA
    troca_obrigatoria = False
    fila_acoes = []
    mensagens = [
        treinador()["nome"] + " desafia-te!",
        "«" + treinador()["frase"] + "»",
        treinador()["nome"] + " manda " + equipa_inimiga[0]["nome"] + "!",
        "Vai, " + minha_equipa[0]["nome"] + "!",
    ]
    fase = "texto"


# =====================================================================
#                          O TURNO, PASSO A PASSO
#
# Um turno e uma fila de acoes. Executamos uma, mostramos as mensagens
# que ela deixou, e so depois de o jogador carregar em Enter passamos a
# seguinte. Quando a fila acaba, vemos quem desmaiou.
# =====================================================================

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


def jogador_escolheu(acao_jogador):
    global fila_acoes
    acao_inimigo = {"quem": "inimigo", "tipo": "atacar", "ataque": escolher_ataque_inimigo()}
    eu = minha_equipa[ativo_meu]
    inimigo = equipa_inimiga[ativo_inimigo]
    # Trocar de bicho e comer sopa vem sempre antes dos ataques.
    # Entre dois ataques, vai primeiro o mais rapido.
    if acao_jogador["tipo"] != "atacar":
        fila_acoes = [acao_jogador, acao_inimigo]
    elif eu["velocidade"] > inimigo["velocidade"]:
        fila_acoes = [acao_jogador, acao_inimigo]
    elif eu["velocidade"] < inimigo["velocidade"]:
        fila_acoes = [acao_inimigo, acao_jogador]
    elif random.randint(0, 1) == 0:
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
    if random.randint(1, 100) > dados["precisao"]:
        mensagens.append("Mas falhou!")
        return
    efeito = dados["efeito"]
    if efeito == "dano":
        dano = calcular_dano(atacante, alvo, nome)
        if random.randint(1, 16) == 1:
            dano = int(dano * 1.5)
            mensagens.append("Golpe crítico!")
        alvo["vida"] = max(0, alvo["vida"] - dano)
        alvo["tremor"] = 24
        multiplicador = eficacia(dados["tipo"], alvo["tipo"])
        if multiplicador > 1:
            mensagens.append("É super eficaz!")
        if multiplicador < 1:
            mensagens.append("Não é muito eficaz...")
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
    elif acao["tipo"] == "entrar_inimigo":
        ativo_inimigo = acao["indice"]
        mensagens.append(treinador()["nome"] + " manda " + equipa_inimiga[ativo_inimigo]["nome"] + "!")
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


def fim_do_turno():
    global fase, estado, troca_obrigatoria, cursor
    inimigo = equipa_inimiga[ativo_inimigo]
    eu = minha_equipa[ativo_meu]

    if inimigo["vida"] <= 0:
        if not inimigo["anunciado"]:
            inimigo["anunciado"] = True
            mensagens.append(inimigo["nome"] + " desmaiou!")
            ganhar_xp(eu, inimigo["nivel"] * 12)
            fase = "texto"
            return
        seguinte = proximo_vivo(equipa_inimiga)
        if seguinte == -1:
            if indice_treinador == len(TREINADORES) - 1:
                estado = "vitoria"
            else:
                estado = "intervalo"
            return
        fila_acoes.append({"quem": "inimigo", "tipo": "entrar_inimigo", "indice": seguinte})
        continuar()
        return

    if eu["vida"] <= 0:
        if not eu["anunciado"]:
            eu["anunciado"] = True
            mensagens.append(eu["nome"] + " desmaiou!")
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
    global fase, cursor, troca_obrigatoria, ativo_meu
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
                fase = "texto"
            else:
                jogador_escolheu({"quem": "jogador", "tipo": "trocar", "indice": cursor})


# =====================================================================
#                          DESENHAR
# =====================================================================

def desenhar_bicho(bicho, cx, cy, tamanho, olha_para):
    # olha_para: 1 se o bicho olha para a direita, -1 para a esquerda.
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

    # Os olhos: dois circulos brancos com a pupila virada para o outro bicho.
    olho_y = cy + tamanho // 10
    raio_olho = tamanho // 9
    for lado in [-1, 1]:
        olho_x = cx + lado * tamanho // 5
        pygame.draw.circle(ecra, BRANCO, (olho_x, olho_y), raio_olho)
        pygame.draw.circle(ecra, PRETO, (olho_x + olha_para * raio_olho // 2, olho_y), raio_olho // 2)


def desenhar_barra_vida(bicho, x, y, largura):
    fracao = bicho["vida_mostrada"] / bicho["vida_max"]
    cor = VERDE
    if fracao < 0.5:
        cor = AMARELO
    if fracao < 0.2:
        cor = VERMELHO
    pygame.draw.rect(ecra, PRETO, (x, y, largura, 12), border_radius=6)
    pygame.draw.rect(ecra, cor, (x, y, int(largura * fracao), 12), border_radius=6)


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
        y = 462
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
            y = y + 40
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
    indice = 0
    for nome in nomes_dos_bichos:
        x = 30 + (indice % colunas) * 188
        y = 85 + (indice // colunas) * 170
        cartao = pygame.Rect(x, y, 176, 158)
        cor_borda = CINZA
        if indice == cursor_escolha:
            cor_borda = AMARELO
        pygame.draw.rect(ecra, PAINEL, cartao, border_radius=12)
        pygame.draw.rect(ecra, cor_borda, cartao, 3, border_radius=12)
        modelo = {"nome": nome, "vida_mostrada": 1, "tremor": 0}
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
            comecar_batalha()


def desenhar_intervalo():
    ecra.fill(PRETO)
    mostrar_texto("Ganhaste a " + TREINADORES[indice_treinador]["nome"] + "!", 60, 50, AMARELO, fonte_grande)
    mostrar_texto("A tua equipa descansou e está curada.", 60, 130, BRANCO, fonte)
    y = 190
    for bicho in minha_equipa:
        desenhar_bicho(bicho, 110, y + 30, 60, 1)
        mostrar_texto(bicho["nome"] + "  Nv " + str(bicho["nivel"]), 160, y + 18, BRANCO, fonte)
        y = y + 80
    seguinte = TREINADORES[indice_treinador + 1]
    mostrar_texto("Segue-se: " + seguinte["nome"], 60, 460, AMARELO, fonte)
    mostrar_texto("Enter para continuar", 60, 520, CINZA, fonte)


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
            elif estado == "batalha":
                tecla_na_batalha(evento.key)
            elif estado == "intervalo" and confirmar:
                curar_tudo(minha_equipa)
                indice_treinador = indice_treinador + 1
                comecar_batalha()
            elif estado == "vitoria" or estado == "derrota":
                if evento.key == pygame.K_r:
                    comecar_escolha()

    # ------------------------- 2. LOGICA --------------------------
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
        mostrar_texto("BICHARADA", 230, 170, AMARELO, fonte_grande)
        mostrar_texto("A feira dos bichos mais portugueses do mundo", 160, 260, BRANCO, fonte)
        modelo = {"nome": "Galo de Barcelos", "vida_mostrada": 1, "tremor": 0}
        desenhar_bicho(modelo, 300, 380, 90, 1)
        modelo = {"nome": "Sardinhão", "vida_mostrada": 1, "tremor": 0}
        desenhar_bicho(modelo, 500, 380, 90, -1)
        mostrar_texto("Enter para começar", 290, 490, CINZA, fonte)
    elif estado == "escolha":
        desenhar_escolha()
    elif estado == "batalha":
        desenhar_batalha()
    elif estado == "intervalo":
        desenhar_intervalo()
    elif estado == "vitoria":
        ecra.fill(PRETO)
        mostrar_texto("CAMPEÃ(O) DA FEIRA!", 90, 200, AMARELO, fonte_grande)
        mostrar_texto("Ganhaste a todos os treinadores.", 220, 300, BRANCO, fonte)
        mostrar_texto("R para jogar outra vez", 270, 380, CINZA, fonte)
    elif estado == "derrota":
        ecra.fill(PRETO)
        mostrar_texto("A tua equipa desmaiou...", 120, 200, VERMELHO, fonte_grande)
        mostrar_texto("Perdeste contra " + treinador()["nome"] + ".", 230, 300, BRANCO, fonte)
        mostrar_texto("R para tentar outra vez", 265, 380, CINZA, fonte)

    # ------------------------- 4. MOSTRAR -------------------------
    pygame.display.flip()

    # ------------------------- 5. ESPERAR -------------------------
    clock.tick(FPS)

pygame.quit()
