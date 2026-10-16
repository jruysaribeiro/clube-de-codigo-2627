# S10 — FADO//NEON
# Um roguelite twin-stick de saudade e neon.
# Jogo do Ano 2026 (segundo o proprio jogo).
#
# A sessao 9 disse: "escolher pequeno e uma competencia, nao uma desistencia".
# Este ficheiro leu isso e decidiu ignorar.
#
# Zero assets: o som, a musica, os graficos e a saudade sao todos gerados
# por codigo. So precisa de pygame-ce.
#
# Joga-se so com o teclado (o rato tambem funciona, se quiseres):
#   WASD                mover               Setas           disparar nessa direcao
#   Espaco / Shift      investida (dash)    E               LASER (quando o farol encher)
#   1 2 3 / setas+Enter escolher melhoria   Esc / P         pausa
#   T  tiro automatico   F  ecra inteiro   M  musica   B  bloom   C  CRT   F3  FPS
#   Com rato: apontar com o rato, clique esquerdo dispara, direito investe, meio laser.
#
# Como se ganha: sobrevive a 10 ondas. O Saudosista aparece na 5 e na 10.
# Depois podes continuar no modo infinito, que a saudade nao acaba.

import array
import math
import random

import pygame
from pygame import Vector2

# --- Constantes: e aqui que se mexe primeiro (como sempre) ---
LARGURA = 960
ALTURA = 540
FPS = 60
CENTRO = Vector2(LARGURA / 2, ALTURA / 2)
TAU = math.tau
ONDAS_TOTAIS = 10

FUNDO = (7, 5, 16)
BRANCO = (240, 240, 255)
CIANO = (50, 235, 255)
ROSA = (255, 55, 165)
AMARELO = (255, 205, 70)
ROXO = (155, 95, 255)
VERDE = (80, 255, 160)
VERMELHO = (255, 60, 80)
LARANJA = (255, 140, 50)
CINZENTO = (120, 115, 150)

CORES_RARIDADE = {1: CIANO, 2: ROXO, 3: AMARELO}
NOMES_RARIDADE = {1: "COMUM", 2: "RARA", 3: "LENDÁRIA"}
PESOS_RARIDADE = {1: 6, 2: 3, 3: 1}

# id, nome, descricao, raridade, unica
MELHORIAS = [
    ("guitarra", "Guitarra Portuguesa", "+1 projétil. Doze cordas, doze balas.", 2, False),
    ("cafe", "Café Duplo", "Disparas 20% mais depressa. Não dormes.", 1, False),
    ("calcada", "Calçada", "As balas atravessam mais 1 inimigo.", 1, False),
    ("eletrico", "Elétrico 28", "As balas fazem ricochete nas paredes.", 2, False),
    ("nata", "Pastel de Nata", "+1 coração máximo e cura total.", 1, False),
    ("saudade", "Saudade Afiada", "+30% de dano. Dói mais.", 1, False),
    ("gaivota", "Gaivota Orbital", "Uma gaivota roda à tua volta e morde.", 2, False),
    ("bacalhau", "Bacalhau Crítico", "+12% de crítico (dano x2.5).", 1, False),
    ("vira", "Vira do Minho", "A investida rebenta com tudo à volta.", 3, True),
    ("azulejo", "Azulejo", "Balas maiores e +10% de dano.", 1, False),
    ("sardinha", "Sardinha Teleguiada", "As balas perseguem os inimigos.", 3, True),
    ("ginjinha", "Ginjinha", "+12% velocidade, investida recarrega mais rápido.", 1, False),
    ("fado", "Fado Vampiro", "10% de hipótese de curar ao matar.", 2, False),
    ("bugio", "Farol do Bugio", "O laser dura +40% e carrega 30% mais depressa.", 2, False),
]

CONQUISTAS = {
    "abrir": ("Abriste o jogo", "O mais difícil está feito."),
    "sangue": ("Primeiro sangue", "Metafórico. Isto é neon."),
    "combo10": ("Combo x10", "Os teus dedos estão bem?"),
    "combo25": ("Combo x25", "Já podes ir para a final."),
    "dash": ("Vira do Minho", "50 investidas. Que tontura."),
    "chefe": ("Adeus, Saudosista", "Mas ele volta sempre."),
    "morte": ("Morreste", "Muito indie. Muito arte."),
    "auto": ("Acessibilidade", "Tiro automático ligado. Respeito."),
    "nata": ("Guloso", "Três pastéis de nata."),
    "onda10": ("Onda 10", "A sessão 9 recomendava 30 segundos."),
    "raspao": ("Por um fio", "25 raspões em balas inimigas."),
    "laser": ("Farol aceso", "Disparaste o laser. Finalmente."),
    "vitoria": ("Fim?", "Ganhaste. A saudade, essa, fica."),
}

CREDITOS = [
    "FADO//NEON",
    "",
    "Programação  —  um ficheiro só",
    "Música  —  math.sin, com muito sentimento",
    "Arte  —  pygame.draw.polygon",
    "Física da grelha  —  molas imaginárias",
    "Controlo de qualidade  —  o tiro automático",
    "Lasers  —  porque alguém perguntou",
    "Agradecimentos especiais  —  à sessão 9, que bem avisou",
    "",
    "Obrigado por jogares.",
]

CRITICAS = [
    "«Ignorou por completo o conselho de escolher pequeno.»  — NOTAS.md, Sessão 9  — 10/10",
    "«Chorei. Depois morri. Depois chorei outra vez.»  — Um aluno do 8.º B  — 10/10",
    "«Tem mais linhas do que as outras sessões todas juntas.»  — O professor  — 9/10",
    "«Jogo do Ano 2026.»  — O próprio jogo  — 11/10",
    "«Não usa assets. Usa saudade.»  — Revista Pixel & Bacalhau  — 10/10",
    "«Faltou o modo multijogador online.»  — Ninguém  — 3/10",
]

FRASES_ONDA = [
    "As gaivotas estão inquietas.",
    "Cheira a sardinha assada.",
    "Alguém chora num elétrico.",
    "O nevoeiro traz mais deles.",
    "A guitarra desafina.",
    "Ninguém volta igual de Alfama.",
    "O D. Sebastião não vem ajudar.",
]

PERFIS = {
    # raio, vida, velocidade, cor, lados, pontos
    "corredor": (12, 20, 150, ROSA, 3, 10),
    "atirador": (15, 34, 90, LARANJA, 4, 20),
    "divisor": (24, 60, 60, VERDE, 6, 25),
    "pequeno": (12, 16, 125, VERDE, 6, 8),
    "investida": (14, 40, 70, ROXO, 4, 25),
}

# ======================================================================
#  SOM: tudo sintetizado amostra a amostra. Sem numpy, sem ficheiros.
# ======================================================================
TAXA = 22050
SONS = {}
ULTIMO_SOM = {}


def para_som(mono):
    canais = pygame.mixer.get_init()[2]
    a = array.array("h", (int(max(-1.0, min(1.0, v)) * 32000) for v in mono))
    if canais > 1:
        multi = array.array("h", bytes(len(a) * 2 * canais))
        for c in range(canais):
            multi[c::canais] = a
        a = multi
    return pygame.mixer.Sound(buffer=a)


def gerar_varrimento(duracao, f0, f1, forma, ruido=0.0, volume=0.5):
    n = int(TAXA * duracao)
    out = [0.0] * n
    fase = 0.0
    for i in range(n):
        p = i / n
        fase += (f0 + (f1 - f0) * p) / TAXA
        c = fase % 1.0
        if forma == "quadrada":
            v = 1.0 if c < 0.5 else -1.0
        elif forma == "serra":
            v = 2 * c - 1
        elif forma == "triangulo":
            v = 4 * abs(c - 0.5) - 1
        else:
            v = math.sin(TAU * c)
        if ruido:
            v = v * (1 - ruido) + (random.random() * 2 - 1) * ruido
        ataque = min(1.0, i / 40)
        out[i] = v * ataque * (1 - p) ** 2 * volume
    return out


def gerar_explosao(duracao, volume=0.7, grave=55):
    n = int(TAXA * duracao)
    out = [0.0] * n
    filtro = 0.0
    for i in range(n):
        p = i / n
        t = i / TAXA
        filtro += (random.random() * 2 - 1 - filtro) * (0.5 * (1 - p) ** 2 + 0.02)
        pancada = math.sin(TAU * grave * t * (1 - p * 0.5)) * math.exp(-t * 12)
        out[i] = (filtro * 1.6 + pancada * 0.9) * (1 - p) ** 1.5 * volume
    return out


def gerar_laser(duracao, volume=0.35):
    n = int(TAXA * duracao)
    out = [0.0] * n
    fase = 0.0
    for i in range(n):
        p = i / n
        t = i / TAXA
        fase += (110 + math.sin(t * TAU * 9) * 12 + p * 40) / TAXA
        v = (2 * (fase % 1) - 1) * 0.6 + math.sin(TAU * fase * 2.01) * 0.3 + (random.random() * 2 - 1) * 0.15
        out[i] = v * min(1.0, t * 30) * min(1.0, (1 - p) * 6) * volume
    return out


def gerar_arpejo(notas, duracao_nota, forma="quadrada", volume=0.3):
    out = []
    for f in notas:
        out += gerar_varrimento(duracao_nota, f, f * 1.01, forma, volume=volume)
    return out


def compor_musica():
    # Lá menor, Fá, Dó, Mi: a cadência andaluza. O fado agradece.
    bpm = 112
    passo = 60 / bpm / 4
    amostras_passo = passo * TAXA
    n = int(amostras_passo * 64)
    acordes = [
        (110.0, (220.0, 261.63, 329.63)),
        (87.31, (174.61, 220.0, 261.63)),
        (130.81, (261.63, 329.63, 392.0)),
        (82.41, (164.81, 207.65, 246.94)),
    ]
    padrao = [0, 1, 2, 1, 0, 2, 1, 2, 0, 1, 2, 0, 2, 1, 0, 1]
    base = [0.0] * n
    arp = [0.0] * n
    filtro = 0.0
    prato_antes = 0.0
    for i in range(n):
        t = i / TAXA
        k = int(i / amostras_passo)
        dentro = (i - k * amostras_passo) / TAXA
        raiz, triade = acordes[(k // 16) % 4]
        s = 0.0
        if k % 4 == 0:  # bombo
            s += math.sin(TAU * (45 + 90 * math.exp(-dentro * 30)) * dentro) * math.exp(-dentro * 9) * 0.9
        if k % 8 == 4:  # palmas
            s += (random.random() * 2 - 1) * math.exp(-dentro * 25) * 0.3
        if k % 2 == 1:  # pratos
            r = random.random() * 2 - 1
            s += (r - prato_antes) * math.exp(-dentro * 70) * 0.1
            prato_antes = r
        # baixo em colcheias, com um salto de oitava no fim de cada compasso
        desde_colcheia = dentro + (passo if k % 2 else 0)
        fb = raiz * 2 if (k // 2) % 8 == 7 else raiz
        filtro += ((2 * ((fb * t) % 1) - 1) - filtro) * 0.12
        s += filtro * math.exp(-desde_colcheia * 5) * 0.5
        s += (math.sin(TAU * triade[0] * t) + math.sin(TAU * triade[1] * t * 1.003)
              + math.sin(TAU * triade[2] * t * 0.997)) * 0.03
        base[i] = s
        nota = triade[padrao[k % 16]] * (4 if k % 16 >= 12 else 2)
        arp[i] = (1.0 if (nota * t) % 1 < 0.3 else -1.0) * math.exp(-dentro * 14) * 0.09
    # Eco de tres passos no arpejo. Da a volta ao fim para o loop nao ter costura.
    atraso = int(amostras_passo * 3)
    for i in range(n):
        arp[i] += arp[i - atraso] * 0.4
    return [math.tanh((base[i] + arp[i]) * 1.2) * 0.75 for i in range(n)]


def tocar(nome, volume=1.0):
    if nome not in SONS:
        return
    agora = pygame.time.get_ticks()
    if agora - ULTIMO_SOM.get(nome, -1000) < 35:
        return  # vinte tiros no mesmo frame nao soam melhor, so mais alto
    ULTIMO_SOM[nome] = agora
    som = random.choice(SONS[nome])
    canal = som.play()
    if canal is not None:
        canal.set_volume(volume)


# ======================================================================
#  AJUDANTES DE DESENHO
# ======================================================================
FONTES = {}


def fonte(tamanho):
    if tamanho not in FONTES:
        FONTES[tamanho] = pygame.font.Font(None, tamanho)
    return FONTES[tamanho]


def escrever(surf, texto, tamanho, pos, cor=BRANCO, ancora="center", alpha=255):
    img = fonte(tamanho).render(texto, True, cor)
    if alpha < 255:
        img.set_alpha(max(0, int(alpha)))
    r = img.get_rect(**{ancora: (int(pos[0]), int(pos[1]))})
    surf.blit(img, r)
    return r


def escrever_glitch(surf, texto, tamanho, pos, forca):
    # Aberracao cromatica "a mao": tres copias do texto, uma por canal de cor.
    base = fonte(tamanho).render(texto, True, BRANCO, (0, 0, 0))
    r = base.get_rect(center=(int(pos[0]), int(pos[1])))
    for cor, dx in (((255, 30, 90), -forca), ((40, 255, 120), 0), ((60, 120, 255), forca)):
        canal = base.copy()
        canal.fill(cor, special_flags=pygame.BLEND_RGB_MULT)
        dy = random.randint(-1, 1) if forca > 3 else 0
        surf.blit(canal, r.move(dx, dy), special_flags=pygame.BLEND_ADD)


def poligono(centro, raio, lados, angulo):
    return [(centro[0] + math.cos(angulo + k * TAU / lados) * raio,
             centro[1] + math.sin(angulo + k * TAU / lados) * raio) for k in range(lados)]


def coracao(surf, centro, tam, cor, cheio):
    x, y = centro
    pontos = [(x, y + tam)]
    for k in range(21):
        a = math.pi * k / 20
        pontos.append((x - tam * 0.5 - math.cos(a) * tam * 0.5, y - math.sin(a) * tam * 0.55))
    for k in range(21):
        a = math.pi * k / 20
        pontos.append((x + tam * 0.5 - math.cos(a) * tam * 0.5, y - math.sin(a) * tam * 0.55))
    pygame.draw.polygon(surf, cor, pontos, 0 if cheio else 2)


def dist_segmento(p, a, b):
    # Distancia de um ponto a um segmento de reta. E assim que um laser acerta.
    ab = b - a
    t = max(0.0, min(1.0, (p - a).dot(ab) / (ab.length_squared() or 1)))
    return p.distance_to(a + ab * t)


def misturar(a, b, t):
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0] - a[0]) * t), int(a[1] + (b[1] - a[1]) * t), int(a[2] + (b[2] - a[2]) * t))


def suavizar(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


# ======================================================================
#  A GRELHA: uma malha de molas que ondula com as explosoes.
# ======================================================================
class Grelha:
    def __init__(self, espaco=36):
        self.esp = espaco
        self.nx = LARGURA // espaco + 2
        self.ny = ALTURA // espaco + 2
        n = self.nx * self.ny
        self.dx = [0.0] * n
        self.dy = [0.0] * n
        self.vx = [0.0] * n
        self.vy = [0.0] * n
        self.cores = [misturar((22, 16, 52), (120, 80, 255), k / 7) for k in range(8)]

    def impulso(self, pos, forca, raio):
        e = self.esp
        i0 = max(1, int((pos[0] - raio) / e))
        i1 = min(self.nx - 2, int((pos[0] + raio) / e) + 1)
        j0 = max(1, int((pos[1] - raio) / e))
        j1 = min(self.ny - 2, int((pos[1] + raio) / e) + 1)
        for j in range(j0, j1 + 1):
            for i in range(i0, i1 + 1):
                k = j * self.nx + i
                ox = i * e + self.dx[k] - pos[0]
                oy = j * e + self.dy[k] - pos[1]
                d = math.hypot(ox, oy)
                if 0.01 < d < raio:
                    f = forca * (1 - d / raio)
                    self.vx[k] += ox / d * f
                    self.vy[k] += oy / d * f

    def atualizar(self, dt):
        nx = self.nx
        dx, dy, vx, vy = self.dx, self.dy, self.vx, self.vy
        amort = 0.06 ** dt
        for j in range(1, self.ny - 1):
            for i in range(1, nx - 1):
                k = j * nx + i
                lx = (dx[k - 1] + dx[k + 1] + dx[k - nx] + dx[k + nx]) * 0.25 - dx[k]
                ly = (dy[k - 1] + dy[k + 1] + dy[k - nx] + dy[k + nx]) * 0.25 - dy[k]
                vx[k] = (vx[k] + (-30 * dx[k] + 260 * lx) * dt) * amort
                vy[k] = (vy[k] + (-30 * dy[k] + 260 * ly) * dt) * amort
        for k in range(len(dx)):
            dx[k] = max(-40.0, min(40.0, dx[k] + vx[k] * dt))
            dy[k] = max(-40.0, min(40.0, dy[k] + vy[k] * dt))

    def desenhar(self, surf, cam):
        e, nx = self.esp, self.nx
        pts = []
        brilho = []
        for j in range(self.ny):
            for i in range(nx):
                k = j * nx + i
                pts.append((i * e + self.dx[k] - cam.x, j * e + self.dy[k] - cam.y))
                brilho.append(min(7, int((abs(self.dx[k]) + abs(self.dy[k])) / 3) + (1 if i % 4 == 0 or j % 4 == 0 else 0)))
        linha = pygame.draw.line
        for j in range(self.ny):
            for i in range(nx):
                k = j * nx + i
                if i < nx - 1:
                    linha(surf, self.cores[brilho[k]], pts[k], pts[k + 1])
                if j < self.ny - 1:
                    linha(surf, self.cores[brilho[k]], pts[k], pts[k + nx])


# ======================================================================
#  AS COISAS QUE EXISTEM NO MUNDO
# ======================================================================
class Particula:
    __slots__ = ("pos", "vel", "vida", "vida_max", "cor", "tam", "atrito", "faisca")

    def __init__(self, pos, vel, vida, cor, tam=2.0, atrito=3.0, faisca=True):
        self.pos = Vector2(pos)
        self.vel = Vector2(vel)
        self.vida = self.vida_max = vida
        self.cor = cor
        self.tam = tam
        self.atrito = atrito
        self.faisca = faisca


class Bala:
    __slots__ = ("pos", "vel", "dano", "raio", "cor", "perfura", "ricochete",
                 "teleguiada", "atingidos", "vida", "critica", "raspada")

    def __init__(self, pos, vel, dano, raio, cor):
        self.pos = Vector2(pos)
        self.vel = Vector2(vel)
        self.dano = dano
        self.raio = raio
        self.cor = cor
        self.perfura = 0
        self.ricochete = 0
        self.teleguiada = False
        self.atingidos = set()
        self.vida = 4.0
        self.critica = False
        self.raspada = False


class Texto:
    __slots__ = ("pos", "texto", "cor", "tam", "vida", "vida_max")

    def __init__(self, pos, texto, cor, tam=22, vida=0.7):
        self.pos = Vector2(pos) + Vector2(random.uniform(-8, 8), 0)
        self.texto = texto
        self.cor = cor
        self.tam = tam
        self.vida = self.vida_max = vida


class Recompensa:
    def __init__(self, pos, tipo):
        self.pos = Vector2(pos)
        self.vel = Vector2(random.uniform(-1, 1), random.uniform(-1, 1)) * random.uniform(60, 220)
        self.tipo = tipo  # "nota" ou "coracao"
        self.vida = 9.0
        self.ang = random.uniform(0, TAU)


class Aviso:
    # Um inimigo nunca aparece sem avisar. E uma questao de educacao.
    def __init__(self, pos, tipo):
        self.pos = Vector2(pos)
        self.tipo = tipo
        self.t = 0.9


class Jogador:
    def __init__(self):
        self.pos = Vector2(CENTRO)
        self.vel = Vector2()
        self.raio = 10
        self.ang = 0.0
        self.vida_max = 5
        self.vida = 5
        self.invulneravel = 0.0
        self.dash_t = 0.0
        self.dash_cd = 0.0
        self.dash_recarga = 0.6
        self.dash_dir = Vector2(1, 0)
        self.fantasmas = []
        self.cd_tiro = 0.0
        self.intervalo = 0.15
        self.multi = 1
        self.dano = 10.0
        self.perfura = 0
        self.ricochete = 0
        self.critico = 0.05
        self.tam_bala = 4.0
        self.teleguiada = False
        self.orbes = 0
        self.vira = False
        self.velocidade = 270.0
        self.vampiro = 0.0
        self.laser_duracao = 1.6
        self.farol_ganho = 1.0
        self.coice = 0.0
        self.melhorias = {}

    @property
    def a_investir(self):
        return self.dash_t > 0


class Inimigo:
    def __init__(self, tipo, pos, onda):
        raio, vida, vel, cor, lados, valor = PERFIS[tipo]
        self.tipo = tipo
        self.pos = Vector2(pos)
        self.raio = raio
        self.vida_max = self.vida = vida * (1 + 0.09 * (onda - 1))
        self.velocidade = vel * min(1.6, 1 + 0.025 * (onda - 1))
        self.cor = cor
        self.lados = lados
        self.valor = valor
        self.ang = random.uniform(0, TAU)
        self.t = random.uniform(0, 5)
        self.flash = 0.0
        self.empurrao = Vector2()
        self.cd_orbe = 0.0
        self.cd_laser = 0.0
        self.cd_tiro = random.uniform(1.0, 2.2)
        self.estado = "vaguear"
        self.estado_t = random.uniform(1.0, 2.0)
        self.direcao = Vector2(1, 0)
        self.onda = onda
        self.chefe = False

    def atualizar(self, jogo, dt):
        self.t += dt
        self.flash -= dt
        self.cd_orbe -= dt
        self.cd_laser -= dt
        alvo = jogo.jogador.pos
        para = alvo - self.pos
        dist = para.length() or 1
        dirc = para / dist
        mov = Vector2()
        if self.tipo == "corredor":
            mov = dirc * self.velocidade
            self.ang = math.atan2(dirc.y, dirc.x)
        elif self.tipo in ("divisor", "pequeno"):
            mov = dirc.rotate(math.sin(self.t * 2) * 35) * self.velocidade
            self.ang += dt * 1.2
        elif self.tipo == "atirador":
            lado = dirc.rotate(90) * math.sin(self.t * 0.7)
            mov = (dirc * (1 if dist > 280 else -1 if dist < 220 else 0) + lado * 0.8) * self.velocidade
            self.ang += dt * 2
            self.cd_tiro -= dt
            if self.cd_tiro <= 0:
                self.cd_tiro = random.uniform(1.6, 2.4)
                quantas = 1 if self.onda < 6 else 3
                for k in range(quantas):
                    a = dirc.rotate((k - (quantas - 1) / 2) * 14)
                    jogo.bala_inimiga(self.pos + a * self.raio, a * 210, LARANJA)
                tocar("inimigo_tiro", 0.4)
        elif self.tipo == "investida":
            self.estado_t -= dt
            if self.estado == "vaguear":
                mov = dirc * self.velocidade
                self.ang = math.atan2(dirc.y, dirc.x)
                if self.estado_t <= 0:
                    self.estado, self.estado_t, self.direcao = "mirar", 0.6, dirc
            elif self.estado == "mirar":
                self.ang += dt * 20
                if self.estado_t <= 0:
                    self.estado, self.estado_t = "carregar", 0.45
                    tocar("investida", 0.5)
            elif self.estado == "carregar":
                mov = self.direcao * 640
                if random.random() < 0.6:
                    jogo.particula(self.pos, -self.direcao * 80, 0.3, ROXO, 3)
                if self.estado_t <= 0:
                    self.estado, self.estado_t = "vaguear", random.uniform(1.2, 2.2)
        self.pos += (mov + self.empurrao) * dt
        self.empurrao *= 0.002 ** dt
        self.pos.x = max(self.raio, min(LARGURA - self.raio, self.pos.x))
        self.pos.y = max(self.raio, min(ALTURA - self.raio, self.pos.y))

    def desenhar(self, surf, cam):
        p = self.pos - cam
        cor = BRANCO if self.flash > 0 else self.cor
        escala = 1 + max(0, self.flash) * 3
        if self.tipo == "investida" and self.estado == "mirar":
            fim = p + self.direcao * 640 * 0.45
            if int(self.t * 20) % 2:
                pygame.draw.line(surf, (120, 40, 70), p, fim, 2)
        if self.tipo == "atirador" and self.cd_tiro < 0.35:
            pygame.draw.circle(surf, AMARELO, p, (0.35 - self.cd_tiro) * 22, 2)
        lados = self.lados
        raio = self.raio * escala
        if self.tipo == "investida":
            pts = poligono(p, raio, 4, self.ang)
            pts[0] = (p.x + math.cos(self.ang) * raio * 1.6, p.y + math.sin(self.ang) * raio * 1.6)
        else:
            pts = poligono(p, raio, lados, self.ang)
        pygame.draw.polygon(surf, misturar(cor, FUNDO, 0.75), pts)
        pygame.draw.polygon(surf, cor, pts, 2)
        pygame.draw.polygon(surf, cor, poligono(p, raio * 0.4, lados, -self.ang * 1.5), 1)


class Chefe(Inimigo):
    PADROES = ["espiral", "farol", "aneis", "rajada", "invocar"]

    def __init__(self, onda):
        super().__init__("corredor", (LARGURA / 2, -90), onda)
        self.chefe = True
        self.tipo = "chefe"
        self.raio = 44
        self.vida_max = self.vida = 1100 * (1 + 0.7 * (onda // 5 - 1))
        self.vida_rasto = self.vida
        self.cor = ROSA
        self.valor = 1000
        self.fase = 1
        self.padrao = "espera"
        self.padrao_t = 1.0
        self.ordem = 0
        self.cd = 0.0
        self.espiral = 0.0
        self.lasers = []
        self.laser_aviso = 0.0
        self.final = onda == ONDAS_TOTAIS

    def atualizar(self, jogo, dt):
        self.t += dt
        self.flash -= dt
        self.cd_orbe -= dt
        self.cd_laser -= dt
        self.ang += dt * (0.8 if self.fase == 1 else 1.8)
        self.vida_rasto += (self.vida - self.vida_rasto) * min(1, dt * 2)
        alvo = Vector2(LARGURA / 2 + math.sin(self.t * 0.45) * 300, ALTURA * 0.33 + math.sin(self.t * 0.9) * 70)
        self.pos += (alvo - self.pos) * min(1, dt * 1.3) + self.empurrao * dt
        self.empurrao *= 0.01 ** dt
        if jogo.fase == "chefe_intro":
            return
        if self.fase == 1 and self.vida < self.vida_max / 2:
            self.fase = 2
            self.cor = AMARELO
            jogo.mudanca_de_fase(self)
        f2 = self.fase == 2
        self.padrao_t -= dt
        self.cd -= dt
        para = jogo.jogador.pos - self.pos
        mira = para.normalize() if para.length() > 0 else Vector2(0, 1)
        if self.padrao_t <= 0:
            if self.padrao == "espera":
                self.padrao = self.PADROES[self.ordem % len(self.PADROES)]
                self.ordem += 1
                self.padrao_t = 3.6
                self.cd = 0
                if self.padrao == "farol":
                    n = (4 if self.final else 3) if f2 else 2
                    base = math.atan2(mira.y, mira.x) + math.pi / n
                    self.lasers = [base + k * TAU / n for k in range(n)]
                    self.laser_aviso = 1.1
                    tocar("carga", 0.7)
                if self.padrao == "invocar":
                    for k in range(5 if f2 else 3):
                        a = Vector2(1, 0).rotate(k * 360 / (5 if f2 else 3) + random.uniform(0, 60))
                        pos = self.pos + a * 120
                        pos.x = max(30, min(LARGURA - 30, pos.x))
                        pos.y = max(30, min(ALTURA - 30, pos.y))
                        jogo.avisos.append(Aviso(pos, random.choice(["corredor", "corredor", "investida"])))
            else:
                self.padrao = "espera"
                self.padrao_t = 0.9 if f2 else 1.3
                self.lasers = []
        if self.padrao == "farol" and self.lasers:
            # O farol: avisa com linhas finas, depois varre a arena com raios.
            antes = self.laser_aviso
            self.laser_aviso -= dt
            if antes > 0 >= self.laser_aviso:
                tocar("laser_chefe", 0.8)
                jogo.trauma = max(jogo.trauma, 0.5)
            rodar = 0.15 if self.laser_aviso > 0 else (0.75 if f2 else 0.5)
            self.lasers = [a + rodar * dt for a in self.lasers]
            if self.laser_aviso <= 0:
                j = jogo.jogador
                for a in self.lasers:
                    fim = self.pos + Vector2(math.cos(a), math.sin(a)) * 1300
                    if dist_segmento(j.pos, self.pos, fim) < 11 + j.raio:
                        jogo.ferir_jogador(self.pos)
                    if random.random() < 0.5:
                        ponto = self.pos.lerp(fim, random.random() * 0.6)
                        jogo.particula(ponto, Vector2(random.uniform(-1, 1), random.uniform(-1, 1)) * 200, 0.3, self.cor, 2)
        elif self.padrao == "espiral" and self.cd <= 0:
            self.cd = 0.05 if f2 else 0.075
            bracos = 5 if f2 else 3
            self.espiral += 0.21
            for b in range(bracos):
                for sentido in ((1, -1) if f2 else (1,)):
                    a = self.espiral * sentido + b * TAU / bracos
                    d = Vector2(math.cos(a), math.sin(a))
                    jogo.bala_inimiga(self.pos + d * self.raio, d * 165, self.cor)
            tocar("inimigo_tiro", 0.15)
        elif self.padrao == "aneis" and self.cd <= 0:
            self.cd = 0.55 if f2 else 0.75
            n = 30 if f2 else 22
            desvio = random.uniform(0, TAU)
            for k in range(n):
                a = desvio + k * TAU / n
                d = Vector2(math.cos(a), math.sin(a))
                jogo.bala_inimiga(self.pos + d * self.raio, d * 150, self.cor)
            jogo.onda_choque(self.pos, self.cor, 90)
            tocar("inimigo_tiro", 0.5)
        elif self.padrao == "rajada" and self.cd <= 0:
            self.cd = 0.4 if f2 else 0.55
            n = 7 if f2 else 5
            for k in range(n):
                d = mira.rotate((k - (n - 1) / 2) * 9)
                jogo.bala_inimiga(self.pos + d * self.raio, d * 270, self.cor)
            tocar("inimigo_tiro", 0.5)
        elif self.padrao == "invocar" and self.cd <= 0:
            self.cd = 0.9
            for k in range(8):
                d = Vector2(1, 0).rotate(k * 45 + self.t * 40)
                jogo.bala_inimiga(self.pos + d * self.raio, d * 120, self.cor)

    def desenhar(self, surf, cam):
        p = self.pos - cam
        cor = BRANCO if self.flash > 0 else self.cor
        pulso = 1 + math.sin(self.t * 6) * 0.05
        for a in self.lasers:
            fim = p + Vector2(math.cos(a), math.sin(a)) * 1300
            if self.laser_aviso > 0:
                if int(self.t * 16) % 2:
                    pygame.draw.line(surf, misturar(FUNDO, self.cor, 0.6), p, fim, 2)
            else:
                largura = 22 + math.sin(self.t * 45) * 4
                pygame.draw.line(surf, misturar(FUNDO, self.cor, 0.5), p, fim, int(largura + 12))
                pygame.draw.line(surf, self.cor, p, fim, int(largura))
                pygame.draw.line(surf, BRANCO, p, fim, 7)
        pygame.draw.polygon(surf, misturar(cor, FUNDO, 0.85), poligono(p, self.raio * 1.25, 8, self.ang))
        pygame.draw.polygon(surf, cor, poligono(p, self.raio * 1.25, 8, self.ang), 3)
        estrela = []
        for k in range(10):
            r = self.raio * (0.8 if k % 2 == 0 else 0.4) * pulso
            a = -self.ang * 1.7 + k * TAU / 10
            estrela.append((p.x + math.cos(a) * r, p.y + math.sin(a) * r))
        pygame.draw.polygon(surf, cor, estrela, 2)
        pygame.draw.circle(surf, BRANCO, p, 9 * pulso)
        for k in range(6):
            a = self.ang * -0.6 + k * TAU / 6
            c = p + Vector2(math.cos(a), math.sin(a)) * self.raio * 1.75
            pygame.draw.polygon(surf, cor, poligono(c, 7, 3, a), 2)


# ======================================================================
#  O JOGO
# ======================================================================
class Jogo:
    def __init__(self, ecra):
        self.ecra = ecra
        self.cena = pygame.Surface((LARGURA, ALTURA))
        self.relogio = pygame.time.Clock()
        self.estado = "titulo"
        self.sair = False
        self.bloom = True
        self.crt = True
        self.ver_fps = False
        self.auto = False
        self.usar_rato = False
        self.musica_ligada = True
        self.canal_musica = None
        self.tempo_real = 0.0
        self.recorde = 0
        self.conquistas = set()
        self.notificacoes = []
        self.trauma = 0.0
        self.cam = Vector2()
        self.aberracao_t = 0.0
        self.flash_t = 0.0
        self.titulo_t = 0.0
        self.critica_x = LARGURA
        self.critica_i = 0
        self.ultimo_frame = None
        self.cartas = []
        self.carta_rato = -1
        self.estado_t = 0.0
        self.posicoes_orbes = []
        self.grelha = Grelha()
        self.estrelas = [(random.uniform(0, LARGURA), random.uniform(0, ALTURA), random.choice((0.2, 0.45, 0.8)))
                         for _ in range(140)]
        self.particulas = []
        self.ondas_choque = []
        self.textos = []
        self.limpar_mundo()

    # ---------------------------------------------------------- arranque
    def carregar(self):
        passos = [
            ("A sintetizar sons de tiro...", self.criar_sons),
            ("A afinar a guitarra portuguesa...", self.criar_musica),
            ("A compilar shaders (não há shaders)...", None),
            ("A tecer a grelha do espaço-tempo...", self.criar_ecras),
            ("A ignorar o NOTAS.md da sessão 9...", None),
            ("A fritar pastéis de nata...", None),
            ("A calibrar a saudade...", None),
        ]
        for k, (mensagem, funcao) in enumerate(passos):
            inicio = pygame.time.get_ticks()
            while True:
                for ev in pygame.event.get():
                    if ev.type == pygame.QUIT:
                        return False
                passou = (pygame.time.get_ticks() - inicio) / 1000
                progresso = (k + min(1.0, passou / 0.3)) / len(passos)
                self.desenhar_carregamento(mensagem, progresso)
                pygame.display.flip()
                self.relogio.tick(FPS)
                if funcao is not None:
                    funcao()
                    break
                if passou >= 0.3:
                    break
        self.desbloquear("abrir")
        if self.canal_musica is None and "musica" in SONS:
            self.canal_musica = SONS["musica"][0].play(loops=-1)
            self.ajustar_musica()
        return True

    def desenhar_carregamento(self, mensagem, progresso):
        self.cena.fill(FUNDO)
        escrever(self.cena, "CLUBE DE CÓDIGO apresenta", 28, (LARGURA / 2, ALTURA / 2 - 60), CINZENTO)
        escrever(self.cena, "uma experiência de um só ficheiro", 22, (LARGURA / 2, ALTURA / 2 - 32), (80, 75, 110))
        barra = pygame.Rect(0, 0, 420, 6)
        barra.center = (LARGURA // 2, ALTURA // 2 + 20)
        pygame.draw.rect(self.cena, (30, 25, 60), barra)
        pygame.draw.rect(self.cena, CIANO, (barra.x, barra.y, int(barra.w * progresso), barra.h))
        escrever(self.cena, mensagem, 22, (LARGURA / 2, ALTURA / 2 + 50), CIANO)
        self.ecra.blit(self.cena, (0, 0))

    def criar_sons(self):
        if pygame.mixer.get_init() is None:
            return
        SONS["tiro"] = [para_som(gerar_varrimento(0.07, f, f * 0.3, "quadrada", 0.15, 0.13)) for f in (900, 1000, 1100)]
        SONS["acerto"] = [para_som(gerar_varrimento(0.05, f, f * 0.5, "triangulo", 0.3, 0.35)) for f in (300, 360, 420)]
        SONS["explosao"] = [para_som(gerar_explosao(0.4, 0.55, g)) for g in (50, 65)]
        SONS["grande"] = [para_som(gerar_explosao(1.3, 0.85, 38))]
        SONS["dash"] = [para_som(gerar_varrimento(0.18, 200, 900, "seno", 0.6, 0.3))]
        SONS["dano"] = [para_som(gerar_varrimento(0.35, 220, 50, "serra", 0.3, 0.5))]
        SONS["nota"] = [para_som(gerar_varrimento(0.06, f, f * 1.5, "seno", 0, 0.18)) for f in (880, 988, 1175, 1319)]
        SONS["melhoria"] = [para_som(gerar_arpejo((523, 659, 784, 1047), 0.07, volume=0.25))]
        SONS["conquista"] = [para_som(gerar_arpejo((784, 1047, 1319, 1568), 0.06, "triangulo", 0.35))]
        SONS["investida"] = [para_som(gerar_varrimento(0.25, 120, 600, "serra", 0.4, 0.25))]
        SONS["inimigo_tiro"] = [para_som(gerar_varrimento(0.09, 500, 250, "triangulo", 0.1, 0.25))]
        SONS["rugido"] = [para_som(gerar_varrimento(1.4, 70, 40, "serra", 0.5, 0.6))]
        SONS["onda"] = [para_som(gerar_arpejo((440, 554, 659, 880), 0.09, "triangulo", 0.3))]
        SONS["laser"] = [para_som(gerar_laser(1.7))]
        SONS["laser_chefe"] = [para_som(gerar_laser(2.6, 0.3))]
        SONS["carga"] = [para_som(gerar_varrimento(0.9, 150, 900, "seno", 0.2, 0.25))]

    def criar_musica(self):
        if pygame.mixer.get_init() is not None:
            SONS["musica"] = [para_som(compor_musica())]

    def criar_ecras(self):
        # Vinheta: feita pequenina e esticada, que o smoothscale faz o resto.
        pequena = pygame.Surface((48, 27), pygame.SRCALPHA)
        for y in range(27):
            for x in range(48):
                d = math.hypot((x - 23.5) / 24, (y - 13) / 13.5)
                pequena.set_at((x, y), (0, 0, 0, int(max(0.0, min(1.0, (d - 0.55) * 1.6)) * 200)))
        self.vinheta = pygame.transform.smoothscale(pequena, (LARGURA, ALTURA))
        self.linhas = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        for y in range(0, ALTURA, 3):
            pygame.draw.line(self.linhas, (0, 0, 0, 45), (0, y), (LARGURA, y))

    # ---------------------------------------------------------- estado
    def limpar_mundo(self):
        self.jogador = Jogador()
        self.inimigos = []
        self.balas = []
        self.balas_inimigas = []
        self.recompensas = []
        self.avisos = []
        self.fila = []
        self.onda = 0
        self.fase = "banner"
        self.fase_t = 0.0
        self.spawn_cd = 0.0
        self.pontos = 0
        self.pontos_mostrados = 0.0
        self.combo = 0
        self.combo_t = 0.0
        self.combo_max = 0
        self.mortes = 0
        self.raspoes = 0
        self.investidas = 0
        self.natas = 0
        self.tempo_jogo = 0.0
        self.hitstop = 0.0
        self.escala_tempo = 1.0
        self.frase = ""
        self.chefe = None
        self.infinito = False
        self.farol = 0.0
        self.laser_t = 0.0
        self.laser_ang = 0.0

    def novo_jogo(self):
        self.limpar_mundo()
        self.estado = "jogo"
        self.proxima_onda()

    def proxima_onda(self):
        self.onda += 1
        self.fase = "banner"
        self.fase_t = 1.8
        self.frase = random.choice(FRASES_ONDA)
        self.spawn_cd = 1.0
        if self.onda == 10:
            self.desbloquear("onda10")
        if self.onda % 5 == 0:
            self.fila = []
            self.chefe = Chefe(self.onda)
            self.inimigos.append(self.chefe)
            self.fase = "chefe_intro"
            self.fase_t = 3.0
            tocar("rugido")
            self.trauma = max(self.trauma, 0.5)
        else:
            orcamento = 4 + self.onda * 3
            tipos = [("corredor", 1, 1), ("atirador", 2, 2), ("divisor", 3, 3), ("investida", 2, 4)]
            while orcamento > 0:
                possiveis = [t for t in tipos if t[2] <= self.onda and t[1] <= orcamento]
                if not possiveis:
                    break
                t = random.choice(possiveis)
                self.fila.append(t[0])
                orcamento -= t[1]
            tocar("onda")

    def desbloquear(self, chave):
        if chave in self.conquistas:
            return
        self.conquistas.add(chave)
        titulo, texto = CONQUISTAS[chave]
        self.notificacoes.append([titulo, texto, 0.0])
        tocar("conquista", 0.7)

    def ajustar_musica(self):
        if self.canal_musica is not None:
            volume = 0.0 if not self.musica_ligada else 0.35 if self.estado == "titulo" else 0.55
            self.canal_musica.set_volume(volume)

    # ---------------------------------------------------------- efeitos
    def particula(self, pos, vel, vida, cor, tam=2.0, atrito=3.0, faisca=True):
        if len(self.particulas) < 1600:
            self.particulas.append(Particula(pos, vel, vida, cor, tam, atrito, faisca))

    def explosao(self, pos, cor, quantas=28, forca=320, grelha=380):
        for _ in range(quantas):
            v = Vector2(1, 0).rotate(random.uniform(0, 360)) * random.uniform(0.2, 1) * forca
            self.particula(pos, v, random.uniform(0.3, 0.8), cor, random.uniform(1.5, 3))
        for _ in range(quantas // 3):
            v = Vector2(1, 0).rotate(random.uniform(0, 360)) * random.uniform(20, 90)
            self.particula(pos, v, random.uniform(0.4, 1.0), BRANCO, random.uniform(2, 4), 2, False)
        self.onda_choque(pos, cor, 60 + quantas * 1.5)
        self.grelha.impulso(pos, grelha, 140)

    def onda_choque(self, pos, cor, raio_max):
        self.ondas_choque.append([Vector2(pos), 4.0, raio_max, 0.35, cor])

    def texto(self, pos, texto, cor, tam=22, vida=0.7):
        if len(self.textos) < 60:
            self.textos.append(Texto(pos, texto, cor, tam, vida))

    def bala_inimiga(self, pos, vel, cor):
        if len(self.balas_inimigas) < 500:
            self.balas_inimigas.append(Bala(pos, vel, 1, 5, cor))

    def mudanca_de_fase(self, chefe):
        self.texto(chefe.pos + Vector2(0, -70), "A SAUDADE APERTA", AMARELO, 40, 1.8)
        for b in self.balas_inimigas:
            self.recompensas.append(Recompensa(b.pos, "nota"))
        self.balas_inimigas.clear()
        self.explosao(chefe.pos, AMARELO, 60, 500, 900)
        self.flash_t = 0.25
        self.trauma = 1.0
        self.hitstop = 0.15
        tocar("rugido")

    # ---------------------------------------------------------- combate
    def ferir(self, inimigo, dano, direcao, critico=False, carrega=True):
        inimigo.vida -= dano
        if carrega:
            self.farol = min(1.0, self.farol + dano * 0.0005 * self.jogador.farol_ganho)
        inimigo.flash = 0.06
        if not inimigo.chefe:
            inimigo.empurrao += direcao * (180 if critico else 90)
        else:
            inimigo.empurrao += direcao * 15
        cor = AMARELO if critico else BRANCO
        self.texto(inimigo.pos + Vector2(0, -inimigo.raio), str(int(dano)) + ("!" if critico else ""), cor, 30 if critico else 20)
        for _ in range(4):
            v = direcao.rotate(random.uniform(-50, 50)) * random.uniform(80, 260)
            self.particula(inimigo.pos, v, 0.25, inimigo.cor, 2)
        tocar("acerto", 0.5)
        if inimigo.vida <= 0 and inimigo in self.inimigos:
            self.matar(inimigo)

    def matar(self, inimigo):
        self.inimigos.remove(inimigo)
        self.mortes += 1
        self.combo += 1
        self.combo_t = 2.5
        self.combo_max = max(self.combo_max, self.combo)
        self.farol = min(1.0, self.farol + 0.06 * self.jogador.farol_ganho)
        mult = 1 + self.combo // 5
        self.pontos += inimigo.valor * mult
        self.desbloquear("sangue")
        if self.combo >= 10:
            self.desbloquear("combo10")
        if self.combo >= 25:
            self.desbloquear("combo25")
        if inimigo.chefe:
            self.morte_do_chefe(inimigo)
            return
        self.explosao(inimigo.pos, inimigo.cor, 18 + inimigo.raio)
        self.trauma = min(1.0, self.trauma + 0.12 + inimigo.raio / 200)
        if inimigo.raio > 20:
            self.hitstop = max(self.hitstop, 0.04)
        tocar("explosao", 0.6)
        for _ in range(random.randint(2, 4)):
            self.recompensas.append(Recompensa(inimigo.pos, "nota"))
        if random.random() < 0.04:
            self.recompensas.append(Recompensa(inimigo.pos, "coracao"))
        j = self.jogador
        if j.vampiro and random.random() < j.vampiro and j.vida < j.vida_max:
            j.vida += 1
            self.texto(j.pos + Vector2(0, -24), "+1", VERMELHO, 28)
        if inimigo.tipo == "divisor":
            for k in (-1, 1):
                filho = Inimigo("pequeno", inimigo.pos + Vector2(k * 14, 0), self.onda)
                filho.empurrao = Vector2(k * 260, random.uniform(-80, 80))
                self.inimigos.append(filho)

    def morte_do_chefe(self, chefe):
        self.chefe = None
        self.desbloquear("chefe")
        for k in range(4):
            pos = chefe.pos + Vector2(random.uniform(-50, 50), random.uniform(-50, 50))
            self.explosao(pos, random.choice((ROSA, AMARELO, BRANCO, CIANO)), 70, 600, 1200)
        for b in self.balas_inimigas:
            self.recompensas.append(Recompensa(b.pos, "nota"))
        self.balas_inimigas.clear()
        for _ in range(25):
            self.recompensas.append(Recompensa(chefe.pos, "nota"))
        self.recompensas.append(Recompensa(chefe.pos, "coracao"))
        self.recompensas.append(Recompensa(chefe.pos, "coracao"))
        self.texto(chefe.pos, "+" + str(chefe.valor * (1 + self.combo // 5)), AMARELO, 56, 2.0)
        self.trauma = 1.0
        self.flash_t = 0.4
        self.hitstop = 0.25
        self.escala_tempo = 0.15
        tocar("grande")
        for e in list(self.inimigos):
            self.matar(e)

    def ferir_jogador(self, origem):
        j = self.jogador
        if j.invulneravel > 0 or j.a_investir or self.fase == "morte":
            return
        j.vida -= 1
        j.invulneravel = 1.3
        afastar = j.pos - origem
        if afastar.length() > 0:
            j.vel += afastar.normalize() * 500
        self.trauma = 0.8
        self.aberracao_t = 0.4
        self.hitstop = 0.09
        self.combo = 0
        self.explosao(j.pos, VERMELHO, 24, 260, 500)
        tocar("dano")
        if j.vida <= 0:
            self.fase = "morte"
            self.fase_t = 2.2
            self.escala_tempo = 0.2
            self.explosao(j.pos, CIANO, 90, 500, 1200)
            self.desbloquear("morte")
            tocar("grande")

    def disparar(self, alvo):
        j = self.jogador
        mira = alvo - j.pos
        if mira.length() < 1:
            mira = Vector2(1, 0)
        base = math.degrees(math.atan2(mira.y, mira.x))
        for k in range(j.multi):
            a = base + (k - (j.multi - 1) / 2) * 8 + random.uniform(-2, 2)
            d = Vector2(1, 0).rotate(a)
            critico = random.random() < j.critico
            b = Bala(j.pos + d * 14, d * 720, j.dano * (2.5 if critico else 1), j.tam_bala * (1.4 if critico else 1),
                     AMARELO if critico else CIANO)
            b.perfura = j.perfura
            b.ricochete = j.ricochete
            b.teleguiada = j.teleguiada
            b.critica = critico
            self.balas.append(b)
        d = Vector2(1, 0).rotate(base)
        for _ in range(3):
            self.particula(j.pos + d * 16, d.rotate(random.uniform(-25, 25)) * random.uniform(150, 350), 0.12, CIANO, 2)
        j.vel -= d * 30
        j.coice = 1.0
        j.cd_tiro = j.intervalo
        self.trauma = min(1.0, self.trauma + 0.015)
        tocar("tiro", 0.35)

    def disparar_laser(self):
        if self.farol < 1 or self.laser_t > 0 or self.fase not in ("combate", "banner"):
            return
        self.farol = 0.0
        self.laser_t = self.jogador.laser_duracao
        self.laser_ang = self.jogador.ang
        self.flash_t = 0.08
        self.trauma = max(self.trauma, 0.6)
        self.desbloquear("laser")
        tocar("laser")

    def atualizar_laser(self, dt):
        j = self.jogador
        self.laser_t -= dt
        # O raio segue a mira, mas com peso: nao roda mais do que 4 rad/s.
        diferenca = (j.ang - self.laser_ang + math.pi) % TAU - math.pi
        self.laser_ang += max(-dt * 4, min(dt * 4, diferenca))
        self.trauma = max(self.trauma, 0.25)
        d = Vector2(math.cos(self.laser_ang), math.sin(self.laser_ang))
        inicio = j.pos + d * 16
        fim = j.pos + d * 1200
        for e in list(self.inimigos):
            if e.cd_laser <= 0 and dist_segmento(e.pos, inicio, fim) < e.raio + 16:
                e.cd_laser = 0.1
                self.ferir(e, j.dano * 1.5, d, carrega=False)
        antes = len(self.balas_inimigas)
        self.balas_inimigas = [b for b in self.balas_inimigas if dist_segmento(b.pos, inicio, fim) > 18]
        if len(self.balas_inimigas) < antes:
            self.pontos += 2 * (antes - len(self.balas_inimigas))
        for k in range(1, 7):
            self.grelha.impulso(j.pos + d * k * 150, 90, 70)
        for _ in range(3):
            ponto = inicio.lerp(fim, random.random() * 0.7)
            self.particula(ponto, d.rotate(random.choice((90, -90))) * random.uniform(80, 260), 0.3, CIANO, 2)

    def investir(self):
        j = self.jogador
        if j.dash_cd > 0 or j.a_investir or self.fase in ("morte", "chefe_intro"):
            return
        entrada = self.direcao_teclas()
        if entrada.length() == 0 and self.usar_rato:
            entrada = self.rato_mundo() - j.pos
        if entrada.length() == 0:
            entrada = Vector2(math.cos(j.ang), math.sin(j.ang))
        if entrada.length() == 0:
            entrada = Vector2(1, 0)
        j.dash_dir = entrada.normalize()
        j.dash_t = 0.16
        j.dash_cd = j.dash_recarga
        self.investidas += 1
        if self.investidas >= 50:
            self.desbloquear("dash")
        self.grelha.impulso(j.pos, 250, 90)
        for _ in range(12):
            self.particula(j.pos, -j.dash_dir.rotate(random.uniform(-40, 40)) * random.uniform(100, 300), 0.35, CIANO, 2)
        tocar("dash", 0.6)

    def fim_de_investida(self):
        j = self.jogador
        if not j.vira:
            return
        self.explosao(j.pos, AMARELO, 30, 380, 700)
        self.trauma = min(1.0, self.trauma + 0.3)
        tocar("explosao", 0.7)
        for e in list(self.inimigos):
            para = e.pos - j.pos
            if para.length() < 95 + e.raio:
                self.ferir(e, j.dano * 3, para.normalize() if para.length() > 0 else Vector2(1, 0))

    # ---------------------------------------------------------- melhorias
    def sortear_cartas(self):
        j = self.jogador
        pool = [m for m in MELHORIAS if not (m[4] and m[0] in j.melhorias)]
        escolhidas = []
        while len(escolhidas) < 3 and pool:
            m = random.choices(pool, weights=[PESOS_RARIDADE[x[3]] for x in pool])[0]
            pool.remove(m)
            escolhidas.append(m)
        self.cartas = [[m, 0.0] for m in escolhidas]
        self.carta_rato = len(self.cartas) // 2
        self.estado = "melhoria"
        self.estado_t = 0.0

    def escolher(self, indice):
        if indice >= len(self.cartas) or self.estado_t < 0.6:
            return
        mid = self.cartas[indice][0][0]
        j = self.jogador
        j.melhorias[mid] = j.melhorias.get(mid, 0) + 1
        if mid == "guitarra":
            j.multi += 1
        elif mid == "cafe":
            j.intervalo *= 0.8
        elif mid == "calcada":
            j.perfura += 1
        elif mid == "eletrico":
            j.ricochete += 1
        elif mid == "nata":
            j.vida_max += 1
            j.vida = j.vida_max
            self.natas += 1
            if self.natas >= 3:
                self.desbloquear("nata")
        elif mid == "saudade":
            j.dano *= 1.3
        elif mid == "gaivota":
            j.orbes += 1
        elif mid == "bacalhau":
            j.critico += 0.12
        elif mid == "vira":
            j.vira = True
        elif mid == "azulejo":
            j.tam_bala *= 1.4
            j.dano *= 1.1
        elif mid == "sardinha":
            j.teleguiada = True
        elif mid == "ginjinha":
            j.velocidade *= 1.12
            j.dash_recarga *= 0.85
        elif mid == "fado":
            j.vampiro += 0.1
        elif mid == "bugio":
            j.laser_duracao *= 1.4
            j.farol_ganho *= 1.3
        tocar("melhoria")
        self.flash_t = 0.12
        self.grelha.impulso(j.pos, 600, 400)
        self.estado = "jogo"
        self.proxima_onda()

    # ---------------------------------------------------------- entrada
    def direcao_teclas(self):
        t = pygame.key.get_pressed()
        d = Vector2(t[pygame.K_d] - t[pygame.K_a], t[pygame.K_s] - t[pygame.K_w])
        return d.normalize() if d.length() > 0 else d

    def mira_teclas(self):
        # As setas disparam para onde apontam, como no Binding of Isaac.
        t = pygame.key.get_pressed()
        d = Vector2(t[pygame.K_RIGHT] - t[pygame.K_LEFT], t[pygame.K_DOWN] - t[pygame.K_UP])
        return d.normalize() if d.length() > 0 else d

    def rato_mundo(self):
        return Vector2(pygame.mouse.get_pos()) + self.cam

    def retangulos_cartas(self):
        rects = []
        n = len(self.cartas)
        for k, (m, anim) in enumerate(self.cartas):
            r = pygame.Rect(0, 0, 230, 310)
            r.center = (int(LARGURA / 2 + (k - (n - 1) / 2) * 260), int(ALTURA / 2 + 20 + (1 - suavizar(anim)) * 420))
            if k == self.carta_rato:
                r = r.inflate(14, 14).move(0, -12)
            rects.append(r)
        return rects

    def evento(self, ev):
        if ev.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN):
            self.usar_rato = True
        elif ev.type == pygame.KEYDOWN and ev.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
            self.usar_rato = False
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_f:
                pygame.display.toggle_fullscreen()
            elif ev.key == pygame.K_m:
                self.musica_ligada = not self.musica_ligada
                self.ajustar_musica()
            elif ev.key == pygame.K_b:
                self.bloom = not self.bloom
            elif ev.key == pygame.K_c:
                self.crt = not self.crt
            elif ev.key == pygame.K_F3:
                self.ver_fps = not self.ver_fps
            elif ev.key == pygame.K_t:
                self.auto = not self.auto
                if self.auto:
                    self.desbloquear("auto")
        if self.estado == "titulo":
            if ev.type == pygame.KEYDOWN and ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.novo_jogo()
                self.ajustar_musica()
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                self.sair = True
        elif self.estado == "jogo":
            if ev.type == pygame.KEYDOWN and ev.key in (pygame.K_ESCAPE, pygame.K_p):
                self.estado = "pausa"
                pequeno = pygame.transform.smoothscale(self.cena, (LARGURA // 8, ALTURA // 8))
                self.ultimo_frame = pygame.transform.smoothscale(pequeno, (LARGURA, ALTURA))
            elif ev.type == pygame.KEYDOWN and ev.key in (pygame.K_SPACE, pygame.K_LSHIFT, pygame.K_RSHIFT):
                self.investir()
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 3:
                self.investir()
            elif (ev.type == pygame.KEYDOWN and ev.key == pygame.K_e) or (ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 2):
                self.disparar_laser()
        elif self.estado == "pausa":
            if ev.type == pygame.KEYDOWN and ev.key in (pygame.K_ESCAPE, pygame.K_p):
                self.estado = "jogo"
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_q:
                self.estado = "titulo"
                self.ajustar_musica()
        elif self.estado == "melhoria":
            if ev.type == pygame.KEYDOWN and ev.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                self.escolher(ev.key - pygame.K_1)
            elif ev.type == pygame.KEYDOWN and ev.key in (pygame.K_LEFT, pygame.K_a):
                self.carta_rato = max(0, self.carta_rato - 1)
            elif ev.type == pygame.KEYDOWN and ev.key in (pygame.K_RIGHT, pygame.K_d):
                self.carta_rato = min(len(self.cartas) - 1, self.carta_rato + 1)
            elif ev.type == pygame.KEYDOWN and ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER) and self.carta_rato >= 0:
                self.escolher(self.carta_rato)
            elif ev.type == pygame.MOUSEMOTION:
                self.carta_rato = -1
                for k, r in enumerate(self.retangulos_cartas()):
                    if r.collidepoint(ev.pos):
                        self.carta_rato = k
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1 and self.carta_rato >= 0:
                self.escolher(self.carta_rato)
        elif self.estado == "vitoria":
            if ev.type == pygame.KEYDOWN and ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER) and self.estado_t > 1.5:
                self.infinito = True
                self.sortear_cartas()
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_r:
                self.novo_jogo()
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                self.estado = "titulo"
                self.ajustar_musica()
        elif self.estado == "fim":
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_r:
                self.novo_jogo()
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                self.estado = "titulo"
                self.ajustar_musica()

    # ---------------------------------------------------------- atualizar
    def atualizar(self, dt):
        self.tempo_real += dt
        for n in self.notificacoes:
            n[2] += dt
        self.notificacoes = [n for n in self.notificacoes if n[2] < 3.5]
        self.trauma = max(0.0, self.trauma - dt * 1.6)
        self.aberracao_t -= dt
        self.flash_t -= dt
        abanao = self.trauma ** 2 * 16
        segue = (self.jogador.pos - CENTRO) * 0.04 if self.estado != "titulo" else Vector2()
        self.cam = segue + Vector2(random.uniform(-1, 1), random.uniform(-1, 1)) * abanao

        if self.estado == "titulo":
            self.atualizar_titulo(dt)
            mundo_dt = dt
        elif self.estado == "jogo":
            mundo_dt = self.atualizar_jogo(dt)
        elif self.estado == "melhoria":
            self.estado_t += dt
            for k, carta in enumerate(self.cartas):
                if self.estado_t > k * 0.12:
                    carta[1] = min(1.0, carta[1] + dt * 2.2)
            mundo_dt = dt * 0.15
        elif self.estado == "fim":
            mundo_dt = dt * 0.5
        elif self.estado == "vitoria":
            self.estado_t += dt
            if random.random() < dt * 2.5:
                pos = Vector2(random.uniform(80, LARGURA - 80), random.uniform(60, ALTURA - 60))
                self.explosao(pos, random.choice((ROSA, CIANO, AMARELO, ROXO, VERDE)), 40, 320, 400)
                if random.random() < 0.3:
                    tocar("explosao", 0.25)
            mundo_dt = dt
        else:
            return
        self.grelha.atualizar(min(dt, 1 / 30))
        self.atualizar_efeitos(mundo_dt)

    def atualizar_titulo(self, dt):
        self.titulo_t += dt
        if random.random() < dt * 1.6:
            pos = Vector2(random.uniform(100, LARGURA - 100), random.uniform(80, ALTURA - 80))
            self.explosao(pos, random.choice((ROSA, CIANO, AMARELO, ROXO)), 30, 260, 300)
        self.critica_x -= dt * 110
        largura = fonte(24).size(CRITICAS[self.critica_i])[0]
        if self.critica_x < -largura:
            self.critica_x = LARGURA
            self.critica_i = (self.critica_i + 1) % len(CRITICAS)

    def atualizar_efeitos(self, dt):
        vivas = []
        for p in self.particulas:
            p.vida -= dt
            if p.vida > 0:
                p.pos += p.vel * dt
                p.vel *= 1 / (1 + p.atrito * dt)
                vivas.append(p)
        self.particulas = vivas
        for o in self.ondas_choque:
            o[3] -= dt
            o[1] += (o[2] - o[1]) * min(1, dt * 12)
        self.ondas_choque = [o for o in self.ondas_choque if o[3] > 0]
        for t in self.textos:
            t.vida -= dt
            t.pos.y -= 40 * dt
        self.textos = [t for t in self.textos if t.vida > 0]

    def atualizar_jogo(self, dt_real):
        if self.hitstop > 0:
            self.hitstop -= dt_real
            return 0.0
        self.escala_tempo += (1.0 - self.escala_tempo) * min(1, dt_real * (0.8 if self.fase == "morte" else 2.5))
        dt = dt_real * self.escala_tempo
        self.tempo_jogo += dt
        self.fase_t -= dt_real
        j = self.jogador

        if self.fase == "morte":
            if self.fase_t <= 0:
                self.recorde = max(self.recorde, self.pontos)
                self.estado = "fim"
                self.estado_t = 0.0
            return dt
        if self.fase == "banner" and self.fase_t <= 0:
            self.fase = "combate"
        if self.fase == "chefe_intro":
            if self.fase_t <= 0:
                self.fase = "combate"
            self.chefe.atualizar(self, dt)
            return dt
        if self.fase == "limpo" and self.fase_t <= 0:
            if self.onda == ONDAS_TOTAIS and not self.infinito:
                self.estado = "vitoria"
                self.estado_t = 0.0
                self.recorde = max(self.recorde, self.pontos)
                self.desbloquear("vitoria")
            else:
                self.sortear_cartas()
            return dt

        # Os inimigos chegam da fila, com aviso.
        self.spawn_cd -= dt
        if self.fila and self.spawn_cd <= 0:
            self.spawn_cd = max(0.22, 0.55 - self.onda * 0.025)
            for _ in range(10):
                pos = Vector2(random.uniform(40, LARGURA - 40), random.uniform(40, ALTURA - 40))
                if pos.distance_to(j.pos) > 220:
                    break
            self.avisos.append(Aviso(pos, self.fila.pop(0)))
        for a in self.avisos:
            a.t -= dt
            if a.t <= 0:
                self.inimigos.append(Inimigo(a.tipo, a.pos, self.onda))
                self.onda_choque(a.pos, PERFIS[a.tipo][3], 40)
                self.grelha.impulso(a.pos, -200, 80)
        self.avisos = [a for a in self.avisos if a.t > 0]

        # O jogador
        j.invulneravel -= dt
        j.dash_cd -= dt
        j.cd_tiro -= dt
        j.coice = max(0.0, j.coice - dt * 8)
        if j.a_investir:
            j.dash_t -= dt
            j.vel = j.dash_dir * 980
            j.fantasmas.append([Vector2(j.pos), j.ang, 0.25])
            for e in self.inimigos:
                if j.vira and e.pos.distance_to(j.pos) < e.raio + 18 and e.cd_orbe <= 0:
                    e.cd_orbe = 0.3
                    self.ferir(e, j.dano * 2, j.dash_dir)
            if j.dash_t <= 0:
                j.vel = j.dash_dir * j.velocidade
                self.fim_de_investida()
        else:
            alvo_vel = self.direcao_teclas() * j.velocidade * (0.45 if self.laser_t > 0 else 1)
            j.vel += (alvo_vel - j.vel) * min(1, dt * 12)
        j.pos += j.vel * dt
        j.pos.x = max(j.raio, min(LARGURA - j.raio, j.pos.x))
        j.pos.y = max(j.raio, min(ALTURA - j.raio, j.pos.y))
        for f in j.fantasmas:
            f[2] -= dt
        j.fantasmas = [f for f in j.fantasmas if f[2] > 0]

        alvo = self.rato_mundo()
        a_disparar = self.usar_rato and pygame.mouse.get_pressed()[0]
        setas = self.mira_teclas()
        andar = self.direcao_teclas()
        if setas.length() > 0:
            a_disparar = True
            alvo = j.pos + setas * 200
        elif not self.usar_rato:
            # So teclado e sem disparar: olha para onde anda.
            alvo = j.pos + (andar if andar.length() > 0 else Vector2(math.cos(j.ang), math.sin(j.ang))) * 200
        if self.auto and self.inimigos:
            a_disparar = True
            alvo = min(self.inimigos, key=lambda e: e.pos.distance_squared_to(j.pos)).pos
            if self.farol >= 1:
                self.disparar_laser()
        mira = alvo - j.pos
        if mira.length() > 0:
            j.ang = math.atan2(mira.y, mira.x)
        if self.laser_t > 0:
            self.atualizar_laser(dt)
        elif a_disparar and j.cd_tiro <= 0 and self.fase in ("combate", "banner"):
            self.disparar(alvo)
        if random.random() < 0.5:
            self.particula(j.pos - Vector2(math.cos(j.ang), math.sin(j.ang)) * 10,
                           Vector2(random.uniform(-20, 20), random.uniform(-20, 20)) - j.vel * 0.2, 0.3, (40, 140, 255), 2, 2, False)

        # As gaivotas orbitais
        orbes = []
        for k in range(j.orbes):
            a = self.tempo_jogo * 3.2 + k * TAU / j.orbes
            orbes.append(j.pos + Vector2(math.cos(a), math.sin(a)) * 58)
        self.posicoes_orbes = orbes

        # Inimigos
        for e in list(self.inimigos):
            e.atualizar(self, dt)
        for i, a in enumerate(self.inimigos):  # nao se empilham uns em cima dos outros
            for b in self.inimigos[i + 1:]:
                d = a.pos - b.pos
                minimo = a.raio + b.raio
                if 0 < d.length_squared() < minimo * minimo:
                    empurra = d.normalize() * (minimo - d.length()) * 0.5
                    if not a.chefe:
                        a.pos += empurra
                    if not b.chefe:
                        b.pos -= empurra
        for e in list(self.inimigos):
            if e not in self.inimigos:
                continue
            if e.pos.distance_to(j.pos) < e.raio + j.raio:
                self.ferir_jogador(e.pos)
            for o in orbes:
                if e.cd_orbe <= 0 and e.pos.distance_to(o) < e.raio + 9:
                    e.cd_orbe = 0.35
                    afastar = e.pos - j.pos
                    self.ferir(e, j.dano * 1.2, afastar.normalize() if afastar.length() > 0 else Vector2(1, 0))
                    break

        self.atualizar_balas(dt)

        # Recompensas: as notas vem ter contigo, como os problemas
        for r in self.recompensas:
            r.vida -= dt
            r.ang += dt * 4
            para = j.pos - r.pos
            dist = para.length()
            iman = self.fase == "limpo" or dist < 130
            if iman and dist > 0:
                r.vel += para / dist * 2200 * dt
            r.vel *= 0.05 ** dt
            r.pos += r.vel * dt
            if dist < j.raio + 10:
                r.vida = 0
                if r.tipo == "nota":
                    self.pontos += 10 * (1 + self.combo // 5)
                    tocar("nota", 0.3)
                elif j.vida < j.vida_max:
                    j.vida += 1
                    self.texto(j.pos + Vector2(0, -24), "+1", VERMELHO, 28)
                    tocar("melhoria", 0.5)
        self.recompensas = [r for r in self.recompensas if r.vida > 0]

        self.combo_t -= dt
        if self.combo_t <= 0:
            self.combo = 0
        self.pontos_mostrados += (self.pontos - self.pontos_mostrados) * min(1, dt_real * 10)

        if self.fase == "combate" and not self.fila and not self.inimigos and not self.avisos:
            self.fase = "limpo"
            self.fase_t = 1.6
            self.escala_tempo = 0.25
            self.balas_inimigas.clear()
            tocar("onda")
        return dt

    def atualizar_balas(self, dt):
        j = self.jogador
        vivas = []
        for b in self.balas:
            b.vida -= dt
            if b.teleguiada and self.inimigos:
                alvo = min(self.inimigos, key=lambda e: e.pos.distance_squared_to(b.pos))
                if alvo.pos.distance_to(b.pos) < 300:
                    desejo = (alvo.pos - b.pos).normalize() * b.vel.length()
                    b.vel = b.vel.lerp(desejo, min(1, dt * 6))
            b.pos += b.vel * dt
            fora = False
            if b.pos.x < 0 or b.pos.x > LARGURA:
                if b.ricochete > 0:
                    b.ricochete -= 1
                    b.vel.x *= -1
                    b.pos.x = max(0, min(LARGURA, b.pos.x))
                    b.atingidos.clear()
                else:
                    fora = True
            if b.pos.y < 0 or b.pos.y > ALTURA:
                if b.ricochete > 0:
                    b.ricochete -= 1
                    b.vel.y *= -1
                    b.pos.y = max(0, min(ALTURA, b.pos.y))
                    b.atingidos.clear()
                else:
                    fora = True
            if fora or b.vida <= 0:
                self.grelha.impulso(b.pos, 120, 50)
                continue
            self.grelha.impulso(b.pos, -14, 40)
            viva = True
            for e in self.inimigos:
                if id(e) in b.atingidos:
                    continue
                if b.pos.distance_squared_to(e.pos) < (e.raio + b.raio) ** 2:
                    b.atingidos.add(id(e))
                    self.ferir(e, b.dano, b.vel.normalize(), b.critica)
                    if b.perfura > 0:
                        b.perfura -= 1
                    else:
                        viva = False
                        break
            if viva:
                vivas.append(b)
        self.balas = vivas

        vivas = []
        for b in self.balas_inimigas:
            b.pos += b.vel * dt
            if not (-20 < b.pos.x < LARGURA + 20 and -20 < b.pos.y < ALTURA + 20):
                continue
            d2 = b.pos.distance_squared_to(j.pos)
            if d2 < (b.raio + j.raio - 3) ** 2:
                self.ferir_jogador(b.pos)
                if j.invulneravel > 1.0:
                    continue
            elif d2 < 30 ** 2 and not b.raspada and self.fase == "combate":
                b.raspada = True
                self.raspoes += 1
                self.pontos += 5
                self.particula(b.pos, (b.pos - j.pos) * 4, 0.3, BRANCO, 2)
                if self.raspoes >= 25:
                    self.desbloquear("raspao")
            vivas.append(b)
        self.balas_inimigas = vivas

    # ---------------------------------------------------------- desenhar
    def desenhar(self):
        if self.estado == "pausa":
            self.desenhar_pausa()
            return
        cena = self.cena
        cena.fill(FUNDO)
        cam = self.cam
        for x, y, prof in self.estrelas:
            px = (x - cam.x * prof * 3 + self.tempo_real * prof * 8) % LARGURA
            py = (y - cam.y * prof * 3) % ALTURA
            c = int(60 + prof * 150)
            cena.fill((c, c, min(255, c + 40)), (px, py, 1 + (prof > 0.7), 1 + (prof > 0.7)))
        self.grelha.desenhar(cena, cam)
        if self.estado != "titulo":
            self.desenhar_mundo(cena, cam)
        self.desenhar_efeitos(cena, cam)
        if self.bloom:
            self.aplicar_bloom(cena)
        if self.aberracao_t > 0:
            self.aplicar_aberracao(cena, int(2 + self.aberracao_t * 18))
        if self.flash_t > 0:
            branco = pygame.Surface((LARGURA, ALTURA))
            branco.fill(BRANCO)
            branco.set_alpha(int(min(1, self.flash_t * 4) * 180))
            cena.blit(branco, (0, 0))

        if self.estado == "titulo":
            self.desenhar_titulo(cena)
        elif self.estado == "jogo":
            self.desenhar_hud(cena)
        elif self.estado == "melhoria":
            self.desenhar_hud(cena)
            self.desenhar_cartas(cena)
        elif self.estado == "fim":
            self.desenhar_fim(cena)
        elif self.estado == "vitoria":
            self.desenhar_vitoria(cena)
        self.desenhar_notificacoes(cena)
        if self.crt:
            cena.blit(self.linhas, (0, 0))
            cena.blit(self.vinheta, (0, 0))
        self.desenhar_cursor(cena)
        if self.ver_fps:
            escrever(cena, f"{self.relogio.get_fps():.0f} FPS", 20, (LARGURA - 10, ALTURA - 10), VERDE, "bottomright")
        self.ecra.blit(cena, (0, 0))

    def aplicar_bloom(self, cena):
        # Bloom de pobre: encolhe, volta a esticar (fica desfocado) e soma por cima.
        pequeno = pygame.transform.smoothscale(cena, (LARGURA // 4, ALTURA // 4))
        mais_pequeno = pygame.transform.smoothscale(pequeno, (LARGURA // 10, ALTURA // 10))
        for img, forca in ((pequeno, 150), (mais_pequeno, 200)):
            brilho = pygame.transform.smoothscale(img, (LARGURA, ALTURA))
            brilho.fill((28, 28, 28), special_flags=pygame.BLEND_RGB_SUB)
            brilho.fill((forca, forca, forca), special_flags=pygame.BLEND_RGB_MULT)
            cena.blit(brilho, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    def aplicar_aberracao(self, cena, d):
        canais = []
        for cor, dx in (((255, 0, 0), d), ((0, 255, 0), 0), ((0, 0, 255), -d)):
            c = cena.copy()
            c.fill(cor, special_flags=pygame.BLEND_RGB_MULT)
            canais.append((c, dx))
        cena.fill((0, 0, 0))
        for c, dx in canais:
            cena.blit(c, (dx, 0), special_flags=pygame.BLEND_RGB_ADD)

    def desenhar_mundo(self, cena, cam):
        j = self.jogador
        for a in self.avisos:
            p = a.pos - cam
            cor = PERFIS[a.tipo][3]
            r = 8 + a.t * 30
            if int(a.t * 12) % 2:
                pygame.draw.circle(cena, cor, p, r, 2)
            pygame.draw.line(cena, cor, p + Vector2(-6, -6), p + Vector2(6, 6), 2)
            pygame.draw.line(cena, cor, p + Vector2(-6, 6), p + Vector2(6, -6), 2)
        for r in self.recompensas:
            p = r.pos - cam
            if r.vida < 2 and int(r.vida * 10) % 2:
                continue
            if r.tipo == "nota":
                pygame.draw.polygon(cena, AMARELO, poligono(p, 5, 4, r.ang), 0)
            else:
                coracao(cena, (p.x, p.y - 2), 9 + math.sin(r.ang * 2) * 1.5, VERMELHO, True)
        for e in self.inimigos:
            if e is self.chefe and self.fase == "chefe_intro" and e.pos.y < -60:
                continue
            e.desenhar(cena, cam)
        for b in self.balas:
            p = b.pos - cam
            cauda = p - b.vel * 0.025
            pygame.draw.line(cena, b.cor, cauda, p, max(2, int(b.raio)))
            pygame.draw.circle(cena, BRANCO, p, b.raio * 0.7)
        for b in self.balas_inimigas:
            p = b.pos - cam
            pygame.draw.circle(cena, b.cor, p, b.raio + 2)
            pygame.draw.circle(cena, BRANCO, p, b.raio - 1)
        if self.fase != "morte" or self.fase_t > 2.1:
            for f in j.fantasmas:
                cor = misturar(FUNDO, CIANO, f[2] / 0.25)
                pygame.draw.polygon(cena, cor, self.forma_jogador(f[0] - cam, f[1]), 1)
            for o in self.posicoes_orbes:
                p = o - cam
                pygame.draw.circle(cena, BRANCO, p, 5)
                pygame.draw.circle(cena, CIANO, p, 9, 2)
            p = j.pos - cam
            if self.laser_t > 0:
                d = Vector2(math.cos(self.laser_ang), math.sin(self.laser_ang))
                f = min(1.0, (j.laser_duracao - self.laser_t) * 10, self.laser_t * 6)
                a, b = p + d * 16, p + d * 1200
                largura = (20 + math.sin(self.tempo_real * 50) * 4) * f
                pygame.draw.line(cena, (30, 110, 190), a, b, int(largura + 14))
                pygame.draw.line(cena, CIANO, a, b, int(largura) + 1)
                pygame.draw.line(cena, BRANCO, a, b, int(7 * f) + 1)
                pygame.draw.circle(cena, BRANCO, a, 13 * f)
            if j.invulneravel <= 0 or int(j.invulneravel * 15) % 2:
                pygame.draw.polygon(cena, (20, 60, 90), self.forma_jogador(p, j.ang))
                pygame.draw.polygon(cena, CIANO, self.forma_jogador(p, j.ang), 2)
                pygame.draw.circle(cena, BRANCO, p, 3 + math.sin(self.tempo_real * 10))
                if j.dash_cd > 0:  # anel que mostra a recarga da investida
                    fracao = 1 - j.dash_cd / j.dash_recarga
                    rect = pygame.Rect(0, 0, 40, 40)
                    rect.center = p
                    pygame.draw.arc(cena, (60, 80, 140), rect, -math.pi / 2, -math.pi / 2 + fracao * TAU, 2)

    def forma_jogador(self, p, ang):
        pontos = []
        for a, r in ((0, 17), (2.5, 12), (math.pi, 5), (-2.5, 12)):
            pontos.append((p.x + math.cos(ang + a) * r, p.y + math.sin(ang + a) * r))
        return pontos

    def desenhar_efeitos(self, cena, cam):
        for o in self.ondas_choque:
            largura = max(1, int(o[3] / 0.35 * 5))
            pygame.draw.circle(cena, o[4], o[0] - cam, o[1], largura)
        for p in self.particulas:
            f = p.vida / p.vida_max
            cor = misturar(FUNDO, p.cor, f * 1.3)
            pos = p.pos - cam
            if p.faisca:
                pygame.draw.line(cena, cor, pos, pos - p.vel * 0.04, max(1, int(p.tam * f + 0.5)))
            else:
                pygame.draw.circle(cena, cor, pos, p.tam * f)
        for t in self.textos:
            f = t.vida / t.vida_max
            tam = int(t.tam * (1 + max(0, f - 0.8) * 2))
            escrever(cena, t.texto, tam, t.pos - cam, t.cor, alpha=min(1, f * 2) * 255)

    def desenhar_hud(self, cena):
        j = self.jogador
        for k in range(j.vida_max):
            coracao(cena, (28 + k * 30, 26), 11, VERMELHO, k < j.vida)
        barra = pygame.Rect(16, 48, 150, 6)
        pygame.draw.rect(cena, (25, 30, 60), barra)
        if self.laser_t > 0:
            pygame.draw.rect(cena, BRANCO, (barra.x, barra.y, int(barra.w * self.laser_t / j.laser_duracao), barra.h))
        elif self.farol >= 1:
            pulso = 0.5 + 0.5 * math.sin(self.tempo_real * 10)
            pygame.draw.rect(cena, misturar(CIANO, BRANCO, pulso), barra)
            escrever(cena, "LASER PRONTO  [E]", 20, (barra.right + 10, barra.centery), misturar(CIANO, BRANCO, pulso), "midleft")
        else:
            pygame.draw.rect(cena, (40, 130, 200), (barra.x, barra.y, int(barra.w * self.farol), barra.h))
            escrever(cena, "laser", 18, (barra.right + 10, barra.centery), (70, 90, 140), "midleft")
        escrever(cena, f"{int(self.pontos_mostrados):,}".replace(",", " "), 46, (LARGURA - 20, 14), BRANCO, "topright")
        if self.combo >= 2:
            mult = 1 + self.combo // 5
            escrever(cena, f"COMBO {self.combo}  x{mult}", 26, (LARGURA - 20, 52), AMARELO, "topright")
            pygame.draw.rect(cena, AMARELO, (LARGURA - 180, 74, int(160 * max(0, self.combo_t) / 2.5), 3))
        rotulo = f"ONDA {self.onda}  ·  INFINITO" if self.infinito else f"ONDA {self.onda}/{ONDAS_TOTAIS}"
        x = escrever(cena, rotulo, 28, (20, ALTURA - 14), CINZENTO, "bottomleft").right + 20
        for mid, n in j.melhorias.items():
            m = next(m for m in MELHORIAS if m[0] == mid)
            r = escrever(cena, m[1] + (f" x{n}" if n > 1 else ""), 18, (x, ALTURA - 17), CORES_RARIDADE[m[3]], "bottomleft")
            x = r.right + 14
        if self.auto:
            escrever(cena, "TIRO AUTOMÁTICO", 18, (LARGURA - 20, ALTURA - 17), VERDE, "bottomright")
        if self.chefe is not None and self.fase != "chefe_intro":
            c = self.chefe
            barra = pygame.Rect(LARGURA // 2 - 250, 22, 500, 10)
            pygame.draw.rect(cena, (40, 20, 40), barra)
            pygame.draw.rect(cena, BRANCO, (barra.x, barra.y, int(barra.w * c.vida_rasto / c.vida_max), barra.h))
            pygame.draw.rect(cena, c.cor, (barra.x, barra.y, int(barra.w * max(0, c.vida) / c.vida_max), barra.h))
            escrever(cena, "O SAUDOSISTA", 22, (LARGURA / 2, 46), c.cor)
        if self.fase in ("banner", "limpo") and self.estado == "jogo":
            dur = 1.8 if self.fase == "banner" else 1.6
            t = 1 - self.fase_t / dur
            alpha = min(1, t * 5, self.fase_t * 3) * 255
            if self.fase == "banner":
                escrever_glitch(cena, f"ONDA {self.onda}", 96, (LARGURA / 2, ALTURA / 2 - 30), int(6 * (1 - t)))
                escrever(cena, self.frase, 28, (LARGURA / 2, ALTURA / 2 + 30), CINZENTO, alpha=alpha)
            else:
                escrever_glitch(cena, "ONDA LIMPA", 90, (LARGURA / 2, ALTURA / 2), 3)
        if self.fase == "chefe_intro":
            t = 1 - self.fase_t / 3.0
            barra = int(suavizar(min(1, t * 3, self.fase_t * 3)) * 70)
            pygame.draw.rect(cena, (0, 0, 0), (0, 0, LARGURA, barra))
            pygame.draw.rect(cena, (0, 0, 0), (0, ALTURA - barra, LARGURA, barra))
            if t > 0.25:
                escrever_glitch(cena, "O SAUDOSISTA", 92, (LARGURA / 2, ALTURA - 150), 4)
                subtitulo = "A Saudade Final" if self.chefe.final and not self.infinito else "Guardião da Melancolia"
                if self.infinito:
                    subtitulo += " (outra vez)"
                escrever(cena, subtitulo, 30, (LARGURA / 2, ALTURA - 100), ROSA)

    def desenhar_cartas(self, cena):
        escuro = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        escuro.fill((5, 3, 12, int(170 * min(1, self.estado_t * 3))))
        cena.blit(escuro, (0, 0))
        escrever(cena, "ESCOLHE UMA MELHORIA", 44, (LARGURA / 2, 70), BRANCO, alpha=min(1, self.estado_t * 3) * 255)
        for k, ((mid, nome, desc, rar, _), anim), r in zip(range(3), self.cartas, self.retangulos_cartas()):
            cor = CORES_RARIDADE[rar]
            pygame.draw.rect(cena, (14, 10, 30), r, border_radius=12)
            pygame.draw.rect(cena, cor, r, 3 if k == self.carta_rato else 2, border_radius=12)
            centro = (r.centerx, r.y + 85)
            girar = self.tempo_real * (1.5 if k == self.carta_rato else 0.5)
            lados = 3 + (sum(map(ord, mid)) % 5)
            pygame.draw.polygon(cena, misturar(cor, FUNDO, 0.7), poligono(centro, 42, lados, girar))
            pygame.draw.polygon(cena, cor, poligono(centro, 42, lados, girar), 2)
            pygame.draw.polygon(cena, BRANCO, poligono(centro, 16, lados, -girar * 2), 2)
            escrever(cena, NOMES_RARIDADE[rar], 18, (r.centerx, r.y + 150), cor)
            escrever(cena, nome, 27, (r.centerx, r.y + 178), BRANCO)
            y = r.y + 210
            linha = ""
            for palavra in desc.split():
                if fonte(21).size(linha + " " + palavra)[0] > r.w - 30:
                    escrever(cena, linha, 21, (r.centerx, y), CINZENTO)
                    y += 20
                    linha = palavra
                else:
                    linha = (linha + " " + palavra).strip()
            escrever(cena, linha, 21, (r.centerx, y), CINZENTO)
            escrever(cena, f"[{k + 1}]", 22, (r.centerx, r.bottom - 20), cor)
        escrever(cena, "1 2 3  ou  ← → e ENTER", 22, (LARGURA / 2, ALTURA - 40), CINZENTO,
                 alpha=min(1, self.estado_t * 3) * 255)

    def desenhar_titulo(self, cena):
        t = self.titulo_t
        forca = 3 + int(abs(math.sin(t * 1.3)) ** 8 * 14)
        escrever_glitch(cena, "FADO//NEON", 150, (LARGURA / 2, 170 + math.sin(t * 1.5) * 6), forca)
        escrever(cena, "um roguelite de saudade", 30, (LARGURA / 2, 250), ROSA)
        piscar = 255 if int(t * 2) % 2 == 0 else 120
        escrever(cena, "ENTER para jogar", 34, (LARGURA / 2, 340), BRANCO, alpha=piscar)
        escrever(cena, "Sobrevive a 10 ondas. Derrota o Saudosista. Duas vezes.", 24, (LARGURA / 2, 290), BRANCO)
        escrever(cena, "WASD mover  ·  SETAS disparar  ·  ESPAÇO investida  ·  E laser  ·  T tiro automático",
                 20, (LARGURA / 2, 385), CINZENTO)
        escrever(cena, "(o rato também funciona: apontar, clique esquerdo dispara, direito investe)",
                 18, (LARGURA / 2, 408), (90, 85, 110))
        if self.recorde:
            escrever(cena, f"Recorde desta sessão: {self.recorde}", 22, (LARGURA / 2, 440), AMARELO)
        pygame.draw.polygon(cena, AMARELO, [(LARGURA - 120, 30), (LARGURA - 20, 30), (LARGURA - 20, 70), (LARGURA - 120, 70)], 1)
        escrever(cena, "JOGO DO ANO", 18, (LARGURA - 70, 42), AMARELO)
        escrever(cena, "2026", 22, (LARGURA - 70, 59), AMARELO)
        escrever(cena, CRITICAS[self.critica_i], 24, (self.critica_x, ALTURA - 40), (150, 140, 190), "midleft")

    def desenhar_fim(self, cena):
        escuro = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        escuro.fill((5, 3, 12, 175))
        cena.blit(escuro, (0, 0))
        escrever_glitch(cena, "MORRESTE", 120, (LARGURA / 2, 120), 3 + int(abs(math.sin(self.tempo_real * 2)) * 6))
        escrever(cena, "mas a saudade fica", 30, (LARGURA / 2, 185), ROSA)
        minutos, segundos = divmod(int(self.tempo_jogo), 60)
        linhas = [
            ("Pontos", f"{self.pontos}"),
            ("Onda", f"{self.onda}"),
            ("Inimigos", f"{self.mortes}"),
            ("Combo máximo", f"{self.combo_max}"),
            ("Raspões", f"{self.raspoes}"),
            ("Tempo", f"{minutos}:{segundos:02d}"),
        ]
        for k, (nome, valor) in enumerate(linhas):
            y = 240 + k * 30
            escrever(cena, nome, 26, (LARGURA / 2 - 20, y), CINZENTO, "midright")
            escrever(cena, valor, 26, (LARGURA / 2 + 20, y), BRANCO, "midleft")
        if self.pontos >= self.recorde and self.pontos > 0:
            escrever(cena, "NOVO RECORDE!", 30, (LARGURA / 2, 438), AMARELO)
        escrever(cena, "R recomeçar   ·   ESC menu", 26, (LARGURA / 2, 480), BRANCO)

    def desenhar_vitoria(self, cena):
        escuro = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        escuro.fill((5, 3, 12, int(140 * min(1, self.estado_t))))
        cena.blit(escuro, (0, 0))
        escrever_glitch(cena, "VENCESTE", 130, (LARGURA / 2, 100), 2 + int(abs(math.sin(self.tempo_real * 3)) * 8))
        escrever(cena, "A saudade foi derrotada. Por agora.", 30, (LARGURA / 2, 170), AMARELO)
        minutos, segundos = divmod(int(self.tempo_jogo), 60)
        dados = [("Pontos", self.pontos), ("Tempo", f"{minutos}:{segundos:02d}"),
                 ("Inimigos", self.mortes), ("Combo máximo", self.combo_max)]
        for k, (nome, valor) in enumerate(dados):
            x = LARGURA / 2 + (k - 1.5) * 200
            escrever(cena, str(valor), 36, (x, 225), BRANCO)
            escrever(cena, nome, 20, (x, 252), CINZENTO)
        # Os creditos sobem dentro de uma janela, como nos filmes.
        janela = pygame.Rect(0, 285, LARGURA, 165)
        cena.set_clip(janela)
        altura_total = len(CREDITOS) * 26 + janela.h
        desvio = (self.estado_t * 32) % altura_total
        for k, linha in enumerate(CREDITOS):
            y = janela.bottom + k * 26 - desvio
            escrever(cena, linha, 30 if k == 0 else 22, (LARGURA / 2, y), ROSA if k == 0 else (190, 180, 220))
        cena.set_clip(None)
        if self.estado_t > 1.5:
            escrever(cena, "ENTER continuar no modo infinito   ·   R recomeçar   ·   ESC menu", 24, (LARGURA / 2, 490), BRANCO)

    def desenhar_pausa(self):
        cena = self.cena
        cena.blit(self.ultimo_frame, (0, 0))
        escuro = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        escuro.fill((5, 3, 12, 140))
        cena.blit(escuro, (0, 0))
        escrever_glitch(cena, "PAUSA", 110, (LARGURA / 2, 150), 3)
        opcoes = [
            ("Bloom (B)", self.bloom), ("CRT (C)", self.crt), ("Música (M)", self.musica_ligada),
            ("Tiro automático (T)", self.auto), ("Contador de FPS (F3)", self.ver_fps),
        ]
        for k, (nome, ligado) in enumerate(opcoes):
            y = 240 + k * 32
            escrever(cena, nome, 26, (LARGURA / 2 - 10, y), CINZENTO, "midright")
            escrever(cena, "LIGADO" if ligado else "desligado", 26, (LARGURA / 2 + 10, y), VERDE if ligado else (90, 85, 110), "midleft")
        escrever(cena, "Definições gráficas: ULTRA (não há outras)", 20, (LARGURA / 2, 420), (90, 85, 110))
        escrever(cena, "ESC continuar   ·   Q desistir   ·   F ecrã inteiro", 24, (LARGURA / 2, 470), BRANCO)
        self.desenhar_notificacoes(cena)
        self.desenhar_cursor(cena)
        self.ecra.blit(cena, (0, 0))

    def desenhar_notificacoes(self, cena):
        for k, (titulo, texto, t) in enumerate(self.notificacoes[:3]):
            entrada = suavizar(t * 3) - suavizar((t - 3.0) * 3)
            r = pygame.Rect(0, 0, 300, 58)
            r.topright = (LARGURA - 16 + int((1 - entrada) * 330), 90 + k * 66)
            pygame.draw.rect(cena, (16, 12, 34), r, border_radius=8)
            pygame.draw.rect(cena, AMARELO, r, 2, border_radius=8)
            estrela = []
            for i in range(10):
                raio = 14 if i % 2 == 0 else 6
                a = -math.pi / 2 + i * TAU / 10
                estrela.append((r.x + 30 + math.cos(a) * raio, r.centery + math.sin(a) * raio))
            pygame.draw.polygon(cena, AMARELO, estrela)
            escrever(cena, "CONQUISTA: " + titulo, 21, (r.x + 54, r.y + 12), AMARELO, "topleft")
            escrever(cena, texto, 19, (r.x + 54, r.y + 34), CINZENTO, "topleft")

    def desenhar_cursor(self, cena):
        if not self.usar_rato:
            return
        p = Vector2(pygame.mouse.get_pos())
        if self.estado in ("melhoria", "pausa", "titulo", "vitoria", "fim"):
            pygame.draw.circle(cena, BRANCO, p, 3)
            return
        abre = 10 + self.jogador.coice * 6
        a = self.tempo_real * 1.5
        for k in range(4):
            d = Vector2(math.cos(a + k * math.pi / 2), math.sin(a + k * math.pi / 2))
            pygame.draw.line(cena, CIANO, p + d * abre, p + d * (abre + 7), 2)
        pygame.draw.circle(cena, BRANCO, p, 2)

    # ---------------------------------------------------------- ciclo
    def correr(self):
        while not self.sair:
            dt = min(self.relogio.tick(FPS) / 1000, 1 / 20)
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    return
                self.evento(ev)
            self.atualizar(dt)
            self.desenhar()
            pygame.display.flip()


def main():
    global TAXA
    pygame.mixer.pre_init(22050, -16, 2, 512)
    pygame.init()
    if pygame.mixer.get_init() is not None:
        TAXA = pygame.mixer.get_init()[0]
    ecra = pygame.display.set_mode((LARGURA, ALTURA), pygame.SCALED | pygame.RESIZABLE)
    pygame.display.set_caption("FADO//NEON — Jogo do Ano 2026")
    pygame.mouse.set_visible(False)
    jogo = Jogo(ecra)
    if jogo.carregar():
        jogo.correr()
    pygame.quit()


if __name__ == "__main__":
    main()
