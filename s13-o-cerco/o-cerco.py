# S13 — O CERCO
# Um tower defense. Guimaraes, 1128. Aqui nasceu Portugal, e convinha que
# nao morresse ja hoje.
#
# ESTE FICHEIRO E UMA BASE, NAO UM JOGO ACABADO.
# O mapa, as torres, os inimigos e as ondas sao todos DADOS, aqui em cima.
# Para inventares uma torre nova escreves mais um dicionario em TORRES.
# Para uma onda nova, mais uma linha em ONDAS. O resto do ficheiro sabe ler
# o que la puseres.
#
#   1 2 3 4          escolher a torre a construir
#   Clique esquerdo  construir na relva / escolher uma torre ja feita
#   Clique direito   cancelar
#   U                melhorar a torre escolhida
#   V                vender a torre escolhida
#   Espaco           mandar vir a proxima onda
#   F                velocidade a dobrar        P   pausa
#
# Zero assets: tudo e desenhado com formas.

import math
import random

import pygame

# --- Constantes: e aqui que se mexe primeiro ---
LARGURA = 800
ALTURA = 600
FPS = 60
TILE = 40
TOPO = 40                # altura da barra de cima (ouro, vidas, onda)

OURO_INICIAL = 200
VIDAS_INICIAIS = 20
BONUS_POR_ONDA = 25      # ouro que se ganha ao acabar cada onda
VENDA = 0.6              # ao vender, recebes 60% do que gastaste
NIVEL_MAXIMO = 3
VIDA_EXTRA_POR_ONDA = 0.15   # cada onda, os inimigos tem mais 15% de vida

PRETO = (18, 18, 28)
BRANCO = (240, 240, 240)
CINZA = (130, 130, 145)
AMARELO = (240, 200, 70)
VERDE = (80, 200, 100)
VERMELHO = (220, 70, 60)
PAINEL = (30, 30, 48)
RELVA = (86, 140, 70)
RELVA_ESCURA = (78, 130, 64)
CAMINHO = (190, 165, 120)
ARVORE = (40, 95, 50)


# =====================================================================
#                              OS DADOS
# =====================================================================

# --- O mapa ---
# Cada letra e um quadrado de 40 por 40. Mudar uma letra muda o mapa.
#   .  relva (pode-se construir)     #  caminho
#   E  entrada dos inimigos          C  o castelo (o fim do caminho)
#   T  arvore (nao se constroi)
# O caminho tem de ter UM quadrado de largura e nao pode tocar em si
# proprio, senao o jogo nao sabe por onde ir.
MAPA = [
    "....................",
    "E######.............",
    "......#.....T.......",
    "......#.............",
    "..T...#....#######..",
    "......#....#.....#..",
    "......######.....#..",
    "........T........#..",
    "...#########.....#..",
    "...#.......#.....#..",
    "...#...T...#######..",
    "...#................",
    "...##############C..",
]

# --- As torres ---
# custo:      quanto ouro custa
# alcance:    ate onde chega, em pixeis
# dano:       quanto tira a cada golpe
# cadencia:   frames entre dois golpes (60 = um por segundo)
# efeito:     "tiro"      dispara uma seta contra um inimigo
#             "explosao"  dispara uma pedra que rebenta e magoa a volta
#             "area"      magoa todos os que estao perto, e abranda-os
#             "golpe"     acerta logo, sem projetil (curto alcance)
TORRES = [
    {
        "nome": "Besteiro", "tecla": pygame.K_1, "custo": 50,
        "alcance": 120, "dano": 7, "cadencia": 35, "efeito": "tiro",
        "cor": (70, 110, 200),
    },
    {
        "nome": "Trabuco", "tecla": pygame.K_2, "custo": 100,
        "alcance": 170, "dano": 22, "cadencia": 100, "efeito": "explosao",
        "raio_explosao": 55, "cor": (140, 100, 70),
    },
    {
        "nome": "Caldeirão", "tecla": pygame.K_3, "custo": 75,
        "alcance": 75, "dano": 2, "cadencia": 45, "efeito": "area",
        "lentidao": 0.45, "cor": (220, 170, 40),
    },
    {
        "nome": "Padeira", "tecla": pygame.K_4, "custo": 130,
        "alcance": 65, "dano": 30, "cadencia": 60, "efeito": "golpe",
        "cor": (230, 220, 200),
    },
]

# --- Os inimigos ---
# velocidade: pixeis por frame
# recompensa: ouro que dao ao cair
# estrago:    vidas que tiram se chegarem ao castelo
INIMIGOS = {
    "Soldado": {"vida": 40, "velocidade": 1.2, "recompensa": 5, "estrago": 1,
                "tamanho": 16, "cor": (200, 60, 60), "forma": "circulo"},
    "Cavaleiro": {"vida": 35, "velocidade": 2.4, "recompensa": 7, "estrago": 1,
                  "tamanho": 18, "cor": (230, 140, 60), "forma": "circulo"},
    "Aríete": {"vida": 220, "velocidade": 0.6, "recompensa": 20, "estrago": 3,
               "tamanho": 26, "cor": (110, 75, 45), "forma": "quadrado"},
    "General": {"vida": 1500, "velocidade": 0.7, "recompensa": 100, "estrago": 10,
                "tamanho": 32, "cor": (120, 40, 140), "forma": "quadrado"},
}

# --- As ondas ---
# Cada onda e uma lista de grupos. Um grupo diz: "manda X inimigos deste
# tipo, com Y frames entre cada um". Os grupos saem uns a seguir aos outros.
ONDAS = [
    [{"inimigo": "Soldado", "quantos": 8, "intervalo": 50}],
    [{"inimigo": "Soldado", "quantos": 12, "intervalo": 40}],
    [{"inimigo": "Soldado", "quantos": 6, "intervalo": 40},
     {"inimigo": "Cavaleiro", "quantos": 6, "intervalo": 30}],
    [{"inimigo": "Cavaleiro", "quantos": 14, "intervalo": 25}],
    [{"inimigo": "Soldado", "quantos": 10, "intervalo": 30},
     {"inimigo": "Aríete", "quantos": 2, "intervalo": 120}],
    [{"inimigo": "Aríete", "quantos": 5, "intervalo": 90},
     {"inimigo": "Cavaleiro", "quantos": 10, "intervalo": 20}],
    [{"inimigo": "Soldado", "quantos": 25, "intervalo": 15}],
    [{"inimigo": "Cavaleiro", "quantos": 12, "intervalo": 18},
     {"inimigo": "Aríete", "quantos": 6, "intervalo": 60}],
    [{"inimigo": "Soldado", "quantos": 15, "intervalo": 20},
     {"inimigo": "Cavaleiro", "quantos": 15, "intervalo": 15},
     {"inimigo": "Aríete", "quantos": 6, "intervalo": 50}],
    [{"inimigo": "Soldado", "quantos": 20, "intervalo": 15},
     {"inimigo": "General", "quantos": 1, "intervalo": 60}],
]


# =====================================================================
#                          PYGAME E UTILITARIOS
# =====================================================================

pygame.init()
ecra = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("O Cerco")
clock = pygame.time.Clock()
fonte_pequena = pygame.font.SysFont(None, 22)
fonte = pygame.font.SysFont(None, 30)
fonte_grande = pygame.font.SysFont(None, 80)

# Uma folha transparente, do tamanho do ecra, para desenhar os alcances
# meio a ver-se. O pygame.draw normal nao sabe fazer transparencias.
camada_transparente = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)


def mostrar_texto(texto, x, y, cor, letra):
    desenho = letra.render(texto, True, cor)
    ecra.blit(desenho, (x, y))


def escurecer(cor, quanto):
    return (int(cor[0] * quanto), int(cor[1] * quanto), int(cor[2] * quanto))


def distancia(x1, y1, x2, y2):
    # O teorema de Pitagoras. O colliderect so serve para retangulos; o
    # alcance de uma torre e um circulo, por isso medimos a distancia.
    return math.hypot(x2 - x1, y2 - y1)


def centro_do_quadrado(coluna, linha):
    return (coluna * TILE + TILE // 2, TOPO + linha * TILE + TILE // 2)


def quadrado_do_rato(x, y):
    # Converte pixeis do rato em coluna e linha do mapa.
    coluna = x // TILE
    linha = (y - TOPO) // TILE
    return (coluna, linha)


def letra_do_mapa(coluna, linha):
    if linha < 0 or linha >= len(MAPA):
        return " "
    if coluna < 0 or coluna >= len(MAPA[linha]):
        return " "
    return MAPA[linha][coluna]


def e_caminho(coluna, linha):
    letra = letra_do_mapa(coluna, linha)
    return letra == "#" or letra == "E" or letra == "C"


def encontrar_caminho():
    # Comeca no E e vai andando para o quadrado de caminho ao lado que
    # ainda nao visitou, ate chegar ao C. Devolve a lista dos centros por
    # onde os inimigos vao passar.
    atual = None
    linha = 0
    while linha < len(MAPA):
        coluna = 0
        while coluna < len(MAPA[linha]):
            if MAPA[linha][coluna] == "E":
                atual = (coluna, linha)
            coluna = coluna + 1
        linha = linha + 1

    visitados = [atual]
    pontos = [centro_do_quadrado(atual[0], atual[1])]
    while letra_do_mapa(atual[0], atual[1]) != "C":
        andou = False
        for passo in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            vizinho = (atual[0] + passo[0], atual[1] + passo[1])
            if not andou and e_caminho(vizinho[0], vizinho[1]) and vizinho not in visitados:
                atual = vizinho
                visitados.append(atual)
                pontos.append(centro_do_quadrado(atual[0], atual[1]))
                andou = True
        if not andou:
            print("O caminho do MAPA nao chega ao C! Ve se ha um buraco.")
            break
    return pontos


CAMINHO_PONTOS = encontrar_caminho()


# =====================================================================
#                          O ESTADO DO JOGO
# =====================================================================

estado = "menu"          # menu, jogo, vitoria, derrota
ouro = OURO_INICIAL
vidas = VIDAS_INICIAIS
numero_onda = 0          # quantas ondas ja comecaram
onda_a_decorrer = False
a_por_sair = []          # os inimigos desta onda que ainda nao sairam
espera_saida = 0

torres = []
inimigos = []
projeteis = []
efeitos = []             # circulos e numeros que aparecem e desaparecem

torre_para_construir = 0   # posicao em TORRES
torre_escolhida = None     # uma torre ja construida, para melhorar/vender
velocidade_jogo = 1
pausa = False


def comecar_jogo():
    global estado, ouro, vidas, numero_onda, onda_a_decorrer, a_por_sair
    global torres, inimigos, projeteis, efeitos, torre_escolhida, velocidade_jogo, pausa
    estado = "jogo"
    ouro = OURO_INICIAL
    vidas = VIDAS_INICIAIS
    numero_onda = 0
    onda_a_decorrer = False
    a_por_sair = []
    torres = []
    inimigos = []
    projeteis = []
    efeitos = []
    torre_escolhida = None
    velocidade_jogo = 1
    pausa = False


def comecar_onda():
    global onda_a_decorrer, numero_onda, a_por_sair, espera_saida
    if onda_a_decorrer or numero_onda >= len(ONDAS):
        return
    # Desdobramos os grupos numa fila simples: um nome por inimigo.
    a_por_sair = []
    for grupo in ONDAS[numero_onda]:
        vezes = 0
        while vezes < grupo["quantos"]:
            a_por_sair.append({"inimigo": grupo["inimigo"], "intervalo": grupo["intervalo"]})
            vezes = vezes + 1
    numero_onda = numero_onda + 1
    onda_a_decorrer = True
    espera_saida = 0


def criar_inimigo(nome):
    dados = INIMIGOS[nome]
    vida = int(dados["vida"] * (1 + VIDA_EXTRA_POR_ONDA * (numero_onda - 1)))
    inicio = CAMINHO_PONTOS[0]
    return {
        "nome": nome,
        "x": inicio[0] - TILE,   # nasce um bocadinho fora do ecra
        "y": inicio[1],
        "vida": vida,
        "vida_max": vida,
        "ponto": 0,              # o proximo ponto do caminho para onde vai
        "andado": 0,             # quanto ja andou: quem andou mais vai a frente
        "lento": 0,              # frames que ainda faltam de lentidao
        "fator_lento": 1.0,
        "chegou": False,
    }


def construir(coluna, linha):
    global ouro, torre_escolhida
    if letra_do_mapa(coluna, linha) != ".":
        return
    for torre in torres:
        if torre["coluna"] == coluna and torre["linha"] == linha:
            torre_escolhida = torre
            return
    modelo = TORRES[torre_para_construir]
    if ouro < modelo["custo"]:
        efeitos.append(texto_a_voar("Falta ouro!", LARGURA // 2 - 50, ALTURA // 2, VERMELHO))
        return
    ouro = ouro - modelo["custo"]
    centro = centro_do_quadrado(coluna, linha)
    torres.append({
        "tipo": torre_para_construir,
        "coluna": coluna,
        "linha": linha,
        "x": centro[0],
        "y": centro[1],
        "nivel": 1,
        "gasto": modelo["custo"],
        "recarga": 0,
        "mira": (centro[0] + 1, centro[1]),
    })
    torre_escolhida = None


def valor_da_torre(torre, chave):
    # Cada nivel a mais: +50% de dano e +10% de alcance.
    base = TORRES[torre["tipo"]][chave]
    if chave == "dano":
        return base * (1 + 0.5 * (torre["nivel"] - 1))
    if chave == "alcance":
        return base * (1 + 0.1 * (torre["nivel"] - 1))
    return base


def custo_melhoria(torre):
    return TORRES[torre["tipo"]]["custo"] * torre["nivel"]


def melhorar():
    global ouro
    if torre_escolhida is None or torre_escolhida["nivel"] >= NIVEL_MAXIMO:
        return
    custo = custo_melhoria(torre_escolhida)
    if ouro < custo:
        efeitos.append(texto_a_voar("Falta ouro!", torre_escolhida["x"] - 40, torre_escolhida["y"] - 30, VERMELHO))
        return
    ouro = ouro - custo
    torre_escolhida["gasto"] = torre_escolhida["gasto"] + custo
    torre_escolhida["nivel"] = torre_escolhida["nivel"] + 1
    efeitos.append(circulo_a_crescer(torre_escolhida["x"], torre_escolhida["y"], AMARELO, 30))


def vender():
    global ouro, torre_escolhida
    if torre_escolhida is None:
        return
    ganho = int(torre_escolhida["gasto"] * VENDA)
    ouro = ouro + ganho
    efeitos.append(texto_a_voar("+" + str(ganho), torre_escolhida["x"] - 15, torre_escolhida["y"], AMARELO))
    torres.remove(torre_escolhida)
    torre_escolhida = None


# --- Efeitos: sao so dicionarios com um tempo de vida ---

def circulo_a_crescer(x, y, cor, raio):
    return {"tipo": "circulo", "x": x, "y": y, "cor": cor, "raio": raio, "tempo": 15, "tempo_max": 15}


def texto_a_voar(texto, x, y, cor):
    return {"tipo": "texto", "x": x, "y": y, "cor": cor, "texto": texto, "tempo": 45, "tempo_max": 45}


# =====================================================================
#                          A LOGICA, UM PASSO
# =====================================================================

def escolher_alvo(torre):
    # A torre ataca o inimigo dentro do alcance que vai mais a frente.
    alcance = valor_da_torre(torre, "alcance")
    melhor = None
    for inimigo in inimigos:
        if distancia(torre["x"], torre["y"], inimigo["x"], inimigo["y"]) <= alcance:
            if melhor is None or inimigo["andado"] > melhor["andado"]:
                melhor = inimigo
    return melhor


def magoar(inimigo, dano):
    inimigo["vida"] = inimigo["vida"] - dano


def atualizar_torres():
    for torre in torres:
        if torre["recarga"] > 0:
            torre["recarga"] = torre["recarga"] - 1
            continue
        alvo = escolher_alvo(torre)
        if alvo is None:
            continue
        modelo = TORRES[torre["tipo"]]
        dano = valor_da_torre(torre, "dano")
        torre["recarga"] = modelo["cadencia"]
        torre["mira"] = (alvo["x"], alvo["y"])

        if modelo["efeito"] == "tiro" or modelo["efeito"] == "explosao":
            raio = 0
            velocidade = 9
            if modelo["efeito"] == "explosao":
                raio = modelo["raio_explosao"]
                velocidade = 5
            projeteis.append({
                "x": torre["x"], "y": torre["y"], "alvo": alvo,
                "destino_x": alvo["x"], "destino_y": alvo["y"],
                "dano": dano, "raio": raio, "velocidade": velocidade,
                "cor": modelo["cor"],
            })
        elif modelo["efeito"] == "area":
            alcance = valor_da_torre(torre, "alcance")
            for inimigo in inimigos:
                if distancia(torre["x"], torre["y"], inimigo["x"], inimigo["y"]) <= alcance:
                    magoar(inimigo, dano)
                    inimigo["lento"] = 90
                    inimigo["fator_lento"] = modelo["lentidao"]
            efeitos.append(circulo_a_crescer(torre["x"], torre["y"], modelo["cor"], alcance))
        elif modelo["efeito"] == "golpe":
            magoar(alvo, dano)
            efeitos.append(circulo_a_crescer(alvo["x"], alvo["y"], BRANCO, 18))


def atualizar_projeteis():
    global projeteis
    sobreviventes = []
    for projetil in projeteis:
        # Enquanto o alvo esta vivo, a seta persegue-o. Se ele morrer pelo
        # caminho, a seta continua para o ultimo sitio onde ele estava.
        if projetil["alvo"] in inimigos:
            projetil["destino_x"] = projetil["alvo"]["x"]
            projetil["destino_y"] = projetil["alvo"]["y"]
        dx = projetil["destino_x"] - projetil["x"]
        dy = projetil["destino_y"] - projetil["y"]
        falta = math.hypot(dx, dy)
        if falta > projetil["velocidade"]:
            projetil["x"] = projetil["x"] + dx / falta * projetil["velocidade"]
            projetil["y"] = projetil["y"] + dy / falta * projetil["velocidade"]
            sobreviventes.append(projetil)
            continue
        # Chegou.
        if projetil["raio"] > 0:
            for inimigo in inimigos:
                if distancia(projetil["destino_x"], projetil["destino_y"], inimigo["x"], inimigo["y"]) <= projetil["raio"]:
                    magoar(inimigo, projetil["dano"])
            efeitos.append(circulo_a_crescer(projetil["destino_x"], projetil["destino_y"], (250, 150, 60), projetil["raio"]))
        elif projetil["alvo"] in inimigos:
            magoar(projetil["alvo"], projetil["dano"])
    projeteis = sobreviventes


def atualizar_inimigos():
    global inimigos, vidas, ouro
    for inimigo in inimigos:
        dados = INIMIGOS[inimigo["nome"]]
        velocidade = dados["velocidade"]
        if inimigo["lento"] > 0:
            inimigo["lento"] = inimigo["lento"] - 1
            velocidade = velocidade * inimigo["fator_lento"]
        destino = CAMINHO_PONTOS[inimigo["ponto"]]
        dx = destino[0] - inimigo["x"]
        dy = destino[1] - inimigo["y"]
        falta = math.hypot(dx, dy)
        if falta <= velocidade:
            inimigo["x"] = destino[0]
            inimigo["y"] = destino[1]
            inimigo["ponto"] = inimigo["ponto"] + 1
            if inimigo["ponto"] >= len(CAMINHO_PONTOS):
                inimigo["chegou"] = True
        else:
            inimigo["x"] = inimigo["x"] + dx / falta * velocidade
            inimigo["y"] = inimigo["y"] + dy / falta * velocidade
        inimigo["andado"] = inimigo["andado"] + velocidade

    # A receita dos sobreviventes: quem morreu ou chegou ao castelo nao
    # passa para a lista nova.
    sobreviventes = []
    for inimigo in inimigos:
        dados = INIMIGOS[inimigo["nome"]]
        if inimigo["vida"] <= 0:
            ouro = ouro + dados["recompensa"]
            efeitos.append(texto_a_voar("+" + str(dados["recompensa"]), inimigo["x"] - 10, inimigo["y"] - 20, AMARELO))
            efeitos.append(circulo_a_crescer(inimigo["x"], inimigo["y"], dados["cor"], dados["tamanho"]))
        elif inimigo["chegou"]:
            vidas = vidas - dados["estrago"]
            efeitos.append(texto_a_voar("-" + str(dados["estrago"]), inimigo["x"] - 10, inimigo["y"] - 30, VERMELHO))
        else:
            sobreviventes.append(inimigo)
    inimigos = sobreviventes


def atualizar_ondas():
    global espera_saida, onda_a_decorrer, ouro, estado
    if not onda_a_decorrer:
        return
    if len(a_por_sair) > 0:
        espera_saida = espera_saida - 1
        if espera_saida <= 0:
            proximo = a_por_sair.pop(0)
            inimigos.append(criar_inimigo(proximo["inimigo"]))
            espera_saida = proximo["intervalo"]
    elif len(inimigos) == 0:
        onda_a_decorrer = False
        if numero_onda >= len(ONDAS):
            estado = "vitoria"
        else:
            ouro = ouro + BONUS_POR_ONDA
            efeitos.append(texto_a_voar("Onda vencida! +" + str(BONUS_POR_ONDA), LARGURA // 2 - 90, ALTURA // 2, AMARELO))


def atualizar_efeitos():
    global efeitos
    sobreviventes = []
    for efeito in efeitos:
        efeito["tempo"] = efeito["tempo"] - 1
        if efeito["tipo"] == "texto":
            efeito["y"] = efeito["y"] - 0.7
        if efeito["tempo"] > 0:
            sobreviventes.append(efeito)
    efeitos = sobreviventes


def um_passo():
    global estado
    atualizar_ondas()
    atualizar_inimigos()
    atualizar_torres()
    atualizar_projeteis()
    atualizar_efeitos()
    if vidas <= 0:
        estado = "derrota"


# =====================================================================
#                          DESENHAR
# =====================================================================

def desenhar_mapa():
    linha = 0
    while linha < len(MAPA):
        coluna = 0
        while coluna < len(MAPA[linha]):
            letra = MAPA[linha][coluna]
            quadrado = pygame.Rect(coluna * TILE, TOPO + linha * TILE, TILE, TILE)
            cor = RELVA
            if (coluna + linha) % 2 == 0:
                cor = RELVA_ESCURA
            pygame.draw.rect(ecra, cor, quadrado)
            if letra == "#" or letra == "E" or letra == "C":
                pygame.draw.rect(ecra, CAMINHO, quadrado)
            if letra == "T":
                pygame.draw.circle(ecra, ARVORE, quadrado.center, 16)
                pygame.draw.circle(ecra, escurecer(ARVORE, 0.7), quadrado.center, 16, 3)
            coluna = coluna + 1
        linha = linha + 1

    # O castelo, por cima do C.
    fim = CAMINHO_PONTOS[len(CAMINHO_PONTOS) - 1]
    muralha = pygame.Rect(0, 0, 56, 44)
    muralha.midbottom = (fim[0], fim[1] + 20)
    pygame.draw.rect(ecra, (150, 145, 140), muralha)
    for dente in [0, 2, 4, 6]:
        pygame.draw.rect(ecra, (150, 145, 140), (muralha.x + dente * 8, muralha.y - 8, 8, 8))
    pygame.draw.rect(ecra, (60, 40, 30), (muralha.centerx - 7, muralha.bottom - 18, 14, 18))
    pygame.draw.line(ecra, (90, 80, 70), (muralha.centerx, muralha.y - 8), (muralha.centerx, muralha.y - 30), 2)
    pygame.draw.polygon(ecra, (40, 90, 200), [(muralha.centerx, muralha.y - 30), (muralha.centerx + 16, muralha.y - 24), (muralha.centerx, muralha.y - 18)])


def desenhar_torre(torre):
    modelo = TORRES[torre["tipo"]]
    base = pygame.Rect(0, 0, TILE - 6, TILE - 6)
    base.center = (torre["x"], torre["y"])
    pygame.draw.rect(ecra, escurecer(modelo["cor"], 0.5), base, border_radius=6)
    pygame.draw.circle(ecra, modelo["cor"], base.center, 13)
    # O "cano" aponta para o ultimo alvo.
    dx = torre["mira"][0] - torre["x"]
    dy = torre["mira"][1] - torre["y"]
    tamanho = math.hypot(dx, dy)
    if tamanho > 0:
        ponta = (torre["x"] + dx / tamanho * 18, torre["y"] + dy / tamanho * 18)
        pygame.draw.line(ecra, escurecer(modelo["cor"], 0.4), base.center, ponta, 5)
    # Um pontinho amarelo por cada nivel.
    pontinho = 0
    while pontinho < torre["nivel"]:
        pygame.draw.circle(ecra, AMARELO, (base.x + 6 + pontinho * 8, base.bottom - 5), 3)
        pontinho = pontinho + 1


def desenhar_inimigo(inimigo):
    dados = INIMIGOS[inimigo["nome"]]
    tamanho = dados["tamanho"]
    x = int(inimigo["x"])
    y = int(inimigo["y"])
    cor = dados["cor"]
    if inimigo["lento"] > 0:
        cor = (cor[0] // 2 + 100, cor[1] // 2 + 90, cor[2] // 2 + 20)
    if dados["forma"] == "quadrado":
        corpo = pygame.Rect(0, 0, tamanho, tamanho)
        corpo.center = (x, y)
        pygame.draw.rect(ecra, cor, corpo, border_radius=4)
        pygame.draw.rect(ecra, escurecer(cor, 0.5), corpo, 2, border_radius=4)
    else:
        pygame.draw.circle(ecra, cor, (x, y), tamanho // 2)
        pygame.draw.circle(ecra, escurecer(cor, 0.5), (x, y), tamanho // 2, 2)
    # A barra de vida so aparece depois de levar o primeiro golpe.
    if inimigo["vida"] < inimigo["vida_max"]:
        largura = tamanho + 6
        fracao = max(0, inimigo["vida"]) / inimigo["vida_max"]
        pygame.draw.rect(ecra, PRETO, (x - largura // 2, y - tamanho // 2 - 9, largura, 5))
        pygame.draw.rect(ecra, VERDE, (x - largura // 2, y - tamanho // 2 - 9, int(largura * fracao), 5))


def desenhar_alcance(x, y, raio, cor):
    camada_transparente.fill((0, 0, 0, 0))
    pygame.draw.circle(camada_transparente, (cor[0], cor[1], cor[2], 50), (int(x), int(y)), int(raio))
    pygame.draw.circle(camada_transparente, (cor[0], cor[1], cor[2], 160), (int(x), int(y)), int(raio), 2)
    ecra.blit(camada_transparente, (0, 0))


def desenhar_efeitos():
    for efeito in efeitos:
        if efeito["tipo"] == "circulo":
            fracao = 1 - efeito["tempo"] / efeito["tempo_max"]
            raio = max(2, int(efeito["raio"] * fracao))
            pygame.draw.circle(ecra, efeito["cor"], (int(efeito["x"]), int(efeito["y"])), raio, 3)
        elif efeito["tipo"] == "texto":
            mostrar_texto(efeito["texto"], int(efeito["x"]), int(efeito["y"]), efeito["cor"], fonte)


def desenhar_barra_cima():
    pygame.draw.rect(ecra, PAINEL, (0, 0, LARGURA, TOPO))
    mostrar_texto("Ouro " + str(ouro), 14, 10, AMARELO, fonte)
    mostrar_texto("Vidas " + str(vidas), 150, 10, VERMELHO, fonte)
    mostrar_texto("Onda " + str(numero_onda) + "/" + str(len(ONDAS)), 280, 10, BRANCO, fonte)
    if pausa:
        mostrar_texto("PAUSA", 420, 10, AMARELO, fonte)
    elif not onda_a_decorrer:
        mostrar_texto("Espaço: próxima onda", 420, 10, VERDE, fonte)
    if velocidade_jogo > 1:
        mostrar_texto("x2", 750, 10, AMARELO, fonte)


def desenhar_barra_baixo():
    y = TOPO + len(MAPA) * TILE
    pygame.draw.rect(ecra, PAINEL, (0, y, LARGURA, ALTURA - y))

    # Se ha uma torre escolhida, mostramos a ficha dela.
    if torre_escolhida is not None:
        modelo = TORRES[torre_escolhida["tipo"]]
        texto = modelo["nome"] + " nível " + str(torre_escolhida["nivel"])
        texto = texto + "   dano " + str(int(valor_da_torre(torre_escolhida, "dano")))
        mostrar_texto(texto, 14, y + 10, BRANCO, fonte)
        if torre_escolhida["nivel"] < NIVEL_MAXIMO:
            mostrar_texto("U melhorar (" + str(custo_melhoria(torre_escolhida)) + ")", 380, y + 10, VERDE, fonte)
        else:
            mostrar_texto("nível máximo", 380, y + 10, CINZA, fonte)
        mostrar_texto("V vender (+" + str(int(torre_escolhida["gasto"] * VENDA)) + ")", 590, y + 10, AMARELO, fonte)
        return

    x = 10
    indice = 0
    for modelo in TORRES:
        caixa = pygame.Rect(x, y + 4, 190, 32)
        if indice == torre_para_construir:
            pygame.draw.rect(ecra, (70, 70, 100), caixa, border_radius=6)
            pygame.draw.rect(ecra, AMARELO, caixa, 2, border_radius=6)
        pygame.draw.circle(ecra, modelo["cor"], (x + 16, y + 20), 9)
        cor = BRANCO
        if ouro < modelo["custo"]:
            cor = CINZA
        mostrar_texto(str(indice + 1) + " " + modelo["nome"] + " " + str(modelo["custo"]), x + 30, y + 12, cor, fonte_pequena)
        x = x + 196
        indice = indice + 1


def desenhar_jogo():
    ecra.fill(PRETO)
    desenhar_mapa()

    # A sombra da torre que se vai construir, debaixo do rato.
    rato = pygame.mouse.get_pos()
    quadrado = quadrado_do_rato(rato[0], rato[1])
    if torre_escolhida is None and letra_do_mapa(quadrado[0], quadrado[1]) != " " and rato[1] > TOPO:
        modelo = TORRES[torre_para_construir]
        centro = centro_do_quadrado(quadrado[0], quadrado[1])
        ocupado = False
        for torre in torres:
            if torre["coluna"] == quadrado[0] and torre["linha"] == quadrado[1]:
                ocupado = True
        if letra_do_mapa(quadrado[0], quadrado[1]) == "." and not ocupado:
            cor = VERDE
            if ouro < modelo["custo"]:
                cor = VERMELHO
            desenhar_alcance(centro[0], centro[1], modelo["alcance"], cor)

    if torre_escolhida is not None:
        desenhar_alcance(torre_escolhida["x"], torre_escolhida["y"], valor_da_torre(torre_escolhida, "alcance"), AMARELO)

    for torre in torres:
        desenhar_torre(torre)
    for inimigo in inimigos:
        desenhar_inimigo(inimigo)
    for projetil in projeteis:
        tamanho = 4
        if projetil["raio"] > 0:
            tamanho = 7
        pygame.draw.circle(ecra, PRETO, (int(projetil["x"]), int(projetil["y"])), tamanho + 1)
        pygame.draw.circle(ecra, projetil["cor"], (int(projetil["x"]), int(projetil["y"])), tamanho)
    desenhar_efeitos()

    desenhar_barra_cima()
    desenhar_barra_baixo()

    if numero_onda == 0 and not onda_a_decorrer:
        mostrar_texto("Constrói torres na relva. Quando estiveres pronto, Espaço.", 110, TOPO + 8, BRANCO, fonte_pequena)


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
            if estado == "menu" and (evento.key == pygame.K_SPACE or evento.key == pygame.K_RETURN):
                comecar_jogo()
            elif estado == "vitoria" or estado == "derrota":
                if evento.key == pygame.K_r:
                    comecar_jogo()
            elif estado == "jogo":
                indice = 0
                for modelo in TORRES:
                    if evento.key == modelo["tecla"]:
                        torre_para_construir = indice
                        torre_escolhida = None
                    indice = indice + 1
                if evento.key == pygame.K_SPACE:
                    comecar_onda()
                if evento.key == pygame.K_u:
                    melhorar()
                if evento.key == pygame.K_v:
                    vender()
                if evento.key == pygame.K_f:
                    velocidade_jogo = 3 - velocidade_jogo   # alterna entre 1 e 2
                if evento.key == pygame.K_p:
                    pausa = not pausa
                if evento.key == pygame.K_ESCAPE:
                    torre_escolhida = None

        if evento.type == pygame.MOUSEBUTTONDOWN and estado == "jogo":
            if evento.button == 3:
                torre_escolhida = None
            if evento.button == 1:
                x = evento.pos[0]
                y = evento.pos[1]
                fundo_do_mapa = TOPO + len(MAPA) * TILE
                if y >= fundo_do_mapa and torre_escolhida is None:
                    # Clique nos botoes de baixo: escolhe a torre.
                    botao = x // 196
                    if botao < len(TORRES):
                        torre_para_construir = botao
                elif y >= fundo_do_mapa:
                    torre_escolhida = None
                elif y > TOPO:
                    quadrado = quadrado_do_rato(x, y)
                    construir(quadrado[0], quadrado[1])

    # ------------------------- 2. LOGICA --------------------------
    # Com velocidade x2 fazemos dois passos de logica por cada desenho.
    if estado == "jogo" and not pausa:
        passo = 0
        while passo < velocidade_jogo and estado == "jogo":
            um_passo()
            passo = passo + 1

    # ------------------------ 3. DESENHAR -------------------------
    if estado == "menu":
        ecra.fill(PRETO)
        mostrar_texto("O CERCO", 255, 170, AMARELO, fonte_grande)
        mostrar_texto("Guimarães, 1128. Aqui nasceu Portugal.", 190, 260, BRANCO, fonte)
        mostrar_texto("Convinha que não morresse já hoje.", 215, 295, BRANCO, fonte)
        mostrar_texto("Espaço para começar", 285, 420, CINZA, fonte)
    elif estado == "jogo":
        desenhar_jogo()
    elif estado == "vitoria":
        desenhar_jogo()
        mostrar_texto("O CASTELO RESISTIU!", 110, 230, AMARELO, fonte_grande)
        mostrar_texto("R para jogar outra vez", 280, 320, BRANCO, fonte)
    elif estado == "derrota":
        desenhar_jogo()
        mostrar_texto("O CASTELO CAIU...", 150, 230, VERMELHO, fonte_grande)
        mostrar_texto("Chegaste à onda " + str(numero_onda) + ". R para tentar outra vez", 200, 320, BRANCO, fonte)

    # ------------------------- 4. MOSTRAR -------------------------
    pygame.display.flip()

    # ------------------------- 5. ESPERAR -------------------------
    clock.tick(FPS)

pygame.quit()
