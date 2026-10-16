# =====================================================================
# HALLOWEEN — A NOITE DOS DOCES
#
# Um Pac-Man as escuras. Apanha todos os doces do labirinto para passar
# a onda seguinte. So ves o que a tua lanterna ilumina, e os fantasmas
# ATRAVESSAM PAREDES. Aponta-lhes a luz: na luz, fogem de ti.
# Quantas ondas aguentas?
#
#                    TECLADO          COMANDO (PS5, PS4, Xbox...)
#   andar            setas            manipulo DIREITO ou setas
#   apontar a luz    W A S D          manipulo ESQUERDO
#   trocar os dois   T                Triangulo (Y na Xbox)
#
#   COM RATO: o rato aponta a luz, e W A S D (ou as setas) anda.
#   Basta mexer o rato para ligar. M desliga e volta a ligar.
#   comecar          Espaco           qualquer botao
#   ecra inteiro     F ou F11
#   sair             Esc
#
# COMO E QUE ISTO FICA TEU:
#   Mexe SO na primeira parte do ficheiro, a que diz "MEXE SÓ AQUI".
#   Muda uma coisa, grava, corre. Se der erro, desfaz (Ctrl+Z) e tenta
#   outra vez. Nao ha nada que possas estragar para sempre.
# =====================================================================


# #####################################################################
# #####################################################################
# ##                                                                 ##
# ##        MEXE SÓ AQUI: nestas constantes e variáveis              ##
# ##                                                                 ##
# #####################################################################
# #####################################################################


# ---------------------------------------------------------------------
# 1. OS TEXTOS
# Tudo o que esta entre aspas e texto. Escreve o que quiseres, mas nao
# apagues as aspas.
# ---------------------------------------------------------------------

TITULO = "A NOITE DOS DOCES"
SUBTITULO = "Apanha os doces. Não deixes que te apanhem."

# Quando um fantasma te apanha, aparece UMA destas frases, ao calhas.
# Podes acrescentar quantas quiseres: entre aspas, separadas por virgulas.
FRASES_DO_SUSTO = [
    "BUUUU!",
    "Apanhei-te!",
    "Os teus doces agora são meus.",
    "Devias ter olhado para trás...",
    "As paredes não me param.",
]

MENSAGEM_DE_ONDA_COMPLETA = "Sobreviveste... por agora."


# ---------------------------------------------------------------------
# 2. AS CORES
# Uma cor sao tres numeros, de 0 a 255: (VERMELHO, VERDE, AZUL).
#   (255, 0, 0) e vermelho puro.   (0, 0, 0) e preto.
#   (255, 255, 255) e branco.      (255, 140, 0) e cor de laranja.
# Podes inventar cores novas aqui e usa-las la em baixo.
# ---------------------------------------------------------------------

PRETO = (0, 0, 0)
BRANCO = (240, 240, 250)
CINZENTO = (120, 120, 130)
LARANJA = (255, 130, 20)
AMARELO = (255, 220, 60)
VERMELHO = (220, 30, 40)
VERDE = (60, 160, 60)
VERDE_ACIDO = (120, 255, 60)
ROXO = (90, 40, 140)
CASTANHO = (110, 70, 40)
AZUL = (40, 60, 230)
AZUL_FANTASMA = (170, 210, 255)
ROSA = (255, 120, 190)

COR_DO_CHAO = (45, 38, 55)          # o chao, onde a lanterna bate
COR_DAS_PAREDES = ROXO
COR_DO_CONTORNO = LARANJA           # a linha a volta das paredes
COR_DO_ESCURO = (8, 6, 16)          # o escuro (quanto mais perto de 0, mais escuro)
COR_DA_LUZ = (255, 235, 190)        # a luz da lanterna
COR_DO_FANTASMA_COM_MEDO = AZUL     # depois de comeres um super-doce
COR_DO_TITULO = LARANJA
COR_DO_TEXTO = BRANCO


# ---------------------------------------------------------------------
# 3. OS NUMEROS DO JOGO
# Experimenta numeros grandes, pequenos, absurdos. E assim que se
# descobre o que cada um faz.
# ---------------------------------------------------------------------

VIDAS = 3
VIDA_EXTRA_A_CADA = 3               # ondas. Poe 0 para nunca dar vidas

VELOCIDADE_DO_JOGADOR = 4
VELOCIDADE_DO_FANTASMA = 0.9
FANTASMAS_NA_PRIMEIRA_ONDA = 1
MAIS_FANTASMAS_POR_ONDA = 1
MAIS_VELOCIDADE_POR_ONDA = 0.1
# O que fazem os fantasmas quando a lanterna lhes bate:
#   numero negativo = fogem (-0.7 foge devagar, -2 foge a correr)
#   0 = ficam parados       1 = nem querem saber da luz
FANTASMA_NA_LUZ = -0.7
SEGUNDOS_ATE_OS_FANTASMAS_ACORDAREM = 3

TAMANHO_DA_LANTERNA = 260           # ate onde chega a luz
ABERTURA_DA_LANTERNA = 35           # em graus: quanto maior, mais larga
BATERIA_GASTA_POR_SEGUNDO = 2       # a bateria vai de 100 a 0. Poe 0 para nunca gastar
BATERIA_POR_DOCE = 2                # cada doce recarrega um bocadinho
SEGUNDOS_DE_SUPER_DOCE = 6          # quanto tempo os fantasmas tem medo de ti
BRILHO_DAS_PAREDES = 0.35           # as paredes no escuro: 0 = invisiveis, 1 = sempre acesas

TAMANHO_DO_PIXEL = 3                # o tamanho de cada quadradinho dos desenhos

ECRA_INTEIRO = True                 # False = abre numa janela (F ou F11 troca a meio do jogo)
TROCAR_MANIPULOS = False            # True = o esquerdo anda e o direito aponta (T ou Triangulo troca a meio)
SOM_LIGADO = True
VOLUME = 0.6                        # de 0 a 1
COMANDO_VIBRA = True                # o comando treme no susto


# ---------------------------------------------------------------------
# 4. OS LABIRINTOS
# Cada labirinto tem 14 linhas de 20 letras.
#   #  parede                    .  doce
#   S  super-doce (os fantasmas ficam com medo e podes manda-los embora)
#   J  onde comeca o jogador     F  onde nascem os fantasmas
#   (espaco) corredor vazio, sem doce
# Se uma linha tiver os dois lados abertos, e um tunel: sai-se por um
# lado e entra-se pelo outro.
# Joga-se um a seguir ao outro, e depois ao calhas, para sempre.
# ---------------------------------------------------------------------

LABIRINTO_1 = [
    "####################",
    "#S . . . ##. . . .S#",
    "# ##.###.## ### ##.#",
    "#. . . . . . . . . #",
    "# ##.#.###### # ##.#",
    "#. . # . ##. .#. . #",
    "####.###.## ### ####",
    "     # . FF. .#.    ",
    "####.#.###### # ####",
    "#. . . . ##. . . . #",
    "# ##.###.## ### ##.#",
    "#S # . . .J. . .#.S#",
    "# . . . . . . . . .#",
    "####################",
]

LABIRINTO_2 = [
    "####################",
    "#S . . . . . . . .S#",
    "# # # # # .#.#.#.#.#",
    "#. . . . . . . . . #",
    "# # # # # .#.#.#.#.#",
    "#. . . . . . . . . #",
    "### ### .FF .###.###",
    "#. . . . . . . . . #",
    "# # # # # .#.#.#.#.#",
    "#. . . . . . . . . #",
    "# # # # # .#.#.#.#.#",
    "#. . . . .J. . . . #",
    "#S. . . . . . . . S#",
    "####################",
]

LABIRINTO_3 = [
    "####################",
    "#J . . #S. . .#. . #",
    "# ####.#.#### # ##.#",
    "#.#. . # . .#. .#. #",
    "# # ######.#### # ##",
    "#.#. . . # . .#.#. #",
    "# ######.#### # ##.#",
    "#. . . # FF.#.#. . #",
    "######.#.## # ####.#",
    "#S . . # . .#. . . #",
    "# ##### ### ######.#",
    "#. . .#. .#. . . # #",
    "# ### . # . ####. S#",
    "####################",
]

LABIRINTO_4 = [
    "####################",
    "#S . . # . .#. . .S#",
    "# ### .#.## # .###.#",
    "#.#. . . . . . . # #",
    "# # ####.## ####.#.#",
    "#. .#. . . . . # . #",
    "### # ###FF###.#.###",
    "     .#. . . # .    ",
    "### # ########.#.###",
    "#. .#. . J . . # . #",
    "# # ####.## ####.#.#",
    "#.#. . . . . . . # #",
    "#S. . .#. . # . . S#",
    "####################",
]

LABIRINTO_5 = [
    "####################",
    "#S . . . ##. . . .S#",
    "# .## . . . . .## .#",
    "#. ##. # . .#. ##. #",
    "# . . .#. . # . . .#",
    "#. # . . . . . .#. #",
    "# .#. . #FF#. . # .#",
    "#. . . .#. # . . . #",
    "# .## . . . . .## .#",
    "#. ##. .#. # . ##. #",
    "# . . . # .#. . . .#",
    "#. # . . .J. . .#. #",
    "#S. . . . . . . . S#",
    "####################",
]

# A ordem em que aparecem. Para acrescentares um labirinto, faz um
# LABIRINTO_6 la em cima e poe-no aqui, com um nome na outra lista.
LABIRINTOS = [LABIRINTO_1, LABIRINTO_2, LABIRINTO_3, LABIRINTO_4, LABIRINTO_5]
NOMES_DOS_LABIRINTOS = [
    "O Cemitério",
    "A Cave",
    "O Labirinto da Bruxa",
    "A Mansão",
    "O Campo de Abóboras",
]


# ---------------------------------------------------------------------
# 5. OS DESENHOS
# Cada desenho e uma lista de linhas. Cada letra e um quadradinho.
#   "."  e transparente (nao se desenha nada)
#   as outras letras tem a cor que esta na PALETA, aqui em baixo.
#
# A letra "O" e especial: BRILHA NO ESCURO. Usa-a para os olhos.
# Podes acrescentar letras novas a PALETA. Uma letra que nao esteja na
# PALETA aparece cor-de-rosa choque, para veres onde esta o engano.
# ---------------------------------------------------------------------

PALETA = {
    "X": AZUL_FANTASMA,
    "O": VERDE_ACIDO,
    "P": PRETO,
    "B": BRANCO,
    "L": LARANJA,
    "A": AMARELO,
    "V": VERDE,
    "R": VERMELHO,
    "Z": ROXO,
    "C": CASTANHO,
    "G": CINZENTO,
}

DESENHO_DO_FANTASMA = [
    "....XXXX....",
    "..XXXXXXXX..",
    ".XXXXXXXXXX.",
    ".XXOOXXOOXX.",
    "XXXOOXXOOXXX",
    "XXXXXXXXXXXX",
    "XXXXXPPXXXXX",
    "XXXXPPPPXXXX",
    "XXXXXPPXXXXX",
    "XXXXXXXXXXXX",
    "XXXXXXXXXXXX",
    "XX.XXX.XXX.X",
    "X...X...X...",
]

DESENHO_DO_JOGADOR = [
    "....VV....",
    "..LLVVLL..",
    ".LLLLLLLL.",
    "LLAALLAALL",
    "LLAALLAALL",
    "LLLLLLLLLL",
    "LAAAAAAAAL",
    "LLAALLAALL",
    ".LLLLLLLL.",
    "..LLLLLL..",
]

DESENHO_DO_DOCE = [
    "R.....R",
    "RRZZZRR",
    "R.....R",
]

DESENHO_DO_SUPER_DOCE = [
    "...V...",
    ".LLVLL.",
    "LLLLLLL",
    "LALLLAL",
    "LLLLLLL",
    "LAAAAAL",
    ".LLLLL.",
]


# #####################################################################
# #####################################################################
# ##                                                                 ##
# ##        NÃO MEXER DAQUI PARA BAIXO                               ##
# ##                                                                 ##
# ##   Este e o motor do jogo. Na proxima aula vamos abri-lo e       ##
# ##   perceber como funciona. Hoje, e so usar.                      ##
# ##                                                                 ##
# #####################################################################
# #####################################################################

import array
import math
import random

import pygame

TILE = 40
COLUNAS = 20
LINHAS = 14
TOPO = 40                      # a barra de cima, com as vidas e a onda
LARGURA = COLUNAS * TILE
ALTURA = TOPO + LINHAS * TILE
FPS = 60
LETRA_QUE_BRILHA = "O"
ROSA_DO_ENGANO = (255, 0, 200)

# Que eixo do comando e qual. Estes sao os do comando da PS5 e da Xbox.
# Se o teu comando estiver trocado, corre o testar-comando.py, mexe nos
# manipulos e ve que numeros mudam.
EIXO_ESQUERDO_X = 0
EIXO_ESQUERDO_Y = 1
EIXO_DIREITO_X = 2
EIXO_DIREITO_Y = 3
BOTAO_TROCAR = 3   # Triangulo na PS5/PS4, Y na Xbox
ZONA_MORTA = 0.3   # os manipulos nunca estao bem no zero: ignora-se o que for menos

pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()
# SCALED estica o jogo para encher o ecra sem estragar o desenho.
ecra_inteiro = ECRA_INTEIRO
if ecra_inteiro:
    ecra = pygame.display.set_mode((LARGURA, ALTURA), pygame.SCALED | pygame.FULLSCREEN)
else:
    ecra = pygame.display.set_mode((LARGURA, ALTURA), pygame.SCALED)


def alternar_ecra_inteiro():
    # Primeiro tenta a maneira rapida. Se este computador nao deixar,
    # volta a abrir a janela ja em ecra inteiro (ou ja sem ele).
    global ecra, ecra_inteiro
    ecra_inteiro = not ecra_inteiro
    try:
        resultado = pygame.display.toggle_fullscreen()
    except pygame.error:
        resultado = 0
    if not resultado:
        if ecra_inteiro:
            ecra = pygame.display.set_mode((LARGURA, ALTURA), pygame.SCALED | pygame.FULLSCREEN)
        else:
            ecra = pygame.display.set_mode((LARGURA, ALTURA), pygame.SCALED)
pygame.display.set_caption(TITULO)
clock = pygame.time.Clock()
fonte_pequena = pygame.font.SysFont(None, 26)
fonte = pygame.font.SysFont(None, 34)
fonte_grande = pygame.font.SysFont(None, 84)


# --------------------------- DESENHOS ---------------------------------

def fazer_desenho(linhas, pixel, so_o_que_brilha, cor_forcada):
    # Transforma uma lista de textos numa imagem.
    #   so_o_que_brilha=True  so desenha a letra que brilha (os olhos)
    #   cor_forcada           pinta tudo dessa cor, menos os olhos
    largura = 0
    for linha in linhas:
        if len(linha) > largura:
            largura = len(linha)
    imagem = pygame.Surface((max(1, largura * pixel), max(1, len(linhas) * pixel)), pygame.SRCALPHA)
    y = 0
    for linha in linhas:
        x = 0
        for letra in linha:
            desenhar = letra != " " and letra != "."
            if so_o_que_brilha and letra != LETRA_QUE_BRILHA:
                desenhar = False
            if desenhar:
                cor = ROSA_DO_ENGANO
                if letra in PALETA:
                    cor = PALETA[letra]
                if cor_forcada is not None and letra != LETRA_QUE_BRILHA:
                    cor = cor_forcada
                imagem.fill(cor, (x * pixel, y * pixel, pixel, pixel))
            x = x + 1
        y = y + 1
    return imagem


imagem_fantasma = fazer_desenho(DESENHO_DO_FANTASMA, TAMANHO_DO_PIXEL, False, None)
imagem_fantasma_medo = fazer_desenho(DESENHO_DO_FANTASMA, TAMANHO_DO_PIXEL, False, COR_DO_FANTASMA_COM_MEDO)
imagem_fantasma_pisca = fazer_desenho(DESENHO_DO_FANTASMA, TAMANHO_DO_PIXEL, False, BRANCO)
olhos_fantasma = fazer_desenho(DESENHO_DO_FANTASMA, TAMANHO_DO_PIXEL, True, None)
imagem_jogador = fazer_desenho(DESENHO_DO_JOGADOR, TAMANHO_DO_PIXEL, False, None)
olhos_jogador = fazer_desenho(DESENHO_DO_JOGADOR, TAMANHO_DO_PIXEL, True, None)
imagem_doce = fazer_desenho(DESENHO_DO_DOCE, TAMANHO_DO_PIXEL, False, None)
imagem_super_doce = fazer_desenho(DESENHO_DO_SUPER_DOCE, TAMANHO_DO_PIXEL, False, None)
icone_vida = fazer_desenho(DESENHO_DO_JOGADOR, 2, False, None)
# Para o susto: o mesmo fantasma, mas enorme.
pixel_susto = max(1, int(ALTURA * 0.7) // max(1, len(DESENHO_DO_FANTASMA)))
fantasma_gigante = fazer_desenho(DESENHO_DO_FANTASMA, pixel_susto, False, None)
fantasma_do_titulo = fazer_desenho(DESENHO_DO_FANTASMA, TAMANHO_DO_PIXEL * 4, False, None)


# --------------------------- LUZ --------------------------------------

def fazer_luz_redonda(raio, cor, forca):
    # Um circulo que e claro no meio e escurece ate as bordas.
    luz = pygame.Surface((raio * 2, raio * 2))
    luz.fill(PRETO)
    passos = 30
    passo = 0
    while passo < passos:
        fracao = passo / passos
        brilho = (fracao ** 0.7) * forca
        cor_agora = (int(cor[0] * brilho), int(cor[1] * brilho), int(cor[2] * brilho))
        pygame.draw.circle(luz, cor_agora, (raio, raio), max(1, int(raio * (1 - fracao))))
        passo = passo + 1
    return luz


def fazer_cone(raio, abertura_graus, cor):
    # Um cone de luz virado para a direita. Desenha-se varias vezes, cada
    # vez mais estreito e mais claro, para as bordas ficarem suaves.
    cone = pygame.Surface((raio * 2, raio * 2))
    cone.fill(PRETO)
    camada = pygame.Surface((raio * 2, raio * 2))
    for largura, forca in [(1.35, 0.25), (1.15, 0.55), (1.0, 1.0)]:
        camada.fill(PRETO)
        meia_abertura = math.radians(abertura_graus) * largura / 2
        passos = 24
        passo = 0
        while passo < passos:
            fracao = passo / passos
            r = raio * (1 - fracao)
            brilho = (0.25 + 0.75 * fracao) * forca
            cor_agora = (int(cor[0] * brilho), int(cor[1] * brilho), int(cor[2] * brilho))
            pontos = [(raio, raio)]
            angulo = -meia_abertura
            while angulo <= meia_abertura + 0.001:
                pontos.append((raio + math.cos(angulo) * r, raio + math.sin(angulo) * r))
                angulo = angulo + meia_abertura / 8
            if r > 2:
                pygame.draw.polygon(camada, cor_agora, pontos)
            passo = passo + 1
        cone.blit(camada, (0, 0), special_flags=pygame.BLEND_RGB_MAX)
    return cone


cone_de_luz = fazer_cone(TAMANHO_DA_LANTERNA, ABERTURA_DA_LANTERNA, COR_DA_LUZ)
luz_a_volta = fazer_luz_redonda(70, COR_DA_LUZ, 0.6)
luz_super_doce = fazer_luz_redonda(45, LARANJA, 0.5)
escuro = pygame.Surface((LARGURA, ALTURA))


# --------------------------- SONS --------------------------------------
# Nao ha ficheiros de som: os sons sao feitos com matematica, numero a
# numero, quando o jogo arranca.

som_ativo = SOM_LIGADO and pygame.mixer.get_init() is not None


def fazer_som(amostras):
    if not som_ativo:
        return None
    canais = pygame.mixer.get_init()[2]
    dados = array.array("h")
    for valor in amostras:
        valor = max(-1.0, min(1.0, valor))
        inteiro = int(valor * 30000 * VOLUME)
        canal = 0
        while canal < canais:
            dados.append(inteiro)
            canal = canal + 1
    return pygame.mixer.Sound(buffer=dados)


def tocar(som):
    if som is not None:
        som.play()


def gerar_grito():
    taxa = 44100
    duracao = 1.3
    amostras = []
    fase = 0.0
    i = 0
    while i < int(taxa * duracao):
        t = i / taxa
        frequencia = 950 - 450 * t / duracao + 70 * math.sin(2 * math.pi * 7 * t)
        fase = fase + frequencia / taxa
        serra = 2 * (fase % 1) - 1
        envelope = min(1, t / 0.02) * (1 - t / duracao)
        amostras.append((serra * 0.6 + random.uniform(-1, 1) * 0.45) * envelope)
        i = i + 1
    return amostras


def gerar_coracao():
    taxa = 44100
    amostras = []
    i = 0
    while i < int(taxa * 0.4):
        t = i / taxa
        batida = math.sin(2 * math.pi * 55 * t) * math.exp(-t * 28)
        if t > 0.14:
            t2 = t - 0.14
            batida = batida + 0.7 * math.sin(2 * math.pi * 50 * t2) * math.exp(-t2 * 28)
        amostras.append(batida * 0.9)
        i = i + 1
    return amostras


def gerar_notas(frequencias, duracao, volume):
    taxa = 44100
    amostras = []
    for frequencia in frequencias:
        i = 0
        while i < int(taxa * duracao):
            t = i / taxa
            amostras.append(math.sin(2 * math.pi * frequencia * t) * math.exp(-t * 30) * volume)
            i = i + 1
    return amostras


def gerar_ambiente():
    # Um zumbido grave e vento. Dura 4 segundos e repete-se sem se notar.
    taxa = 44100
    amostras = []
    vento = 0.0
    i = 0
    while i < taxa * 4:
        t = i / taxa
        tremor = 0.6 + 0.4 * math.sin(2 * math.pi * 0.5 * t)
        zumbido = (math.sin(2 * math.pi * 55 * t) + 0.6 * math.sin(2 * math.pi * 82.5 * t)) * 0.18 * tremor
        vento = vento * 0.995 + random.uniform(-1, 1) * 0.005
        amostras.append(zumbido + vento * 1.5)
        i = i + 1
    return amostras


som_grito = fazer_som(gerar_grito())
som_coracao = fazer_som(gerar_coracao())
som_doce = fazer_som(gerar_notas([1320], 0.04, 0.25))
som_super_doce = fazer_som(gerar_notas([440, 554, 659, 880], 0.07, 0.5))
som_fantasma_comido = fazer_som(gerar_notas([1760, 1320, 880, 660], 0.05, 0.5))
som_onda = fazer_som(gerar_notas([523, 659, 784, 1047, 784, 1047], 0.09, 0.5))
som_ambiente = fazer_som(gerar_ambiente())
if som_ambiente is not None:
    som_ambiente.set_volume(0.5)
    som_ambiente.play(-1)


# --------------------------- COMANDO -----------------------------------
# Funciona com comandos de PS5, PS4, Xbox e quase todos os outros, por
# cabo ou Bluetooth. Pode ligar-se a meio do jogo.

pygame.joystick.init()
comandos = []


def vibrar(forte, fraco, milissegundos):
    if not COMANDO_VIBRA:
        return
    for comando in comandos:
        comando.rumble(forte, fraco, milissegundos)


def ler_manipulo(comando, eixo_x, eixo_y):
    if comando.get_numaxes() <= max(eixo_x, eixo_y):
        return [0.0, 0.0]
    x = comando.get_axis(eixo_x)
    y = comando.get_axis(eixo_y)
    if math.hypot(x, y) < ZONA_MORTA:
        return [0.0, 0.0]
    return [x, y]


def ler_teclado(teclas, esquerda, direita, cima, baixo):
    direcao = [0.0, 0.0]
    if teclas[esquerda]:
        direcao[0] = direcao[0] - 1
    if teclas[direita]:
        direcao[0] = direcao[0] + 1
    if teclas[cima]:
        direcao[1] = direcao[1] - 1
    if teclas[baixo]:
        direcao[1] = direcao[1] + 1
    return direcao


def direcao_para_andar(teclas):
    # Normalmente: setas e manipulo direito. Trocado: WASD e manipulo
    # esquerdo. As setas do comando andam sempre. Devolve [x, y].
    if modo_rato:
        # Com o rato a apontar, as duas maos do teclado ficam livres:
        # tanto WASD como as setas servem para andar.
        wasd = ler_teclado(teclas, pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s)
        setas = ler_teclado(teclas, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN)
        direcao = [wasd[0] + setas[0], wasd[1] + setas[1]]
    elif manipulos_trocados:
        direcao = ler_teclado(teclas, pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s)
    else:
        direcao = ler_teclado(teclas, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN)
    for comando in comandos:
        if manipulos_trocados:
            manipulo = ler_manipulo(comando, EIXO_ESQUERDO_X, EIXO_ESQUERDO_Y)
        else:
            manipulo = ler_manipulo(comando, EIXO_DIREITO_X, EIXO_DIREITO_Y)
        direcao[0] = direcao[0] + manipulo[0]
        direcao[1] = direcao[1] + manipulo[1]
        if comando.get_numhats() > 0:
            seta = comando.get_hat(0)
            direcao[0] = direcao[0] + seta[0]
            direcao[1] = direcao[1] - seta[1]
        # No comando da PS5 as setas sao os botoes 11 a 14.
        if comando.get_numbuttons() >= 15:
            if comando.get_button(11):
                direcao[1] = direcao[1] - 1
            if comando.get_button(12):
                direcao[1] = direcao[1] + 1
            if comando.get_button(13):
                direcao[0] = direcao[0] - 1
            if comando.get_button(14):
                direcao[0] = direcao[0] + 1
    return direcao


def direcao_para_apontar(teclas):
    # Normalmente: WASD e manipulo esquerdo. Trocado: setas e manipulo
    # direito. Devolve [x, y], ou [0, 0] se nada.
    if modo_rato:
        direcao = [0.0, 0.0]     # com rato, o teclado so anda
    elif manipulos_trocados:
        direcao = ler_teclado(teclas, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN)
    else:
        direcao = ler_teclado(teclas, pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s)
    for comando in comandos:
        if manipulos_trocados:
            manipulo = ler_manipulo(comando, EIXO_DIREITO_X, EIXO_DIREITO_Y)
        else:
            manipulo = ler_manipulo(comando, EIXO_ESQUERDO_X, EIXO_ESQUERDO_Y)
        direcao[0] = direcao[0] + manipulo[0]
        direcao[1] = direcao[1] + manipulo[1]
    return direcao


def trocar_manipulos():
    global manipulos_trocados, aviso, tempo_aviso
    manipulos_trocados = not manipulos_trocados
    if manipulos_trocados:
        aviso = "Trocado: esquerdo anda, direito aponta a lanterna"
    else:
        aviso = "Normal: direito anda, esquerdo aponta a lanterna"
    tempo_aviso = 2 * FPS


def ligar_rato(ligado):
    global modo_rato, aviso, tempo_aviso
    modo_rato = ligado
    if modo_rato:
        aviso = "Rato: aponta com o rato, anda com W A S D ou setas  (M desliga)"
    else:
        aviso = "Teclado: setas andam, W A S D apontam  (M volta ao rato)"
    tempo_aviso = 2 * FPS


manipulos_trocados = TROCAR_MANIPULOS
modo_rato = False
aviso = ""
tempo_aviso = 0


# --------------------------- O LABIRINTO -------------------------------

def centro(coluna, linha):
    return (coluna * TILE + TILE // 2, TOPO + linha * TILE + TILE // 2)


def e_parede(coluna, linha):
    if linha < 0 or linha >= LINHAS:
        return True
    # Na horizontal, o mapa da a volta: e assim que funcionam os tuneis.
    return mapa[linha][coluna % COLUNAS] == "#"


def carregar_labirinto(indice):
    global mapa, inicio_jogador, ninhos, doces_que_faltam, imagem_labirinto, contorno_paredes
    desenho = LABIRINTOS[indice]
    # Copia o labirinto para uma grelha de letras que se pode alterar
    # (quando comes um doce, ele passa a ser um espaco). Linhas curtas
    # ou que faltem sao preenchidas com parede.
    mapa = []
    linha = 0
    while linha < LINHAS:
        letras = []
        coluna = 0
        while coluna < COLUNAS:
            letra = "#"
            if linha < len(desenho) and coluna < len(desenho[linha]):
                letra = desenho[linha][coluna]
            letras.append(letra)
            coluna = coluna + 1
        mapa.append(letras)
        linha = linha + 1

    inicio_jogador = None
    ninhos = []
    doces_que_faltam = 0
    primeiro_livre = (1, 1)
    linha = 0
    while linha < LINHAS:
        coluna = 0
        while coluna < COLUNAS:
            letra = mapa[linha][coluna]
            if letra != "#" and primeiro_livre == (1, 1):
                primeiro_livre = (coluna, linha)
            if letra == "J":
                inicio_jogador = (coluna, linha)
                mapa[linha][coluna] = " "
            if letra == "F":
                ninhos.append((coluna, linha))
                mapa[linha][coluna] = " "
            if letra == "." or letra == "S":
                doces_que_faltam = doces_que_faltam + 1
            coluna = coluna + 1
        linha = linha + 1
    if inicio_jogador is None:
        inicio_jogador = primeiro_livre
    if len(ninhos) == 0:
        ninhos.append((COLUNAS // 2, 1))

    # O desenho do labirinto faz-se uma vez so, e depois e so copiar.
    imagem_labirinto = pygame.Surface((LARGURA, ALTURA))
    imagem_labirinto.fill(COR_DO_CHAO)
    contorno_paredes = pygame.Surface((LARGURA, ALTURA))
    contorno_paredes.fill(PRETO)
    cor_fraca = (int(COR_DO_CONTORNO[0] * BRILHO_DAS_PAREDES),
                 int(COR_DO_CONTORNO[1] * BRILHO_DAS_PAREDES),
                 int(COR_DO_CONTORNO[2] * BRILHO_DAS_PAREDES))
    linha = 0
    while linha < LINHAS:
        coluna = 0
        while coluna < COLUNAS:
            if mapa[linha][coluna] == "#":
                quadrado = pygame.Rect(coluna * TILE, TOPO + linha * TILE, TILE, TILE)
                pygame.draw.rect(imagem_labirinto, COR_DAS_PAREDES, quadrado)
                # Uma linha em cada lado da parede que da para um corredor.
                lados = [
                    (0, -1, quadrado.topleft, quadrado.topright),
                    (0, 1, quadrado.bottomleft, quadrado.bottomright),
                    (-1, 0, quadrado.topleft, quadrado.bottomleft),
                    (1, 0, quadrado.topright, quadrado.bottomright),
                ]
                for lado in lados:
                    vizinha_coluna = coluna + lado[0]
                    vizinha_linha = linha + lado[1]
                    dentro = 0 <= vizinha_coluna < COLUNAS and 0 <= vizinha_linha < LINHAS
                    if dentro and mapa[vizinha_linha][vizinha_coluna] != "#":
                        pygame.draw.line(imagem_labirinto, COR_DO_CONTORNO, lado[2], lado[3], 3)
                        pygame.draw.line(contorno_paredes, cor_fraca, lado[2], lado[3], 3)
            coluna = coluna + 1
        linha = linha + 1


# --------------------------- O JOGO ------------------------------------

def texto_centrado(texto, y, cor, letra):
    desenhos = [letra.render(texto, True, PRETO), letra.render(texto, True, cor)]
    desvio = 3
    for desenho in desenhos:
        # Se o texto for comprido de mais, encolhe-o para caber no ecra.
        if desenho.get_width() > LARGURA - 40:
            nova_altura = int(desenho.get_height() * (LARGURA - 40) / desenho.get_width())
            desenho = pygame.transform.smoothscale(desenho, (LARGURA - 40, max(1, nova_altura)))
        ecra.blit(desenho, (LARGURA // 2 - desenho.get_width() // 2 + desvio, y + desvio))
        desvio = 0


def desenhar_centrado(imagem, x, y):
    ecra.blit(imagem, imagem.get_rect(center=(int(x), int(y))))


def colocar_personagens():
    # Poe o jogador e os fantasmas nos sitios de partida.
    global jogador, fantasmas, tempo_de_medo
    sitio = centro(inicio_jogador[0], inicio_jogador[1])
    jogador = {"x": sitio[0], "y": sitio[1], "coluna": inicio_jogador[0], "linha": inicio_jogador[1],
               "direcao": [0, 0], "quero": [0, 0]}
    quantos = FANTASMAS_NA_PRIMEIRA_ONDA + (onda - 1) * MAIS_FANTASMAS_POR_ONDA
    fantasmas = []
    numero = 0
    while numero < quantos:
        ninho = ninhos[numero % len(ninhos)]
        sitio = centro(ninho[0], ninho[1])
        # Acordam um de cada vez, com um segundo de intervalo.
        espera = SEGUNDOS_ATE_OS_FANTASMAS_ACORDAREM * FPS + numero * FPS
        fantasmas.append({"x": sitio[0], "y": sitio[1], "ninho": ninho, "espera": espera,
                          "onda": random.uniform(0, 6), "na_luz": False})
        numero = numero + 1
    tempo_de_medo = 0


def escolher_labirinto():
    # Primeiro todos por ordem. Depois, ao calhas, sem repetir o anterior.
    if onda <= len(LABIRINTOS):
        return onda - 1
    escolhido = random.randint(0, len(LABIRINTOS) - 1)
    if len(LABIRINTOS) > 1:
        while escolhido == indice_labirinto:
            escolhido = random.randint(0, len(LABIRINTOS) - 1)
    return escolhido


def comecar_onda():
    global indice_labirinto, bateria
    indice_labirinto = escolher_labirinto()
    carregar_labirinto(indice_labirinto)
    bateria = 100
    colocar_personagens()


def comecar_jogo():
    global onda, vidas, apanhados, mira
    onda = 1
    vidas = VIDAS
    apanhados = 0
    mira = -math.pi / 2
    comecar_onda()


def mover_jogador(teclas):
    # Como no Pac-Man: o jogador anda de centro em centro de quadrado.
    # Quando chega ao centro de um, ve se pode virar para onde queres; se
    # nao, continua em frente; se for parede, para.
    vontade = direcao_para_andar(teclas)
    if abs(vontade[0]) > abs(vontade[1]) and vontade[0] != 0:
        if vontade[0] > 0:
            jogador["quero"] = [1, 0]
        else:
            jogador["quero"] = [-1, 0]
    elif vontade[1] != 0:
        if vontade[1] > 0:
            jogador["quero"] = [0, 1]
        else:
            jogador["quero"] = [0, -1]

    direcao = jogador["direcao"]
    quero = jogador["quero"]
    alvo = centro(jogador["coluna"], jogador["linha"])
    dx = alvo[0] - jogador["x"]
    dy = alvo[1] - jogador["y"]
    falta = math.hypot(dx, dy)

    # Dar meia volta pode-se a qualquer momento.
    a_meio = 0 < jogador["x"] < LARGURA
    if falta > 0 and quero[0] == -direcao[0] and quero[1] == -direcao[1] and quero != [0, 0] and a_meio:
        jogador["coluna"] = (jogador["coluna"] - direcao[0]) % COLUNAS
        jogador["linha"] = jogador["linha"] - direcao[1]
        jogador["direcao"] = quero
        return

    if falta > VELOCIDADE_DO_JOGADOR:
        jogador["x"] = jogador["x"] + dx / falta * VELOCIDADE_DO_JOGADOR
        jogador["y"] = jogador["y"] + dy / falta * VELOCIDADE_DO_JOGADOR
        return

    # Chegou ao centro do quadrado.
    jogador["x"] = alvo[0]
    jogador["y"] = alvo[1]
    if not e_parede(jogador["coluna"] + quero[0], jogador["linha"] + quero[1]):
        jogador["direcao"] = quero
    direcao = jogador["direcao"]
    if direcao == [0, 0] or e_parede(jogador["coluna"] + direcao[0], jogador["linha"] + direcao[1]):
        jogador["direcao"] = [0, 0]
        return
    nova_coluna = jogador["coluna"] + direcao[0]
    if nova_coluna < 0 or nova_coluna >= COLUNAS:
        # Tunel: aparece do outro lado do ecra.
        nova_coluna = nova_coluna % COLUNAS
        jogador["x"] = centro(nova_coluna, 0)[0] - direcao[0] * TILE
    jogador["coluna"] = nova_coluna
    jogador["linha"] = jogador["linha"] + direcao[1]


def raio_da_lanterna():
    return 0.35 + 0.65 * bateria / 100


def esta_na_luz(x, y):
    # So conta o cone da lanterna, e nao o brilho a volta do jogador:
    # senao, um fantasma colado a ti fugia sempre e nunca te apanhava.
    distancia = math.hypot(x - jogador["x"], y - jogador["y"])
    if distancia > TAMANHO_DA_LANTERNA * raio_da_lanterna():
        return False
    angulo = math.atan2(y - jogador["y"], x - jogador["x"])
    diferenca = abs((angulo - mira + math.pi) % (2 * math.pi) - math.pi)
    return diferenca < math.radians(ABERTURA_DA_LANTERNA) / 2


def mover_fantasmas():
    # Os fantasmas nao querem saber de paredes: vem direitos a ti.
    global estado, tempo_susto, frase_do_susto, apanhados
    velocidade = VELOCIDADE_DO_FANTASMA + (onda - 1) * MAIS_VELOCIDADE_POR_ONDA
    mais_perto = 9999
    for fantasma in fantasmas:
        fantasma["na_luz"] = esta_na_luz(fantasma["x"], fantasma["y"])
        if fantasma["espera"] > 0:
            fantasma["espera"] = fantasma["espera"] - 1
            continue
        dx = jogador["x"] - fantasma["x"]
        dy = jogador["y"] - fantasma["y"]
        distancia = math.hypot(dx, dy)
        mais_perto = min(mais_perto, distancia)
        andar = velocidade
        if fantasma["na_luz"]:
            andar = andar * FANTASMA_NA_LUZ
        if tempo_de_medo > 0:
            andar = -velocidade * 0.6      # com medo, fogem
        if distancia > 1:
            fantasma["onda"] = fantasma["onda"] + 0.05
            ondular = math.sin(fantasma["onda"]) * 0.6
            fantasma["x"] = fantasma["x"] + dx / distancia * andar - dy / distancia * ondular
            fantasma["y"] = fantasma["y"] + dy / distancia * andar + dx / distancia * ondular
            fantasma["x"] = max(TILE // 2, min(LARGURA - TILE // 2, fantasma["x"]))
            fantasma["y"] = max(TOPO + TILE // 2, min(ALTURA - TILE // 2, fantasma["y"]))
        if distancia < TILE * 0.6 and estado == "jogo":
            if tempo_de_medo > 0:
                # Apanhaste-o: volta para o ninho e fica la um bocado.
                sitio = centro(fantasma["ninho"][0], fantasma["ninho"][1])
                fantasma["x"] = sitio[0]
                fantasma["y"] = sitio[1]
                fantasma["espera"] = 3 * FPS
                tocar(som_fantasma_comido)
            else:
                estado = "susto"
                tempo_susto = 110
                frase_do_susto = random.choice(FRASES_DO_SUSTO)
                tocar(som_grito)
                vibrar(1.0, 1.0, 1300)
    return mais_perto


def comer_doces():
    global apanhados, doces_que_faltam, bateria, tempo_de_medo
    coluna = int(jogador["x"] // TILE) % COLUNAS
    linha = int((jogador["y"] - TOPO) // TILE)
    if linha < 0 or linha >= LINHAS:
        return
    letra = mapa[linha][coluna]
    if letra == "." or letra == "S":
        mapa[linha][coluna] = " "
        apanhados = apanhados + 1
        doces_que_faltam = doces_que_faltam - 1
        bateria = min(100, bateria + BATERIA_POR_DOCE)
        if letra == "S":
            tempo_de_medo = SEGUNDOS_DE_SUPER_DOCE * FPS
            bateria = 100
            tocar(som_super_doce)
        else:
            tocar(som_doce)


def desenhar_jogo():
    agora = pygame.time.get_ticks()
    ecra.blit(imagem_labirinto, (0, 0))
    linha = 0
    while linha < LINHAS:
        coluna = 0
        while coluna < COLUNAS:
            letra = mapa[linha][coluna]
            if letra == ".":
                sitio = centro(coluna, linha)
                desenhar_centrado(imagem_doce, sitio[0], sitio[1])
            if letra == "S":
                sitio = centro(coluna, linha)
                desenhar_centrado(imagem_super_doce, sitio[0], sitio[1] + math.sin(agora / 200) * 3)
            coluna = coluna + 1
        linha = linha + 1

    for fantasma in fantasmas:
        imagem = imagem_fantasma
        if tempo_de_medo > 0:
            imagem = imagem_fantasma_medo
            if tempo_de_medo < 2 * FPS and tempo_de_medo // 10 % 2 == 0:
                imagem = imagem_fantasma_pisca
        # Na luz, os fantasmas tremem de medo.
        tremer = 0
        if fantasma["na_luz"] and FANTASMA_NA_LUZ < 1:
            tremer = 2
        desenhar_centrado(imagem, fantasma["x"] + random.randint(-tremer, tremer), fantasma["y"] + random.randint(-tremer, tremer))
    desenhar_centrado(imagem_jogador, jogador["x"], jogador["y"])

    # O escuro: tudo preto, menos onde ha luz. A luz soma-se ao escuro e
    # depois o ecra e MULTIPLICADO por ele. Onde o escuro e preto, o ecra
    # fica preto.
    escuro.fill(COR_DO_ESCURO)
    tamanho = raio_da_lanterna() * random.uniform(0.97, 1.03)   # a lanterna treme
    cone = pygame.transform.rotozoom(cone_de_luz, -math.degrees(mira), tamanho)
    escuro.blit(cone, cone.get_rect(center=(int(jogador["x"]), int(jogador["y"]))), special_flags=pygame.BLEND_RGB_MAX)
    escuro.blit(luz_a_volta, luz_a_volta.get_rect(center=(int(jogador["x"]), int(jogador["y"]))), special_flags=pygame.BLEND_RGB_MAX)
    linha = 0
    while linha < LINHAS:
        coluna = 0
        while coluna < COLUNAS:
            if mapa[linha][coluna] == "S":
                sitio = centro(coluna, linha)
                escuro.blit(luz_super_doce, luz_super_doce.get_rect(center=sitio), special_flags=pygame.BLEND_RGB_MAX)
            coluna = coluna + 1
        linha = linha + 1
    ecra.blit(escuro, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

    # As paredes brilham um bocadinho, e os olhos brilham muito.
    ecra.blit(contorno_paredes, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
    for fantasma in fantasmas:
        desenhar_centrado(olhos_fantasma, fantasma["x"], fantasma["y"])
    desenhar_centrado(olhos_jogador, jogador["x"], jogador["y"])

    # A barra de cima.
    pygame.draw.rect(ecra, (15, 12, 25), (0, 0, LARGURA, TOPO))
    ecra.blit(fonte.render("Onda " + str(onda), True, COR_DO_TITULO), (12, 8))
    ecra.blit(fonte_pequena.render(NOMES_DOS_LABIRINTOS[indice_labirinto % len(NOMES_DOS_LABIRINTOS)], True, CINZENTO), (110, 12))
    ecra.blit(imagem_doce, (330, 15))
    ecra.blit(fonte.render(str(apanhados), True, COR_DO_TEXTO), (360, 8))
    numero = 0
    while numero < vidas and numero < 8:
        ecra.blit(icone_vida, (440 + numero * 24, 10))
        numero = numero + 1
    pygame.draw.rect(ecra, CINZENTO, (LARGURA - 160, 11, 148, 18), 2)
    cor_bateria = AMARELO
    if bateria < 25:
        cor_bateria = VERMELHO
    pygame.draw.rect(ecra, cor_bateria, (LARGURA - 157, 14, int(142 * bateria / 100), 12))


# --------------------------- O ESTADO ----------------------------------

onda = 1
vidas = VIDAS
apanhados = 0
indice_labirinto = 0
mira = -math.pi / 2
recorde_onda = 0
recorde_doces = 0
comecar_jogo()

estado = "titulo"        # titulo, jogo, susto, onda_completa, fim
tempo_susto = 0
tempo_onda_completa = 0
frase_do_susto = ""
espera_coracao = 0


def tecla_ou_botao_para_comecar():
    global estado
    if estado == "titulo" or estado == "fim":
        comecar_jogo()
        estado = "jogo"


a_correr = True
while a_correr:

    # ------------------------- 1. EVENTOS -------------------------
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            a_correr = False
        if evento.type == pygame.JOYDEVICEADDED:
            comandos.append(pygame.joystick.Joystick(evento.device_index))
        if evento.type == pygame.JOYDEVICEREMOVED:
            ficam = []
            for comando in comandos:
                if comando.get_instance_id() != evento.instance_id:
                    ficam.append(comando)
            comandos = ficam
        if evento.type == pygame.MOUSEMOTION and not modo_rato:
            # Um toque sem querer no rato nao conta: tem de mexer a serio.
            if abs(evento.rel[0]) + abs(evento.rel[1]) > 6:
                ligar_rato(True)
        if evento.type == pygame.MOUSEBUTTONDOWN:
            tecla_ou_botao_para_comecar()
        if evento.type == pygame.JOYBUTTONDOWN:
            if evento.button == BOTAO_TROCAR:
                trocar_manipulos()
            elif not (11 <= evento.button <= 14):
                tecla_ou_botao_para_comecar()
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                a_correr = False
            if evento.key == pygame.K_m:
                ligar_rato(not modo_rato)
            if evento.key == pygame.K_t:
                trocar_manipulos()
            if evento.key == pygame.K_f or evento.key == pygame.K_F11:
                alternar_ecra_inteiro()
            if evento.key == pygame.K_SPACE or evento.key == pygame.K_RETURN or evento.key == pygame.K_r:
                tecla_ou_botao_para_comecar()

    teclas = pygame.key.get_pressed()

    # ------------------------- 2. LOGICA --------------------------
    if estado == "jogo":
        mover_jogador(teclas)
        comer_doces()

        # A lanterna aponta para onde dizes, e roda devagarinho ate la.
        apontar = direcao_para_apontar(teclas)
        if modo_rato and apontar == [0.0, 0.0]:
            rato = pygame.mouse.get_pos()
            if math.hypot(rato[0] - jogador["x"], rato[1] - jogador["y"]) > 5:
                apontar = [rato[0] - jogador["x"], rato[1] - jogador["y"]]
        if apontar != [0.0, 0.0]:
            desejado = math.atan2(apontar[1], apontar[0])
            diferenca = (desejado - mira + math.pi) % (2 * math.pi) - math.pi
            mira = mira + diferenca * 0.3

        bateria = max(0, bateria - BATERIA_GASTA_POR_SEGUNDO / FPS)
        if tempo_de_medo > 0:
            tempo_de_medo = tempo_de_medo - 1

        mais_perto = mover_fantasmas()

        # O coracao bate mais depressa quando um fantasma esta perto.
        espera_coracao = espera_coracao - 1
        if mais_perto < 300 and espera_coracao <= 0 and tempo_de_medo == 0:
            tocar(som_coracao)
            vibrar(0.4, 0.0, 100)
            espera_coracao = int(max(18, mais_perto / 4))

        if doces_que_faltam <= 0 and estado == "jogo":
            estado = "onda_completa"
            tempo_onda_completa = int(2.5 * FPS)
            tocar(som_onda)

    elif estado == "susto":
        tempo_susto = tempo_susto - 1
        if tempo_susto <= 0:
            vidas = vidas - 1
            if vidas > 0:
                colocar_personagens()
                estado = "jogo"
            else:
                recorde_onda = max(recorde_onda, onda)
                recorde_doces = max(recorde_doces, apanhados)
                estado = "fim"

    elif estado == "onda_completa":
        tempo_onda_completa = tempo_onda_completa - 1
        if tempo_onda_completa <= 0:
            onda = onda + 1
            if VIDA_EXTRA_A_CADA > 0 and (onda - 1) % VIDA_EXTRA_A_CADA == 0:
                vidas = vidas + 1
            comecar_onda()
            estado = "jogo"

    # ------------------------ 3. DESENHAR -------------------------
    agora = pygame.time.get_ticks()

    if estado == "titulo":
        ecra.fill(COR_DO_ESCURO)
        sobe = math.sin(agora / 400) * 12
        desenhar_centrado(fantasma_do_titulo, LARGURA // 2, 290 + sobe)
        texto_centrado(TITULO, 60, COR_DO_TITULO, fonte_grande)
        texto_centrado(SUBTITULO, 140, COR_DO_TEXTO, fonte)
        if len(comandos) > 0:
            if manipulos_trocados:
                texto_centrado("Manípulo esquerdo: andar  ·  Manípulo direito: lanterna", 440, CINZENTO, fonte)
            else:
                texto_centrado("Manípulo direito: andar  ·  Manípulo esquerdo: lanterna", 440, CINZENTO, fonte)
            frase = "Carrega num botão para começar"
        elif modo_rato:
            texto_centrado("W A S D ou setas: andar  ·  Rato: lanterna", 440, CINZENTO, fonte)
            frase = "Clica ou carrega em Espaço para começar"
        else:
            if manipulos_trocados:
                texto_centrado("W A S D: andar  ·  Setas: lanterna", 440, CINZENTO, fonte)
            else:
                texto_centrado("Setas: andar  ·  W A S D: lanterna", 440, CINZENTO, fonte)
            frase = "Espaço para começar"
        if recorde_onda > 0:
            texto_centrado("Recorde: onda " + str(recorde_onda), 480, AMARELO, fonte)
        ecra.blit(fonte_pequena.render("F: ecrã inteiro  ·  M: rato  ·  T / Triângulo: trocar", True, CINZENTO), (LARGURA - 470, ALTURA - 30))
        if agora // 500 % 2 == 0:
            texto_centrado(frase, 530, COR_DO_TEXTO, fonte)

    if estado == "jogo" or estado == "onda_completa":
        desenhar_jogo()
        if estado == "jogo" and len(fantasmas) > 0 and fantasmas[0]["espera"] > 0 and fantasmas[0]["espera"] < SEGUNDOS_ATE_OS_FANTASMAS_ACORDAREM * FPS:
            segundos = fantasmas[0]["espera"] // FPS + 1
            texto_centrado("Os fantasmas acordam em " + str(segundos) + "...", ALTURA - 50, CINZENTO, fonte)

    if estado == "onda_completa":
        faixa = pygame.Surface((LARGURA, 200), pygame.SRCALPHA)
        faixa.fill((0, 0, 0, 180))
        ecra.blit(faixa, (0, 200))
        texto_centrado("Onda " + str(onda) + " completa!", 220, COR_DO_TITULO, fonte_grande)
        texto_centrado(MENSAGEM_DE_ONDA_COMPLETA, 310, COR_DO_TEXTO, fonte)
        texto_centrado("Vem aí mais um fantasma...", 350, CINZENTO, fonte)

    if estado == "susto":
        # Pisca entre vermelho e preto, e o fantasma gigante treme.
        if tempo_susto % 8 < 4 and tempo_susto > 70:
            ecra.fill(VERMELHO)
        else:
            ecra.fill(PRETO)
        forca = tempo_susto // 6
        desenhar_centrado(fantasma_gigante, LARGURA // 2 + random.randint(-forca, forca), ALTURA // 2 - 40 + random.randint(-forca, forca))
        texto_centrado(frase_do_susto, ALTURA - 90, BRANCO, fonte_grande)

    if estado == "fim":
        ecra.fill(PRETO)
        desenhar_centrado(fantasma_do_titulo, LARGURA // 2, 150)
        texto_centrado(frase_do_susto, 260, VERMELHO, fonte_grande)
        texto_centrado("Chegaste à onda " + str(onda) + " e apanhaste " + str(apanhados) + " doces.", 360, COR_DO_TEXTO, fonte)
        texto_centrado("Recorde: onda " + str(recorde_onda) + "  ·  " + str(recorde_doces) + " doces", 405, AMARELO, fonte)
        texto_centrado("Espaço (ou um botão do comando) para jogar outra vez", 480, COR_DO_TEXTO, fonte)

    # Com o rato a apontar, a seta do rato da lugar a uma mira.
    mostrar_mira = modo_rato and (estado == "jogo" or estado == "onda_completa")
    pygame.mouse.set_visible(not mostrar_mira)
    if mostrar_mira:
        rato = pygame.mouse.get_pos()
        pygame.draw.circle(ecra, COR_DO_CONTORNO, rato, 10, 2)
        pygame.draw.line(ecra, COR_DO_CONTORNO, (rato[0] - 15, rato[1]), (rato[0] - 5, rato[1]), 2)
        pygame.draw.line(ecra, COR_DO_CONTORNO, (rato[0] + 5, rato[1]), (rato[0] + 15, rato[1]), 2)
        pygame.draw.line(ecra, COR_DO_CONTORNO, (rato[0], rato[1] - 15), (rato[0], rato[1] - 5), 2)
        pygame.draw.line(ecra, COR_DO_CONTORNO, (rato[0], rato[1] + 5), (rato[0], rato[1] + 15), 2)

    # O aviso (rato, manipulos trocados) aparece por cima de tudo, uns segundos.
    if tempo_aviso > 0:
        tempo_aviso = tempo_aviso - 1
        texto_centrado(aviso, ALTURA // 2 + 60, AMARELO, fonte)

    # ------------------------- 4. MOSTRAR -------------------------
    pygame.display.flip()

    # ------------------------- 5. ESPERAR -------------------------
    clock.tick(FPS)

pygame.quit()
