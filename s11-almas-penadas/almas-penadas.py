# S11 — ALMAS PENADAS
# Um soulslike de saudade, visto de cima.
#
# D. Sebastiao desapareceu no nevoeiro em 1578 e prometeu voltar numa manha
# de nevoeiro. Hoje esta nevoeiro.
#
# Zero assets: o mapa e texto, o som e matematica, a luz e uma multiplicacao.
#
#   WASD / setas     mover                Shift (manter)   correr
#   Espaco           rolar (invulneravel a meio do rolamento)
#   J ou Z           ataque leve (carrega 3x para combo)
#   K ou X           ataque pesado        L ou C           aparar (parry)
#   Q                beber caldo verde    Tab ou R         fixar alvo
#   E / Enter        interagir: fogareiros, mensagens, portas, nevoeiro
#   Esc              pausa
#
# Dica de quem ja morreu muitas vezes: apara um golpe com brilho BRANCO e
# depois ataca (J) para um golpe critico. Os golpes com brilho VERMELHO nao se
# aparam: rola.

import array
import math
import random

import pygame
from pygame import Vector2

# --- Constantes: e aqui que se mexe primeiro ---
LARGURA = 960
ALTURA = 540
FPS = 60
TILE = 32
TAU = math.tau

BRANCO = (235, 230, 220)
OURO = (225, 190, 110)
SANGUE = (150, 20, 25)
VIDA = (165, 30, 35)
FOLEGO = (70, 150, 75)
CINZA = (130, 125, 135)
FOGO = (255, 150, 60)
ALMA = (150, 230, 200)
FUNDO = (8, 7, 10)

# O mapa e so texto. Muda uma letra e o mundo muda.
#   #  parede          .  chao             S  inicio          F  fogareiro
#   M  mensagem        I  objeto           N  nevoeiro        X  portao
#   P  porta do atalho (so abre de um lado)
#   o  ossada   c  cao vadio   l  lanceiro   G  Guarda da Calcada   D  D. Sebastiao
MAPA = [
    "################################################################",
    "################################################################",
    "################################################################",
    "###..........#######...................#####..................##",
    "###........o.#######...................#####.I................##",
    "###....F.....#######...#...........#...#####................o.##",
    "###..........#######...................#####...#...#...#...#..##",
    "###..........#######...................#####..................##",
    "###................X.........G.........X.........l............##",
    "###................X...................X.................l....##",
    "###.......o..#######...................#####..................##",
    "###..........#######...................#####...#...#...#...#..##",
    "###.I........#######...#...........#...#####..................##",
    "###..........#######...................#####.........l........##",
    "#######..###########...................#####..c.............F.##",
    "#######..###################NNN#############..................##",
    "#######.M###################...####################....#########",
    "#######..###################...####################....#########",
    "#######..###################.M.####################..M.#########",
    "#######..###################...####################....#########",
    "#######..###################...####################....#########",
    "#######c.###################...####################NNNN#########",
    "#######..###################...###########.....................#",
    "#######..###################...###########.....................#",
    "#######..###########...................###.....................#",
    "#######..###########.........M.........###...#.............#...#",
    "#######..###########..........o........###.....................#",
    "#######..###########....#.........#....###.....................#",
    "#######..###########...................###.....................#",
    "#######PP###########...................###.....................#",
    "##...........#######......o............###..........D..........#",
    "##...........#######.........#.........###.....................#",
    "##.......F...#######...................###.....................#",
    "##..............................o......###.....................#",
    "##...S..................#.........#....###.....................#",
    "##.........M.#######..o................###...#.............#...#",
    "##...........#######................c..###.....................#",
    "##...........#######...................###.....................#",
    "##########################################.....................#",
    "################################################################",
]

# Pela ordem em que aparecem no mapa (da esquerda para a direita, de cima para baixo)
MENSAGENS = [
    "Isto não é o FADO//NEON. Não há laser. Desculpa.",
    "Inimigo forte adiante. Prepara o caldo verde.",
    "Ele volta numa manhã de nevoeiro. Hoje está nevoeiro.",
    "Tesouro adiante... mentira, são esqueletos.",
    "Rola com ESPAÇO. A sério, rola.",
]
ITENS = ["almas", "tigela"]

ARENAS = {
    "guarda": pygame.Rect(20 * TILE, 3 * TILE, 19 * TILE, 12 * TILE),
    "final": pygame.Rect(42 * TILE, 22 * TILE, 21 * TILE, 17 * TILE),
}
NOMES_CHEFES = {"G": "Guarda da Calçada", "D": "D. Sebastião, o Desejado"}


def golpe(ante, ativo, rec, alcance, arco, dano, impulso=0, aparavel=True, forma="arco",
          postura=20, rastreio=4.0, largura=16):
    # Todos os golpes do jogo tem tres fases: anuncio, golpe e recuperacao.
    # E na recuperacao que se castiga. E no anuncio que se rola.
    return dict(ante=ante, ativo=ativo, rec=rec, alcance=alcance, arco=math.radians(arco), dano=dano,
                impulso=impulso, aparavel=aparavel, forma=forma, postura=postura, rastreio=rastreio,
                largura=largura)


TIPOS = {
    "ossada": dict(nome="Ossada", vida=70, raio=13, vel=70, postura=30, almas=45, aggro=230, cor=(205, 195, 170),
                   combos=[(0, 70, [golpe(0.6, 0.12, 0.7, 46, 110, 22, 140)]),
                           (0, 70, [golpe(0.45, 0.1, 0.25, 44, 110, 18, 120), golpe(0.4, 0.1, 0.8, 46, 110, 20, 160)])]),
    "cao": dict(nome="Cão Vadio", vida=40, raio=11, vel=150, postura=10, almas=30, aggro=280, cor=(125, 92, 62),
                combos=[(0, 110, [golpe(0.38, 0.2, 0.55, 30, 80, 16, 430)])]),
    "lanceiro": dict(nome="Lanceiro", vida=110, raio=14, vel=60, postura=50, almas=90, aggro=260, cor=(140, 145, 160),
                     combos=[(40, 120, [golpe(0.7, 0.15, 0.6, 95, 0, 30, 220, forma="estocada", largura=12)]),
                             (0, 60, [golpe(0.5, 0.12, 0.7, 60, 160, 24, 80)])]),
    "guarda": dict(nome="Guarda da Calçada", vida=1000, raio=24, vel=65, postura=140, almas=1500, aggro=0,
                   cor=(120, 130, 150), chefe=True,
                   combos=[(0, 95, [golpe(0.8, 0.15, 0.45, 82, 120, 40, 150, postura=40),
                                    golpe(0.6, 0.15, 0.9, 82, 150, 45, 180)]),
                           (0, 130, [golpe(1.1, 0.2, 1.0, 105, 0, 60, 0, aparavel=False, forma="pancada")]),
                           (130, 400, [golpe(0.9, 0.6, 0.8, 46, 100, 40, 470, aparavel=False, forma="carga")])]),
    "sebastiao": dict(nome="D. Sebastião, o Desejado", vida=1800, raio=18, vel=120, postura=160, almas=5000, aggro=0,
                      cor=(215, 175, 90), chefe=True,
                      combos=[(0, 85, [golpe(0.45, 0.12, 0.2, 64, 130, 30, 160), golpe(0.4, 0.12, 0.2, 64, 130, 30, 160),
                                       golpe(0.55, 0.15, 0.9, 72, 160, 40, 200)]),
                              (0, 95, [golpe(1.35, 0.15, 0.9, 74, 140, 55, 200, rastreio=6.0)]),
                              (100, 340, [golpe(0.6, 0.25, 0.7, 44, 100, 40, 700, forma="carga")]),
                              (80, 420, [golpe(0.9, 0.15, 1.0, 92, 0, 55, 0, aparavel=False, forma="salto")])],
                      combos_fase2=[(0, 600, [golpe(1.4, 0.1, 1.0, 0, 0, 45, 0, aparavel=False, forma="fantasmas")]),
                                    (0, 600, [golpe(0.8, 0.15, 0.6, 72, 150, 45, 250, forma="teleporte")])]),
}

LEVES = [
    dict(ante=0.12, ativo=0.1, rec=0.28, alcance=56, arco=math.radians(120), dano=22, custo=14, impulso=140, postura=12),
    dict(ante=0.1, ativo=0.1, rec=0.28, alcance=56, arco=math.radians(120), dano=24, custo=14, impulso=140, postura=12),
    dict(ante=0.16, ativo=0.12, rec=0.42, alcance=62, arco=math.radians(150), dano=34, custo=18, impulso=200, postura=22),
]
PESADO = dict(ante=0.42, ativo=0.14, rec=0.45, alcance=66, arco=math.radians(150), dano=58, custo=30, impulso=220,
              postura=50)

CREDITOS = [
    "ALMAS PENADAS",
    "",
    "Um soulslike de um só ficheiro",
    "",
    "Mapa  —  uma lista de strings",
    "Luz  —  BLEND_RGB_MULT",
    "Música  —  math.sin, em ré menor",
    "Dificuldade  —  sim",
    "D. Sebastião  —  ele próprio, finalmente",
    "",
    "Obrigado por morreres connosco.",
]

# ======================================================================
#  SOM: sintetizado amostra a amostra, como no FADO//NEON
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


def som_golpe(duracao=0.2, volume=1.0):
    # Ruido "passa-banda": a diferenca entre dois filtros. Soa a espada no ar.
    n = int(TAXA * duracao)
    out = [0.0] * n
    a = b = 0.0
    for i in range(n):
        p = i / n
        c = 0.05 + 0.45 * math.sin(math.pi * p)
        a += (random.random() * 2 - 1 - a) * c
        b += (a - b) * c
        out[i] = (a - b) * math.sin(math.pi * p) ** 1.5 * 2.4 * volume
    return out


def som_impacto(grave=90, duracao=0.25, volume=0.8):
    n = int(TAXA * duracao)
    out = [0.0] * n
    f = 0.0
    for i in range(n):
        p = i / n
        t = i / TAXA
        f += (random.random() * 2 - 1 - f) * 0.3
        out[i] = (math.sin(TAU * grave * t * (1 - p * 0.6)) * math.exp(-t * 18) + f * math.exp(-t * 30)) * volume
    return out


def som_metal(base=520, duracao=0.9, volume=0.5):
    # Um sino desafinado: parciais que nao sao multiplos inteiros da base.
    n = int(TAXA * duracao)
    parciais = [(1.0, 1.0), (2.76, 0.6), (5.4, 0.4), (8.93, 0.25)]
    out = [0.0] * n
    for i in range(n):
        t = i / TAXA
        v = sum(math.sin(TAU * base * m * t) * a * math.exp(-t * (5 + k * 3)) for k, (m, a) in enumerate(parciais))
        if t < 0.01:
            v += random.random() * 2 - 1
        out[i] = v * volume * 0.5
    return out


def som_varrimento(duracao, f0, f1, forma="seno", ruido=0.0, volume=0.5):
    n = int(TAXA * duracao)
    out = [0.0] * n
    fase = 0.0
    for i in range(n):
        p = i / n
        fase += (f0 + (f1 - f0) * p) / TAXA
        c = fase % 1.0
        v = 2 * c - 1 if forma == "serra" else math.sin(TAU * c)
        if ruido:
            v = v * (1 - ruido) + (random.random() * 2 - 1) * ruido
        out[i] = v * min(1.0, i / 60) * (1 - p) ** 2 * volume
    return out


def som_ruido(duracao, corte, volume=0.5, subida=0.1):
    n = int(TAXA * duracao)
    out = [0.0] * n
    f = 0.0
    for i in range(n):
        p = i / n
        f += (random.random() * 2 - 1 - f) * corte
        out[i] = f * min(1.0, p / subida) * (1 - p) ** 1.5 * volume * 3
    return out


def som_acorde(notas, duracao, ataque=0.4, volume=0.3):
    n = int(TAXA * duracao)
    out = [0.0] * n
    for i in range(n):
        t = i / TAXA
        p = i / n
        env = min(1.0, t / ataque) * (1 - p) ** 1.2
        out[i] = sum(math.sin(TAU * f * t) for f in notas) / len(notas) * env * volume
    return out


def musica_vento(duracao=12.0):
    n = int(TAXA * duracao)
    out = [0.0] * n
    f = 0.0
    seno = math.sin
    for i in range(n):
        t = i / TAXA
        f += (random.random() * 2 - 1 - f) * 0.015
        rajada = 0.55 + 0.45 * seno(TAU * t * 2 / duracao) * seno(TAU * t * 3 / duracao)
        drone = (seno(TAU * 55 * t) + 0.5 * seno(TAU * 82.4 * t)) * 0.035
        out[i] = f * 4 * rajada + drone * (0.6 + 0.4 * seno(TAU * t / duracao))
    return out


def musica_chefe():
    # Re menor, Si bemol, Sol menor, La. Cordas a tremer, timbales, um coro de senos.
    acordes = [(146.83, 174.61, 220.0), (116.54, 146.83, 174.61), (98.0, 116.54, 146.83), (110.0, 138.59, 164.81)]
    dur_acorde = 4.0
    n = int(TAXA * dur_acorde * 4)
    out = [0.0] * n
    seno = math.sin
    baixo = 0.0
    for i in range(n):
        t = i / TAXA
        k = int(t / dur_acorde)
        dentro = t - k * dur_acorde
        a, b, c = acordes[k]
        tremolo = 0.75 + 0.25 * seno(TAU * 7 * t)
        cordas = (seno(TAU * a * t) + 0.4 * seno(TAU * 2 * a * t) + seno(TAU * b * t) + 0.4 * seno(TAU * 2 * b * t)
                  + seno(TAU * c * t)) * 0.07 * tremolo * min(1.0, dentro * 3)
        coro = seno(TAU * 2 * c * t + 0.6 * seno(TAU * 5 * t)) * 0.06 * min(1.0, dentro / 1.5)
        baixo += ((2 * ((a / 2 * t) % 1) - 1) - baixo) * 0.03
        batida = t % 1.0
        timbale = 0.0
        if int(t) % 4 in (0, 2) or (int(t) % 4 == 3 and batida > 0.5):
            tb = batida if batida < 0.5 else batida - 0.5
            timbale = seno(TAU * 55 * tb * (1 - tb * 0.5)) * math.exp(-tb * 7) * 0.6
        out[i] = math.tanh((cordas + coro + baixo * 0.35 + timbale) * 1.3) * 0.8
    return out


def tocar(nome, volume=1.0):
    if nome not in SONS:
        return
    agora = pygame.time.get_ticks()
    if agora - ULTIMO_SOM.get(nome, -1000) < 40:
        return
    ULTIMO_SOM[nome] = agora
    canal = random.choice(SONS[nome]).play()
    if canal is not None:
        canal.set_volume(volume)


# ======================================================================
#  AJUDANTES
# ======================================================================
FONTES = {}


def fonte(tamanho, serifa=False):
    chave = (tamanho, serifa)
    if chave not in FONTES:
        if serifa:
            FONTES[chave] = pygame.font.SysFont("georgia,timesnewroman,times,serif", tamanho)
        else:
            FONTES[chave] = pygame.font.Font(None, tamanho)
    return FONTES[chave]


def escrever(surf, texto, tamanho, pos, cor=BRANCO, ancora="center", alpha=255, serifa=False):
    img = fonte(tamanho, serifa).render(texto, True, cor)
    if alpha < 255:
        img.set_alpha(max(0, int(alpha)))
    r = img.get_rect(**{ancora: (int(pos[0]), int(pos[1]))})
    surf.blit(img, r)
    return r


def angulo_dif(a, b):
    return (a - b + math.pi) % TAU - math.pi


def rodar_para(atual, alvo, passo):
    d = angulo_dif(alvo, atual)
    return atual + max(-passo, min(passo, d))


def direcao(angulo):
    return Vector2(math.cos(angulo), math.sin(angulo))


def dist_segmento(p, a, b):
    ab = b - a
    t = max(0.0, min(1.0, (p - a).dot(ab) / (ab.length_squared() or 1)))
    return p.distance_to(a + ab * t)


def misturar(a, b, t):
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0] - a[0]) * t), int(a[1] + (b[1] - a[1]) * t), int(a[2] + (b[2] - a[2]) * t))


def crescente(centro, raio_in, raio_out, a0, a1, passos=10):
    # Um "meia-lua" entre dois angulos: e o rasto da espada.
    fora = [centro + direcao(a0 + (a1 - a0) * k / passos) * raio_out for k in range(passos + 1)]
    dentro = [centro + direcao(a1 + (a0 - a1) * k / passos) * raio_in for k in range(passos + 1)]
    return fora + dentro


def tecla(teclas, *codigos):
    return any(teclas[c] for c in codigos)


# ======================================================================
#  O MUNDO: o mapa de texto transformado em paredes, portas e nevoeiro
# ======================================================================
class Mundo:
    def __init__(self):
        self.grelha = [list(linha) for linha in MAPA]
        self.w = len(MAPA[0])
        self.h = len(MAPA)
        self.inicio = Vector2()
        self.fogareiros = []
        self.mensagens = []
        self.itens = []
        self.spawns = []
        self.nevoeiro = {"guarda": [], "final": []}
        self.nevoeiro_ativo = {"guarda": True, "final": True}
        self.portoes = []
        self.portoes_abertos = False
        self.porta = []
        self.porta_aberta = False
        tipos = {"o": "ossada", "c": "cao", "l": "lanceiro", "G": "guarda", "D": "sebastiao"}
        for y, linha in enumerate(self.grelha):
            for x, c in enumerate(linha):
                centro = Vector2(x * TILE + TILE / 2, y * TILE + TILE / 2)
                if c == "S":
                    self.inicio = centro
                elif c == "F":
                    self.fogareiros.append({"pos": centro, "aceso": False})
                elif c == "M":
                    self.mensagens.append({"pos": centro, "texto": MENSAGENS[len(self.mensagens) % len(MENSAGENS)]})
                elif c == "I":
                    self.itens.append({"pos": centro, "tipo": ITENS[len(self.itens) % len(ITENS)], "apanhado": False})
                elif c in tipos:
                    self.spawns.append((tipos[c], centro))
                elif c == "N":
                    self.nevoeiro["guarda" if x < 40 else "final"].append((x, y))
                    continue
                elif c == "X":
                    self.portoes.append((x, y))
                    continue
                elif c == "P":
                    self.porta.append((x, y))
                    continue
                if c != "#":
                    linha[x] = "."
        self.superficie = self.pre_desenhar()

    def solido(self, tx, ty):
        if not (0 <= tx < self.w and 0 <= ty < self.h):
            return True
        c = self.grelha[ty][tx]
        if c == "#":
            return True
        if c == "N":
            return self.nevoeiro_ativo["guarda" if tx < 40 else "final"]
        if c == "X":
            return not self.portoes_abertos
        if c == "P":
            return not self.porta_aberta
        return False

    def empurrar(self, ent):
        # Um circulo contra os quadrados das paredes: empurra-se para fora.
        for _ in range(2):
            r = ent.raio
            for ty in range(int((ent.pos.y - r) // TILE), int((ent.pos.y + r) // TILE) + 1):
                for tx in range(int((ent.pos.x - r) // TILE), int((ent.pos.x + r) // TILE) + 1):
                    if not self.solido(tx, ty):
                        continue
                    cx = max(tx * TILE, min(ent.pos.x, tx * TILE + TILE))
                    cy = max(ty * TILE, min(ent.pos.y, ty * TILE + TILE))
                    d = Vector2(ent.pos.x - cx, ent.pos.y - cy)
                    dist = d.length()
                    if 0 < dist < r:
                        ent.pos += d / dist * (r - dist)
                    elif dist == 0:
                        ent.pos.y += r

    def mover(self, ent, delta):
        passos = max(1, int(delta.length() / 10) + 1)
        for _ in range(passos):
            ent.pos += delta / passos
            self.empurrar(ent)

    def ve(self, a, b):
        d = b - a
        n = int(d.length() / 12) + 1
        for k in range(1, n):
            p = a + d * (k / n)
            if self.solido(int(p.x // TILE), int(p.y // TILE)):
                return False
        return True

    def pre_desenhar(self):
        rnd = random.Random(11)
        s = pygame.Surface((self.w * TILE, self.h * TILE))
        s.fill(FUNDO)
        terreiro = ARENAS["final"]
        for ty in range(self.h):
            for tx in range(self.w):
                r = pygame.Rect(tx * TILE, ty * TILE, TILE, TILE)
                parede = self.grelha[ty][tx] == "#"
                if not parede:
                    if terreiro.colliderect(r):
                        # Calcada portuguesa: pedrinhas brancas e pretas em ondas.
                        for sy in range(4):
                            for sx in range(4):
                                px, py = tx * 4 + sx, ty * 4 + sy
                                onda = math.sin(px * 0.35 + math.sin(py * 0.18) * 2.2)
                                base = (150, 145, 135) if onda > 0.35 else (42, 40, 44)
                                v = rnd.randint(-10, 10)
                                cor = (base[0] + v, base[1] + v, base[2] + v)
                                pygame.draw.rect(s, cor, (r.x + sx * 8 + 1, r.y + sy * 8 + 1, 6, 6))
                        continue
                    v = rnd.randint(-5, 5)
                    pygame.draw.rect(s, (46 + v, 43 + v, 52 + v), r)
                    pygame.draw.line(s, (33, 31, 39), r.topright, r.bottomright)
                    pygame.draw.line(s, (33, 31, 39), r.bottomleft, r.bottomright)
                    sorte = rnd.random()
                    if sorte < 0.1:
                        x0 = r.x + rnd.randint(4, 26)
                        y0 = r.y + rnd.randint(4, 26)
                        pygame.draw.line(s, (30, 28, 34), (x0, y0), (x0 + rnd.randint(-8, 8), y0 + rnd.randint(-8, 8)))
                    elif sorte < 0.14:
                        x0 = r.x + rnd.randint(6, 24)
                        y0 = r.y + rnd.randint(6, 24)
                        pygame.draw.line(s, (150, 145, 130), (x0, y0), (x0 + 7, y0 + 2), 2)
                        pygame.draw.circle(s, (150, 145, 130), (x0 + 9, y0 + 2), 2)
                    elif sorte < 0.2:
                        for _ in range(4):
                            pygame.draw.circle(s, (40, 60, 40), (r.x + rnd.randint(2, 30), r.y + rnd.randint(2, 30)), 1)
                else:
                    abaixo = ty + 1 < self.h and self.grelha[ty + 1][tx] != "#"
                    if abaixo:
                        # A face da parede virada para nos: da a ilusao de altura.
                        pygame.draw.rect(s, (66, 60, 74), (r.x, r.y, TILE, TILE - 14))
                        pygame.draw.rect(s, (34, 31, 40), (r.x, r.bottom - 14, TILE, 14))
                        for bx in range(0, TILE, 8 if ty % 2 else 10):
                            pygame.draw.line(s, (26, 24, 30), (r.x + bx, r.bottom - 14), (r.x + bx, r.bottom))
                        pygame.draw.line(s, (90, 84, 98), r.topleft, r.topright)
                    else:
                        pygame.draw.rect(s, (22, 20, 27), r)
                        for dx, dy, a, b in ((0, -1, r.topleft, r.topright), (-1, 0, r.topleft, r.bottomleft),
                                             (1, 0, r.topright, r.bottomright)):
                            vx, vy = tx + dx, ty + dy
                            if 0 <= vx < self.w and 0 <= vy < self.h and self.grelha[vy][vx] != "#":
                                pygame.draw.line(s, (70, 64, 80), a, b, 2)
        return s


# ======================================================================
#  AS CRIATURAS
# ======================================================================
class Jogador:
    def __init__(self, pos):
        self.pos = Vector2(pos)
        self.vel = Vector2()
        self.raio = 11
        self.face = -math.pi / 2
        self.estado = "livre"
        self.t = 0.0
        self.ataque = None
        self.fase = ""
        self.fase_t = 0.0
        self.combo = 0
        self.leve = False
        self.atingidos = set()
        self.invul = 0.0
        self.espera = 0.0
        self.rolar_dir = Vector2(1, 0)
        self.curou = False
        self.feito = False
        self.alvo_riposte = None
        self.nevoeiro_de = Vector2()
        self.nevoeiro_para = Vector2()
        self.nivel = 1
        self.vigor = 5
        self.folego = 5
        self.forca = 5
        self.almas = 0
        self.caldo_max = 4
        self.caldo = 4
        self.vida = self.vida_max
        self.vida_rasto = self.vida
        self.stamina = self.stamina_max

    @property
    def vida_max(self):
        return 80 + self.vigor * 12

    @property
    def stamina_max(self):
        return 70 + self.folego * 6

    @property
    def mult_dano(self):
        return 1 + (self.forca - 5) * 0.1

    @property
    def invulneravel(self):
        if self.invul > 0 or self.estado in ("nevoeiro", "riposte", "morto"):
            return True
        return self.estado == "rolar" and 0.04 < self.t < 0.32


class Inimigo:
    def __init__(self, tipo, pos, ng):
        self.tipo = tipo
        self.d = TIPOS[tipo]
        self.casa = Vector2(pos)
        self.chefe = self.d.get("chefe", False)
        self.raio = self.d["raio"]
        self.ng = ng
        self.morto_para_sempre = False
        self.repor()

    def repor(self):
        self.pos = Vector2(self.casa)
        self.vida_max = self.vida = self.d["vida"] * self.ng
        self.vida_rasto = self.vida
        self.postura = self.d["postura"]
        self.postura_t = 0.0
        self.estado = "parado"
        self.t = 0.0
        self.face = random.uniform(0, TAU) if not self.chefe else math.pi / 2
        self.vel = Vector2()
        self.combo = None
        self.passo = 0
        self.fase = "ante"
        self.fase_t = 0.0
        self.flash = 0.0
        self.atingiu = False
        self.morto = self.morto_para_sempre
        self.mostrar_vida = 0.0
        self.cd = random.uniform(0.3, 1.0)
        self.ver_t = random.uniform(0, 0.25)
        self.fase_chefe = 1
        self.salto_ini = Vector2(self.pos)
        self.salto_alvo = Vector2(self.pos)
        self.altura = 0.0
        self.invisivel = False
        self.teleportou = False
        self.espera = 0.0
        self.lado = random.choice((-1, 1))

    @property
    def golpe(self):
        return self.combo[self.passo] if self.combo else None


# ======================================================================
#  O JOGO
# ======================================================================
class Jogo:
    def __init__(self, ecra):
        self.ecra = ecra
        self.cena = pygame.Surface((LARGURA, ALTURA))
        self.luz = pygame.Surface((LARGURA, ALTURA))
        self.relogio = pygame.time.Clock()
        self.estado = "titulo"
        self.sair = False
        self.tempo_real = 0.0
        self.ng = 1
        self.canal_musica = None
        self.musica_atual = None
        self.gradientes = {}
        self.cinzas = [[random.uniform(0, LARGURA), random.uniform(0, ALTURA), random.uniform(0.3, 1)] for _ in range(70)]
        self.criar_nevoa()
        self.novo_mundo()

    # ---------------------------------------------------------- arranque
    def carregar(self):
        passos = [("A acender o fogareiro...", self.criar_sons),
                  ("A afinar as cordas em ré menor...", self.criar_musica),
                  ("A espalhar o nevoeiro...", None)]
        for mensagem, funcao in passos:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    return False
            self.cena.fill(FUNDO)
            escrever(self.cena, mensagem, 30, (LARGURA / 2, ALTURA / 2), (150, 120, 90), serifa=True)
            self.ecra.blit(self.cena, (0, 0))
            pygame.display.flip()
            if funcao is not None:
                funcao()
            else:
                pygame.time.wait(300)
        self.tocar_musica("vento")
        return True

    def criar_sons(self):
        if pygame.mixer.get_init() is None:
            return
        SONS["golpe"] = [para_som(som_golpe(0.2, v)) for v in (0.8, 1.0)]
        SONS["golpe_pesado"] = [para_som(som_golpe(0.35, 1.2))]
        SONS["acerto"] = [para_som(som_impacto(g, 0.25, 0.8)) for g in (80, 100, 120)]
        SONS["critico"] = [para_som(som_impacto(50, 0.6, 1.0))]
        SONS["aparar"] = [para_som(som_metal(520, 0.9)), para_som(som_metal(590, 0.9))]
        SONS["bloqueio"] = [para_som(som_metal(300, 0.3, 0.3))]
        SONS["rolar"] = [para_som(som_ruido(0.3, 0.08, 0.35, 0.3))]
        SONS["dano"] = [para_som(som_varrimento(0.3, 180, 80, "serra", 0.4, 0.5))]
        SONS["beber"] = [para_som(som_varrimento(0.12, 300, 700, "seno", 0, 0.3) * 3)]
        SONS["morte"] = [para_som(som_varrimento(2.2, 110, 35, "serra", 0.3, 0.6))]
        SONS["fogareiro"] = [para_som(som_acorde((220, 261.6, 329.6, 493.9), 2.5, 0.5, 0.35))]
        SONS["almas"] = [para_som(som_acorde((659, 784, 988, 1319), 1.2, 0.05, 0.25))]
        SONS["porta"] = [para_som(som_ruido(1.0, 0.02, 0.6, 0.05))]
        SONS["nevoeiro"] = [para_som(som_ruido(0.9, 0.05, 0.4, 0.5))]
        SONS["pancada"] = [para_som(som_impacto(45, 0.8, 1.0))]
        SONS["inimigo_morre"] = [para_som(som_ruido(0.6, 0.1, 0.4, 0.02))]
        SONS["vitoria"] = [para_som(som_acorde((146.8, 220, 293.7, 370), 4.0, 0.8, 0.4))]
        SONS["rugido"] = [para_som(som_varrimento(1.5, 90, 50, "serra", 0.6, 0.6))]

    def criar_musica(self):
        if pygame.mixer.get_init() is None:
            return
        SONS["vento"] = [para_som(musica_vento())]
        SONS["chefe"] = [para_som(musica_chefe())]

    def tocar_musica(self, nome):
        if nome == self.musica_atual:
            return
        self.musica_atual = nome
        if self.canal_musica is not None:
            self.canal_musica.fadeout(1200)
        self.canal_musica = None
        if nome in SONS:
            self.canal_musica = SONS[nome][0].play(loops=-1, fade_ms=1500)
            if self.canal_musica is not None:
                self.canal_musica.set_volume(0.5 if nome == "chefe" else 0.7)

    def criar_nevoa(self):
        tam = 64
        pequena = pygame.Surface((tam, tam), pygame.SRCALPHA)
        for y in range(tam):
            for x in range(tam):
                d = math.hypot(x - tam / 2 + 0.5, y - tam / 2 + 0.5) / (tam / 2)
                pequena.set_at((x, y), (200, 205, 215, int(max(0.0, 1 - d) ** 2 * 255)))
        self.nuvem = pygame.transform.smoothscale(pequena, (360, 260))
        self.nuvens = [[random.uniform(0, LARGURA), random.uniform(0, ALTURA), random.uniform(8, 22)] for _ in range(7)]
        base = pygame.Surface((64, 64))
        for y in range(64):
            for x in range(64):
                d = math.hypot(x - 31.5, y - 31.5) / 32
                v = int(max(0.0, 1 - d) ** 1.7 * 255)
                base.set_at((x, y), (v, v, v))
        self.gradiente_base = base

    def gradiente(self, raio, cor):
        raio = max(8, int(raio) // 8 * 8)
        chave = (raio, cor)
        if chave not in self.gradientes:
            g = pygame.transform.smoothscale(self.gradiente_base, (raio * 2, raio * 2))
            g.fill(cor, special_flags=pygame.BLEND_RGB_MULT)
            self.gradientes[chave] = g
        return self.gradientes[chave]

    # ---------------------------------------------------------- estado
    def novo_mundo(self, jogador_antigo=None):
        self.mundo = Mundo()
        self.jogador = Jogador(self.mundo.inicio)
        if jogador_antigo is not None:  # Novo Jogo+: fica-se com o nivel, perde-se o resto
            for campo in ("nivel", "vigor", "folego", "forca", "caldo_max"):
                setattr(self.jogador, campo, getattr(jogador_antigo, campo))
            self.jogador.almas = jogador_antigo.almas
            self.jogador.vida = self.jogador.vida_max
            self.jogador.caldo = self.jogador.caldo_max
            self.jogador.stamina = self.jogador.stamina_max
        self.inimigos = [Inimigo(tipo, pos, self.ng) for tipo, pos in self.mundo.spawns]
        self.respawn = Vector2(self.mundo.inicio)
        self.alvo = None
        self.chefe = None
        self.mancha = None
        self.particulas = []
        self.manchas_sangue = []
        self.perigos = []
        self.textos = []
        self.anuncio = None
        self.leitura = None
        self.leitura_t = 0.0
        self.trauma = 0.0
        self.hitstop = 0.0
        self.escala_tempo = 1.0
        self.cam = Vector2(self.jogador.pos)
        self.camara = Vector2()
        self.menu = None
        self.menu_i = 0
        self.mortes = 0
        self.tempo_jogo = 0.0
        self.fim_t = 0.0
        self.escuridao = 0.0
        self.buffer = None
        self.buffer_t = 0.0

    def anunciar(self, texto, cor, duracao=3.0, tamanho=64):
        self.anuncio = [texto, cor, 0.0, duracao, tamanho]

    def texto(self, pos, texto, cor, tam=20):
        if len(self.textos) < 40:
            self.textos.append([Vector2(pos) + Vector2(random.uniform(-6, 6), 0), texto, cor, tam, 0.8])

    def particula(self, pos, vel, vida, cor, tam=2.0, tipo="faisca", gravidade=0.0):
        if len(self.particulas) < 1200:
            self.particulas.append([Vector2(pos), Vector2(vel), vida, vida, cor, tam, tipo, gravidade])

    def sangue(self, pos, dirc, quantos=10, cor=(140, 15, 20)):
        for _ in range(quantos):
            v = dirc.rotate(random.uniform(-40, 40)) * random.uniform(60, 260)
            self.particula(pos, v, random.uniform(0.3, 0.6), cor, random.uniform(1.5, 3), "ponto")
        for _ in range(2):
            if len(self.manchas_sangue) > 160:
                self.manchas_sangue.pop(0)
            self.manchas_sangue.append([pos + dirc * random.uniform(8, 30) + Vector2(random.uniform(-8, 8), random.uniform(-8, 8)),
                                        random.uniform(3, 7), misturar(cor, (20, 10, 10), 0.4)])

    def faiscas(self, pos, quantas=14, cor=(255, 210, 140), forca=300):
        for _ in range(quantas):
            v = Vector2(1, 0).rotate(random.uniform(0, 360)) * random.uniform(0.3, 1) * forca
            self.particula(pos, v, random.uniform(0.15, 0.4), cor, 2)

    def vivos(self):
        return [e for e in self.inimigos if not e.morto]

    # ---------------------------------------------------------- combate: o jogador
    def tentar(self, acao, mov):
        j = self.jogador
        if acao == "beber":
            if j.estado != "livre":
                return False
            if j.caldo <= 0:
                tocar("bloqueio", 0.3)
                return True
            j.caldo -= 1
            j.estado, j.t, j.curou = "beber", 0.0, False
            return True
        livre = j.estado == "livre"
        em_rec = j.estado == "atacar" and j.fase == "rec" and j.fase_t < j.ataque["rec"] * 0.8
        fim_rolar = j.estado == "rolar" and j.t > 0.34
        if not (livre or em_rec or (fim_rolar and acao == "leve")):
            return False
        if j.stamina <= 0:
            return False
        j.espera = 0.6
        if acao == "rolar":
            j.stamina -= 20
            j.estado, j.t = "rolar", 0.0
            j.rolar_dir = mov if mov.length() > 0 else direcao(j.face)
            tocar("rolar", 0.6)
            return True
        if acao == "aparar":
            j.stamina -= 12
            j.estado, j.t = "aparar", 0.0
            return True
        if acao == "leve":
            for e in self.vivos():  # riposte: um inimigo aparado mesmo a frente
                para = e.pos - j.pos
                if e.estado == "aparado" and para.length() < 70 + e.raio:
                    j.estado, j.t, j.feito = "riposte", 0.0, False
                    j.alvo_riposte = e
                    j.face = math.atan2(para.y, para.x)
                    return True
            continuar = em_rec and j.leve
            j.combo = (j.combo + 1) % 3 if continuar else 0
            a = LEVES[j.combo]
        else:
            a = PESADO
            j.combo = 0
        j.leve = acao == "leve"
        j.stamina -= a["custo"]
        j.estado, j.ataque, j.fase, j.fase_t = "atacar", a, "ante", a["ante"]
        if self.alvo is not None:
            para = self.alvo.pos - j.pos
            j.face = math.atan2(para.y, para.x)
        elif mov.length() > 0:
            j.face = math.atan2(mov.y, mov.x)
        return True

    def atualizar_jogador(self, dt):
        j = self.jogador
        t = pygame.key.get_pressed()
        mov = Vector2(tecla(t, pygame.K_d, pygame.K_RIGHT) - tecla(t, pygame.K_a, pygame.K_LEFT),
                      tecla(t, pygame.K_s, pygame.K_DOWN) - tecla(t, pygame.K_w, pygame.K_UP))
        if mov.length() > 0:
            mov = mov.normalize()
        j.invul -= dt
        j.t += dt
        j.vida_rasto += (j.vida - j.vida_rasto) * min(1, dt * 1.5) if j.vida_rasto > j.vida else 0
        j.vida_rasto = max(j.vida_rasto, j.vida)
        if self.buffer is not None:
            self.buffer_t -= dt
            if self.tentar(self.buffer, mov) or self.buffer_t <= 0:
                self.buffer = None
        a_correr = False
        if self.alvo is not None and (self.alvo.morto or self.alvo.pos.distance_to(j.pos) > 450):
            self.alvo = None
            self.trocar_alvo(silencioso=True)

        if j.estado == "livre":
            velocidade = 150
            if tecla(t, pygame.K_LSHIFT, pygame.K_RSHIFT) and mov.length() > 0 and j.stamina > 0:
                velocidade *= 1.6
                j.stamina -= 24 * dt
                j.espera = 0.5
                a_correr = True
            j.vel += (mov * velocidade - j.vel) * min(1, dt * 14)
            if self.alvo is not None:
                para = self.alvo.pos - j.pos
                j.face = rodar_para(j.face, math.atan2(para.y, para.x), dt * 12)
            elif mov.length() > 0:
                j.face = rodar_para(j.face, math.atan2(mov.y, mov.x), dt * 14)
            if a_correr and random.random() < 0.3:
                self.particula(j.pos + Vector2(random.uniform(-6, 6), 8), Vector2(0, -20), 0.4, (90, 85, 80), 2, "ponto")
        elif j.estado == "rolar":
            p = j.t / 0.42
            j.vel = j.rolar_dir * (400 if p < 0.6 else 400 * (1 - (p - 0.6) / 0.4) + 40)
            if j.t >= 0.42:
                j.estado = "livre"
        elif j.estado == "atacar":
            a = j.ataque
            j.fase_t -= dt
            if j.fase == "ante":
                j.vel *= 0.001 ** dt
                if self.alvo is not None:
                    para = self.alvo.pos - j.pos
                    j.face = rodar_para(j.face, math.atan2(para.y, para.x), dt * 10)
                elif mov.length() > 0:
                    j.face = rodar_para(j.face, math.atan2(mov.y, mov.x), dt * 6)
                if j.fase_t <= 0:
                    j.fase, j.fase_t = "ativo", a["ativo"]
                    j.atingidos = set()
                    tocar("golpe_pesado" if a is PESADO else "golpe", 0.7)
            elif j.fase == "ativo":
                j.vel = direcao(j.face) * a["impulso"]
                self.golpe_do_jogador(a)
                if j.fase_t <= 0:
                    j.fase, j.fase_t = "rec", a["rec"]
            else:
                j.vel *= 0.0005 ** dt
                if j.fase_t <= 0:
                    j.estado = "livre"
        elif j.estado == "aparar":
            j.vel *= 0.001 ** dt
            if j.t >= 0.45:
                j.estado = "livre"
        elif j.estado == "beber":
            j.vel += (mov * 50 - j.vel) * min(1, dt * 10)
            if j.t >= 0.55 and not j.curou:
                j.curou = True
                j.vida = min(j.vida_max, j.vida + j.vida_max * 0.45)
                tocar("beber", 0.6)
                for _ in range(16):
                    self.particula(j.pos + Vector2(random.uniform(-12, 12), random.uniform(-4, 10)),
                                   Vector2(0, -random.uniform(30, 80)), 0.8, (120, 200, 90), 2, "ponto")
            if j.t >= 1.1:
                j.estado = "livre"
        elif j.estado == "atingido":
            j.vel *= 0.002 ** dt
            if j.t >= 0.35:
                j.estado = "livre"
        elif j.estado == "riposte":
            j.vel *= 0.001 ** dt
            e = j.alvo_riposte
            if j.t >= 0.32 and not j.feito:
                j.feito = True
                self.hitstop = 0.22
                self.trauma = 0.7
                self.ferir_inimigo(e, PESADO["dano"] * 4.5 * j.mult_dano, 999, critico=True)
                self.sangue(e.pos, direcao(j.face), 40)
                tocar("critico")
                if not e.morto:
                    e.estado, e.espera = "atordoado", 1.0
            if j.t >= 0.9:
                j.estado = "livre"
        elif j.estado == "nevoeiro":
            p = min(1.0, j.t / 1.0)
            j.pos = j.nevoeiro_de.lerp(j.nevoeiro_para, p)
            j.vel = Vector2()
            if random.random() < 0.6:
                self.particula(j.pos + Vector2(random.uniform(-14, 14), random.uniform(-14, 14)),
                               Vector2(random.uniform(-20, 20), random.uniform(-20, 20)), 0.6, (200, 200, 210), 3, "ponto")
            if p >= 1:
                j.estado = "livre"
        elif j.estado == "morto":
            j.vel = Vector2()
            if j.t >= 4.5:
                self.renascer()
            return

        if j.estado != "nevoeiro":
            self.mundo.mover(j, j.vel * dt)
        if j.estado not in ("rolar", "atacar", "aparar") and not a_correr:
            j.espera -= dt
            if j.espera <= 0:
                j.stamina = min(j.stamina_max, j.stamina + (25 if j.estado == "beber" else 60) * dt)

        # As almas que deixaste cair: tocar-lhes e recupera-las
        if self.mancha is not None and j.pos.distance_to(self.mancha[0]) < 22:
            j.almas += self.mancha[1]
            self.anunciar("ALMAS RECUPERADAS", ALMA, 2.2, 40)
            tocar("almas")
            self.mancha = None

        # Entrar na arena de um chefe acorda-o
        for e in self.inimigos:
            if e.chefe and not e.morto and e.estado == "parado":
                arena = ARENAS["guarda" if e.tipo == "guarda" else "final"]
                if arena.collidepoint(j.pos) and j.estado != "nevoeiro":
                    e.estado = "perseguir"
                    e.cd = 1.2
                    self.chefe = e
                    self.tocar_musica("chefe")
                    tocar("rugido", 0.6)

    def golpe_do_jogador(self, a):
        j = self.jogador
        for e in self.vivos():
            if id(e) in j.atingidos or e.invisivel or e.altura > 0.3:
                continue
            para = e.pos - j.pos
            dist = para.length()
            if dist > a["alcance"] + e.raio:
                continue
            if dist > 1 and abs(angulo_dif(math.atan2(para.y, para.x), j.face)) > a["arco"] / 2 + math.atan2(e.raio, dist):
                continue
            j.atingidos.add(id(e))
            critico = e.estado in ("atordoado",)
            dano = a["dano"] * j.mult_dano * (1.5 if critico else 1)
            self.ferir_inimigo(e, dano, a["postura"], critico)
            self.sangue(e.pos, para.normalize() if dist > 0 else direcao(j.face), 8,
                        (200, 195, 180) if e.tipo in ("ossada",) else (140, 15, 20))
            self.hitstop = max(self.hitstop, 0.09 if a is PESADO else 0.05)
            self.trauma = min(1.0, self.trauma + (0.3 if a is PESADO else 0.15))
            tocar("acerto", 0.7)

    def ferir_inimigo(self, e, dano, postura, critico=False):
        dano = int(dano)
        e.vida -= dano
        e.flash = 0.08
        e.mostrar_vida = 4.0
        e.postura_t = 2.5
        self.texto(e.pos + Vector2(0, -e.raio - 10), str(dano), OURO if critico else BRANCO, 26 if critico else 20)
        if e.estado == "parado" or e.estado == "voltar":
            e.estado = "perseguir"
        if not e.chefe:
            para = e.pos - self.jogador.pos
            if para.length() > 0:
                e.vel += para.normalize() * 160
        e.postura -= postura
        if e.postura <= 0 and e.estado not in ("aparado", "transicao") and e.vida > 0:
            e.postura = e.d["postura"]
            e.estado, e.espera = "atordoado", (1.4 if e.chefe else 0.9)
            e.combo = None
            self.faiscas(e.pos, 20, OURO)
            self.texto(e.pos + Vector2(0, -e.raio - 26), "QUEBRADO", OURO, 22)
        if e.vida <= 0:
            self.matar_inimigo(e)

    def matar_inimigo(self, e):
        e.morto = True
        j = self.jogador
        j.almas += int(e.d["almas"] * self.ng)
        for _ in range(30):
            self.particula(e.pos + Vector2(random.uniform(-e.raio, e.raio), random.uniform(-e.raio, e.raio)),
                           Vector2(random.uniform(-20, 20), -random.uniform(30, 90)), random.uniform(0.8, 1.6),
                           misturar(e.d["cor"], (60, 60, 60), 0.3), random.uniform(1.5, 3), "ponto")
        for _ in range(8):
            self.particula(e.pos, Vector2(random.uniform(-40, 40), -random.uniform(40, 100)), 1.2, ALMA, 2, "ponto")
        tocar("inimigo_morre", 0.6)
        if self.alvo is e:
            self.alvo = None
            self.trocar_alvo(silencioso=True)
        if e.chefe:
            e.morto_para_sempre = True
            self.chefe = None
            self.perigos.clear()
            self.hitstop = 0.4
            self.escala_tempo = 0.2
            self.trauma = 1.0
            self.escuridao = 0.0
            self.tocar_musica(None)
            tocar("vitoria")
            self.anunciar("GRANDE INIMIGO ABATIDO", OURO, 4.5, 60)
            if e.tipo == "guarda":
                self.mundo.nevoeiro_ativo["guarda"] = False
                self.mundo.portoes_abertos = True
            else:
                self.fim_t = 5.5

    def atingir_jogador(self, e, g, origem=None):
        j = self.jogador
        if j.invulneravel or j.estado == "morto":
            return False
        origem = e.pos if origem is None else origem
        para = origem - j.pos
        if j.estado == "aparar" and j.t < 0.2 and g["aparavel"] and e is not None:
            if abs(angulo_dif(math.atan2(para.y, para.x), j.face)) < math.radians(100):
                e.estado, e.espera = "aparado", (1.3 if e.chefe else 1.7)
                e.combo = None
                self.hitstop = 0.14
                self.trauma = 0.5
                self.faiscas(j.pos + direcao(j.face) * 14, 26, (255, 230, 170), 380)
                self.texto(e.pos + Vector2(0, -e.raio - 12), "APARADO", BRANCO, 24)
                tocar("aparar")
                return True
        dano = g["dano"] * (1 + (self.ng - 1) * 0.5)
        j.vida -= dano
        j.invul = 0.45
        j.estado, j.t = "atingido", 0.0
        empurrao = -para.normalize() if para.length() > 0 else Vector2(0, 1)
        j.vel = empurrao * 260
        self.hitstop = 0.08
        self.trauma = min(1.0, self.trauma + 0.5)
        self.sangue(j.pos, empurrao, 14)
        tocar("dano", 0.8)
        if j.vida <= 0:
            self.morrer()
        return True

    def morrer(self):
        j = self.jogador
        j.vida = 0
        j.estado, j.t = "morto", 0.0
        self.mortes += 1
        self.alvo = None
        self.escala_tempo = 0.3
        self.anunciar("MORRESTE", (170, 20, 25), 4.2, 92)
        tocar("morte")
        self.tocar_musica(None)
        self.sangue(j.pos, Vector2(0, 1), 30)

    def renascer(self):
        j = self.jogador
        # As almas ficam onde caiste. Se morreres antes de lá chegar, perdem-se.
        self.mancha = (Vector2(j.pos), j.almas) if j.almas > 0 else None
        j.almas = 0
        j.pos = Vector2(self.respawn) + Vector2(0, 26)
        self.mundo.empurrar(j)
        self.descansar()
        self.cam = Vector2(j.pos)
        self.anuncio = None

    def descansar(self):
        j = self.jogador
        j.vida = j.vida_rasto = j.vida_max
        j.stamina = j.stamina_max
        j.caldo = j.caldo_max
        j.estado, j.t = "livre", 0.0
        j.vel = Vector2()
        for e in self.inimigos:
            e.repor()
        self.chefe = None
        self.alvo = None
        self.perigos.clear()
        self.escuridao = 0.0
        self.tocar_musica("vento")

    # ---------------------------------------------------------- combate: os inimigos
    def iniciar_passo(self, e):
        g = e.golpe
        e.fase, e.fase_t, e.atingiu = "ante", g["ante"] * (0.8 if e.fase_chefe == 2 else 1), False
        e.invisivel = False
        e.teleportou = False
        j = self.jogador
        if g["forma"] == "salto":
            e.salto_ini = Vector2(e.pos)
            e.salto_alvo = Vector2(j.pos)
        elif g["forma"] == "fantasmas":
            arena = ARENAS["final"]
            for k in range(3):
                horizontal = random.random() < 0.5
                if k == 0:
                    y, x = j.pos.y, j.pos.x
                else:
                    y = random.uniform(arena.top + 40, arena.bottom - 40)
                    x = random.uniform(arena.left + 40, arena.right - 40)
                if horizontal:
                    a, b = Vector2(arena.left, y), Vector2(arena.right, y)
                else:
                    a, b = Vector2(x, arena.top), Vector2(x, arena.bottom)
                if random.random() < 0.5:
                    a, b = b, a
                self.perigos.append({"tipo": "faixa", "a": a, "b": b, "aviso": 1.0 + k * 0.35, "t": 0.0,
                                     "dur": 0.45, "atingiu": False, "dano": g["dano"]})

    def atualizar_inimigo(self, e, dt):
        j = self.jogador
        e.t += dt
        e.flash -= dt
        e.mostrar_vida -= dt
        e.vida_rasto += (e.vida - e.vida_rasto) * min(1, dt * 1.2)
        e.postura_t -= dt
        if e.postura_t <= 0:
            e.postura = min(e.d["postura"], e.postura + e.d["postura"] * 0.4 * dt)
        para = j.pos - e.pos
        dist = para.length() or 1
        ang_jogador = math.atan2(para.y, para.x)
        mover = Vector2()

        if e.estado == "parado":
            e.ver_t -= dt
            if not e.chefe and e.ver_t <= 0:
                e.ver_t = 0.25
                if dist < e.d["aggro"] and j.estado != "morto" and self.mundo.ve(e.pos, j.pos):
                    e.estado = "perseguir"
                    e.cd = random.uniform(0.3, 0.8)
        elif e.estado == "voltar":
            casa = e.casa - e.pos
            if casa.length() < 6:
                e.estado = "parado"
                e.vida = e.vida_max
            else:
                mover = casa.normalize() * e.d["vel"]
                e.face = rodar_para(e.face, math.atan2(casa.y, casa.x), dt * 6)
        elif e.estado == "perseguir":
            if j.estado == "morto" or (not e.chefe and dist > 650):
                e.estado = "voltar"
            else:
                e.face = rodar_para(e.face, ang_jogador, dt * 6)
                e.cd -= dt
                combos = e.d["combos"] + (e.d.get("combos_fase2", []) if e.fase_chefe == 2 else [])
                possiveis = [c for c in combos if c[0] <= dist <= c[1]]
                if e.cd <= 0 and possiveis:
                    e.combo = random.choice(possiveis)[2]
                    e.passo = 0
                    e.estado = "atacar"
                    self.iniciar_passo(e)
                else:
                    desejada = 70 if e.tipo == "lanceiro" else e.raio + j.raio + 18
                    if dist > desejada:
                        mover = para / dist * e.d["vel"]
                    else:
                        mover = para.rotate(90 * e.lado) / dist * e.d["vel"] * 0.4
                        if random.random() < dt * 0.5:
                            e.lado *= -1
        elif e.estado == "atacar":
            g = e.golpe
            e.fase_t -= dt
            forma = g["forma"]
            if e.fase == "ante":
                if forma == "salto":
                    total = g["ante"] * (0.8 if e.fase_chefe == 2 else 1)
                    s = 1 - max(0.0, e.fase_t) / total
                    if e.fase_t > 0.35:
                        e.salto_alvo = Vector2(j.pos)
                    if s > 0.2:
                        voo = (s - 0.2) / 0.8
                        e.pos = e.salto_ini.lerp(e.salto_alvo, voo)
                        e.altura = math.sin(math.pi * voo)
                elif forma == "teleporte":
                    total = g["ante"] * (0.8 if e.fase_chefe == 2 else 1)
                    if e.fase_t < total / 2 and not e.teleportou:
                        # Desaparece no nevoeiro e reaparece nas tuas costas.
                        e.invisivel = True
                        e.teleportou = True
                        for _ in range(20):
                            self.particula(e.pos, Vector2(random.uniform(-60, 60), random.uniform(-60, 60)), 0.8,
                                           (200, 200, 210), 4, "ponto")
                        e.pos = j.pos - direcao(j.face) * 70
                        self.mundo.empurrar(e)
                    if e.fase_t < total * 0.2:
                        e.invisivel = False
                    e.face = rodar_para(e.face, ang_jogador, dt * 10)
                else:
                    e.face = rodar_para(e.face, ang_jogador, dt * g["rastreio"])
                if e.fase_t <= 0:
                    e.fase, e.fase_t = "ativo", g["ativo"]
                    e.invisivel = False
                    e.altura = 0.0
                    tocar("golpe", 0.5)
                    if forma in ("pancada", "salto"):
                        tocar("pancada", 0.8)
                        self.trauma = min(1.0, self.trauma + 0.5)
                        self.perigos.append({"tipo": "anel", "c": Vector2(e.pos), "r": 20.0, "max": 230.0,
                                             "atingiu": False, "dano": g["dano"] * 0.6})
                        for _ in range(26):
                            self.particula(e.pos, Vector2(1, 0).rotate(random.uniform(0, 360)) * random.uniform(80, 220),
                                           0.6, (120, 110, 100), 3, "ponto")
            elif e.fase == "ativo":
                if g["impulso"]:
                    mover = direcao(e.face) * g["impulso"]
                if not e.atingiu and forma != "fantasmas":
                    acerta = False
                    if forma == "estocada":
                        acerta = dist_segmento(j.pos, e.pos, e.pos + direcao(e.face) * g["alcance"]) <= g["largura"] + j.raio
                    elif forma in ("pancada", "salto"):
                        acerta = dist <= g["alcance"] + j.raio
                    else:
                        acerta = dist <= g["alcance"] + j.raio and abs(angulo_dif(ang_jogador, e.face)) <= g["arco"] / 2
                    if acerta and self.atingir_jogador(e, g):
                        e.atingiu = True
                if e.fase_t <= 0:
                    e.fase, e.fase_t = "rec", g["rec"] * (0.75 if e.fase_chefe == 2 else 1)
            elif e.fase == "rec":
                if e.fase_t <= 0 and e.estado == "atacar":
                    e.passo += 1
                    if e.passo < len(e.combo):
                        self.iniciar_passo(e)
                    else:
                        e.combo = None
                        e.estado = "perseguir"
                        e.cd = random.uniform(0.2, 0.7) if e.chefe else random.uniform(0.6, 1.4)
        elif e.estado in ("atordoado", "aparado"):
            e.espera -= dt
            if e.espera <= 0:
                e.estado = "perseguir"
                e.cd = 0.3
        elif e.estado == "transicao":
            if e.t > 2.2:
                e.estado = "perseguir"
                e.cd = 0.2

        # D. Sebastiao a meio da vida: o nevoeiro adensa-se
        if e.tipo == "sebastiao" and e.fase_chefe == 1 and e.vida < e.vida_max / 2 and e.estado not in ("aparado", "atordoado"):
            e.fase_chefe = 2
            e.estado, e.t, e.combo = "transicao", 0.0, None
            e.altura = 0.0
            e.invisivel = False
            self.escuridao = 1.0
            self.trauma = 0.8
            tocar("rugido")
            self.anunciar("O nevoeiro adensa-se...", (190, 195, 210), 2.6, 40)

        e.vel *= 0.002 ** dt
        if e.altura <= 0:
            self.mundo.mover(e, (mover + e.vel) * dt)
        # Ninguem atravessa ninguem
        separar = e.pos - j.pos
        minimo = e.raio + j.raio
        if 0 < separar.length() < minimo and j.estado not in ("morto", "nevoeiro") and e.altura <= 0:
            empurra = separar.normalize() * (minimo - separar.length())
            if e.chefe:
                j.pos -= empurra
                self.mundo.empurrar(j)
            else:
                e.pos += empurra * 0.5
                j.pos -= empurra * 0.5

    def atualizar_perigos(self, dt):
        j = self.jogador
        vivos = []
        for p in self.perigos:
            if p["tipo"] == "anel":
                p["r"] += 260 * dt
                if not p["atingiu"] and abs(j.pos.distance_to(p["c"]) - p["r"]) < 12 + j.raio:
                    if self.atingir_jogador(None, {"dano": p["dano"], "aparavel": False}, p["c"]):
                        p["atingiu"] = True
                if p["r"] < p["max"]:
                    vivos.append(p)
            else:
                if p["aviso"] > 0:
                    p["aviso"] -= dt
                    vivos.append(p)
                    continue
                p["t"] += dt
                cavaleiro = p["a"].lerp(p["b"], min(1.0, p["t"] / p["dur"]))
                p["pos"] = cavaleiro
                if random.random() < 0.8:
                    self.particula(cavaleiro, Vector2(random.uniform(-40, 40), random.uniform(-40, 40)), 0.5,
                                   (170, 190, 230), 4, "ponto")
                if not p["atingiu"] and j.pos.distance_to(cavaleiro) < 30 + j.raio:
                    if self.atingir_jogador(None, {"dano": p["dano"], "aparavel": False}, cavaleiro):
                        p["atingiu"] = True
                if p["t"] < p["dur"]:
                    vivos.append(p)
        self.perigos = vivos

    # ---------------------------------------------------------- interagir
    def interacao(self):
        j = self.jogador
        if j.estado != "livre":
            return None
        m = self.mundo
        for f in m.fogareiros:
            if j.pos.distance_to(f["pos"]) < 46:
                return ("fogareiro", f, "Descansar" if f["aceso"] else "Acender o fogareiro")
        for it in m.itens:
            if not it["apanhado"] and j.pos.distance_to(it["pos"]) < 30:
                return ("item", it, "Apanhar")
        for msg in m.mensagens:
            if j.pos.distance_to(msg["pos"]) < 30:
                return ("mensagem", msg, "Ler a mensagem")
        if not m.porta_aberta:
            centro = Vector2((m.porta[0][0] + 1) * TILE, m.porta[0][1] * TILE + TILE / 2)
            if j.pos.distance_to(centro) < 50:
                return ("porta", centro, "Abrir" if j.pos.y < centro.y else "Abrir")
        for nome, tiles in m.nevoeiro.items():
            if not m.nevoeiro_ativo[nome]:
                continue
            xs = [x for x, _ in tiles]
            y = tiles[0][1] * TILE + TILE / 2
            centro = Vector2((min(xs) + max(xs) + 1) / 2 * TILE, y)
            fora = j.pos.y > y if nome == "guarda" else j.pos.y < y
            if fora and j.pos.distance_to(centro) < 44 + len(tiles) * 12 and abs(j.pos.y - y) < 44:
                return ("nevoeiro", (nome, y), "Atravessar o nevoeiro")
        return None

    def interagir(self):
        coisa = self.interacao()
        if coisa is None:
            return
        tipo, obj, _ = coisa
        j = self.jogador
        if tipo == "fogareiro":
            self.respawn = Vector2(obj["pos"])
            if not obj["aceso"]:  # acender e uma coisa, descansar e outra
                obj["aceso"] = True
                self.anunciar("FOGAREIRO ACESO", FOGO, 3.2, 60)
                tocar("fogareiro")
                return
            self.descansar()
            self.estado = "fogareiro"
            self.menu = "principal"
            self.menu_i = 0
        elif tipo == "item":
            obj["apanhado"] = True
            tocar("almas", 0.6)
            if obj["tipo"] == "tigela":
                j.caldo_max += 1
                j.caldo += 1
                self.anunciar("Obtido: Tigela de Caldo Verde", (150, 210, 120), 2.6, 34)
            else:
                j.almas += 600
                self.anunciar("Obtido: Alma de um fadista (+600)", ALMA, 2.6, 34)
        elif tipo == "mensagem":
            self.leitura = obj["texto"]
            self.leitura_t = 5.0
        elif tipo == "porta":
            if j.pos.y < obj.y:
                self.mundo.porta_aberta = True
                tocar("porta")
                self.trauma = 0.3
                self.anunciar("Atalho aberto", BRANCO, 2.2, 34)
            else:
                self.leitura = "Não abre deste lado."
                self.leitura_t = 2.5
        elif tipo == "nevoeiro":
            nome, y = obj
            j.estado, j.t = "nevoeiro", 0.0
            j.nevoeiro_de = Vector2(j.pos)
            destino_y = y - TILE * 1.6 if nome == "guarda" else y + TILE * 1.6
            j.nevoeiro_para = Vector2(j.pos.x, destino_y)
            j.face = -math.pi / 2 if nome == "guarda" else math.pi / 2
            tocar("nevoeiro")

    def trocar_alvo(self, silencioso=False):
        j = self.jogador
        candidatos = [e for e in self.vivos() if e.pos.distance_to(j.pos) < 360 and e is not self.alvo
                      and self.mundo.ve(j.pos, e.pos)]
        if not candidatos:
            if not silencioso:
                self.alvo = None
            return
        frente = direcao(j.face)
        self.alvo = min(candidatos, key=lambda e: e.pos.distance_to(j.pos) - (e.pos - j.pos).normalize().dot(frente) * 80
                        if e.pos != j.pos else 0)

    # ---------------------------------------------------------- nivel
    def custo_nivel(self):
        n = self.jogador.nivel
        return int(60 + 22 * n ** 1.5)

    def subir(self, atributo):
        j = self.jogador
        custo = self.custo_nivel()
        if j.almas < custo:
            tocar("bloqueio", 0.4)
            return
        j.almas -= custo
        j.nivel += 1
        setattr(j, atributo, getattr(j, atributo) + 1)
        j.vida = j.vida_max
        j.stamina = j.stamina_max
        tocar("almas", 0.7)

    # ---------------------------------------------------------- eventos
    def evento(self, ev):
        if ev.type != pygame.KEYDOWN:
            return
        k = ev.key
        if self.estado == "titulo":
            if k == pygame.K_ESCAPE:
                self.sair = True
            elif k in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e):
                self.estado = "jogo"
                self.buffer = None
                self.particulas = []
        elif self.estado == "jogo":
            j = self.jogador
            if k == pygame.K_ESCAPE:
                self.estado = "pausa"
                return
            if self.leitura is not None and k in (pygame.K_e, pygame.K_RETURN):
                self.leitura = None
                return
            if j.estado == "morto":
                return
            acoes = {pygame.K_SPACE: "rolar", pygame.K_j: "leve", pygame.K_z: "leve", pygame.K_k: "pesado",
                     pygame.K_x: "pesado", pygame.K_l: "aparar", pygame.K_c: "aparar", pygame.K_q: "beber"}
            if k in acoes:
                self.buffer = acoes[k]
                self.buffer_t = 0.3
            elif k in (pygame.K_TAB, pygame.K_r):
                if self.alvo is None:
                    self.trocar_alvo()
                else:
                    self.alvo = None
            elif k in (pygame.K_e, pygame.K_RETURN):
                self.interagir()
        elif self.estado == "pausa":
            if k in (pygame.K_ESCAPE, pygame.K_RETURN):
                self.estado = "jogo"
            elif k == pygame.K_q:
                self.sair = True
        elif self.estado == "fogareiro":
            opcoes = self.opcoes_menu()
            if k in (pygame.K_w, pygame.K_UP):
                self.menu_i = (self.menu_i - 1) % len(opcoes)
            elif k in (pygame.K_s, pygame.K_DOWN):
                self.menu_i = (self.menu_i + 1) % len(opcoes)
            elif k in (pygame.K_e, pygame.K_RETURN, pygame.K_j, pygame.K_z):
                escolha = opcoes[self.menu_i][1]
                if escolha == "nivel":
                    self.menu, self.menu_i = "nivel", 0
                elif escolha == "partir":
                    self.estado = "jogo"
                    self.buffer = None
                elif escolha == "voltar":
                    self.menu, self.menu_i = "principal", 0
                else:
                    self.subir(escolha)
            elif k == pygame.K_ESCAPE:
                if self.menu == "nivel":
                    self.menu, self.menu_i = "principal", 0
                else:
                    self.estado = "jogo"
                    self.buffer = None
        elif self.estado == "fim":
            if k == pygame.K_RETURN and self.fim_t > 6:
                self.ng += 1
                self.novo_mundo(self.jogador)
                self.estado = "jogo"
                self.buffer = None
                self.tocar_musica("vento")
            elif k == pygame.K_ESCAPE:
                self.sair = True

    def opcoes_menu(self):
        if self.menu == "principal":
            return [("Subir de nível", "nivel"), ("Partir", "partir")]
        j = self.jogador
        return [(f"Vigor  {j.vigor}   (vida {j.vida_max})", "vigor"),
                (f"Fôlego  {j.folego}   (stamina {j.stamina_max})", "folego"),
                (f"Força  {j.forca}   (dano x{j.mult_dano:.1f})", "forca"),
                ("Voltar", "voltar")]

    # ---------------------------------------------------------- atualizar
    def atualizar(self, dt):
        self.tempo_real += dt
        self.trauma = max(0.0, self.trauma - dt * 1.4)
        for c in self.cinzas:
            c[1] += (14 + c[2] * 22) * dt
            c[0] += math.sin(self.tempo_real * 0.7 + c[2] * 9) * 10 * dt
            if c[1] > ALTURA:
                c[0], c[1] = random.uniform(0, LARGURA), -5
        for n in self.nuvens:
            n[0] += n[2] * dt
            if n[0] > LARGURA + 200:
                n[0], n[1] = -360, random.uniform(-60, ALTURA)
        if self.anuncio is not None:
            self.anuncio[2] += dt
            if self.anuncio[2] > self.anuncio[3]:
                self.anuncio = None
        if self.estado == "titulo":
            self.atualizar_particulas(dt)
            return
        if self.estado not in ("jogo", "fim"):
            return
        if self.estado == "fim":
            self.fim_t += dt
            return
        if self.hitstop > 0:
            self.hitstop -= dt
            return
        self.escala_tempo += (1 - self.escala_tempo) * min(1, dt * 2)
        dt *= self.escala_tempo
        self.tempo_jogo += dt
        if self.leitura is not None:
            self.leitura_t -= dt
            if self.leitura_t <= 0:
                self.leitura = None
        if self.fim_t > 0:
            self.fim_t -= dt
            if self.fim_t <= 0:
                self.estado = "fim"
                self.fim_t = 0.0
                return
        self.atualizar_jogador(dt)
        for e in self.inimigos:
            if not e.morto:
                self.atualizar_inimigo(e, dt)
        self.atualizar_perigos(dt)
        self.atualizar_particulas(dt)
        j = self.jogador
        alvo_cam = Vector2(j.pos)
        if self.alvo is not None:
            alvo_cam += (self.alvo.pos - j.pos) * 0.3
        self.cam += (alvo_cam - self.cam) * min(1, dt * 6)
        abanao = self.trauma ** 2 * 14
        self.camara = self.cam - Vector2(LARGURA / 2, ALTURA / 2) + Vector2(random.uniform(-1, 1), random.uniform(-1, 1)) * abanao
        # As brasas dos fogareiros
        for f in self.mundo.fogareiros:
            if f["aceso"] and abs(f["pos"].x - self.cam.x) < LARGURA and random.random() < 0.5:
                self.particula(f["pos"] + Vector2(random.uniform(-8, 8), -4), Vector2(random.uniform(-15, 15), -random.uniform(40, 90)),
                               random.uniform(0.6, 1.4), FOGO, 2, "ponto")

    def atualizar_particulas(self, dt):
        vivas = []
        for p in self.particulas:
            p[2] -= dt
            if p[2] > 0:
                p[0] += p[1] * dt
                p[1] *= 1 / (1 + 3 * dt)
                p[1].y += p[7] * dt
                vivas.append(p)
        self.particulas = vivas
        for t in self.textos:
            t[4] -= dt
            t[0].y -= 30 * dt
        self.textos = [t for t in self.textos if t[4] > 0]

    # ---------------------------------------------------------- desenhar
    def desenhar(self):
        cena = self.cena
        if self.estado == "titulo":
            self.desenhar_titulo(cena)
        elif self.estado == "fim":
            self.desenhar_fim(cena)
        else:
            self.desenhar_mundo(cena)
            self.desenhar_hud(cena)
            if self.estado == "fogareiro":
                self.desenhar_menu(cena)
            elif self.estado == "pausa":
                self.desenhar_pausa(cena)
        self.desenhar_anuncio(cena)
        self.ecra.blit(cena, (0, 0))

    def desenhar_mundo(self, cena):
        cam = self.camara
        m = self.mundo
        j = self.jogador
        cena.fill(FUNDO)
        cena.blit(m.superficie, (-cam.x, -cam.y))
        visivel = pygame.Rect(cam.x - 64, cam.y - 64, LARGURA + 128, ALTURA + 128)

        # Portas e portoes
        if not m.porta_aberta:
            for x, y in m.porta:
                r = pygame.Rect(x * TILE - cam.x, y * TILE - cam.y, TILE, TILE)
                pygame.draw.rect(cena, (70, 48, 30), r)
                pygame.draw.rect(cena, (40, 26, 16), r, 2)
                for k in range(1, 4):
                    pygame.draw.line(cena, (50, 34, 20), (r.x + k * 8, r.y), (r.x + k * 8, r.bottom))
        if not m.portoes_abertos:
            for x, y in m.portoes:
                r = pygame.Rect(x * TILE - cam.x, y * TILE - cam.y, TILE, TILE)
                for k in range(4):
                    pygame.draw.line(cena, (90, 90, 100), (r.x + 4 + k * 8, r.y), (r.x + 4 + k * 8, r.bottom), 3)
                pygame.draw.line(cena, (90, 90, 100), (r.x, r.y + 10), (r.right, r.y + 10), 2)

        for s in self.manchas_sangue:
            pygame.draw.circle(cena, s[2], s[0] - cam, s[1])
        for f in m.fogareiros:
            p = f["pos"] - cam
            pygame.draw.rect(cena, (50, 45, 45), (p.x - 14, p.y - 6, 28, 14))
            pygame.draw.rect(cena, (25, 22, 22), (p.x - 14, p.y - 6, 28, 14), 2)
            pygame.draw.line(cena, (25, 22, 22), (p.x - 10, p.y + 8), (p.x - 12, p.y + 16), 2)
            pygame.draw.line(cena, (25, 22, 22), (p.x + 10, p.y + 8), (p.x + 12, p.y + 16), 2)
            for k in range(3):  # tres sardinhas na grelha, claro
                pygame.draw.ellipse(cena, (150, 160, 170), (p.x - 11 + k * 8, p.y - 4, 6, 10))
        for e in self.inimigos:
            if not e.morto and visivel.collidepoint(e.pos):
                pygame.draw.ellipse(cena, (12, 10, 14), (e.pos.x - cam.x - e.raio, e.pos.y - cam.y + e.raio * 0.4,
                                                         e.raio * 2, e.raio * 0.9))
        pygame.draw.ellipse(cena, (12, 10, 14), (j.pos.x - cam.x - 11, j.pos.y - cam.y + 5, 22, 10))
        coisas = [e for e in self.inimigos if not e.morto and visivel.collidepoint(e.pos)]
        coisas.sort(key=lambda e: e.pos.y)
        jogador_desenhado = False
        for e in coisas:
            if not jogador_desenhado and e.pos.y > j.pos.y:
                self.desenhar_jogador(cena)
                jogador_desenhado = True
            self.desenhar_inimigo(cena, e)
        if not jogador_desenhado:
            self.desenhar_jogador(cena)

        # ---- A luz: tudo o que esta acima e multiplicado por isto ----
        luz = self.luz
        ambiente = misturar((66, 62, 78), (26, 26, 34), self.escuridao)
        luz.fill(ambiente)
        tocha = 270 - self.escuridao * 90 + math.sin(self.tempo_real * 11) * 4
        self.acender(j.pos, tocha, (255, 215, 170))
        for f in m.fogareiros:
            if visivel.collidepoint(f["pos"]):
                tremor = math.sin(self.tempo_real * 13 + f["pos"].x) * 10 + random.uniform(-6, 6)
                self.acender(f["pos"], (280 if f["aceso"] else 90) + tremor, (255, 150, 70) if f["aceso"] else (90, 60, 40))
        for msg in m.mensagens:
            if visivel.collidepoint(msg["pos"]):
                self.acender(msg["pos"], 48, (180, 110, 50))
        for it in m.itens:
            if not it["apanhado"] and visivel.collidepoint(it["pos"]):
                self.acender(it["pos"], 64, (170, 200, 220))
        if self.mancha is not None:
            self.acender(self.mancha[0], 90, (90, 200, 150))
        for nome, tiles in m.nevoeiro.items():
            if m.nevoeiro_ativo[nome]:
                for x, y in tiles:
                    self.acender(Vector2(x * TILE + 16, y * TILE + 16), 80, (120, 120, 140))
        for e in coisas:
            if e.tipo == "sebastiao":
                self.acender(e.pos, 140, (150, 120, 60))
        cena.blit(luz, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

        # ---- Coisas que brilham: desenham-se depois da luz ----
        self.desenhar_brilhos(cena, cam)
        alpha_nevoa = 26 + int(self.escuridao * 40)
        self.nuvem.set_alpha(alpha_nevoa)
        for n in self.nuvens:
            cena.blit(self.nuvem, (n[0], n[1]))
        for c in self.cinzas:  # cinza a cair, nao estrelas: escura e lenta
            v = int(55 + c[2] * 45)
            cena.fill((v, v - 4, v - 8), (c[0], c[1], 2, 2 if c[2] > 0.6 else 1))

    def acender(self, pos, raio, cor):
        g = self.gradiente(raio, cor)
        self.luz.blit(g, (pos.x - self.camara.x - g.get_width() / 2, pos.y - self.camara.y - g.get_height() / 2),
                      special_flags=pygame.BLEND_RGB_ADD)

    def desenhar_jogador(self, cena):
        j = self.jogador
        cam = self.camara
        p = j.pos - cam
        if j.estado == "morto":
            pygame.draw.ellipse(cena, (55, 45, 42), (p.x - 14, p.y - 6, 28, 14))
            return
        if j.invul > 0 and int(j.invul * 20) % 2:
            return  # pisca depois de levar um golpe
        frente = direcao(j.face)
        if j.estado == "rolar":
            giro = j.t * 22
            pygame.draw.circle(cena, (58, 50, 46), p, 10)
            pygame.draw.line(cena, (100, 90, 80), p + direcao(giro) * -8, p + direcao(giro) * 8, 3)
            return
        # espada
        espada_ang = j.face + 0.9
        if j.estado == "atacar":
            a = j.ataque
            lado = -1 if j.combo % 2 else 1
            ini = j.face + lado * a["arco"] / 2
            fim = j.face - lado * a["arco"] / 2
            if j.fase == "ante":
                espada_ang = ini + lado * 0.4 * (1 - j.fase_t / a["ante"])
            elif j.fase == "ativo":
                espada_ang = ini + (fim - ini) * (1 - j.fase_t / a["ativo"])
            else:
                espada_ang = fim
        elif j.estado == "riposte":
            espada_ang = j.face
        d = direcao(espada_ang)
        comprimento = 34 if j.estado != "riposte" else 40
        pygame.draw.line(cena, (200, 200, 210), p + d * 8, p + d * comprimento, 3)
        pygame.draw.line(cena, (120, 90, 50), p + d * 6 + d.rotate(90) * 5, p + d * 6 - d.rotate(90) * 5, 3)
        # corpo, capa e elmo
        pygame.draw.circle(cena, (60, 50, 46), p - frente * 2, 12)
        pygame.draw.circle(cena, (95, 82, 70), p, 10)
        pygame.draw.circle(cena, (140, 132, 125), p + frente * 3, 6)
        pygame.draw.line(cena, (30, 28, 30), p + frente * 6 + frente.rotate(90) * 3, p + frente * 6 - frente.rotate(90) * 3, 2)
        # escudo
        if j.estado == "aparar":
            centro = p + frente * 13
            pygame.draw.circle(cena, (170, 120, 60), centro, 8)
            pygame.draw.circle(cena, (90, 60, 30), centro, 8, 2)
        else:
            centro = p + frente.rotate(-80) * 11
            pygame.draw.circle(cena, (130, 95, 50), centro, 6)
            pygame.draw.circle(cena, (70, 50, 25), centro, 6, 2)
        if j.estado == "beber":
            pygame.draw.circle(cena, (100, 150, 70), p + frente * 9, 4)

    def desenhar_inimigo(self, cena, e):
        cam = self.camara
        p = e.pos - cam - Vector2(0, e.altura * 70)
        if e.invisivel:
            return
        cor = BRANCO if e.flash > 0 else e.d["cor"]
        escuro = misturar(cor, (0, 0, 0), 0.5)
        frente = direcao(e.face)
        g = e.golpe if e.estado == "atacar" else None
        arma = e.face + 0.8
        if g is not None:
            total = max(0.01, g["ante"] * (0.8 if e.fase_chefe == 2 else 1))
            if e.fase == "ante":
                arma = e.face + 1.3 + 0.6 * (1 - max(0.0, e.fase_t) / total)
            elif e.fase == "ativo":
                arma = e.face + 1.3 - 2.6 * (1 - max(0.0, e.fase_t) / g["ativo"])
            else:
                arma = e.face - 1.3
            if g["forma"] in ("estocada", "carga"):
                arma = e.face + (0.25 if e.fase == "ante" else 0)
        escala = 1 + e.altura * 0.4
        r = e.raio * escala
        if e.estado in ("atordoado", "aparado"):
            arma = e.face + 2.2
        if e.tipo == "cao":
            corpo = [p + frente * (r * 1.2 * math.cos(a)) + frente.rotate(90) * (r * 0.6 * math.sin(a))
                     for a in [k * TAU / 12 for k in range(12)]]
            pygame.draw.polygon(cena, cor, corpo)
            pygame.draw.polygon(cena, escuro, corpo, 2)
            pygame.draw.circle(cena, cor, p + frente * r * 1.3, r * 0.55)
            pygame.draw.circle(cena, (200, 40, 30), p + frente * r * 1.5 + frente.rotate(90) * 3, 1.5)
            return
        if e.tipo == "sebastiao":
            capa = [p - frente * r * 1.6 + frente.rotate(90) * r * 1.1, p + frente.rotate(90) * r,
                    p - frente.rotate(90) * r, p - frente * r * 1.6 - frente.rotate(90) * r * 1.1]
            pygame.draw.polygon(cena, (110, 20, 30), capa)
        comprimento = {"lanceiro": 64, "guarda": 46, "sebastiao": 50}.get(e.tipo, 30) * escala
        d = direcao(arma)
        if e.tipo == "lanceiro":
            pygame.draw.line(cena, (110, 85, 60), p - d * 18, p + d * comprimento, 3)
            pygame.draw.polygon(cena, (190, 190, 200), [p + d * (comprimento + 10), p + d * comprimento + d.rotate(90) * 4,
                                                         p + d * comprimento - d.rotate(90) * 4])
        elif e.tipo == "guarda":
            pygame.draw.line(cena, (90, 75, 60), p, p + d * comprimento, 5)
            cabeca = p + d * comprimento
            pygame.draw.polygon(cena, (100, 100, 110), [cabeca + d.rotate(90) * 12 - d * 6, cabeca + d.rotate(90) * 12 + d * 8,
                                                         cabeca - d.rotate(90) * 12 + d * 8, cabeca - d.rotate(90) * 12 - d * 6])
        else:
            pygame.draw.line(cena, (170, 165, 160) if e.tipo == "ossada" else (215, 215, 225), p + d * 6, p + d * comprimento, 3)
        pygame.draw.circle(cena, escuro, p, r + 1)
        pygame.draw.circle(cena, cor, p, r)
        cabeca = p + frente * r * 0.35
        if e.tipo == "ossada":
            for s in (-1, 1):
                pygame.draw.circle(cena, (20, 15, 15), cabeca + frente.rotate(90 * s) * 4 + frente * 2, 2.5)
        elif e.tipo == "sebastiao":
            pygame.draw.circle(cena, (240, 210, 130), cabeca, r * 0.55)
            pygame.draw.line(cena, (190, 30, 40), cabeca, cabeca - frente * r * 1.2, 4)
        else:
            pygame.draw.circle(cena, misturar(cor, BRANCO, 0.2), cabeca, r * 0.5)
            pygame.draw.line(cena, (20, 20, 25), cabeca + frente * 3 + frente.rotate(90) * 4, cabeca + frente * 3 - frente.rotate(90) * 4, 2)

    def desenhar_brilhos(self, cena, cam):
        j = self.jogador
        t = self.tempo_real
        for msg in self.mundo.mensagens:
            p = msg["pos"] - cam
            pygame.draw.circle(cena, (220, 140, 60), p, 6 + math.sin(t * 3) * 1.5, 2)
            pygame.draw.line(cena, (220, 140, 60), p + Vector2(-4, 0), p + Vector2(4, 0), 2)
        for it in self.mundo.itens:
            if not it["apanhado"]:
                p = it["pos"] - cam
                brilho = 3 + math.sin(t * 5) * 1.5
                pygame.draw.circle(cena, (230, 240, 255), p, brilho)
                pygame.draw.line(cena, (200, 220, 255), p + Vector2(0, -9), p + Vector2(0, 9))
                pygame.draw.line(cena, (200, 220, 255), p + Vector2(-9, 0), p + Vector2(9, 0))
        if self.mancha is not None:
            p = self.mancha[0] - cam
            pygame.draw.circle(cena, (120, 240, 180), p, 7 + math.sin(t * 4) * 2)
            pygame.draw.circle(cena, (60, 160, 110), p, 13, 2)
        for nome, tiles in self.mundo.nevoeiro.items():
            if self.mundo.nevoeiro_ativo[nome]:
                for x, y in tiles:
                    for k in range(3):
                        p = Vector2(x * TILE + 16 + math.sin(t * 1.3 + x + k * 2) * 12,
                                    y * TILE + 16 + math.cos(t * 0.9 + k * 1.7 + x) * 8) - cam
                        pygame.draw.circle(cena, (170 + k * 15, 175 + k * 15, 190 + k * 15), p, 12 - k * 3)
        # Os golpes: o brilho de aviso (branco = apara-se, vermelho = rola) e o rasto
        for e in self.inimigos:
            if e.morto or e.invisivel:
                continue
            p = e.pos - cam - Vector2(0, e.altura * 70)
            g = e.golpe if e.estado == "atacar" else None
            if g is not None and e.fase == "ante":
                total = g["ante"] * (0.8 if e.fase_chefe == 2 else 1)
                if total - e.fase_t < 0.22:
                    cor = (255, 255, 255) if g["aparavel"] else (255, 40, 40)
                    ponta = p + direcao(e.face + 1.6) * (e.raio + 14)
                    tam = 10 * (1 - (total - e.fase_t) / 0.22)
                    pygame.draw.line(cena, cor, ponta - Vector2(tam, 0), ponta + Vector2(tam, 0), 2)
                    pygame.draw.line(cena, cor, ponta - Vector2(0, tam), ponta + Vector2(0, tam), 2)
                if g["forma"] == "salto":
                    alvo = e.salto_alvo - cam
                    pygame.draw.circle(cena, (200, 40, 40), alvo, g["alcance"], 2)
                elif g["forma"] == "pancada" and int(t * 14) % 2:
                    pygame.draw.circle(cena, (150, 40, 40), p, g["alcance"], 1)
            if g is not None and e.fase == "ativo" and g["forma"] in ("arco", "teleporte"):
                total = g["ativo"]
                progresso = 1 - max(0.0, e.fase_t) / total
                a0 = e.face + g["arco"] / 2
                a1 = a0 - g["arco"] * progresso
                pygame.draw.polygon(cena, (200, 190, 180) if g["aparavel"] else (220, 90, 80),
                                    crescente(p, e.raio + 6, g["alcance"], a0, a1))
            if g is not None and e.fase == "ativo" and g["forma"] == "estocada":
                fim = p + direcao(e.face) * g["alcance"]
                pygame.draw.line(cena, (230, 230, 240), p, fim, 2)
            if e.estado == "aparado":
                pygame.draw.circle(cena, (230, 50, 50), p + Vector2(0, -e.raio - 10), 4 + math.sin(t * 12) * 1.5)
            if e.estado == "atordoado":
                for k in range(3):
                    a = t * 5 + k * TAU / 3
                    pygame.draw.circle(cena, OURO, p + Vector2(math.cos(a) * 12, -e.raio - 8 + math.sin(a) * 4), 2)
        # O rasto da espada do jogador
        if j.estado == "atacar" and j.fase == "ativo":
            a = j.ataque
            lado = -1 if j.combo % 2 else 1
            ini = j.face + lado * a["arco"] / 2
            progresso = 1 - max(0.0, j.fase_t) / a["ativo"]
            atual = ini - lado * a["arco"] * progresso
            pygame.draw.polygon(cena, (230, 225, 210), crescente(j.pos - cam, 14, a["alcance"], ini, atual))
        if j.estado == "aparar" and j.t < 0.2:
            pygame.draw.circle(cena, (255, 220, 150), j.pos - cam + direcao(j.face) * 13, 10, 1)
        for pg in self.perigos:
            if pg["tipo"] == "anel":
                pygame.draw.circle(cena, (200, 170, 130), pg["c"] - cam, pg["r"], 5)
            else:
                a, b = pg["a"] - cam, pg["b"] - cam
                if pg["aviso"] > 0:
                    if int(pg["aviso"] * 10) % 2:
                        pygame.draw.line(cena, (170, 40, 50), a, b, 3)
                elif "pos" in pg:
                    c = pg["pos"] - cam
                    frente = (b - a).normalize()
                    pygame.draw.line(cena, (120, 140, 200), c - frente * 60, c, 18)
                    pygame.draw.polygon(cena, (200, 215, 245), [c + frente * 24, c + frente.rotate(90) * 14 - frente * 10,
                                                                 c - frente.rotate(90) * 14 - frente * 10])
        for p in self.particulas:
            f = p[2] / p[3]
            pos = p[0] - cam
            if p[6] == "faisca":
                pygame.draw.line(cena, misturar((0, 0, 0), p[4], f * 1.5), pos, pos - p[1] * 0.03, max(1, int(p[5])))
            else:
                pygame.draw.circle(cena, misturar((0, 0, 0), p[4], f * 1.5), pos, max(1, p[5] * f))
        for t_ in self.textos:
            escrever(cena, t_[1], t_[3], t_[0] - cam, t_[2], alpha=min(1, t_[4] * 3) * 255)
        if self.alvo is not None and not self.alvo.morto:
            p = self.alvo.pos - cam - Vector2(0, self.alvo.altura * 70)
            pygame.draw.circle(cena, BRANCO, p, 4)
            pygame.draw.circle(cena, (40, 40, 40), p, 4, 1)
        for e in self.inimigos:
            if not e.morto and not e.chefe and (e.mostrar_vida > 0 or e is self.alvo):
                p = e.pos - cam
                largura = 36
                pygame.draw.rect(cena, (30, 10, 10), (p.x - largura / 2, p.y - e.raio - 14, largura, 4))
                pygame.draw.rect(cena, (200, 170, 90), (p.x - largura / 2, p.y - e.raio - 14, largura * max(0, e.vida_rasto) / e.vida_max, 4))
                pygame.draw.rect(cena, VIDA, (p.x - largura / 2, p.y - e.raio - 14, largura * max(0, e.vida) / e.vida_max, 4))

    def desenhar_hud(self, cena):
        j = self.jogador
        # Vida (com o rasto amarelo do dano recente) e stamina
        ev = min(2.0, 440 / j.vida_max)  # a barra cresce com o vigor, mas nao sai do ecra
        es = min(2.0, 440 / j.stamina_max)
        pygame.draw.rect(cena, (20, 12, 12), (20, 20, j.vida_max * ev + 4, 14))
        pygame.draw.rect(cena, (190, 160, 80), (22, 22, j.vida_rasto * ev, 10))
        pygame.draw.rect(cena, VIDA, (22, 22, max(0, j.vida) * ev, 10))
        pygame.draw.rect(cena, (12, 20, 12), (20, 38, j.stamina_max * es + 4, 10))
        pygame.draw.rect(cena, FOLEGO, (22, 40, max(0, j.stamina) * es, 6))
        # Caldo verde
        x, y = 30, ALTURA - 44
        pygame.draw.rect(cena, (25, 22, 20), (x - 10, y - 12, 66, 40), border_radius=4)
        pygame.draw.circle(cena, (150, 130, 110), (x + 10, y + 6), 12, draw_top_right=False, draw_top_left=False,
                           draw_bottom_left=True, draw_bottom_right=True)
        pygame.draw.line(cena, (100, 160, 70) if j.caldo else (60, 60, 60), (x - 1, y + 6), (x + 21, y + 6), 3)
        escrever(cena, str(j.caldo), 30, (x + 40, y + 6), BRANCO if j.caldo else CINZA)
        # Almas
        r = pygame.Rect(0, 0, 150, 34)
        r.bottomright = (LARGURA - 20, ALTURA - 20)
        pygame.draw.rect(cena, (20, 18, 22), r, border_radius=4)
        pygame.draw.rect(cena, (70, 65, 75), r, 1, border_radius=4)
        pygame.draw.circle(cena, ALMA, (r.x + 18, r.centery), 6)
        escrever(cena, str(j.almas), 28, (r.right - 12, r.centery), BRANCO, "midright")
        # Chefe
        if self.chefe is not None and not self.chefe.morto:
            c = self.chefe
            barra = pygame.Rect(LARGURA / 2 - 300, ALTURA - 54, 600, 9)
            escrever(cena, c.d["nome"], 22, (barra.x, barra.y - 6), BRANCO, "bottomleft", serifa=True)
            pygame.draw.rect(cena, (25, 10, 10), barra.inflate(4, 4))
            pygame.draw.rect(cena, (190, 160, 80), (barra.x, barra.y, barra.w * max(0, c.vida_rasto) / c.vida_max, barra.h))
            pygame.draw.rect(cena, (140, 20, 25), (barra.x, barra.y, barra.w * max(0, c.vida) / c.vida_max, barra.h))
        # Interagir e mensagens
        coisa = self.interacao() if self.estado == "jogo" else None
        if coisa is not None and self.leitura is None:
            caixa = pygame.Rect(0, 0, 300, 34)
            caixa.center = (LARGURA // 2, ALTURA - 120)
            pygame.draw.rect(cena, (15, 13, 18), caixa, border_radius=4)
            pygame.draw.rect(cena, (110, 100, 90), caixa, 1, border_radius=4)
            escrever(cena, f"[E]  {coisa[2]}", 24, caixa.center, BRANCO)
        if self.leitura is not None:
            caixa = pygame.Rect(0, 0, 640, 70)
            caixa.center = (LARGURA // 2, ALTURA - 130)
            pygame.draw.rect(cena, (12, 10, 14), caixa, border_radius=6)
            pygame.draw.rect(cena, (180, 120, 60), caixa, 1, border_radius=6)
            escrever(cena, self.leitura, 24, caixa.center, (235, 215, 190), serifa=True)

    def desenhar_menu(self, cena):
        j = self.jogador
        sombra = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        sombra.fill((0, 0, 0, 150))
        cena.blit(sombra, (0, 0))
        caixa = pygame.Rect(0, 0, 440, 300)
        caixa.center = (LARGURA // 2, ALTURA // 2)
        pygame.draw.rect(cena, (16, 13, 14), caixa, border_radius=6)
        pygame.draw.rect(cena, (120, 80, 45), caixa, 2, border_radius=6)
        titulo = "Fogareiro" if self.menu == "principal" else f"Nível {j.nivel}"
        escrever(cena, titulo, 40, (caixa.centerx, caixa.y + 40), FOGO, serifa=True)
        if self.menu == "nivel":
            escrever(cena, f"Custo: {self.custo_nivel()} almas   ·   Tens: {j.almas}", 22, (caixa.centerx, caixa.y + 78), ALMA)
        for k, (texto, _) in enumerate(self.opcoes_menu()):
            y = caixa.y + 120 + k * 38
            cor = BRANCO if k == self.menu_i else CINZA
            if k == self.menu_i:
                pygame.draw.polygon(cena, FOGO, [(caixa.x + 40, y - 6), (caixa.x + 50, y), (caixa.x + 40, y + 6)])
            escrever(cena, texto, 28, (caixa.x + 64, y), cor, "midleft")
        escrever(cena, "W/S escolher   ·   E confirmar   ·   Esc sair", 20, (caixa.centerx, caixa.bottom - 22), CINZA)

    def desenhar_pausa(self, cena):
        sombra = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        sombra.fill((0, 0, 0, 170))
        cena.blit(sombra, (0, 0))
        escrever(cena, "Pausa", 64, (LARGURA / 2, 90), BRANCO, serifa=True)
        linhas = [("WASD / setas", "mover"), ("Shift", "correr"), ("Espaço", "rolar"), ("J / Z", "ataque leve"),
                  ("K / X", "ataque pesado"), ("L / C", "aparar"), ("Q", "beber caldo verde"), ("Tab / R", "fixar alvo"),
                  ("E", "interagir")]
        for k, (t, o) in enumerate(linhas):
            y = 160 + k * 28
            escrever(cena, t, 24, (LARGURA / 2 - 14, y), OURO, "midright")
            escrever(cena, o, 24, (LARGURA / 2 + 14, y), BRANCO, "midleft")
        escrever(cena, f"Mortes: {self.mortes}   ·   Nível {self.jogador.nivel}", 22, (LARGURA / 2, 440), CINZA)
        escrever(cena, "Esc continuar   ·   Q sair do jogo", 24, (LARGURA / 2, 480), BRANCO)

    def desenhar_anuncio(self, cena):
        if self.anuncio is None:
            return
        texto, cor, t, dur, tam = self.anuncio
        alpha = min(1.0, t / 0.6, (dur - t) / 0.8)
        banda = pygame.Surface((LARGURA, int(tam * 1.7)), pygame.SRCALPHA)
        banda.fill((0, 0, 0, int(160 * alpha)))
        cena.blit(banda, (0, ALTURA / 2 - banda.get_height() / 2))
        img = fonte(tam, True).render(texto, True, cor)
        escala = 1 + t * 0.025
        img = pygame.transform.smoothscale(img, (int(img.get_width() * escala), int(img.get_height() * escala)))
        img.set_alpha(int(255 * alpha))
        cena.blit(img, img.get_rect(center=(LARGURA // 2, ALTURA // 2)))

    def desenhar_titulo(self, cena):
        cena.fill(FUNDO)
        t = self.tempo_real
        base = Vector2(LARGURA / 2, ALTURA - 120)
        if random.random() < 0.6:
            self.particula(base + Vector2(random.uniform(-14, 14), 0), Vector2(random.uniform(-15, 15), -random.uniform(40, 100)),
                           random.uniform(1, 2.5), FOGO, 2, "ponto")
        luz = self.gradiente(320 + math.sin(t * 9) * 8, (120, 60, 25))
        cena.blit(luz, (base.x - luz.get_width() / 2, base.y - luz.get_height() / 2), special_flags=pygame.BLEND_RGB_ADD)
        pygame.draw.rect(cena, (40, 32, 30), (base.x - 18, base.y - 6, 36, 14))
        for p in self.particulas:
            f = p[2] / p[3]
            pygame.draw.circle(cena, misturar((0, 0, 0), p[4], f * 1.5), p[0], max(1, p[5] * f))
        self.nuvem.set_alpha(30)
        for n in self.nuvens:
            cena.blit(self.nuvem, (n[0], n[1]))
        for c in self.cinzas:
            cena.fill((120, 115, 110), (c[0], c[1], 1, 1))
        escrever(cena, "ALMAS PENADAS", 84, (LARGURA / 2, 150), (215, 200, 175), serifa=True)
        escrever(cena, "um soulslike de saudade", 26, (LARGURA / 2, 210), (150, 120, 90), serifa=True)
        alpha = 140 + math.sin(t * 2.5) * 110
        escrever(cena, "Prime ENTER", 30, (LARGURA / 2, 290), BRANCO, alpha=alpha, serifa=True)
        escrever(cena, "WASD mover  ·  Espaço rolar  ·  J/K atacar  ·  L aparar  ·  Q curar  ·  Tab alvo  ·  E interagir",
                 20, (LARGURA / 2, ALTURA - 40), CINZA)
        if self.ng > 1:
            escrever(cena, f"Novo Jogo +{self.ng - 1}", 22, (LARGURA / 2, 250), OURO)

    def desenhar_fim(self, cena):
        cena.fill((0, 0, 0))
        t = self.fim_t
        linhas = ["O Desejado regressou ao nevoeiro.", "Lisboa pode, finalmente, ter saudades em paz."]
        for k, linha in enumerate(linhas):
            a = max(0.0, min(1.0, (t - k * 1.5) / 1.5))
            escrever(cena, linha, 30, (LARGURA / 2, 90 + k * 44), (215, 200, 175), alpha=a * 255, serifa=True)
        if t > 3:
            desvio = (t - 3) * 30
            for k, linha in enumerate(CREDITOS):
                y = ALTURA - 60 + k * 30 - desvio % (len(CREDITOS) * 30 + 300)
                if 180 < y < ALTURA - 50:
                    escrever(cena, linha, 34 if k == 0 else 24, (LARGURA / 2, y), OURO if k == 0 else CINZA, serifa=k == 0)
        if t > 6:
            minutos, segundos = divmod(int(self.tempo_jogo), 60)
            escrever(cena, f"Mortes: {self.mortes}   ·   Tempo: {minutos}:{segundos:02d}   ·   Nível {self.jogador.nivel}",
                     22, (LARGURA / 2, ALTURA - 60), BRANCO)
            escrever(cena, "ENTER  Novo Jogo+   ·   ESC  sair", 24, (LARGURA / 2, ALTURA - 28), OURO)

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
    pygame.display.set_caption("ALMAS PENADAS")
    jogo = Jogo(ecra)
    if jogo.carregar():
        jogo.correr()
    pygame.quit()


if __name__ == "__main__":
    main()
