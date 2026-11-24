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
# Zero assets: tudo e desenhado com formas. Se puseres um PNG com o nome
# que esta em "imagem" na pasta comum/assets/imagens/, aparece a imagem; e
# um WAV com o nome que esta em "som" em comum/assets/sons/ passa a ouvir-se.

import math
import random
from pathlib import Path

import pygame

# --- Constantes: e aqui que se mexe primeiro ---
LARGURA = 800
ALTURA = 600
FPS = 60                 # o jogo da 60 passos por segundo (60 frames = 1 segundo)
TILE = 40                # cada letra do MAPA e um quadrado de 40x40 pixeis
TOPO = 40                # altura da barra de cima (ouro, vidas, onda)

PASTA_ASSETS = Path(__file__).parent.parent / "comum" / "assets"

# =====================================================================
#                 AFINAR O JOGO: MUDA UM NUMERO, JOGA, VE
# =====================================================================
# Regra de ouro: muda UM numero de cada vez, corre o jogo e repara no que
# mudou. Se mudares cinco ao mesmo tempo, nao sabes qual fez o que.
#
# Leitura:   MAIS -> o que acontece se o numero subir
#            MENOS -> o que acontece se o numero descer

OURO_INICIAL = 200
# O ouro com que comecas. Uma torre custa entre 50 e 130.
#   MAIS  -> mais torres logo no inicio, jogo mais facil
#   MENOS -> tens de escolher bem a primeira torre
#   Experimenta: 1000 (modo rico) ou 50 (so da para um Besteiro)

VIDAS_INICIAIS = 20
# Quantos inimigos podem chegar ao castelo antes de perderes.
#   MAIS  -> perdoa mais erros       MENOS -> cada fuga doi
#   Experimenta: 1 (um so inimigo e perdes tudo)

BONUS_POR_ONDA = 25
# Ouro que ganhas ao acabar cada onda, alem do ouro de cada inimigo.
#   MAIS  -> as torres crescem mais depressa ao longo do jogo

VENDA = 0.6
# Ao vender uma torre, recebes esta parte do que gastaste nela.
# 0.6 quer dizer 60%. 1.0 seria 100% (vender nao custava nada).
#   Experimenta: 1.0 e muda as torres de sitio a vontade

NIVEL_MAXIMO = 3
# Quantas vezes se pode melhorar uma torre (tecla U), contando com o nivel 1.

DANO_EXTRA_POR_NIVEL = 0.5
# Cada melhoria soma esta parte ao dano. 0.5 = +50% por nivel,
# por isso ao nivel 3 a torre faz o dobro do dano do nivel 1.
#   MAIS  -> melhorar compensa mais do que construir torres novas

ALCANCE_EXTRA_POR_NIVEL = 0.1
# Cada melhoria soma esta parte ao alcance. 0.1 = +10% por nivel.

VIDA_EXTRA_POR_ONDA = 0.15
# Os inimigos ficam mais rijos a cada onda. 0.15 = +15% de vida por onda,
# por isso um Soldado na onda 10 tem mais do dobro da vida da onda 1.
#   MAIS  -> as ultimas ondas ficam muito mais dificeis
#   0     -> um Soldado e sempre igual, da primeira a ultima onda

TEMPO_LENTIDAO = 90
# Quanto tempo um inimigo fica lento depois de levar com o Caldeirao,
# em frames (60 = 1 segundo, por isso 90 = um segundo e meio).

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
# nome:       o que aparece na barra de baixo
# tecla:      a tecla que a escolhe (pygame.K_1 e a tecla 1, K_5 seria a 5)
# custo:      quanto ouro custa.            MAIS -> mais cara
# alcance:    ate onde chega, em pixeis.    Um quadrado do mapa tem 40,
#             por isso 120 chega a 3 quadrados de distancia.
#             (Ao passar o rato por cima ves o circulo do alcance.)
# dano:       quanto tira a cada golpe.     Um Soldado tem 40 de vida:
#             com dano 7 precisa de 6 setas, com dano 40 cai a primeira.
# cadencia:   ATENCAO, e ao contrario do que parece: e quanto a torre
#             ESPERA entre dois golpes, em frames (60 = 1 segundo).
#             MENOS -> dispara mais depressa.   MAIS -> mais devagar.
#             35 = quase dois tiros por segundo. 120 = um a cada 2 segundos.
# efeito:     "tiro"      dispara uma seta contra um inimigo
#             "explosao"  dispara uma pedra que rebenta e magoa a volta
#                         (raio_explosao: o tamanho do rebentamento, em pixeis)
#             "area"      magoa todos os que estao perto, e abranda-os
#                         (lentidao: a que velocidade ficam. 0.45 = andam a
#                         45% da velocidade normal. MENOS -> mais lentos!
#                         0.1 quase os para, 1.0 nao abranda nada)
#             "golpe"     acerta logo, sem projetil (curto alcance)
# cor:        (vermelho, verde, azul), cada um de 0 a 255
# imagem:     o nome de um PNG. Se ele existir em comum/assets/imagens/,
#             a torre aparece com essa imagem; se nao, fica a forma.
# som:        o nome de um WAV. Se ele existir em comum/assets/sons/,
#             ouve-se cada vez que a torre dispara.
#
# Para inventar uma torre: copia um bloco { ... }, cola por baixo, muda o
# nome, a tecla e os numeros. So cabem 4 botoes na barra de baixo.
TORRES = [
    {
        "nome": "Besteiro", "tecla": pygame.K_1, "custo": 50,
        "alcance": 120, "dano": 7, "cadencia": 35, "efeito": "tiro",
        "cor": (70, 110, 200), "imagem": "besteiro.png",
        "som": "besteiro.wav",
    },
    {
        "nome": "Trabuco", "tecla": pygame.K_2, "custo": 100,
        "alcance": 170, "dano": 22, "cadencia": 100, "efeito": "explosao",
        "raio_explosao": 55, "cor": (140, 100, 70), "imagem": "trabuco.png",
        "som": "trabuco.wav",
    },
    {
        "nome": "Caldeirão", "tecla": pygame.K_3, "custo": 75,
        "alcance": 75, "dano": 2, "cadencia": 45, "efeito": "area",
        "lentidao": 0.45, "cor": (220, 170, 40), "imagem": "caldeirao.png",
        "som": "caldeirao.wav",
    },
    {
        "nome": "Padeira", "tecla": pygame.K_4, "custo": 130,
        "alcance": 65, "dano": 30, "cadencia": 60, "efeito": "golpe",
        "cor": (230, 220, 200), "imagem": "padeira.png",
        "som": "padeira.wav",
    },
]

# --- Os inimigos ---
# vida:       quanto dano aguentam (na onda 1; depois sobe, ver
#             VIDA_EXTRA_POR_ONDA la em cima)
# velocidade: pixeis por frame. 1.2 = mais ou menos um quadrado do mapa
#             a cada meio segundo. 3 ja e muito rapido; 0.3 e um caracol.
# recompensa: ouro que dao ao cair.   MAIS -> o jogo fica mais facil
# estrago:    vidas que tiram se chegarem ao castelo
# tamanho:    o tamanho do desenho, em pixeis (nao muda a dificuldade)
# forma:      "circulo" ou "quadrado"
# imagem:     o nome de um PNG. Se ele existir em comum/assets/imagens/,
#             o inimigo aparece com essa imagem; se nao, fica a forma.
# som:        o nome de um WAV. Se ele existir em comum/assets/sons/,
#             ouve-se quando o inimigo cai.
INIMIGOS = {
    "Soldado": {"vida": 40, "velocidade": 1.2, "recompensa": 5, "estrago": 1,
                "tamanho": 16, "cor": (200, 60, 60), "forma": "circulo",
                "imagem": "soldado.png", "som": "soldado.wav"},
    "Cavaleiro": {"vida": 35, "velocidade": 2.4, "recompensa": 7, "estrago": 1,
                  "tamanho": 18, "cor": (230, 140, 60), "forma": "circulo",
                  "imagem": "cavaleiro.png", "som": "cavaleiro.wav"},
    "Aríete": {"vida": 220, "velocidade": 0.6, "recompensa": 20, "estrago": 3,
               "tamanho": 26, "cor": (110, 75, 45), "forma": "quadrado",
               "imagem": "ariete.png", "som": "ariete.wav"},
    "General": {"vida": 1500, "velocidade": 0.7, "recompensa": 100, "estrago": 10,
                "tamanho": 32, "cor": (120, 40, 140), "forma": "quadrado",
                "imagem": "general.png", "som": "general.wav"},
}

# --- As ondas ---
# Cada [ ... ] e uma onda. Ha 10, ha 10 ondas: acrescenta uma e passa a
# haver 11. Cada onda comeca numa linha nova.
# Dentro de cada onda ha grupos { ... }. Um grupo diz:
#   inimigo:    que inimigo (escrito igual ao nome em INIMIGOS, com acentos)
#   quantos:    quantos vem
#   intervalo:  quanto tempo entre um e o seguinte, em frames (60 = 1 segundo)
#               MENOS -> vem todos encavalitados (mais dificil)
# Os grupos saem uns a seguir aos outros.
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

# Guardamos aqui as imagens ja carregadas, para nao ler o disco 60 vezes
# por segundo. None quer dizer "procurei e nao ha".
imagens_carregadas = {}


def obter_imagem(nome_ficheiro, tamanho):
    # Devolve a imagem ja do tamanho pedido, ou None se o ficheiro nao existir.
    tamanho = max(1, int(tamanho))
    chave = nome_ficheiro + str(tamanho)
    if chave not in imagens_carregadas:
        caminho = PASTA_ASSETS / "imagens" / nome_ficheiro
        if caminho.is_file():
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
    memoria.clear()


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
    ao_comecar_onda(numero_onda)


def criar_inimigo(nome):
    vida = vida_do_inimigo(nome, numero_onda)
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
    if not pode_construir(coluna, linha):
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
    ao_construir(torres[len(torres) - 1])


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
    ao_melhorar(torre_escolhida)


def vender():
    global ouro, torre_escolhida
    if torre_escolhida is None:
        return
    vendida = torre_escolhida
    ganho = valor_de_venda(vendida)
    ouro = ouro + ganho
    efeitos.append(texto_a_voar("+" + str(ganho), vendida["x"] - 15, vendida["y"], AMARELO))
    torres.remove(vendida)
    torre_escolhida = None
    ao_vender(vendida)


# --- Efeitos: sao so dicionarios com um tempo de vida ---

def circulo_a_crescer(x, y, cor, raio):
    return {"tipo": "circulo", "x": x, "y": y, "cor": cor, "raio": raio, "tempo": 15, "tempo_max": 15}


def texto_a_voar(texto, x, y, cor):
    return {"tipo": "texto", "x": x, "y": y, "cor": cor, "texto": texto, "tempo": 45, "tempo_max": 45}


# =====================================================================
#                          ACONTECIMENTOS
# =====================================================================

# --- Os acontecimentos ---
# O jogo chama cada uma destas funcoes quando acontece o que o nome diz.
# Estao vazias (so tem "pass"): o que la escreveres passa a acontecer nesse
# momento. E aqui que se INVENTA: uma bomba, um poder, um premio.
#
# Alem do que as regras do jogo podem usar (ver mais abaixo), tens:
#   memoria                     um dicionario so teu, para guardares o que
#                               quiseres de um frame para o outro:
#                               memoria["bombas"] = 3
#                               (fica vazio cada vez que o jogo recomeca)
#   inimigos.append(criar_inimigo("Soldado"))    manda vir mais um inimigo
#   magoar(inimigo, 50)         tira 50 de vida a um inimigo
#   numero_onda, ouro, vidas    para os MUDAR, a primeira linha da funcao
#                               tem de ser "global ouro" (ou "global vidas")
memoria = {}


# QUANDO COMECA UMA ONDA
# numero: 1 na primeira onda, 2 na segunda, e por ai fora.
# Ideias: dar 50 de ouro de 3 em 3 ondas; avisar com um texto_a_voar que vem
# ai uma onda dificil; mandar vir um General de surpresa na onda 5.
def ao_comecar_onda(numero):
    pass


# QUANDO UM INIMIGO CAI
# inimigo: o que acabou de cair. inimigo["x"], inimigo["y"] dizem onde foi, e
# inimigo["nome"] diz qual era, escrito tal e qual como em INIMIGOS, com os
# acentos: "Soldado", "Cavaleiro", "Aríete", "General".
# Ideias: rebentar e magoar os que estao perto; de vez em quando deixar ouro
# a dobrar; um Ariete que ao cair larga dois Soldados.
def ao_cair_inimigo(inimigo):
    pass


# QUANDO UM INIMIGO CHEGA AO CASTELO
# inimigo: o que acabou de entrar no castelo (as vidas ja foram tiradas).
# Ideias: dar um bocadinho de ouro de consolacao; magoar todos os outros
# inimigos, como se o castelo se defendesse.
def ao_chegar_ao_castelo(inimigo):
    pass


# QUANDO SE CONSTROI UMA TORRE
# torre: a que acabou de ser construida. torre["x"], torre["y"] dizem onde, e
# TORRES[torre["tipo"]]["nome"] diz qual e. torre["nivel"] e o nivel dela.
# Ideias: a primeira torre de cada jogo ja nascer no nivel 2; um circulo a
# crescer no sitio onde ela aparece.
def ao_construir(torre):
    pass


# QUANDO SE CARREGA NUMA TECLA
# tecla: a tecla em que se carregou. pygame.K_b e a tecla B, pygame.K_m a M.
# (As teclas 1 2 3 4, Espaco, U, V, F e P ja fazem coisas no jogo.)
# Para uma coisa so poder ser usada uma vez por onda, guarda na memoria o
# numero da onda em que foi usada e compara com numero_onda.
# Ideias: a tecla B magoa todos os inimigos, mas so uma vez por onda (usa a
# memoria para te lembrares se ja foi usada); a tecla G da ouro (batota!).
def ao_carregar_tecla(tecla):
    pass


# A CADA FRAME
# Corre 60 vezes por segundo enquanto se joga. Cuidado: o que aqui puseres
# acontece MUITAS vezes.
# Ideias: 1 de ouro a cada segundo (conta os frames na memoria); os inimigos
# perderem vida aos poucos.
def a_cada_frame():
    pass


# QUANDO ACABA UMA ONDA
# numero: a onda que acabou (1 na primeira). Corre quando o ultimo inimigo
# dela cai ou chega ao castelo, ja com o premio da onda no ouro. Tambem corre
# na ultima onda, quando ganhas o jogo.
# Ideias: recuperar uma vida por cada onda vencida; um premio a dobrar se
# nenhum inimigo chegou ao castelo nessa onda (conta-os na memoria, em
# ao_chegar_ao_castelo); avisar com um texto_a_voar o que vem a seguir.
def ao_acabar_onda(numero):
    pass


# QUANDO SE MELHORA UMA TORRE
# torre: a que acabou de subir de nivel (tecla U). torre["nivel"] ja e o
# nivel novo, e o ouro ja foi gasto.
# Ideias: a torre disparar logo a seguir (torre["recarga"] = 0); devolver
# metade do ouro quando ela chega ao ultimo nivel; um texto_a_voar a festejar.
def ao_melhorar(torre):
    pass


# QUANDO SE VENDE UMA TORRE
# torre: a que acabou de ser vendida (tecla V). Ja saiu do mapa e o ouro da
# venda ja entrou. torre["x"], torre["y"] dizem onde estava.
# Ideias: rebentar ao sair e magoar os inimigos que estao perto; contar na
# memoria quantas ja vendeste; um circulo_a_crescer no sitio onde estava.
def ao_vender(torre):
    pass


# =====================================================================
#                          A LOGICA, UM PASSO
# =====================================================================

# --- As regras do jogo ---
# Ha dez funcoes neste ficheiro que sao as REGRAS. Quatro sao do combate: quem
# as torres atacam (escolher_alvo), o que fazem ao disparar (disparar), o que
# acontece a um inimigo atingido (magoar) e como anda um inimigo
# (mover_inimigo). Seis sao das contas: quanta vida tem um inimigo
# (vida_do_inimigo), o que vale uma torre em cada nivel (valor_da_torre),
# quanto custa melhora-la (custo_melhoria), quanto se recebe ao vende-la
# (valor_de_venda), quanto ouro da acabar uma onda (premio_da_onda) e onde se
# pode construir (pode_construir). Mudar uma delas muda a maneira como o jogo
# se comporta.
#
# Dentro delas podes usar tudo o que o jogo tem:
#   inimigos, torres, projeteis, efeitos    as listas do que esta no ecra
#   distancia(x1, y1, x2, y2)               quantos pixeis vao de um ponto a outro
#   valor_da_torre(torre, "dano")           o dano (ou o "alcance") ja com o nivel
#   TORRES[torre["tipo"]]                   a ficha dessa torre ("nome", "custo"...)
#   torre["nivel"], torre["gasto"]          o nivel dela, e o ouro que ja la foi gasto
#   letra_do_mapa(coluna, linha)            a letra desse quadrado do MAPA
#   random.random()                         um numero ao calhas entre 0 e 1
# Para aparecer um efeito no ecra tem de se por na lista efeitos:
#   efeitos.append(texto_a_voar("ola", x, y, cor))        um texto que sobe e some
#   efeitos.append(circulo_a_crescer(x, y, cor, raio))    um circulo que cresce
# Para mudar o ouro ou as vidas dentro de uma funcao, a primeira linha dela
# tem de ser "global ouro" (ou "global vidas").

# QUEM A TORRE ATACA
# Recebe uma torre e devolve o inimigo que ela vai atacar (ou None, se nao
# houver nenhum ao alcance). Como esta: o que vai mais a frente.
#   torre["x"], torre["y"]    onde esta a torre, em pixeis
#   inimigo["x"], inimigo["y"], inimigo["vida"], inimigo["vida_max"]
#   inimigo["andado"]         quanto ja andou: quem andou mais vai a frente
#   inimigo["nome"]           "Soldado", "Cavaleiro"...
# Ideias: atacar o que tem menos vida; o que esta mais perto da torre; so os
# Cavaleiros.
def escolher_alvo(torre):
    alcance = valor_da_torre(torre, "alcance")
    melhor = None
    for inimigo in inimigos:
        if distancia(torre["x"], torre["y"], inimigo["x"], inimigo["y"]) <= alcance:
            if melhor is None or inimigo["andado"] > melhor["andado"]:
                melhor = inimigo
    return melhor


# O QUE ACONTECE A UM INIMIGO ATINGIDO
# Corre cada vez que um golpe acerta num inimigo. Recebe o inimigo e o dano
# desse golpe. Como esta: tira o dano a vida, e mais nada.
#   inimigo["vida"]       a vida que lhe resta (com 0 ou menos, cai)
#   inimigo["vida_max"]   a vida com que nasceu
#   inimigo["nome"]       "Soldado", "Cavaleiro"...
#   inimigo["x"], inimigo["y"]
# Ideias: golpes criticos (as vezes o dano conta a dobrar); uma armadura (o
# Ariete so leva metade); mostrar o dano com um texto_a_voar.
def magoar(inimigo, dano):
    inimigo["vida"] = inimigo["vida"] - dano


# O QUE A TORRE FAZ AO DISPARAR
# Corre quando uma torre esta pronta e tem um alvo. Recebe a torre e o
# inimigo escolhido. Como esta: faz o que diz o "efeito" da torre.
#   modelo           a ficha da torre em TORRES ("efeito", "cadencia", "cor"...)
#   torre["recarga"] os frames que a torre fica a espera ate ao proximo disparo
#   torre["mira"]    para onde aponta o cano
# Um projetil e um dicionario posto na lista projeteis: voa de "x", "y" ate
# ao "alvo", e ao chegar tira-lhe o "dano". Com "raio" maior que 0 rebenta e
# magoa todos os que estiverem a essa distancia.
# Ideias: disparar duas setas de cada vez; a pedra do Trabuco voar mais
# depressa; o golpe da Padeira acertar tambem em quem esta ao lado do alvo.
def disparar(torre, alvo):
    modelo = TORRES[torre["tipo"]]
    dano = valor_da_torre(torre, "dano")
    torre["recarga"] = modelo["cadencia"]
    torre["mira"] = (alvo["x"], alvo["y"])
    if "som" in modelo:
        tocar_som(modelo["som"])

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
                inimigo["lento"] = TEMPO_LENTIDAO
                inimigo["fator_lento"] = modelo["lentidao"]
        efeitos.append(circulo_a_crescer(torre["x"], torre["y"], modelo["cor"], alcance))
    elif modelo["efeito"] == "golpe":
        magoar(alvo, dano)
        efeitos.append(circulo_a_crescer(alvo["x"], alvo["y"], BRANCO, 18))


# QUANTA VIDA TEM UM INIMIGO
# Corre quando um inimigo nasce. Recebe o nome dele (como esta em INIMIGOS) e
# o numero da onda (1 na primeira), e devolve a vida com que ele nasce. Como
# esta: a "vida" da ficha dele, mais VIDA_EXTRA_POR_ONDA por cada onda que ja
# passou. Tem de devolver pelo menos 1.
# Ideias: os inimigos nao ficarem mais rijos com as ondas; a vida dobrar de 5
# em 5 ondas; os Cavaleiros nascerem com a vida ao calhas.
def vida_do_inimigo(nome, onda):
    return int(INIMIGOS[nome]["vida"] * (1 + VIDA_EXTRA_POR_ONDA * (onda - 1)))


# O QUE VALE UMA TORRE EM CADA NIVEL
# Recebe uma torre e o nome de uma coisa da ficha dela ("dano", "alcance"...)
# e devolve quanto isso vale para ESTA torre, ja com o nivel dela. Como esta:
# cada nivel a mais soma DANO_EXTRA_POR_NIVEL ao dano e
# ALCANCE_EXTRA_POR_NIVEL ao alcance (os numeros estao la em cima); o resto
# fica como na ficha.
# Ideias: o alcance nao crescer com o nivel; no ultimo nivel o dano triplicar;
# o Besteiro ganhar mais alcance do que os outros.
def valor_da_torre(torre, chave):
    base = TORRES[torre["tipo"]][chave]
    if chave == "dano":
        return base * (1 + DANO_EXTRA_POR_NIVEL * (torre["nivel"] - 1))
    if chave == "alcance":
        return base * (1 + ALCANCE_EXTRA_POR_NIVEL * (torre["nivel"] - 1))
    return base


# QUANTO CUSTA MELHORAR UMA TORRE
# Recebe uma torre e devolve o ouro que custa subi-la um nivel (tecla U).
# Como esta: o custo da ficha dela, vezes o nivel em que esta. Um Besteiro
# (50) custa 50 para o nivel 2 e 100 para o nivel 3.
# Ideias: custar sempre o mesmo; a primeira melhoria ser de borla; ficar mais
# caro quantas mais torres tiveres (len(torres)).
def custo_melhoria(torre):
    return TORRES[torre["tipo"]]["custo"] * torre["nivel"]


# QUANTO SE RECEBE AO VENDER UMA TORRE
# Recebe uma torre e devolve o ouro que ela da ao ser vendida (tecla V). Como
# esta: uma parte (VENDA, la em cima) de todo o ouro que ja se gastou nela.
# Ideias: devolver tudo; devolver menos enquanto ha uma onda a decorrer
# (onda_a_decorrer); as torres no nivel maximo valerem o dobro.
def valor_de_venda(torre):
    return int(torre["gasto"] * VENDA)


# QUANTO OURO DA ACABAR UMA ONDA
# Recebe o numero da onda que acabou (1 na primeira) e devolve o ouro de
# premio. Como esta: sempre BONUS_POR_ONDA. (Na ultima onda nao ha premio:
# ganhaste o jogo.)
# Ideias: cada onda dar mais do que a anterior; um premio grande de 5 em 5
# ondas; dar mais ouro a quem ainda tem as vidas todas.
def premio_da_onda(numero):
    return BONUS_POR_ONDA


# ONDE SE PODE CONSTRUIR
# Recebe a coluna e a linha de um quadrado do mapa (0, 0 e o canto de cima, a
# esquerda) e devolve True se da para construir la uma torre, ou False se
# nao da. Como esta: so na relva (a letra "." do MAPA).
# Ideias: tambem por cima das arvores (a letra "T"); so nos quadrados colados
# ao caminho; nunca na primeira linha do mapa.
def pode_construir(coluna, linha):
    return letra_do_mapa(coluna, linha) == "."


def atualizar_torres():
    for torre in torres:
        if torre["recarga"] > 0:
            torre["recarga"] = torre["recarga"] - 1
            continue
        alvo = escolher_alvo(torre)
        if alvo is None:
            continue
        disparar(torre, alvo)


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


# COMO ANDA UM INIMIGO
# Corre uma vez por frame (60 vezes por segundo) para cada inimigo, e da-lhe
# um passo. Como esta: vai a direito ate ao proximo ponto do caminho.
#   velocidade          quantos pixeis anda neste passo
#   CAMINHO_PONTOS      a lista dos pontos (x, y) do caminho, por ordem
#   inimigo["ponto"]    o numero do ponto para onde ele vai agora
#   inimigo["lento"]    os frames de lentidao que ainda lhe faltam
#   inimigo["andado"]   quanto ja andou ao todo (as torres usam isto)
#   inimigo["chegou"]   passa a True quando chega ao castelo
# Ideias: acelerar quando ja tem pouca vida; parar um bocadinho de vez em
# quando; andar aos solucos (um passo grande, depois nenhum).
def mover_inimigo(inimigo):
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


def atualizar_inimigos():
    global inimigos, vidas, ouro
    for inimigo in inimigos:
        mover_inimigo(inimigo)

    # A receita dos sobreviventes: quem morreu ou chegou ao castelo nao
    # passa para a lista nova.
    sobreviventes = []
    caidos = []
    chegados = []
    for inimigo in inimigos:
        dados = INIMIGOS[inimigo["nome"]]
        if inimigo["vida"] <= 0:
            ouro = ouro + dados["recompensa"]
            efeitos.append(texto_a_voar("+" + str(dados["recompensa"]), inimigo["x"] - 10, inimigo["y"] - 20, AMARELO))
            efeitos.append(circulo_a_crescer(inimigo["x"], inimigo["y"], dados["cor"], dados["tamanho"]))
            if "som" in dados:
                tocar_som(dados["som"])
            caidos.append(inimigo)
        elif inimigo["chegou"]:
            vidas = vidas - dados["estrago"]
            efeitos.append(texto_a_voar("-" + str(dados["estrago"]), inimigo["x"] - 10, inimigo["y"] - 30, VERMELHO))
            chegados.append(inimigo)
        else:
            sobreviventes.append(inimigo)
    inimigos = sobreviventes
    # So agora, com a lista ja arrumada, se avisa de quem caiu e de quem
    # chegou: assim esses acontecimentos podem mexer nos inimigos a vontade.
    for inimigo in caidos:
        ao_cair_inimigo(inimigo)
    for inimigo in chegados:
        ao_chegar_ao_castelo(inimigo)


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
            premio = premio_da_onda(numero_onda)
            ouro = ouro + premio
            efeitos.append(texto_a_voar("Onda vencida! +" + str(premio), LARGURA // 2 - 90, ALTURA // 2, AMARELO))
        ao_acabar_onda(numero_onda)


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
    a_cada_frame()
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
            desenhar_quadrado(MAPA[linha][coluna], coluna, linha)
            coluna = coluna + 1
        linha = linha + 1

    # O castelo, por cima do C.
    fim = CAMINHO_PONTOS[len(CAMINHO_PONTOS) - 1]
    desenhar_castelo(fim[0], fim[1])


# --- Os desenhos ---
# As funcoes que se seguem desenham uma torre, um inimigo, um quadrado do
# mapa, o castelo e um projetil. Desenha-se com formas do pygame, sempre no
# "ecra":
#   pygame.draw.circle(ecra, cor, (x, y), raio)
#   pygame.draw.rect(ecra, cor, (x, y, largura, altura))
#   pygame.draw.line(ecra, cor, (x1, y1), (x2, y2), grossura)
#   pygame.draw.polygon(ecra, cor, [(x1, y1), (x2, y2), (x3, y3)])
# O x cresce para a direita e o y cresce para BAIXO. Uma cor sao tres
# numeros (vermelho, verde, azul), de 0 a 255. O que se desenha depois fica
# por cima do que se desenhou antes. escurecer(cor, 0.5) da a mesma cor, mais
# escura.

# O DESENHO DE UMA TORRE
# torre["x"], torre["y"]   o centro do quadrado onde ela esta (o quadrado
#                          tem TILE pixeis de lado)
# torre["mira"]            o ponto (x, y) para onde aponta
# torre["nivel"]           1, 2 ou 3
# modelo["cor"]            a cor da ficha dela em TORRES
# Ideias: uma bandeira no topo; uma torre que muda de cor com o nivel; dois
# canos em vez de um.
def desenhar_torre(torre):
    modelo = TORRES[torre["tipo"]]
    base = pygame.Rect(0, 0, TILE - 6, TILE - 6)
    base.center = (torre["x"], torre["y"])
    imagem = None
    if "imagem" in modelo:
        imagem = obter_imagem(modelo["imagem"], base.width)
    if imagem is not None:
        ecra.blit(imagem, base)
    else:
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


# O DESENHO DE UM INIMIGO
# x, y        o centro do inimigo         tamanho   o "tamanho" da ficha dele
# cor         a cor da ficha (mais clara enquanto esta lento)
# inimigo["vida"], inimigo["vida_max"]    para a barra de vida
# Ideias: dar-lhe olhos; um chapeu ao General; ficar vermelho quando ja tem
# pouca vida.
def desenhar_inimigo(inimigo):
    dados = INIMIGOS[inimigo["nome"]]
    tamanho = dados["tamanho"]
    x = int(inimigo["x"])
    y = int(inimigo["y"])
    cor = dados["cor"]
    if inimigo["lento"] > 0:
        cor = (cor[0] // 2 + 100, cor[1] // 2 + 90, cor[2] // 2 + 20)
    imagem = None
    if "imagem" in dados:
        imagem = obter_imagem(dados["imagem"], tamanho)
    if imagem is not None:
        ecra.blit(imagem, imagem.get_rect(center=(x, y)))
    elif dados["forma"] == "quadrado":
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


# UM QUADRADO DO MAPA
# letra: a letra desse quadrado no MAPA ("." relva, "#" caminho, "T" arvore,
# "E" entrada, "C" castelo). coluna, linha: onde ele fica no mapa (0, 0 e o
# canto de cima, a esquerda).
#   quadrado          o retangulo desse quadrado no ecra: quadrado.center e o
#                     meio, quadrado.x e quadrado.y o canto de cima
# Como esta: relva aos quadrados (um claro, um escuro), o caminho por cima, e
# as arvores sao um circulo.
# Ideias: flores na relva; um caminho de pedras; arvores com tronco; uma
# letra nova, por exemplo "A" para agua (if letra == "A").
def desenhar_quadrado(letra, coluna, linha):
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


# O CASTELO
# x, y: o meio do quadrado do C, onde acaba o caminho. Como esta: uma
# muralha com quatro ameias, uma porta e uma bandeira azul.
#   muralha    o retangulo da muralha: muralha.x, muralha.y, muralha.centerx,
#              muralha.bottom
#   vidas      as vidas que te restam (VIDAS_INICIAIS sao as do inicio)
# Ideias: outra cor de bandeira; duas torres dos lados; o castelo ficar mais
# escuro quando ja tens poucas vidas.
def desenhar_castelo(x, y):
    muralha = pygame.Rect(0, 0, 56, 44)
    muralha.midbottom = (x, y + 20)
    pygame.draw.rect(ecra, (150, 145, 140), muralha)
    for dente in [0, 2, 4, 6]:
        pygame.draw.rect(ecra, (150, 145, 140), (muralha.x + dente * 8, muralha.y - 8, 8, 8))
    pygame.draw.rect(ecra, (60, 40, 30), (muralha.centerx - 7, muralha.bottom - 18, 14, 18))
    pygame.draw.line(ecra, (90, 80, 70), (muralha.centerx, muralha.y - 8), (muralha.centerx, muralha.y - 30), 2)
    pygame.draw.polygon(ecra, (40, 90, 200), [(muralha.centerx, muralha.y - 30), (muralha.centerx + 16, muralha.y - 24), (muralha.centerx, muralha.y - 18)])


# UM PROJETIL
# projetil: uma seta ou uma pedra a voar.
#   projetil["x"], projetil["y"]    onde vai agora
#   projetil["raio"]                maior que 0 se rebenta ao chegar (a pedra
#                                   do Trabuco); 0 se e uma seta
#   projetil["cor"]                 a cor da torre que o disparou
# Como esta: uma bolinha da cor da torre com um contorno preto, maior se for
# das que rebentam.
# Ideias: uma seta comprida em vez de uma bolinha; a pedra ser cinzenta;
# brilhar a amarelo.
def desenhar_projetil(projetil):
    tamanho = 4
    if projetil["raio"] > 0:
        tamanho = 7
    pygame.draw.circle(ecra, PRETO, (int(projetil["x"]), int(projetil["y"])), tamanho + 1)
    pygame.draw.circle(ecra, projetil["cor"], (int(projetil["x"]), int(projetil["y"])), tamanho)


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
        mostrar_texto("V vender (+" + str(valor_de_venda(torre_escolhida)) + ")", 590, y + 10, AMARELO, fonte)
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
        if pode_construir(quadrado[0], quadrado[1]) and not ocupado:
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
        desenhar_projetil(projetil)
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
                ao_carregar_tecla(evento.key)

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
