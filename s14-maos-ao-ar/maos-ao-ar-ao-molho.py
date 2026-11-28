# =====================================================================
# S14 — MAOS AO AR! TODOS AO MOLHO
#
# O Maos ao Ar para 2, 3 ou 4 jogadores, TODOS NO MESMO ECRA e todos com
# a mesma camara. Cada jogador tem o seu bocado da imagem da camara, e e
# so ai que a mao dele manda:
#
#   2 jogadores      3 ou 4 jogadores
#   +-----+-----+    +-----+-----+
#   |     |     |    | J1  | J2  |      Os de cima ficam de pe, atras.
#   | J1  | J2  |    +-----+-----+      Os de baixo ficam a frente, de
#   |     |     |    | J3  | J4  |      joelhos ou sentados.
#   +-----+-----+    +-----+-----+
#
# O bocado de cada um aparece no canto do ecra que lhe corresponde: o teu
# canto da camara e o teu canto do ecra.
#
# Os gestos sao os de sempre, mas dentro do teu bocado:
#   andar      mostrar a mao                 virar     mao para o outro lado
#   parar      tirar a mao                   correr    mao bem alto
#   saltar     fechar o punho                disparar  apontar o indicador
#
# E UM TORNEIO: seis rondas de tres tipos, e quem fizer mais pontos ganha.
#   CORRIDA           o primeiro a chegar a porta. As moedas dao turbo.
#   CACA AS MOEDAS    quem tiver mais moedas quando o tempo acabar.
#   BATALHA           tiros e pisadelas tiram coracoes. O ultimo de pe.
# Em todas elas os jogadores RESSALTAM uns nos outros, um tiro deixa o
# outro tonto, e saltar para cima de alguem tambem.
#
# Cada jogador escolhe a sua personagem SO COM A MAO: mao para os lados
# muda, punho fechado escolhe, apontar o indicador volta atras.
#
#   2, 3, 4   quantos jogam (no titulo; ou clica)   P   pausa
#   C         a camara seguinte              T   jogar so com o teclado
#   F, F11    janela / ecra inteiro          Esc voltar ao titulo / sair
#   Enter     comecar ja com quem esta pronto
#   N         atalho do professor: acaba a ronda
#
# Este ficheiro PRECISA do maos-ao-ar.py, que esta ao lado dele: e de la
# que vem o motor do jogo (a fisica, os inimigos, os desenhos do mapa, os
# sons) e tambem os numeros (GRAVIDADE, FORCA_SALTO, VEL_ANDAR...). Quem
# mudar esses numeros la, muda-os aqui tambem.
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
# ---------------------------------------------------------------------
TITULO = "MÃOS AO AR!"
SUBTITULO = "Todos ao molho: 2, 3 ou 4 jogadores, uma só câmara"


# ---------------------------------------------------------------------
# 2. A CAMARA E OS GESTOS
# As linhas sao medidas DENTRO do bocado de cada jogador, de 0.0
# (esquerda / cima) a 1.0 (direita / baixo).
# ---------------------------------------------------------------------
JOGADORES = 4            # quantos jogam quando o jogo abre: 2, 3 ou 4
CAMARA = 0               # 0 e a primeira camara. Se abrir a errada, tenta 1
ZONA_ESQUERDA = 0.38     # mao a esquerda desta linha: vira-se para la
ZONA_DIREITA = 0.62      # mao a direita desta linha: vira-se para a direita
LINHA_CORRER = 0.36      # mao acima desta linha: corre
TEMPO_SEM_MAO = 0.35     # segundos sem ver a mao ate a personagem parar
ECRA_INTEIRO = True


# ---------------------------------------------------------------------
# 3. AS REGRAS DO TORNEIO
# ---------------------------------------------------------------------
PONTOS_POR_LUGAR = [5, 3, 2, 1]   # pontos do 1.o, do 2.o, do 3.o e do 4.o
FINAL_A_DOBRAR = True             # a ultima ronda vale o dobro

TEMPO_CORRIDA = 120               # segundos, no maximo
TEMPO_DEPOIS_DO_PRIMEIRO = 20     # segundos que os outros tem para chegar
TEMPO_MOEDAS = 60
TEMPO_BATALHA = 90
CHUVA_DE_MOEDAS = 15              # nos ultimos segundos chovem moedas

VIDAS_BATALHA = 4                 # coracoes de cada um numa batalha
MOEDAS_PERDIDAS = 3               # moedas que caem quando se leva uma pancada
TURBO_DA_MOEDA = 1.4              # numa corrida, uma moeda da velocidade...
TEMPO_DO_TURBO = 40               # ...durante estes frames (60 = um segundo)

# O molho: o que acontece quando os jogadores se tocam.
FORCA_DO_CHOQUE = 8.0             # o empurrao quando dois chocam de lado
SALTO_DO_CHOQUE = 5.0             # e o saltinho que dao
FORCA_DO_TIRO = 10.0              # o empurrao de um tiro
TEMPO_TONTO = 40                  # frames sem se mexer, depois de uma pancada


# ---------------------------------------------------------------------
# 4. OS JOGADORES E AS PERSONAGENS
# ---------------------------------------------------------------------
# A cor de cada jogador: a do canto dele e a da seta por cima da personagem.
CORES_DOS_JOGADORES = [
    (235, 80, 80),      # J1 vermelho
    (80, 160, 245),     # J2 azul
    (95, 210, 115),     # J3 verde
    (250, 205, 60),     # J4 amarelo
]

# Todas as personagens tem o mesmo tamanho. O que muda e o jeito:
#   velocidade   multiplica a velocidade a andar e a correr (1 e o normal)
#   salto        multiplica a forca do salto
#   gravidade    multiplica a gravidade (menos de 1: cai devagar)
#   recarga      frames entre dois tiros (menos e mais depressa)
#   vel_tiro     a velocidade dos tiros
#   peso         quem pesa mais empurra mais e e menos empurrado
#   tonto        multiplica o tempo que fica tonto (menos e melhor)
#   feitio       o desenho: "robot", "gato", "sapo", "fantasma", "pinguim",
#                "dragao", "ninja" ou "alien"
#   cor, cor2    a cor do corpo e a cor escura (pernas, contorno)
#   tiro         a cor dos tiros
# Cuidado: com menos de 0.94 de velocidade ou de salto ha buracos das
# corridas que deixam de se conseguir saltar.
PERSONAGENS = [
    {"nome": "Faísca", "talento": "Faz tudo bem", "feitio": "robot",
     "cor": (255, 220, 40), "cor2": (40, 40, 50), "tiro": (255, 240, 120),
     "velocidade": 1.0, "salto": 1.0, "gravidade": 1.0, "recarga": 18,
     "vel_tiro": 11, "peso": 1.0, "tonto": 1.0},
    {"nome": "Bigodes", "talento": "O mais rápido", "feitio": "gato",
     "cor": (245, 150, 60), "cor2": (120, 60, 20), "tiro": (255, 200, 140),
     "velocidade": 1.12, "salto": 0.97, "gravidade": 1.0, "recarga": 20,
     "vel_tiro": 11, "peso": 0.9, "tonto": 1.0},
    {"nome": "Coaxa", "talento": "Salta mais alto", "feitio": "sapo",
     "cor": (90, 200, 100), "cor2": (30, 100, 50), "tiro": (190, 255, 150),
     "velocidade": 0.95, "salto": 1.1, "gravidade": 1.0, "recarga": 18,
     "vel_tiro": 11, "peso": 1.0, "tonto": 1.0},
    {"nome": "Buu", "talento": "Cai devagarinho", "feitio": "fantasma",
     "cor": (235, 235, 250), "cor2": (120, 120, 170), "tiro": (200, 200, 255),
     "velocidade": 1.0, "salto": 0.94, "gravidade": 0.8, "recarga": 18,
     "vel_tiro": 11, "peso": 0.8, "tonto": 1.0},
    {"nome": "Pingo", "talento": "Dispara sem parar", "feitio": "pinguim",
     "cor": (60, 70, 110), "cor2": (25, 30, 55), "tiro": (150, 220, 255),
     "velocidade": 0.96, "salto": 1.0, "gravidade": 1.0, "recarga": 10,
     "vel_tiro": 11, "peso": 1.0, "tonto": 1.0},
    {"nome": "Brasa", "talento": "Tiros que vão longe", "feitio": "dragao",
     "cor": (230, 80, 70), "cor2": (120, 30, 40), "tiro": (255, 150, 60),
     "velocidade": 1.0, "salto": 0.97, "gravidade": 1.0, "recarga": 20,
     "vel_tiro": 16, "peso": 1.0, "tonto": 1.0},
    {"nome": "Sombra", "talento": "Nunca fica tonto muito tempo", "feitio": "ninja",
     "cor": (70, 60, 90), "cor2": (200, 50, 70), "tiro": (220, 220, 230),
     "velocidade": 1.05, "salto": 1.0, "gravidade": 1.0, "recarga": 20,
     "vel_tiro": 11, "peso": 0.9, "tonto": 0.4},
    {"nome": "Zorg", "talento": "Pesado: empurra toda a gente", "feitio": "alien",
     "cor": (170, 110, 230), "cor2": (80, 40, 130), "tiro": (150, 255, 220),
     "velocidade": 0.95, "salto": 1.0, "gravidade": 1.0, "recarga": 18,
     "vel_tiro": 11, "peso": 1.8, "tonto": 1.0},
]


# ---------------------------------------------------------------------
# 5. AS RONDAS
# Os mapas desenham-se com as letras do maos-ao-ar.py (a legenda esta la,
# por cima de NIVEIS), e mais estas:
#   1 2 3 4   onde comeca cada jogador
# Cada ronda tem:
#   modo    "corrida", "moedas" ou "batalha"
#   mundo   a posicao do mundo na lista MUNDOS do maos-ao-ar.py (0 e o Prado)
# Uma corrida tem um mapa comprido com uma saida (F). As outras duas
# passam-se num mapa do tamanho do ecra: 20 letras de largura.
# Os cantos de baixo do ecra ficam tapados pelas camaras: deixa la chao.
#
# Para os niveis darem luta ha sempre DOIS CAMINHOS: um rapido e
# arriscado (uma ponte podre que cai para quem vem atras, uma mola onde
# so cabe um) e outro lento e seguro.
# ---------------------------------------------------------------------
RONDAS = [
    {"nome": "A corrida do Prado", "modo": "corrida", "mundo": 0,
     "mapa": [
        "....................................................................................................",
        "....................................................................................................",
        "....................................................................................................",
        "....................................................................................................",
        "...................................o.o.o.o.o.o......................................................",
        "..................................============......................................................",
        "....................................................o.o.o.........................o.................",
        "................oo....oo..........................=======..........oo.....ooo.............oo........",
        "......................................B...................................###........B..............",
        ".1234...o.o.o...##..........a...M.....B...^.....##...........a..a.......#####.....^..Boo.....ooo.F..",
        "######################..###########################%%%%%%##########..#####################..########",
        "######################..###########################~~~~~~##########..#####################..########",
    ]},
    {"nome": "A mina das moedas", "modo": "moedas", "mundo": 1,
     "mapa": [
        "....................",
        "....................",
        "....................",
        ".........m..........",
        "....................",
        ".........oo.........",
        ".......======.......",
        "...o.o........o.o...",
        "..=====......=====..",
        "M1.3....^..^....4.2M",
        "####################",
        "####################",
    ]},
    {"nome": "O ringue", "modo": "batalha", "mundo": 0,
     "mapa": [
        "....................",
        "....................",
        "....................",
        "....................",
        "....................",
        "....................",
        "........====........",
        "....................",
        "...===........===...",
        "M1.3...B....B...4.2M",
        "####################",
        "####################",
    ]},
    {"nome": "Fuga do Vulcão", "modo": "corrida", "mundo": 2,
     "mapa": [
        "..............................................................................................................",
        "..............................................................................................................",
        "..............................................................................................................",
        "..............................................................................................................",
        "....................................................oo........................................................",
        "....................................................##........................................................",
        "............m.......................................##........................m...............................",
        ".........oo.............oo..t.......o.o.o...........##.............................o.o.o......................",
        "........................#######....=======..........##......B.....................======............oo........",
        ".1234.oo.........^....#########...............s...M.##..ooo.B...e......o...................^...a....##.ooo.F..",
        "#########~~#######################%%%%%%%%##########################~~###~~#######%%%%%%######################",
        "##################################~~~~~~~~########################################~~~~~~######################",
    ]},
    {"nome": "O cofre da Fábrica", "modo": "moedas", "mundo": 3,
     "mapa": [
        "....................",
        "....................",
        "....................",
        "....................",
        "....................",
        "......o......o......",
        ".....===....===.....",
        "..o.o...o..o...o.o..",
        ".%%%%...====...%%%%.",
        ".1.3......t.....4.2.",
        "#####..######..#####",
        "#####..######..#####",
    ]},
    {"nome": "A arena do Vulcão", "modo": "batalha", "mundo": 2,
     "mapa": [
        "....................",
        "....................",
        "....................",
        "....................",
        "....................",
        "....................",
        "......===..===......",
        "....................",
        ".====...%%%%...====.",
        ".1.3.....e......4.2.",
        "######~~####~~######",
        "####################",
    ]},
]

MODOS = {
    "corrida": {"nome": "CORRIDA",
                "regra": "O primeiro a chegar à porta ganha. As moedas dão turbo!"},
    "moedas": {"nome": "CAÇA ÀS MOEDAS",
               "regra": "Ganha quem tiver mais moedas. Uma pancada faz cair moedas!"},
    "batalha": {"nome": "BATALHA",
                "regra": "Tiros e pisadelas tiram corações. Ganha o último de pé!"},
}


# #####################################################################
# #####################################################################
# ##                                                                 ##
# ##        NÃO MEXER: daqui para baixo é o motor do jogo            ##
# ##                                                                 ##
# #####################################################################
# #####################################################################


# =====================================================================
# A. IR BUSCAR O MOTOR AO maos-ao-ar.py
# O nome do ficheiro tem hifenes, por isso nao da para fazer "import":
# carrega-se pelo caminho. Ao carregar, ele trata das bibliotecas que
# faltarem (pygame-ce, mediapipe), tal como quando corre sozinho.
# Daqui para a frente, tudo o que comeca por "b." vem de la.
# =====================================================================
import importlib.util
import os
import sys

PASTA = os.path.dirname(os.path.abspath(__file__))


def carregar_jogo_base():
    caminho = os.path.join(PASTA, "maos-ao-ar.py")
    if not os.path.isfile(caminho):
        print("Falta o maos-ao-ar.py: tem de estar na mesma pasta que este ficheiro.")
        sys.exit(1)
    receita = importlib.util.spec_from_file_location("maos_ao_ar", caminho)
    modulo = importlib.util.module_from_spec(receita)
    sys.modules["maos_ao_ar"] = modulo
    receita.loader.exec_module(modulo)
    return modulo


b = carregar_jogo_base()

import math
import random
import threading
import time

import pygame

LARGURA = b.LARGURA
ALTURA = b.ALTURA
FPS = b.FPS
TILE = b.TILE
LINHAS = b.LINHAS
BRANCO = b.BRANCO
PRETO = b.PRETO
CINZA = b.CINZA
AMARELO = b.AMARELO
VERMELHO = b.VERMELHO
VERDE = b.VERDE
AZUL = b.AZUL
LARANJA = b.LARANJA
LARGURA_J = b.LARGURA_HEROI      # todas as personagens tem este tamanho
ALTURA_J = b.ALTURA_HEROI

nivel = b.nivel                  # o nivel que esta a ser jogado (o do motor)
escrever = b.escrever
tocar = b.tocar
particulas = b.particulas
sinal = b.sinal

# O teclado, para quando nao ha camara (ou para dar uma ajuda): uma linha
# por jogador.
TECLADO = [
    {"esq": pygame.K_LEFT, "dir": pygame.K_RIGHT, "salto": pygame.K_UP, "parar": pygame.K_DOWN,
     "correr": pygame.K_COMMA, "tiro": pygame.K_PERIOD},
    {"esq": pygame.K_a, "dir": pygame.K_d, "salto": pygame.K_w, "parar": pygame.K_s,
     "correr": pygame.K_q, "tiro": pygame.K_e},
    {"esq": pygame.K_j, "dir": pygame.K_l, "salto": pygame.K_i, "parar": pygame.K_k,
     "correr": pygame.K_u, "tiro": pygame.K_o},
    {"esq": pygame.K_KP4, "dir": pygame.K_KP6, "salto": pygame.K_KP8, "parar": pygame.K_KP5,
     "correr": pygame.K_KP7, "tiro": pygame.K_KP9},
]
TEXTO_DO_TECLADO = [
    "J1: setas, vírgula corre, ponto dispara",
    "J2: A D W S, Q corre, E dispara",
    "J3: J L I K, U corre, O dispara",
    "J4: teclado numérico 4 6 8 5, 7 corre, 9 dispara",
]


# =====================================================================
# B. A CAMARA E AS MAOS
# Como no maos-ao-ar.py, a camara e lida noutro fio. A diferenca e que
# aqui se procuram ate 4 maos, e cada uma e entregue ao jogador em cujo
# bocado da imagem ela esta.
# =====================================================================
def zonas_para(quantos):
    # O bocado da imagem de cada jogador: (x0, y0, x1, y1), de 0 a 1.
    if quantos == 2:
        return [(0.0, 0.0, 0.5, 1.0), (0.5, 0.0, 1.0, 1.0)]
    quatro = [(0.0, 0.0, 0.5, 0.5), (0.5, 0.0, 1.0, 0.5),
              (0.0, 0.5, 0.5, 1.0), (0.5, 0.5, 1.0, 1.0)]
    return quatro[:quantos]


def canto_de(indice, quantos):
    # Em que canto do ecra fica o jogador: (0 esquerda / 1 direita, 0 cima / 1 baixo)
    if quantos == 2:
        return (indice, 0)
    return (indice % 2, indice // 2)


def nova_mao():
    return {
        "visivel": False,
        "x": 0.5, "y": 0.5,      # centro da palma DENTRO do bocado, de 0 a 1
        "forma": "nenhuma",      # "aberta", "punho", "apontar" ou "nenhuma"
        "saltos": 0,             # quantas vezes o punho se fechou
        "pontos": [],            # os 21 pontos, na imagem inteira
        "crua": "nenhuma", "repetidas": 0, "vista": 0.0,
    }


olho = {
    "ligada": False, "erro": "", "indice": CAMARA,
    "zonas": [], "maos": [],
    "saltos": 0,             # punhos fechados por todos, ao todo
    "imagem": None, "tamanho": (0, 0), "numero": 0,
}
tranca = threading.Lock()
camara = {"captura": None, "detetor": None, "fio": None}


def definir_zonas(quantos):
    tranca.acquire()
    olho["zonas"] = zonas_para(quantos)
    olho["maos"] = []
    for i in range(quantos):
        olho["maos"].append(nova_mao())
    tranca.release()


def ciclo_da_camara():
    captura = camara["captura"]
    detetor = camara["detetor"]
    ultimo_ms = 0
    falhas = 0
    try:
        while olho["ligada"]:
            ok, imagem = captura.read()
            if not ok or imagem is None:
                falhas += 1
                if falhas > 60:
                    olho["erro"] = "A câmara deixou de responder."
                    break
                time.sleep(0.02)
                continue
            falhas = 0

            imagem = b.cv2.flip(imagem, 1)      # em espelho
            altura = int(imagem.shape[0] * 640 / imagem.shape[1])
            imagem = b.cv2.resize(imagem, (640, altura))
            rgb = b.numpy.ascontiguousarray(b.cv2.cvtColor(imagem, b.cv2.COLOR_BGR2RGB))

            agora_ms = int(time.monotonic() * 1000)
            if agora_ms <= ultimo_ms:
                agora_ms = ultimo_ms + 1
            ultimo_ms = agora_ms
            imagem_mp = b.mediapipe.Image(image_format=b.mediapipe.ImageFormat.SRGB, data=rgb)
            resultado = detetor.detect_for_video(imagem_mp, agora_ms)

            encontradas = []
            for marcos in resultado.hand_landmarks:
                pontos = []
                for ponto in marcos:
                    pontos.append((ponto.x, ponto.y))
                if len(pontos) == 21:
                    encontradas.append(pontos)

            agora = time.monotonic()
            tranca.acquire()
            zonas = olho["zonas"]
            # A quem pertence cada mao: ao dono do bocado onde ela esta.
            # Se houver duas no mesmo bocado, conta a primeira.
            de_quem = [None] * len(zonas)
            for pontos in encontradas:
                x, y = b.centro_da_palma(pontos)
                for i in range(len(zonas)):
                    x0, y0, x1, y1 = zonas[i]
                    if x0 <= x < x1 and y0 <= y < y1:
                        if de_quem[i] is None:
                            de_quem[i] = (pontos, (x - x0) / (x1 - x0), (y - y0) / (y1 - y0))
                        break
            for i in range(len(zonas)):
                m = olho["maos"][i]
                if de_quem[i] is not None:
                    pontos, x, y = de_quem[i]
                    m["vista"] = agora
                    if m["visivel"]:
                        m["x"] = m["x"] * 0.5 + x * 0.5     # para nao tremer
                        m["y"] = m["y"] * 0.5 + y * 0.5
                    else:
                        m["x"] = x
                        m["y"] = y
                    m["visivel"] = True
                    m["pontos"] = pontos
                    # Uma forma so conta quando aparece em 2 imagens seguidas.
                    crua = b.classificar_mao(pontos, 640 / altura)
                    if crua == m["crua"]:
                        m["repetidas"] += 1
                    else:
                        m["repetidas"] = 1
                    m["crua"] = crua
                    if m["repetidas"] >= 2 and crua != "outra" and crua != m["forma"]:
                        if crua == "punho":
                            m["saltos"] += 1
                            olho["saltos"] += 1
                        m["forma"] = crua
                else:
                    m["pontos"] = []
                    if agora - m["vista"] > TEMPO_SEM_MAO:
                        m["visivel"] = False
                        m["forma"] = "nenhuma"
                        m["crua"] = "nenhuma"
            olho["imagem"] = rgb.tobytes()
            olho["tamanho"] = (640, altura)
            olho["numero"] += 1
            tranca.release()
    except Exception as erro:
        olho["erro"] = "Erro na câmara: " + str(erro)
        if tranca.locked():
            tranca.release()
    olho["ligada"] = False


def ligar_camara(indice, espera_no_mac):
    # Igual a do maos-ao-ar.py, mas a procura de 4 maos em vez de 1.
    desligar_camara()
    olho["indice"] = indice
    olho["erro"] = ""
    if not b.HA_BIBLIOTECAS_DA_CAMARA:
        olho["erro"] = "Falta o mediapipe ou o opencv."
        return False
    modelo = b.obter_modelo()
    if modelo is None:
        olho["erro"] = "Falta o modelo das mãos (sem internet?)."
        return False
    guardado = b.calar_avisos()
    try:
        tentativas = 1
        if sys.platform == "darwin" and espera_no_mac:
            tentativas = 12
        captura = None
        for tentativa in range(tentativas):
            if os.name == "nt":
                captura = b.cv2.VideoCapture(indice, b.cv2.CAP_DSHOW)
            else:
                captura = b.cv2.VideoCapture(indice)
            if captura.isOpened():
                break
            captura.release()
            captura = None
            if tentativa + 1 < tentativas:
                pygame.event.pump()
                time.sleep(1.0)
        if captura is None:
            b.repor_avisos(guardado)
            olho["erro"] = "Não há câmara " + str(indice) + " (ou não há permissão)."
            return False
        captura.set(b.cv2.CAP_PROP_FRAME_WIDTH, 640)
        captura.set(b.cv2.CAP_PROP_FRAME_HEIGHT, 480)
        captura.set(b.cv2.CAP_PROP_BUFFERSIZE, 1)

        ficheiro = open(modelo, "rb")
        dados = ficheiro.read()
        ficheiro.close()
        opcoes = b.mp_visao.HandLandmarkerOptions(
            base_options=b.mp_tarefas.BaseOptions(model_asset_buffer=dados),
            running_mode=b.mp_visao.RunningMode.VIDEO,
            num_hands=4,
            # Com quatro pessoas, as maos ficam mais longe e mais pequenas:
            # pede-se um bocadinho menos de certeza.
            min_hand_detection_confidence=0.4,
            min_hand_presence_confidence=0.4,
            min_tracking_confidence=0.4,
        )
        detetor = b.mp_visao.HandLandmarker.create_from_options(opcoes)
        preta = b.mediapipe.Image(image_format=b.mediapipe.ImageFormat.SRGB,
                                  data=b.numpy.zeros((480, 640, 3), b.numpy.uint8))
        detetor.detect_for_video(preta, 0)
    except Exception as erro:
        b.repor_avisos(guardado)
        olho["erro"] = "A câmara não arrancou: " + str(erro)
        return False
    b.repor_avisos(guardado)

    camara["captura"] = captura
    camara["detetor"] = detetor
    olho["ligada"] = True
    olho["numero"] = 0
    camara["fio"] = threading.Thread(target=ciclo_da_camara, daemon=True)
    camara["fio"].start()
    return True


def desligar_camara():
    olho["ligada"] = False
    if camara["fio"] is not None:
        camara["fio"].join(2.0)
        camara["fio"] = None
    if camara["captura"] is not None:
        camara["captura"].release()
        camara["captura"] = None
    if camara["detetor"] is not None:
        try:
            camara["detetor"].close()
        except Exception:
            pass
        camara["detetor"] = None
    olho["imagem"] = None
    for m in olho["maos"]:
        m["visivel"] = False


def ler_olho():
    # Uma copia do que o fio da camara viu, tirada de uma vez so.
    tranca.acquire()
    copia = dict(olho)
    copia["maos"] = []
    for m in olho["maos"]:
        copia["maos"].append(dict(m))
    tranca.release()
    return copia


# =====================================================================
# C. OS JOGADORES E A RONDA
# =====================================================================
jogadores = []       # um dicionario por jogador (ver novo_jogador)
jogo = {
    "fase": "titulo",    # titulo, escolha, contagem, jogar, pausa, ronda_fim, podio
    "quantos": JOGADORES,
    "modo_teclado": False,
    "saltos_vistos": 0,
    "arranque": 0,
    "espera": 0,
    "aviso": "", "aviso_tempo": 0,
}
ronda = {
    "indice": 0, "modo": "corrida", "tempo": 0, "contagem": 0,
    "chegadas": 0, "eliminados": 0,
    "mensagem": "", "mensagem_tempo": 0,
    "tabela": [],
}


def novo_jogador(numero):
    return {
        "numero": numero,                # 1, 2, 3 ou 4
        "personagem": (numero - 1) % len(PERSONAGENS),
        "entrou": False,                 # ja mostrou a mao no ecra de escolha
        "pronto": False,                 # ja escolheu a personagem
        "joga": False,                   # entra neste torneio
        "pontos": 0,
        "saltos_vistos": 0, "lado_antes": 0, "espera_troca": 0,
        "mao_corre": False,
        # o corpo (preenchido por por_no_sitio)
        "x": 0.0, "y": 0.0, "l": LARGURA_J, "a": ALTURA_J,
        "vx": 0.0, "vy": 0.0, "no_chao": False, "virado": 1,
        "chegou": 0, "fora": 0, "vidas": 0, "moedas": 0,
        "tonto": 0, "invencivel": 0, "congelado": 0, "recuo": 0, "passo": 0.0,
        "anda": False, "corre": False,
    }


def definir_jogadores(quantos):
    jogo["quantos"] = quantos
    jogadores.clear()
    for numero in range(1, quantos + 1):
        jogadores.append(novo_jogador(numero))
    definir_zonas(quantos)


def participantes():
    lista = []
    for p in jogadores:
        if p["joga"]:
            lista.append(p)
    return lista


def em_campo():
    # Os que ainda estao a jogar esta ronda: nem chegaram nem foram eliminados.
    lista = []
    for p in jogadores:
        if p["joga"] and p["chegou"] == 0 and p["fora"] == 0:
            lista.append(p)
    return lista


def personagem_de(p):
    return PERSONAGENS[p["personagem"] % len(PERSONAGENS)]


def cor_de(p):
    return CORES_DOS_JOGADORES[(p["numero"] - 1) % len(CORES_DOS_JOGADORES)]


def nome_de(p):
    return "J" + str(p["numero"]) + " " + personagem_de(p)["nome"]


def ordinal(numero):
    return str(numero) + ".º"


def quantas(numero, uma, varias):
    # "1 moeda", mas "2 moedas".
    if numero == 1:
        return "1 " + uma
    return str(numero) + " " + varias


def dizer(texto):
    # A frase grande que aparece no meio do ecra por uns instantes.
    ronda["mensagem"] = texto
    ronda["mensagem_tempo"] = 120


def por_no_sitio(p, x, y):
    p["x"] = float(x)
    p["y"] = float(y)
    p["vx"] = 0.0
    p["vy"] = 0.0
    p["no_chao"] = False
    p["coiote"] = 0
    p["salto_pedido"] = 0
    p["recarga"] = 0
    p["recuo"] = 0
    p["empurrao"] = 0.0      # a velocidade que os choques lhe dao
    p["choque"] = 0          # frames ate poder chocar outra vez
    p["tonto"] = 0
    p["turbo"] = 0
    p["seguros"] = [(float(x), float(y))]    # os ultimos sitios com chao firme


def sitios_de_partida(dados):
    # Procura os algarismos 1 a 4 no mapa.
    mapa = dados["mapa"]
    falta = LINHAS - len(mapa)
    sitios = {}
    for linha in range(len(mapa)):
        texto = mapa[linha]
        for coluna in range(len(texto)):
            if texto[coluna] in "1234":
                sitios[int(texto[coluna])] = (coluna * TILE + 9,
                                              (linha + falta) * TILE + TILE - ALTURA_J)
    return sitios


def comecar_ronda(indice):
    dados = RONDAS[indice]
    # O motor carrega o mapa. Os algarismos dos jogadores, para ele, sao ar.
    b.NIVEIS = RONDAS
    b.carregar_nivel(indice)
    mundo = max(0, min(dados.get("mundo", 0), len(b.MUNDOS) - 1))
    nivel["mundo"] = b.MUNDOS[mundo]

    ronda["indice"] = indice
    ronda["modo"] = dados["modo"]
    ronda["chegadas"] = 0
    ronda["eliminados"] = 0
    ronda["mensagem_tempo"] = 0
    ronda["tabela"] = []
    ronda["contagem"] = 240
    if ronda["modo"] == "corrida":
        ronda["tempo"] = TEMPO_CORRIDA * FPS
    elif ronda["modo"] == "moedas":
        ronda["tempo"] = TEMPO_MOEDAS * FPS
    else:
        ronda["tempo"] = TEMPO_BATALHA * FPS

    sitios = sitios_de_partida(dados)
    for p in jogadores:
        inicio = sitios.get(p["numero"], (TILE * p["numero"] + 9, 9 * TILE + TILE - ALTURA_J))
        p["inicio"] = inicio
        por_no_sitio(p, inicio[0], inicio[1])
        p["chegou"] = 0
        p["fora"] = 0
        p["moedas"] = 0
        p["vidas"] = VIDAS_BATALHA
        p["invencivel"] = 0
        p["congelado"] = 0
        p["passo"] = 0.0
        p["virado"] = 1
        if ronda["modo"] != "corrida" and inicio[0] > nivel["largura"] / 2:
            p["virado"] = -1         # nas arenas comeca-se virado para o meio
    jogo["fase"] = "contagem"


def e_a_final():
    return FINAL_A_DOBRAR and ronda["indice"] == len(RONDAS) - 1


# =====================================================================
# D. UM JOGADOR A MEXER-SE
# =====================================================================
def atualizar_jogador(p, comando):
    pers = personagem_de(p)
    if p["congelado"] > 0 or p["tonto"] > 0:
        # Parado: acabou de renascer, ou levou uma pancada e esta tonto.
        if p["congelado"] > 0:
            p["congelado"] -= 1
        if p["tonto"] > 0:
            p["tonto"] -= 1
        comando = {"direcao": 0, "andar": False, "correr": False,
                   "saltar": False, "disparar": False}
    if p["invencivel"] > 0:
        p["invencivel"] -= 1
    if p["turbo"] > 0:
        p["turbo"] -= 1
    if p["choque"] > 0:
        p["choque"] -= 1

    if comando["direcao"] != 0:
        p["virado"] = comando["direcao"]
    velocidade = 0.0
    if comando["andar"]:
        velocidade = b.VEL_ANDAR
        if comando["correr"]:
            velocidade = b.VEL_CORRER
    velocidade = velocidade * pers["velocidade"]
    if p["turbo"] > 0:
        velocidade = velocidade * TURBO_DA_MOEDA
    p["vx"] = velocidade * p["virado"]
    p["anda"] = comando["andar"]
    p["corre"] = comando["andar"] and (comando["correr"] or p["turbo"] > 0)

    # Saltar, com as duas ajudas do costume (ver o maos-ao-ar.py).
    if comando["saltar"]:
        p["salto_pedido"] = b.TOLERANCIA_SALTO
    if p["no_chao"]:
        p["coiote"] = b.TEMPO_COIOTE
    if p["salto_pedido"] > 0 and p["coiote"] > 0:
        p["vy"] = -b.FORCA_SALTO * pers["salto"]
        p["salto_pedido"] = 0
        p["coiote"] = 0
        tocar("salto")
        particulas(p["x"] + 15, p["y"] + ALTURA_J, BRANCO, 5, 2)
    if p["salto_pedido"] > 0:
        p["salto_pedido"] -= 1
    if p["coiote"] > 0:
        p["coiote"] -= 1

    p["vy"] += b.GRAVIDADE * pers["gravidade"]
    if p["vy"] > b.VEL_QUEDA_MAXIMA:
        p["vy"] = b.VEL_QUEDA_MAXIMA
    # O empurrao dos choques soma-se ao andar, e vai-se gastando. Se o
    # jogador for contra uma parede, ressalta nela.
    bateu = b.mover_corpo(p, p["vx"] + p["empurrao"], p["vy"])
    if bateu and abs(p["empurrao"]) > 1:
        p["empurrao"] = -p["empurrao"] * 0.5
    p["empurrao"] = p["empurrao"] * 0.86
    if abs(p["empurrao"]) < 0.3:
        p["empurrao"] = 0.0
    p["passo"] += abs(p["vx"])

    # Lembrar os sitios com chao firme: e para la que se volta depois de
    # cair num buraco.
    if p["no_chao"] and p["tonto"] == 0 and nivel["tempo"] % 8 == 0:
        coluna = int((p["x"] + LARGURA_J / 2) // TILE)
        linha = int((p["y"] + ALTURA_J + 2) // TILE)
        if b.letra_em(coluna, linha) in "#=B":
            p["seguros"].append((p["x"], p["y"]))
            if len(p["seguros"]) > 5:
                del p["seguros"][0]

    # Disparar
    if p["recarga"] > 0:
        p["recarga"] -= 1
    if p["recuo"] > 0:
        p["recuo"] -= 1
    if comando["disparar"] and p["recarga"] == 0:
        p["recarga"] = pers["recarga"]
        p["recuo"] = 8
        nivel["tiros"].append({
            "x": p["x"] + 15 + p["virado"] * 18, "y": p["y"] + 22,
            "vx": pers["vel_tiro"] * p["virado"], "vida": b.ALCANCE_TIRO,
            "dono": p["numero"], "cor": pers["tiro"],
        })
        tocar("tiro")


# =====================================================================
# E. O MOLHO: os jogadores uns contra os outros
# =====================================================================
def chocar_jogadores():
    vivos = em_campo()
    for i in range(len(vivos)):
        for j in range(i + 1, len(vivos)):
            um = vivos[i]
            outro = vivos[j]
            if um["congelado"] > 0 or outro["congelado"] > 0:
                continue                # quem acabou de renascer fica em paz
            r1 = b.retangulo(um)
            r2 = b.retangulo(outro)
            if not r1.colliderect(r2):
                continue
            # Um vinha a cair para cima do outro? Entao pisou-o.
            if um["vy"] > 1 and r1.bottom - um["vy"] < r2.top + 20:
                pisar(um, outro)
            elif outro["vy"] > 1 and r2.bottom - outro["vy"] < r1.top + 20:
                pisar(outro, um)
            elif um["choque"] == 0 or outro["choque"] == 0:
                ressaltar(um, outro)


def ressaltar(um, outro):
    # Chocaram de lado: cada um vai para o seu lado, com um saltinho.
    # Quem pesa mais empurra mais e e menos empurrado.
    lado = sinal((um["x"] - outro["x"]) + (outro["numero"] - um["numero"]) * 0.01)
    peso_um = personagem_de(um)["peso"]
    peso_outro = personagem_de(outro)["peso"]
    um["empurrao"] = lado * FORCA_DO_CHOQUE * peso_outro / peso_um
    outro["empurrao"] = -lado * FORCA_DO_CHOQUE * peso_um / peso_outro
    for p in (um, outro):
        p["choque"] = 10
        if p["no_chao"]:
            p["vy"] = -SALTO_DO_CHOQUE
    meio_x = (um["x"] + outro["x"]) / 2 + 15
    particulas(meio_x, um["y"] + 20, BRANCO, 6, 3)
    tocar("toque")


def pisar(cima, baixo):
    cima["vy"] = -10.0
    cima["coiote"] = 0
    apanhar_pancada(baixo, 0, cima)


def apanhar_pancada(p, lado, culpado):
    # Um tiro, uma pisadela, um inimigo, uma bala de canhao: o jogador fica
    # tonto, e empurrado, e paga o castigo da ronda. lado: -1, 0 ou 1.
    if p["invencivel"] > 0 or p["congelado"] > 0:
        return
    pers = personagem_de(p)
    p["tonto"] = int(TEMPO_TONTO * pers["tonto"])
    p["invencivel"] = p["tonto"] + 40
    p["empurrao"] = lado * FORCA_DO_TIRO / pers["peso"]
    if lado != 0:
        p["vy"] = -6.0
    b.jogo["tremor"] = 8
    tocar("pancada")
    particulas(p["x"] + 15, p["y"] + 20, pers["cor"], 12, 5)
    castigo(p)


def castigo(p):
    # O que se perde, conforme a ronda.
    if ronda["modo"] == "batalha":
        p["vidas"] -= 1
        if p["vidas"] <= 0:
            eliminar(p)
    elif ronda["modo"] == "moedas":
        # As moedas caem ali perto: quem estiver ao pe apanha-as.
        caem = min(MOEDAS_PERDIDAS, p["moedas"])
        p["moedas"] -= caem
        for i in range(caem):
            sitio = escolher_sitio(p["x"])
            if sitio is not None:
                por_moeda(sitio[0], sitio[1])


def eliminar(p):
    ronda["eliminados"] += 1
    p["fora"] = ronda["eliminados"]
    dizer(nome_de(p) + " está fora!")
    particulas(p["x"] + 15, p["y"] + 20, cor_de(p), 30, 7)
    tocar("perdeu")


def cair(p):
    # Um buraco, a lava ou os espinhos: paga o castigo e volta a nascer.
    b.jogo["tremor"] = 10
    tocar("pancada")
    particulas(p["x"] + 15, min(p["y"], LINHAS * TILE) + 20, personagem_de(p)["cor"], 14, 5)
    castigo(p)
    if p["fora"] == 0:
        renascer(p, False)


def lider():
    # Quem vai a frente (mais a direita), entre os que ainda correm.
    melhor = None
    for p in em_campo():
        if melhor is None or p["x"] > melhor["x"]:
            melhor = p
    return melhor


def renascer(p, ao_pe_do_lider):
    if ronda["modo"] == "corrida":
        # Numa corrida volta-se ao ultimo sitio com chao firme. Quem ficou
        # para tras do ecra vai para junto de quem vai a frente.
        sitio = p["seguros"][0]
        da_frente = lider()
        if da_frente is not None and da_frente is not p:
            if ao_pe_do_lider or sitio[0] < nivel["camara_x"] + TILE:
                sitio = da_frente["seguros"][0]
    else:
        sitio = p["inicio"]
    virado = p["virado"]
    por_no_sitio(p, sitio[0], sitio[1])
    p["virado"] = virado
    p["congelado"] = 60          # um segundo parado: e esse o preco
    p["invencivel"] = 130


# =====================================================================
# F. O MAPA, OS TIROS E OS INIMIGOS
# Sao as funcoes do maos-ao-ar.py, refeitas para varios jogadores.
# =====================================================================
def tocar_no_mapa(p):
    eu = b.retangulo(p)
    if p["y"] > LINHAS * TILE + 80:
        cair(p)
        return

    coluna_0 = eu.left // TILE
    coluna_1 = (eu.right - 1) // TILE
    linha_0 = eu.top // TILE
    linha_1 = (eu.bottom - 1) // TILE
    for linha in range(linha_0, linha_1 + 1):
        for coluna in range(coluna_0, coluna_1 + 1):
            letra = b.letra_em(coluna, linha)
            x = coluna * TILE
            y = linha * TILE
            if letra == "M":
                if p["vy"] >= 0 and eu.bottom >= y + 20:
                    p["vy"] = -b.FORCA_MOLA
                    p["no_chao"] = False
                    p["coiote"] = 0
                    tocar("mola")
            elif letra == "^":
                if eu.colliderect(pygame.Rect(x + 8, y + 22, TILE - 16, 26)):
                    cair(p)
                    return
            elif letra == "~":
                if eu.colliderect(pygame.Rect(x, y + 14, TILE, TILE - 14)):
                    cair(p)
                    return

    # Pontes podres: comecam a tremer quando alguem lhes poe os pes em cima.
    if p["no_chao"]:
        linha = eu.bottom // TILE
        for coluna in range(coluna_0, coluna_1 + 1):
            if b.letra_em(coluna, linha) == "%" and (coluna, linha) not in nivel["pontes"]:
                nivel["pontes"][(coluna, linha)] = 28

    restantes = []
    for moeda in nivel["moedas"]:
        if eu.colliderect(moeda):
            p["moedas"] += 1
            tocar("moeda")
            particulas(moeda.centerx, moeda.centery, b.COR_MOEDA, 6, 3)
            if ronda["modo"] == "corrida":
                p["turbo"] = TEMPO_DO_TURBO
        else:
            restantes.append(moeda)
    nivel["moedas"] = restantes

    restantes = []
    for coracao in nivel["coracoes"]:
        if eu.colliderect(coracao) and p["vidas"] < VIDAS_BATALHA:
            p["vidas"] += 1
            tocar("controlo")
            particulas(coracao.centerx, coracao.centery, VERMELHO, 10, 3)
        else:
            restantes.append(coracao)
    nivel["coracoes"] = restantes

    if ronda["modo"] == "corrida" and nivel["saida"] is not None:
        if eu.colliderect(nivel["saida"]):
            chegar(p)


def chegar(p):
    ronda["chegadas"] += 1
    p["chegou"] = ronda["chegadas"]
    dizer(nome_de(p) + " chegou em " + ordinal(p["chegou"]) + "!")
    particulas(p["x"] + 15, p["y"] + 20, cor_de(p), 30, 7)
    tocar("vitoria")
    if p["chegou"] == 1:
        # Os outros ja nao tem o tempo todo.
        ronda["tempo"] = min(ronda["tempo"], TEMPO_DEPOIS_DO_PRIMEIRO * FPS)


def atualizar_pontes():
    for chave in list(nivel["pontes"].keys()):
        nivel["pontes"][chave] -= 1
        if nivel["pontes"][chave] <= 0:
            del nivel["pontes"][chave]
            nivel["grelha"][chave[1]][chave[0]] = "."
            nivel["pontes_caidas"][chave] = 240
            particulas(chave[0] * TILE + 24, chave[1] * TILE + 8, b.COR_PONTE_PODRE, 8, 3)
            tocar("caixote")
    for chave in list(nivel["pontes_caidas"].keys()):
        nivel["pontes_caidas"][chave] -= 1
        if nivel["pontes_caidas"][chave] <= 0:
            sitio = pygame.Rect(chave[0] * TILE, chave[1] * TILE, TILE, TILE)
            livre = True
            for p in em_campo():
                if b.retangulo(p).colliderect(sitio):
                    livre = False
            if livre:
                del nivel["pontes_caidas"][chave]
                nivel["grelha"][chave[1]][chave[0]] = "%"


def atualizar_tiros():
    vivos = []
    for tiro in nivel["tiros"]:
        tiro["x"] += tiro["vx"]
        tiro["vida"] -= 1
        if tiro["vida"] <= 0:
            continue
        coluna = int(tiro["x"] // TILE)
        linha = int(tiro["y"] // TILE)
        if b.e_solido(coluna, linha):
            if b.letra_em(coluna, linha) == "B":
                nivel["grelha"][linha][coluna] = "."
                particulas(coluna * TILE + 24, linha * TILE + 24, b.COR_MADEIRA, 12, 5)
                tocar("caixote")
            else:
                particulas(tiro["x"], tiro["y"], tiro["cor"], 3, 2)
            continue
        acertou = False
        for inimigo in nivel["inimigos"]:
            alvo = b.retangulo(inimigo).inflate(8, 8)
            if inimigo["vida"] > 0 and alvo.collidepoint(tiro["x"], tiro["y"]):
                b.magoar_inimigo(inimigo, 1)
                acertou = True
                break
        if not acertou:
            # Os tiros tambem acertam nos outros jogadores (nunca no dono).
            for p in em_campo():
                if p["numero"] == tiro["dono"] or p["invencivel"] > 0:
                    continue
                if b.retangulo(p).inflate(6, 6).collidepoint(tiro["x"], tiro["y"]):
                    apanhar_pancada(p, sinal(tiro["vx"]), tiro["dono"])
                    acertou = True
                    break
        if not acertou:
            vivos.append(tiro)
    nivel["tiros"] = vivos


def mais_perto(inimigo):
    melhor = None
    for p in em_campo():
        if melhor is None or abs(p["x"] - inimigo["x"]) < abs(melhor["x"] - inimigo["x"]):
            melhor = p
    return melhor


def atualizar_inimigos():
    vivos = []
    meio_do_ecra = nivel["camara_x"] + LARGURA / 2
    for inimigo in nivel["inimigos"]:
        tipo = b.INIMIGOS[inimigo["letra"]]
        inimigo["t"] += 1
        if inimigo["pisca"] > 0:
            inimigo["pisca"] -= 1
        # Cada inimigo persegue o jogador que tiver mais perto. Para o motor
        # ha um so heroi: diz-se-lhe que e esse.
        alvo = mais_perto(inimigo)
        if alvo is not None and abs(inimigo["x"] - meio_do_ecra) < LARGURA:
            b.heroi = alvo
            b.mexer_inimigo(inimigo)
        if inimigo["y"] > LINHAS * TILE + 200:
            continue                    # caiu num buraco

        ele = b.retangulo(inimigo)
        for p in em_campo():
            if inimigo["vida"] <= 0:
                break
            eu = b.retangulo(p)
            if not eu.colliderect(ele):
                continue
            por_cima = p["vy"] > 0 and eu.bottom - p["vy"] < ele.top + ele.height * 0.6
            if tipo["pisavel"] and por_cima:
                b.magoar_inimigo(inimigo, 99)
                p["vy"] = -9.5
                p["coiote"] = 0
            else:
                apanhar_pancada(p, sinal(p["x"] - inimigo["x"]), None)
        if inimigo["vida"] > 0:
            vivos.append(inimigo)
    nivel["inimigos"] = vivos


def atualizar_balas():
    vivas = []
    for bala in nivel["balas"]:
        bala["x"] += bala["vx"]
        bala["y"] += bala["vy"]
        bala["vida"] -= 1
        if bala["vida"] <= 0:
            continue
        if b.e_solido(int(bala["x"] // TILE), int(bala["y"] // TILE)):
            particulas(bala["x"], bala["y"], LARANJA, 3, 2)
            continue
        acertou = False
        for p in em_campo():
            if p["invencivel"] == 0 and p["congelado"] == 0:
                if b.retangulo(p).inflate(-6, -6).collidepoint(bala["x"], bala["y"]):
                    apanhar_pancada(p, sinal(bala["vx"]), None)
                    acertou = True
                    break
        if not acertou:
            vivas.append(bala)
    nivel["balas"] = vivas


# --- As coisas que vao aparecendo: moedas e coracoes ---
def por_moeda(coluna, linha):
    nivel["moedas"].append(pygame.Rect(coluna * TILE + 14, linha * TILE + 14, 20, 20))


def escolher_sitio(perto_de):
    # Um quadrado de ar com chao por baixo, sem nada la. perto_de: None, ou
    # o x de um jogador (para as moedas que lhe caem dos bolsos).
    sitios = []
    for linha in range(1, LINHAS - 1):
        for coluna in range(nivel["colunas"]):
            if b.letra_em(coluna, linha) != "." or b.letra_em(coluna, linha + 1) not in "#=B":
                continue
            sitio = pygame.Rect(coluna * TILE, linha * TILE, TILE, TILE)
            if sitio.collidelist(nivel["moedas"]) >= 0 or sitio.collidelist(nivel["coracoes"]) >= 0:
                continue
            ocupado = False
            for p in em_campo():
                if b.retangulo(p).inflate(40, 40).colliderect(sitio):
                    ocupado = True
            if ocupado:
                continue
            if perto_de is not None:
                distancia = abs(sitio.centerx - (perto_de + 15))
                if distancia > 6 * TILE:
                    continue
            sitios.append((coluna, linha))
    if len(sitios) == 0:
        return None
    return random.choice(sitios)


def aparecer_coisas():
    restam = ronda["tempo"] // FPS
    if ronda["modo"] == "moedas":
        intervalo = 40
        maximo = 14
        if restam < CHUVA_DE_MOEDAS:
            intervalo = 10
            maximo = 40
        if ronda["tempo"] == CHUVA_DE_MOEDAS * FPS:
            dizer("CHUVA DE MOEDAS!")
        if ronda["tempo"] % intervalo == 0 and len(nivel["moedas"]) < maximo:
            sitio = escolher_sitio(None)
            if sitio is not None:
                por_moeda(sitio[0], sitio[1])
    elif ronda["modo"] == "batalha":
        if ronda["tempo"] % (12 * FPS) == 0 and len(nivel["coracoes"]) == 0:
            sitio = escolher_sitio(None)
            if sitio is not None:
                nivel["coracoes"].append(
                    pygame.Rect(sitio[0] * TILE + 12, sitio[1] * TILE + 12, 24, 24))
    if ronda["tempo"] == 10 * FPS:
        dizer("Faltam 10 segundos!")


# =====================================================================
# G. A RONDA: um frame, a camara do jogo e a classificacao
# =====================================================================
def mexer_camara():
    # Numa corrida, o ecra segue quem vai a frente. Quem ficar para tras
    # do ecra e puxado para junto dele (e perde um segundo).
    alvo = 0.0
    da_frente = lider()
    if ronda["modo"] == "corrida" and da_frente is not None:
        alvo = da_frente["x"] - LARGURA * 0.5
    nivel["camara_x"] += (alvo - nivel["camara_x"]) * 0.08
    if nivel["camara_x"] > nivel["largura"] - LARGURA:
        nivel["camara_x"] = nivel["largura"] - LARGURA
    if nivel["camara_x"] < 0:
        nivel["camara_x"] = 0
    if ronda["modo"] == "corrida":
        for p in em_campo():
            if p is not da_frente and p["x"] + LARGURA_J < nivel["camara_x"] - 30:
                particulas(nivel["camara_x"] + 10, p["y"] + 20, cor_de(p), 10, 4)
                renascer(p, True)
                tocar("mola")


def passo_da_ronda(comandos):
    # Um frame de jogo, sem desenhar nada. comandos: numero do jogador -> comando.
    nivel["tempo"] += 1
    ronda["tempo"] -= 1
    for p in em_campo():
        atualizar_jogador(p, comandos[p["numero"]])
    chocar_jogadores()
    atualizar_pontes()
    atualizar_tiros()
    atualizar_inimigos()
    atualizar_balas()
    for p in em_campo():
        tocar_no_mapa(p)
    mexer_camara()
    aparecer_coisas()
    b.atualizar_particulas()
    ver_se_acabou()


def ver_se_acabou():
    restam = em_campo()
    acabou = ronda["tempo"] <= 0 or len(restam) == 0
    if ronda["modo"] == "batalha" and len(participantes()) > 1 and len(restam) <= 1:
        acabou = True
    if acabou:
        acabar_ronda()


def classificar():
    # Devolve a tabela da ronda, do melhor para o pior. Cada jogador tem
    # uma "chave": quanto mais pequena, melhor. Chaves iguais sao empates.
    linhas = []
    for p in participantes():
        if ronda["modo"] == "corrida":
            if p["chegou"] > 0:
                chave = p["chegou"]
                texto = "chegou em " + ordinal(p["chegou"])
            else:
                chave = 1000 - p["x"] / nivel["largura"]
                texto = "ficou a " + str(int(100 * p["x"] / nivel["largura"])) + "% do caminho"
        elif ronda["modo"] == "moedas":
            chave = -p["moedas"]
            texto = quantas(p["moedas"], "moeda", "moedas")
        else:
            if p["fora"] > 0:
                chave = 1000 - p["fora"]
                texto = "fora de combate"
            else:
                chave = -p["vidas"]
                texto = "de pé, com " + quantas(p["vidas"], "coração", "corações")
        linhas.append({"jogador": p, "chave": chave, "texto": texto})
    linhas.sort(key=lambda linha: linha["chave"])
    for i in range(len(linhas)):
        if i > 0 and linhas[i]["chave"] == linhas[i - 1]["chave"]:
            linhas[i]["lugar"] = linhas[i - 1]["lugar"]
        else:
            linhas[i]["lugar"] = i
        pontos = 0
        if linhas[i]["lugar"] < len(PONTOS_POR_LUGAR):
            pontos = PONTOS_POR_LUGAR[linhas[i]["lugar"]]
        if e_a_final():
            pontos = pontos * 2
        linhas[i]["pontos"] = pontos
    return linhas


def acabar_ronda():
    ronda["tabela"] = classificar()
    for linha in ronda["tabela"]:
        linha["jogador"]["pontos"] += linha["pontos"]
    jogo["fase"] = "ronda_fim"
    jogo["espera"] = 100
    tocar("vitoria")


def classificacao_geral():
    lista = participantes()
    lista.sort(key=lambda p: -p["pontos"])
    return lista


# =====================================================================
# H. OS COMANDOS: da mao (e do teclado) para cada jogador
# =====================================================================
def ler_comando(p, m, teclas, saltou):
    comando = {"direcao": 0, "andar": False, "correr": False,
               "saltar": saltou, "disparar": False}
    if m["visivel"]:
        comando["andar"] = True
        if m["x"] < ZONA_ESQUERDA:
            comando["direcao"] = -1
        elif m["x"] > ZONA_DIREITA:
            comando["direcao"] = 1
        if m["y"] < LINHA_CORRER:
            p["mao_corre"] = True
        elif m["y"] > LINHA_CORRER + 0.06:
            p["mao_corre"] = False
        comando["correr"] = p["mao_corre"]
        comando["disparar"] = m["forma"] == "apontar"
    else:
        p["mao_corre"] = False

    t = TECLADO[p["numero"] - 1]
    if jogo["modo_teclado"]:
        comando["andar"] = True
    if teclas[t["esq"]]:
        comando["direcao"] = -1
        comando["andar"] = True
    if teclas[t["dir"]]:
        comando["direcao"] = 1
        comando["andar"] = True
    if teclas[t["parar"]]:
        comando["andar"] = False
    if teclas[t["correr"]]:
        comando["correr"] = True
    if teclas[t["tiro"]]:
        comando["disparar"] = True
    return comando


# =====================================================================
# I. O ECRA DE ESCOLHA: cada um escolhe a sua personagem, so com a mao
# =====================================================================
def ocupada(indice, quem_pergunta):
    for p in jogadores:
        if p is not quem_pergunta and p["pronto"] and p["personagem"] == indice:
            return True
    return False


def mudar_personagem(p, passo):
    # A seguinte (ou a anterior) que ainda nao tenha dono.
    for tentativa in range(len(PERSONAGENS)):
        p["personagem"] = (p["personagem"] + passo) % len(PERSONAGENS)
        if not ocupada(p["personagem"], p):
            break
    tocar("toque")


def escolher(p, m, toque, saltou):
    # toque: as teclas em que este jogador carregou neste frame.
    if m["visivel"] or toque["esq"] or toque["dir"] or saltou:
        if not p["entrou"]:
            p["entrou"] = True
            if ocupada(p["personagem"], p):
                mudar_personagem(p, 1)
            tocar("controlo")
            return
    if not p["entrou"]:
        return

    if p["pronto"]:
        # Apontar o indicador (ou a tecla de parar) desfaz a escolha.
        if (m["visivel"] and m["forma"] == "apontar") or toque["parar"]:
            p["pronto"] = False
            tocar("toque")
        return

    # Mao para um lado: muda logo, e se la ficar vai mudando devagar.
    lado = 0
    if m["visivel"]:
        if m["x"] < ZONA_ESQUERDA:
            lado = -1
        elif m["x"] > ZONA_DIREITA:
            lado = 1
    if p["espera_troca"] > 0:
        p["espera_troca"] -= 1
    if lado != 0 and (lado != p["lado_antes"] or p["espera_troca"] == 0):
        mudar_personagem(p, lado)
        p["espera_troca"] = 50
    p["lado_antes"] = lado
    if toque["esq"]:
        mudar_personagem(p, -1)
    if toque["dir"]:
        mudar_personagem(p, 1)

    if saltou:
        if ocupada(p["personagem"], p):
            tocar("pancada")            # essa ja tem dono
        else:
            p["pronto"] = True
            tocar("vitoria")


def atualizar_escolha(v, toques, saltos, forcar):
    prontos = 0
    for p in jogadores:
        i = p["numero"] - 1
        escolher(p, v["maos"][i], toques[i], saltos[i])
        if p["pronto"]:
            prontos += 1
    if prontos == len(jogadores):
        jogo["arranque"] -= 1
    else:
        jogo["arranque"] = 150
    if (jogo["arranque"] <= 0 or forcar) and prontos > 0:
        comecar_torneio()


def comecar_torneio():
    for p in jogadores:
        p["joga"] = p["pronto"]
        p["pontos"] = 0
    comecar_ronda(0)


# =====================================================================
# J. DESENHAR AS PERSONAGENS
# Todas cabem num retangulo de 30 por 42. x, y e o canto de cima, do lado
# esquerdo; v e 1 se olha para a direita e -1 para a esquerda.
# =====================================================================
def desenhar_personagem(ecra, pers, x, y, v, p, frame):
    # p: de onde se le como esta o corpo ("no_chao", "anda", "corre",
    # "passo", "recuo", "tonto").
    cor = pers["cor"]
    escura = pers["cor2"]
    feitio = pers["feitio"]
    meio = x + 15
    if feitio == "fantasma":
        y += int(math.sin(frame * 0.1) * 2)         # paira

    if p["corre"]:
        for i in range(3):
            pygame.draw.line(ecra, BRANCO, (meio - v * (22 + i * 6), y + 12 + i * 9),
                             (meio - v * (36 + i * 6), y + 12 + i * 9), 2)

    # pernas
    perna = 0
    if p["no_chao"] and p["anda"]:
        perna = int(math.sin(p["passo"] * 0.25) * 5)
    if not p["no_chao"]:
        perna = 4
    if feitio != "fantasma":
        cor_pes = escura
        if feitio == "pinguim":
            cor_pes = LARANJA
        pygame.draw.rect(ecra, cor_pes, (x + 4, y + 30, 9, 12 - max(0, perna)), border_radius=3)
        pygame.draw.rect(ecra, cor_pes, (x + 17, y + 30, 9, 12 - max(0, -perna)), border_radius=3)

    # o que fica por tras do corpo
    if feitio == "robot":
        ponta = (meio - v * 5, y - 6)
        pygame.draw.line(ecra, escura, (meio, y + 6), ponta, 3)
        pygame.draw.circle(ecra, LARANJA, ponta, 4)
    elif feitio == "gato":
        pygame.draw.line(ecra, cor, (meio - v * 13, y + 28), (meio - v * 22, y + 10), 4)
        pygame.draw.polygon(ecra, cor, [(x + 1, y + 9), (x + 5, y - 5), (x + 12, y + 6)])
        pygame.draw.polygon(ecra, cor, [(x + 18, y + 6), (x + 25, y - 5), (x + 29, y + 9)])
    elif feitio == "dragao":
        pygame.draw.polygon(ecra, escura, [(x + 4, y + 7), (x + 7, y - 6), (x + 11, y + 5)])
        pygame.draw.polygon(ecra, escura, [(x + 19, y + 5), (x + 23, y - 6), (x + 26, y + 7)])
        for i in range(3):
            costas = meio - v * 14
            pygame.draw.polygon(ecra, escura, [(costas, y + 9 + i * 8), (costas - v * 8, y + 13 + i * 8),
                                               (costas, y + 17 + i * 8)])
    elif feitio == "alien":
        for lado in (-1, 1):
            ponta = (meio + lado * 9, y - 7)
            pygame.draw.line(ecra, escura, (meio + lado * 6, y + 6), ponta, 3)
            pygame.draw.circle(ecra, cor, ponta, 4)
    elif feitio == "ninja":
        abana = int(math.sin(frame * 0.3) * 3)
        pygame.draw.line(ecra, escura, (meio - v * 14, y + 12), (meio - v * 27, y + 8 + abana), 4)
        pygame.draw.line(ecra, escura, (meio - v * 14, y + 13), (meio - v * 25, y + 18 - abana), 4)

    # o corpo
    if feitio == "fantasma":
        pygame.draw.rect(ecra, cor, (x, y + 2, 30, 32),
                         border_top_left_radius=15, border_top_right_radius=15)
        for i in range(3):
            pygame.draw.circle(ecra, cor, (x + 5 + i * 10, y + 34), 5)
    else:
        pygame.draw.rect(ecra, cor, (x, y + 4, 30, 30), border_radius=9)
        pygame.draw.rect(ecra, escura, (x, y + 4, 30, 30), 3, border_radius=9)

    # a cara
    if feitio == "robot":
        pygame.draw.rect(ecra, BRANCO, (x + 5 + v * 4, y + 10, 20, 12), border_radius=5)
        pygame.draw.rect(ecra, PRETO, (x + 9 + v * 7, y + 12, 4, 8))
        pygame.draw.rect(ecra, PRETO, (x + 17 + v * 7, y + 12, 4, 8))
    elif feitio == "gato":
        for dx in (10, 20):
            pygame.draw.circle(ecra, BRANCO, (x + dx + v * 4, y + 15), 4)
            pygame.draw.rect(ecra, PRETO, (x + dx - 1 + v * 5, y + 12, 2, 6))
        pygame.draw.circle(ecra, (255, 150, 170), (meio + v * 5, y + 22), 2)
        for dy in (22, 26):
            pygame.draw.line(ecra, escura, (meio + v * 8, y + 23), (meio + v * 17, y + dy), 1)
    elif feitio == "sapo":
        pygame.draw.ellipse(ecra, (190, 240, 170), (x + 6, y + 20, 18, 11))
        for dx in (7, 23):
            pygame.draw.circle(ecra, cor, (x + dx, y + 5), 7)
            pygame.draw.circle(ecra, BRANCO, (x + dx, y + 5), 5)
            pygame.draw.circle(ecra, PRETO, (x + dx + v * 2, y + 5), 2)
        pygame.draw.line(ecra, escura, (x + 7, y + 18), (x + 23, y + 18), 2)
    elif feitio == "fantasma":
        pygame.draw.ellipse(ecra, PRETO, (x + 6 + v * 3, y + 10, 6, 10))
        pygame.draw.ellipse(ecra, PRETO, (x + 17 + v * 3, y + 10, 6, 10))
        pygame.draw.circle(ecra, escura, (meio + v * 3, y + 26), 3)
    elif feitio == "pinguim":
        pygame.draw.ellipse(ecra, BRANCO, (x + 6 + v * 2, y + 11, 18, 21))
        for dx in (11, 19):
            pygame.draw.circle(ecra, PRETO, (x + dx + v * 4, y + 15), 2)
        pygame.draw.polygon(ecra, LARANJA, [(meio + v * 4, y + 18), (meio + v * 14, y + 21),
                                            (meio + v * 4, y + 24)])
    elif feitio == "dragao":
        pygame.draw.rect(ecra, (250, 200, 120), (x + 8, y + 22, 14, 10), border_radius=4)
        pygame.draw.circle(ecra, BRANCO, (meio + v * 6, y + 14), 5)
        pygame.draw.circle(ecra, PRETO, (meio + v * 8, y + 14), 2)
        pygame.draw.circle(ecra, escura, (meio + v * 12, y + 22), 2)
    elif feitio == "ninja":
        pygame.draw.rect(ecra, escura, (x, y + 9, 30, 5))
        pygame.draw.rect(ecra, (245, 215, 180), (x + 4 + v * 3, y + 15, 22, 8), border_radius=3)
        pygame.draw.rect(ecra, PRETO, (x + 9 + v * 5, y + 17, 3, 5))
        pygame.draw.rect(ecra, PRETO, (x + 18 + v * 5, y + 17, 3, 5))
    elif feitio == "alien":
        pygame.draw.circle(ecra, BRANCO, (meio + v * 4, y + 16), 8)
        pygame.draw.circle(ecra, PRETO, (meio + v * 7, y + 16), 4)
        pygame.draw.line(ecra, escura, (meio - 3 + v * 4, y + 28), (meio + 5 + v * 4, y + 28), 2)

    # o braco que dispara
    if p["recuo"] > 0:
        pygame.draw.rect(ecra, escura, (meio + v * 14 - 6, y + 20, 14, 7), border_radius=3)
        pygame.draw.circle(ecra, pers["tiro"], (meio + v * 24, y + 23), p["recuo"])

    # estrelas a volta da cabeca de quem esta tonto
    if p["tonto"] > 0:
        for i in range(3):
            angulo = frame * 0.25 + i * 2.1
            pygame.draw.circle(ecra, AMARELO, (int(meio + math.cos(angulo) * 16),
                                               int(y - 6 + math.sin(angulo) * 5)), 3)


PARADO = {"no_chao": True, "anda": False, "corre": False, "passo": 0.0, "recuo": 0, "tonto": 0}


def retrato(pers, vezes, frame, a_andar):
    # A personagem em grande, para os ecras de escolha e do podio.
    pequeno = pygame.Surface((64, 64), pygame.SRCALPHA)
    pose = dict(PARADO)
    if a_andar:
        pose["anda"] = True
        pose["passo"] = frame * 3.0
    desenhar_personagem(pequeno, pers, 17, 16, 1, pose, frame)
    return pygame.transform.scale(pequeno, (int(64 * vezes), int(64 * vezes)))


def desenhar_jogador(p, camara_x):
    ecra = b.janela["ecra"]
    frame = b.jogo["frame"]
    x = int(p["x"] - camara_x)
    y = int(p["y"])
    cor = cor_de(p)
    # a seta com a cor do jogador, para cada um saber qual e o seu
    salto = int(math.sin(frame * 0.15 + p["numero"]) * 2)
    pygame.draw.polygon(ecra, PRETO, [(x + 5, y - 24 + salto), (x + 25, y - 24 + salto),
                                      (x + 15, y - 10 + salto)])
    pygame.draw.polygon(ecra, cor, [(x + 8, y - 22 + salto), (x + 22, y - 22 + salto),
                                    (x + 15, y - 13 + salto)])
    escrever(str(p["numero"]), "pp", cor, x + 15, y - 42 + salto, "centro")
    if p["invencivel"] > 0 and p["tonto"] == 0 and (p["invencivel"] // 4) % 2 == 0:
        return                      # a piscar
    desenhar_personagem(ecra, personagem_de(p), x, y, p["virado"], p, frame)


# =====================================================================
# K. DESENHAR A CAMARA: o bocado de cada jogador
# =====================================================================
vista = {"numero": -1, "inteira": None, "dados": None, "recortes": {}}


def atualizar_vista(v):
    # Faz a imagem da camara uma vez por cada imagem nova, e nao 60 vezes
    # por segundo.
    if v["imagem"] is None or v["tamanho"][0] == 0:
        vista["inteira"] = None
        return
    if vista["numero"] != v["numero"] or vista["inteira"] is None:
        vista["dados"] = v["imagem"]
        vista["inteira"] = pygame.image.frombuffer(v["imagem"], v["tamanho"], "RGB")
        vista["numero"] = v["numero"]
        vista["recortes"] = {}


def desenhar_bocado(v, indice, sitio, cor):
    # O bocado da camara do jogador com esse indice, dentro do retangulo
    # "sitio", com as linhas dos gestos e o esqueleto da mao.
    ecra = b.janela["ecra"]
    x0, y0, x1, y1 = v["zonas"][indice]
    m = v["maos"][indice]
    if vista["inteira"] is None:
        pygame.draw.rect(ecra, (30, 30, 48), sitio, border_radius=6)
        escrever("J" + str(indice + 1), "m", cor, sitio.centerx, sitio.centery - 14, "centro")
        pygame.draw.rect(ecra, cor, sitio.inflate(4, 4), 4, border_radius=6)
        return
    chave = (indice, sitio.width, sitio.height)
    if chave not in vista["recortes"]:
        largura, altura = vista["inteira"].get_size()
        parte = pygame.Rect(int(x0 * largura), int(y0 * altura),
                            int((x1 - x0) * largura), int((y1 - y0) * altura))
        vista["recortes"][chave] = pygame.transform.scale(vista["inteira"].subsurface(parte),
                                                          sitio.size)
    ecra.blit(vista["recortes"][chave], sitio)

    x_esq = sitio.x + sitio.width * ZONA_ESQUERDA
    x_dir = sitio.x + sitio.width * ZONA_DIREITA
    y_correr = sitio.y + sitio.height * LINHA_CORRER
    pygame.draw.line(ecra, BRANCO, (x_esq, sitio.y), (x_esq, sitio.bottom), 1)
    pygame.draw.line(ecra, BRANCO, (x_dir, sitio.y), (x_dir, sitio.bottom), 1)
    pygame.draw.line(ecra, AMARELO, (sitio.x, y_correr), (sitio.right, y_correr), 2)

    cor_mao = VERDE
    if m["forma"] == "punho":
        cor_mao = AZUL
    elif m["forma"] == "apontar":
        cor_mao = VERMELHO
    if len(m["pontos"]) == 21:
        ecra.set_clip(sitio)
        pontos = []
        for px, py in m["pontos"]:
            pontos.append((sitio.x + (px - x0) / (x1 - x0) * sitio.width,
                           sitio.y + (py - y0) / (y1 - y0) * sitio.height))
        for de, ate in b.LIGACOES_DA_MAO:
            pygame.draw.line(ecra, cor_mao, pontos[de], pontos[ate], 2)
        ecra.set_clip(None)
    if m["visivel"]:
        centro = (int(sitio.x + m["x"] * sitio.width), int(sitio.y + m["y"] * sitio.height))
        pygame.draw.circle(ecra, BRANCO, centro, 5)
        pygame.draw.circle(ecra, cor_mao, centro, 5, 2)
    elif not jogo["modo_teclado"]:
        escrever("MÃO?", "p", BRANCO, sitio.centerx, sitio.centery - 10, "centro")
    pygame.draw.rect(ecra, cor, sitio.inflate(4, 4), 4, border_radius=6)


def sitio_do_canto(indice):
    # Onde fica, no ecra, o bocado da camara de cada jogador durante o jogo.
    largura, altura = 128, 96
    if jogo["quantos"] == 2:
        largura, altura = 96, 144
    lado, andar = canto_de(indice, jogo["quantos"])
    x = 8
    if lado == 1:
        x = LARGURA - largura - 8
    y = 8
    if andar == 1:
        y = ALTURA - altura - 8
    return pygame.Rect(x, y, largura, altura)


# =====================================================================
# L. DESENHAR O JOGO
# =====================================================================
def desenhar_canto(v, p):
    # O canto de um jogador: a camara dele, o nome, como vai nesta ronda e
    # os pontos do torneio.
    ecra = b.janela["ecra"]
    indice = p["numero"] - 1
    sitio = sitio_do_canto(indice)
    cor = cor_de(p)
    desenhar_bocado(v, indice, sitio, cor)
    lado = canto_de(indice, jogo["quantos"])[0]
    if lado == 0:
        x = sitio.right + 10
        alinhar = "esquerda"
    else:
        x = sitio.left - 10
        alinhar = "direita"
    y = sitio.y
    escrever(nome_de(p), "p", cor, x, y, alinhar)

    if not p["joga"]:
        return
    if ronda["modo"] == "batalha":
        for i in range(VIDAS_BATALHA):
            cor_coracao = (60, 50, 70)
            if i < p["vidas"]:
                cor_coracao = VERMELHO
            if lado == 0:
                b.desenhar_coracao(x + i * 26, y + 26, 22, cor_coracao)
            else:
                b.desenhar_coracao(x - (VIDAS_BATALHA - i) * 26, y + 26, 22, cor_coracao)
        if p["fora"] > 0:
            escrever("FORA", "p", CINZA, x, y + 52, alinhar)
    elif ronda["modo"] == "moedas":
        escrever(quantas(p["moedas"], "moeda", "moedas"), "m", b.COR_MOEDA, x, y + 22, alinhar)
    else:
        if p["chegou"] > 0:
            escrever("CHEGOU " + ordinal(p["chegou"]), "m", VERDE, x, y + 22, alinhar)
        else:
            # o lugar em que vai agora
            lugar = ronda["chegadas"] + 1
            for outro in em_campo():
                if outro["x"] > p["x"]:
                    lugar += 1
            escrever(ordinal(lugar), "m", BRANCO, x, y + 22, alinhar)
    escrever(str(p["pontos"]) + " pts", "p", BRANCO, x, y + 54, alinhar)


def texto_do_tempo(frames):
    segundos = max(0, frames) // FPS
    return str(segundos // 60) + ":" + str(segundos % 60).zfill(2)


def desenhar_ronda(v):
    ecra = b.janela["ecra"]
    camara_x = nivel["camara_x"]
    b.desenhar_fundo(camara_x)
    b.desenhar_mapa(camara_x)
    b.desenhar_coisas(camara_x)
    for inimigo in nivel["inimigos"]:
        if -100 < inimigo["x"] - camara_x < LARGURA + 100:
            b.desenhar_inimigo(inimigo, camara_x)
    for p in em_campo():
        desenhar_jogador(p, camara_x)
    for tiro in nivel["tiros"]:
        pygame.draw.rect(ecra, PRETO, (tiro["x"] - camara_x - 9, tiro["y"] - 4, 18, 8), border_radius=4)
        pygame.draw.rect(ecra, tiro["cor"], (tiro["x"] - camara_x - 8, tiro["y"] - 3, 16, 6), border_radius=3)
    for bala in nivel["balas"]:
        pygame.draw.circle(ecra, LARANJA, (int(bala["x"] - camara_x), int(bala["y"])), 8)
        pygame.draw.circle(ecra, AMARELO, (int(bala["x"] - camara_x), int(bala["y"])), 4)
    for parte in nivel["particulas"]:
        pygame.draw.rect(ecra, parte["cor"], (parte["x"] - camara_x, parte["y"],
                                              parte["tamanho"], parte["tamanho"]))
    if b.jogo["tremor"] > 0:
        b.jogo["tremor"] -= 1
        ecra.scroll(random.randint(-5, 5), random.randint(-5, 5))

    # por cima: os cantos, a ronda, o tempo e a frase do momento
    for p in jogadores:
        desenhar_canto(v, p)
    modo = MODOS[ronda["modo"]]
    titulo = "RONDA " + str(ronda["indice"] + 1) + " de " + str(len(RONDAS)) + "  ·  " + modo["nome"]
    if e_a_final():
        titulo = titulo + "  ·  VALE A DOBRAR"
    escrever(titulo, "p", BRANCO, LARGURA // 2, 8, "centro")
    cor_tempo = BRANCO
    if ronda["tempo"] < 10 * FPS:
        cor_tempo = VERMELHO
    escrever(texto_do_tempo(ronda["tempo"]), "g", cor_tempo, LARGURA // 2, 30, "centro")
    if ronda["mensagem_tempo"] > 0:
        ronda["mensagem_tempo"] -= 1
        escrever(ronda["mensagem"], "g", AMARELO, LARGURA // 2, 110, "centro")


def desenhar_contagem():
    # Antes de cada ronda: o que e, a regra, e 3, 2, 1.
    meio = LARGURA // 2
    modo = MODOS[ronda["modo"]]
    b.escurecer(120)
    escrever(modo["nome"], "gg", AMARELO, meio, 110, "centro")
    escrever(RONDAS[ronda["indice"]]["nome"], "g", BRANCO, meio, 200, "centro")
    escrever(modo["regra"], "m", BRANCO, meio, 260, "centro")
    if e_a_final():
        escrever("É a final: os pontos valem a dobrar!", "m", LARANJA, meio, 300, "centro")
    if ronda["contagem"] <= 180:
        numero = (ronda["contagem"] - 1) // 60 + 1
        escrever(str(numero), "gg", VERDE, meio, 350, "centro")


def desenhar_tabela(linhas, y):
    meio = LARGURA // 2
    frame = b.jogo["frame"]
    for linha in linhas:
        p = linha["jogador"]
        cor = cor_de(p)
        escrever(ordinal(linha["lugar"] + 1), "g", BRANCO, meio - 330, y, "esquerda")
        b.janela["ecra"].blit(retrato(personagem_de(p), 1, frame, False), (meio - 262, y - 14))
        escrever(nome_de(p), "m", cor, meio - 190, y + 6, "esquerda")
        escrever(linha["texto"], "p", BRANCO, meio + 40, y + 10, "esquerda")
        escrever("+" + str(linha["pontos"]), "m", VERDE, meio + 300, y + 6, "direita")
        escrever(str(p["pontos"]) + " pts", "m", AMARELO, meio + 400, y + 6, "direita")
        y += 58


def desenhar_fim_da_ronda():
    meio = LARGURA // 2
    b.escurecer(190)
    escrever("FIM DA RONDA " + str(ronda["indice"] + 1), "g", AMARELO, meio, 60, "centro")
    escrever(RONDAS[ronda["indice"]]["nome"], "m", BRANCO, meio, 108, "centro")
    desenhar_tabela(ronda["tabela"], 170)
    if jogo["espera"] == 0:
        escrever(como_confirmar() + " para continuar", "m", VERDE, meio, ALTURA - 130, "centro")


def desenhar_podio():
    ecra = b.janela["ecra"]
    frame = b.jogo["frame"]
    meio = LARGURA // 2
    ecra.fill((22, 24, 48))
    for i in range(40):
        x = (i * 97 + frame * (1 + i % 3)) % LARGURA
        y = (i * 53 + frame * (2 + i % 4)) % ALTURA
        pygame.draw.rect(ecra, CORES_DOS_JOGADORES[i % 4], (x, y, 8, 8))
    geral = classificacao_geral()
    if len(geral) == 0:
        return
    escrever("VENCEDOR", "g", AMARELO, meio, 24, "centro")
    primeiro = geral[0]
    escrever(nome_de(primeiro), "gg", cor_de(primeiro), meio, 66, "centro")
    # os tres primeiros em cima de caixas: o 1.o no meio e mais alto
    lugares = [(meio, 150), (meio - 220, 110), (meio + 220, 80)]
    for i in range(min(3, len(geral))):
        p = geral[i]
        x, altura = lugares[i]
        topo = ALTURA - 90 - altura
        pygame.draw.rect(ecra, (60, 65, 110), (x - 90, topo, 180, altura), border_radius=8)
        pygame.draw.rect(ecra, cor_de(p), (x - 90, topo, 180, altura), 4, border_radius=8)
        escrever(ordinal(i + 1), "g", BRANCO, x, topo + 10, "centro")
        escrever(str(p["pontos"]) + " pts", "m", AMARELO, x, topo + 50, "centro")
        imagem = retrato(personagem_de(p), 3, frame, i == 0)
        salto = 0
        if i == 0:
            salto = int(abs(math.sin(frame * 0.12)) * 18)
        ecra.blit(imagem, (x - 96, topo - 170 - salto))
        escrever(nome_de(p), "p", cor_de(p), x, topo - 26, "centro")
    if len(geral) > 3:
        p = geral[3]
        escrever(ordinal(4) + "  " + nome_de(p) + "  " + str(p["pontos"]) + " pts", "p",
                 cor_de(p), meio, ALTURA - 80, "centro")
    if jogo["espera"] == 0:
        escrever(como_confirmar() + " para voltar ao título", "m", VERDE, meio, ALTURA - 46, "centro")


def como_confirmar():
    if olho["ligada"] and not jogo["modo_teclado"]:
        return "Fechem o punho (ou Espaço)"
    return "Espaço"


# =====================================================================
# M. OS ECRAS DE TITULO E DE ESCOLHA
# =====================================================================
def caixa_de_quantos(quantos):
    # O botao do titulo para escolher 2, 3 ou 4 jogadores.
    return pygame.Rect(80 + (quantos - 2) * 84, 184, 72, 72)


def desenhar_titulo(v):
    ecra = b.janela["ecra"]
    frame = b.jogo["frame"]
    meio = LARGURA // 2
    for y in range(0, ALTURA, 4):
        parte = y / ALTURA
        pygame.draw.rect(ecra, (int(30 + 40 * parte), int(40 + 60 * parte), int(110 + 90 * parte)),
                         (0, y, LARGURA, 4))
    escrever(TITULO, "gg", AMARELO, meio, 16 + int(math.sin(frame * 0.06) * 5), "centro")
    escrever(SUBTITULO, "m", BRANCO, meio, 100, "centro")

    # quantos jogam
    escrever("Quantos jogam?  (clica, ou teclas 2, 3 e 4)", "p", BRANCO, 200, 150, "centro")
    for i in range(3):
        quantos = i + 2
        caixa = caixa_de_quantos(quantos)
        cor = (60, 65, 110)
        if quantos == jogo["quantos"]:
            cor = VERDE
        pygame.draw.rect(ecra, cor, caixa, border_radius=12)
        escrever(str(quantos), "g", BRANCO, caixa.centerx, caixa.y + 16, "centro")
    escrever("Cada um fica no seu bocado", "p", CINZA, 200, 280, "centro")
    escrever("da imagem, e é só aí que", "p", CINZA, 200, 304, "centro")
    escrever("a sua mão manda.", "p", CINZA, 200, 328, "centro")

    # a camara inteira, com o bocado de cada um
    quadro = pygame.Rect(400, 150, 480, 360)
    if vista["inteira"] is not None:
        largura, altura = vista["inteira"].get_size()
        quadro.height = 480 * altura // largura
    for i in range(len(v["zonas"])):
        x0, y0, x1, y1 = v["zonas"][i]
        sitio = pygame.Rect(quadro.x + int(x0 * quadro.width), quadro.y + int(y0 * quadro.height),
                            int((x1 - x0) * quadro.width), int((y1 - y0) * quadro.height))
        cor = CORES_DOS_JOGADORES[i]
        desenhar_bocado(v, i, sitio.inflate(-8, -8), cor)
        escrever("J" + str(i + 1), "m", cor, sitio.x + 14, sitio.y + 10, "esquerda")

    if olho["ligada"] and not jogo["modo_teclado"]:
        if frame % 60 < 40:
            escrever("Fechem o punho", "g", VERDE, 200, 380, "centro")
        escrever("(ou Espaço)", "p", BRANCO, 200, 428, "centro")
    else:
        if frame % 60 < 40:
            escrever("Espaço para começar", "m", VERDE, 200, 380, "centro")
        if olho["erro"] != "":
            escrever(olho["erro"], "pp", LARANJA, 200, 420, "centro")
        escrever("Sem câmara: joga-se com o teclado.", "pp", LARANJA, 200, 440, "centro")
    escrever("C: outra câmara    T: teclado    F: ecrã inteiro    Esc: sair", "p", CINZA,
             20, ALTURA - 32, "esquerda")


def celula(indice):
    # O bocado do ecra de escolha de cada jogador: igual ao da camara.
    if jogo["quantos"] == 2:
        return pygame.Rect(indice * (LARGURA // 2), 0, LARGURA // 2, ALTURA)
    return pygame.Rect((indice % 2) * (LARGURA // 2), (indice // 2) * (ALTURA // 2),
                       LARGURA // 2, ALTURA // 2)


def desenhar_escolha(v):
    ecra = b.janela["ecra"]
    frame = b.jogo["frame"]
    ecra.fill((22, 24, 48))
    com_camara = olho["ligada"] and not jogo["modo_teclado"]
    for p in jogadores:
        indice = p["numero"] - 1
        m = v["maos"][indice]
        r = celula(indice).inflate(-10, -10)
        cor = cor_de(p)
        pygame.draw.rect(ecra, (cor[0] // 6 + 14, cor[1] // 6 + 14, cor[2] // 6 + 22), r, border_radius=14)
        pygame.draw.rect(ecra, cor, r, 4, border_radius=14)
        topo = r.y + (r.height - 278) // 2
        cx = r.centerx
        escrever("JOGADOR " + str(p["numero"]), "m", cor, cx, r.y + 8, "centro")
        if jogo["quantos"] == 2:
            bocado = pygame.Rect(r.x + 16, r.y + 16, 84, 126)
        else:
            bocado = pygame.Rect(r.x + 16, r.y + 16, 104, 78)
        desenhar_bocado(v, indice, bocado, cor)

        if not p["entrou"]:
            if com_camara:
                escrever("Mostra a mão", "g", BRANCO, cx, topo + 110, "centro")
                escrever("no teu canto da câmara", "p", CINZA, cx, topo + 160, "centro")
            else:
                escrever("Carrega numa tecla tua", "m", BRANCO, cx, topo + 110, "centro")
                escrever(TEXTO_DO_TECLADO[indice], "pp", CINZA, cx, topo + 150, "centro")
            continue

        pers = personagem_de(p)
        salto = 0
        if p["pronto"]:
            salto = int(abs(math.sin(frame * 0.15)) * 14)
        ecra.blit(retrato(pers, 2.5, frame, p["pronto"]), (cx - 80, topo + 40 - salto))
        # as setas: acendem quando a mao esta desse lado
        lado = 0
        if m["visivel"] and m["x"] < ZONA_ESQUERDA:
            lado = -1
        elif m["visivel"] and m["x"] > ZONA_DIREITA:
            lado = 1
        if not p["pronto"]:
            for sentido in (-1, 1):
                cor_seta = CINZA
                if lado == sentido:
                    cor_seta = AMARELO
                ponta = cx + sentido * 150
                pygame.draw.polygon(ecra, cor_seta, [(ponta, topo + 120), (ponta - sentido * 26, topo + 96),
                                                     (ponta - sentido * 26, topo + 144)])
        escrever(pers["nome"], "m", BRANCO, cx, topo + 200, "centro")
        escrever(pers["talento"], "p", AMARELO, cx, topo + 230, "centro")
        if p["pronto"]:
            escrever("PRONTO!", "m", VERDE, cx, topo + 40, "centro")
            if com_camara:
                escrever("aponta o dedo para mudar", "pp", CINZA, cx, topo + 256, "centro")
            else:
                escrever("tecla de parar para mudar", "pp", CINZA, cx, topo + 256, "centro")
        elif ocupada(p["personagem"], p):
            escrever("já tem dono: escolhe outra", "pp", LARANJA, cx, topo + 256, "centro")
        elif com_camara:
            escrever("mão para os lados: mudar    punho: escolher", "pp", BRANCO, cx, topo + 256, "centro")
        else:
            escrever("esquerda / direita: mudar    saltar: escolher", "pp", BRANCO, cx, topo + 256, "centro")

    if jogo["quantos"] == 3:
        r = celula(3)
        escrever("Escolham a personagem", "m", BRANCO, r.centerx, r.y + 90, "centro")
        escrever("Enter: começar já com quem está pronto", "p", CINZA, r.centerx, r.y + 140, "centro")
        escrever("Esc: voltar", "p", CINZA, r.centerx, r.y + 170, "centro")
    if jogo["arranque"] < 150:
        b.escurecer(90)
        escrever("Todos prontos!", "g", BRANCO, LARGURA // 2, ALTURA // 2 - 100, "centro")
        escrever(str(jogo["arranque"] // 50 + 1), "gg", VERDE, LARGURA // 2, ALTURA // 2 - 50, "centro")


# =====================================================================
# N. O CICLO PRINCIPAL
# =====================================================================
def toques_vazios():
    lista = []
    for i in range(4):
        lista.append({"esq": False, "dir": False, "salto": False, "parar": False})
    return lista


def ir_para_o_titulo():
    jogo["fase"] = "titulo"
    for p in jogadores:
        p["entrou"] = False
        p["pronto"] = False
        p["joga"] = False


def logica(v, toques, confirmou, forcar):
    # Um frame de logica. toques: as teclas de cada jogador neste frame.
    # confirmou: alguem fechou o punho, ou carregou em Espaco ou em Enter.
    b.jogo["frame"] += 1
    if jogo["espera"] > 0:
        jogo["espera"] -= 1

    # o punho de cada jogador
    saltos = []
    for p in jogadores:
        m = v["maos"][p["numero"] - 1]
        saltou = toques[p["numero"] - 1]["salto"]
        if m["saltos"] != p["saltos_vistos"]:
            p["saltos_vistos"] = m["saltos"]
            if not jogo["modo_teclado"]:
                saltou = True
        saltos.append(saltou)

    fase = jogo["fase"]
    if fase == "titulo":
        if confirmou:
            jogo["fase"] = "escolha"
            jogo["arranque"] = 150
            for p in jogadores:
                p["entrou"] = False
                p["pronto"] = False
    elif fase == "escolha":
        atualizar_escolha(v, toques, saltos, forcar)
    elif fase == "contagem":
        ronda["contagem"] -= 1
        if ronda["contagem"] % 60 == 0 and 0 < ronda["contagem"] <= 180:
            tocar("toque")
        if ronda["contagem"] <= 0:
            jogo["fase"] = "jogar"
            dizer("JÁ!")
            tocar("controlo")
    elif fase == "jogar":
        teclas = pygame.key.get_pressed()
        comandos = {}
        for p in jogadores:
            i = p["numero"] - 1
            comandos[p["numero"]] = ler_comando(p, v["maos"][i], teclas, saltos[i])
        passo_da_ronda(comandos)
    elif fase == "ronda_fim":
        b.atualizar_particulas()
        if confirmou and jogo["espera"] == 0:
            if ronda["indice"] + 1 < len(RONDAS):
                comecar_ronda(ronda["indice"] + 1)
            else:
                jogo["fase"] = "podio"
                jogo["espera"] = 120
    elif fase == "podio":
        if confirmou and jogo["espera"] == 0:
            ir_para_o_titulo()


def desenhar(v):
    atualizar_vista(v)
    fase = jogo["fase"]
    if fase == "titulo":
        desenhar_titulo(v)
    elif fase == "escolha":
        desenhar_escolha(v)
    elif fase == "podio":
        desenhar_podio()
    else:
        desenhar_ronda(v)
        if fase == "contagem":
            desenhar_contagem()
        elif fase == "pausa":
            b.escurecer(170)
            escrever("PAUSA", "gg", BRANCO, LARGURA // 2, 150, "centro")
            escrever("P: continuar      Esc: voltar ao título", "m", BRANCO, LARGURA // 2, 300, "centro")
        elif fase == "ronda_fim":
            desenhar_fim_da_ronda()
    if jogo["aviso_tempo"] > 0:
        jogo["aviso_tempo"] -= 1
        escrever(jogo["aviso"], "p", LARANJA, LARGURA // 2, ALTURA - 60, "centro")


def avisar(texto):
    jogo["aviso"] = texto
    jogo["aviso_tempo"] = 360
    print(texto)


def preparar_letras():
    b.fontes["pp"] = pygame.font.SysFont(None, 22)
    b.fontes["p"] = pygame.font.SysFont(None, 26)
    b.fontes["m"] = pygame.font.SysFont(None, 34)
    b.fontes["g"] = pygame.font.SysFont(None, 56)
    b.fontes["gg"] = pygame.font.SysFont(None, 110)


def main():
    pygame.mixer.pre_init(22050, -16, 1, 512)
    pygame.init()
    b.criar_janela(ECRA_INTEIRO)
    pygame.display.set_caption(TITULO)
    ecra = b.janela["ecra"]
    preparar_letras()
    try:
        b.criar_sons()
    except Exception:
        b.sons.clear()          # sem som joga-se na mesma
    relogio = pygame.time.Clock()
    definir_jogadores(max(2, min(4, JOGADORES)))

    ecra.fill((22, 24, 48))
    escrever("A ligar a câmara...", "g", BRANCO, LARGURA // 2, ALTURA // 2 - 30, "centro")
    if sys.platform == "darwin" and not b.SO_TECLADO:
        escrever("Se o Mac perguntar, autoriza o Terminal a usar a câmara.", "m", AMARELO,
                 LARGURA // 2, ALTURA // 2 + 40, "centro")
    pygame.display.flip()
    pygame.event.pump()
    if b.SO_TECLADO or not ligar_camara(CAMARA, True):
        jogo["modo_teclado"] = True
        if olho["erro"] != "":
            print("Sem câmara: " + olho["erro"] + " Joga-se com o teclado.")

    a_correr = True
    while a_correr:
        toques = toques_vazios()
        confirmou = False
        forcar = False
        fase = jogo["fase"]
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                a_correr = False
            elif evento.type == pygame.MOUSEBUTTONDOWN and fase == "titulo":
                # clicar num dos botoes 2, 3, 4
                for quantos in (2, 3, 4):
                    if caixa_de_quantos(quantos).collidepoint(evento.pos):
                        if quantos != jogo["quantos"]:
                            definir_jogadores(quantos)
                        tocar("toque")
            elif evento.type == pygame.KEYDOWN:
                tecla = evento.key
                for i in range(4):
                    for nome in ("esq", "dir", "salto", "parar"):
                        if tecla == TECLADO[i][nome]:
                            toques[i][nome] = True
                if tecla == pygame.K_ESCAPE:
                    if fase == "titulo":
                        a_correr = False
                    else:
                        ir_para_o_titulo()
                elif tecla == pygame.K_f or tecla == pygame.K_F11:
                    b.criar_janela(not b.janela["inteiro"])
                elif tecla == pygame.K_SPACE:
                    confirmou = True
                    toques[0]["salto"] = True       # o Espaco tambem e o salto do J1
                elif tecla == pygame.K_RETURN or tecla == pygame.K_KP_ENTER:
                    confirmou = True
                    forcar = True
                elif tecla == pygame.K_p:
                    if fase == "jogar":
                        jogo["fase"] = "pausa"
                    elif fase == "pausa":
                        jogo["fase"] = "jogar"
                elif tecla == pygame.K_t:
                    jogo["modo_teclado"] = not jogo["modo_teclado"]
                    if not olho["ligada"]:
                        jogo["modo_teclado"] = True
                elif tecla == pygame.K_c and b.HA_BIBLIOTECAS_DA_CAMARA:
                    if ligar_camara(olho["indice"] + 1, False) or ligar_camara(0, False):
                        jogo["modo_teclado"] = False
                        avisar("Câmara " + str(olho["indice"]))
                    else:
                        jogo["modo_teclado"] = True
                elif tecla == pygame.K_n and fase == "jogar":
                    acabar_ronda()              # atalho do professor
                elif fase == "titulo" and tecla in (pygame.K_2, pygame.K_3, pygame.K_4,
                                                    pygame.K_KP2, pygame.K_KP3, pygame.K_KP4):
                    quantos = {pygame.K_2: 2, pygame.K_3: 3, pygame.K_4: 4,
                               pygame.K_KP2: 2, pygame.K_KP3: 3, pygame.K_KP4: 4}[tecla]
                    definir_jogadores(quantos)

        v = ler_olho()
        # um punho fechado por qualquer jogador serve para confirmar
        if v["saltos"] != jogo["saltos_vistos"]:
            jogo["saltos_vistos"] = v["saltos"]
            if not jogo["modo_teclado"]:
                confirmou = True
        if camara["fio"] is not None and not v["ligada"]:
            desligar_camara()           # a camara foi-se abaixo a meio
            jogo["modo_teclado"] = True
            avisar(olho["erro"] + " Joga-se com o teclado.")

        logica(v, toques, confirmou, forcar)
        desenhar(v)
        pygame.display.flip()
        relogio.tick(FPS)

    desligar_camara()
    pygame.quit()


if __name__ == "__main__":
    main()
