# OS MODELOS
# Desenha os modelos de pixel art que a Oficina oferece no editor de desenho:
# um para cada imagem que os jogos sabem mostrar (galo.png, soldado.png...).
# As criancas podem usa-los tal como estao, ou comecar por eles e mudar.
#
# Cada modelo e desenhado numa grelha de 32 por 32, com as formas do pygame,
# e guardado nesta pasta como um PNG de 128 por 128 (4 pixeis por
# quadradinho), que e como o editor de desenho da Oficina os guarda.
#
# Os PNG ja estao feitos e vao no repositorio: isto so se corre para os
# refazer, depois de mudar um desenho aqui:
#
#     python3 oficina/modelos/fazer_modelos.py
#
# Para ver todos numa folha so:
#
#     python3 oficina/modelos/fazer_modelos.py folha.png

import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
LADO = 32          # quadradinhos de lado
PIXEIS = 4         # pixeis por quadradinho no PNG

TINTA = (34, 28, 40)           # o contorno
BRANCO = (250, 250, 245)
PRETO = (20, 18, 26)
PELE = (255, 210, 170)
PELE_ESCURA = (225, 165, 125)


def clarear(cor, quanto=40):
    return tuple(min(255, c + quanto) for c in cor)


def escurecer(cor, quanto=45):
    return tuple(max(0, c - quanto) for c in cor)


class Tela:
    # Uma grelha de 32 por 32 para desenhar, com atalhos para as formas.

    def __init__(self):
        self.s = pygame.Surface((LADO, LADO), pygame.SRCALPHA)

    def oval(self, cor, x, y, largura, altura):
        pygame.draw.ellipse(self.s, cor, (x, y, largura, altura))

    def caixa(self, cor, x, y, largura, altura, canto=0):
        pygame.draw.rect(self.s, cor, (x, y, largura, altura), border_radius=canto)

    def forma(self, cor, pontos):
        pygame.draw.polygon(self.s, cor, pontos)

    def linha(self, cor, de, ate, grossura=1):
        pygame.draw.line(self.s, cor, de, ate, grossura)

    def ponto(self, cor, x, y):
        if 0 <= x < LADO and 0 <= y < LADO:
            self.s.set_at((x, y), cor)

    def apagar(self, x, y, largura=1, altura=1):
        self.s.fill((0, 0, 0, 0), (x, y, largura, altura))

    def bola(self, cor, x, y, largura, altura):
        # Uma oval com volume: mais escura em baixo, com um brilho em cima.
        self.oval(escurecer(cor), x, y, largura, altura)
        self.oval(cor, x, y, largura, max(2, altura - 2))
        self.oval(clarear(cor), x + largura // 5, y + altura // 7, max(2, largura // 3), max(1, altura // 5))

    def contornar(self, cor=TINTA):
        # Uma linha escura a volta de tudo o que esta desenhado.
        antes = self.s.copy()
        for y in range(LADO):
            for x in range(LADO):
                if antes.get_at((x, y))[3] > 0:
                    continue
                for vx, vy in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if 0 <= vx < LADO and 0 <= vy < LADO and antes.get_at((vx, vy))[3] > 0:
                        self.s.set_at((x, y), cor)
                        break

    def olho(self, x, y, olha=0, tamanho=3):
        # Um olho branco com a pupila escura. olha: -1, 0 ou 1 (para que lado).
        self.caixa(BRANCO, x, y, tamanho, tamanho)
        self.caixa(PRETO, x + (tamanho - 2 if olha >= 0 else 0), y + tamanho - 2, 2, 2)

    def olhos(self, x1, x2, y, olha=0, tamanho=3):
        self.olho(x1, y, olha, tamanho)
        self.olho(x2, y, olha, tamanho)

    def espelhar(self):
        # A metade esquerda repete-se na direita: fica igual dos dois lados.
        for y in range(LADO):
            for x in range(LADO // 2):
                self.s.set_at((LADO - 1 - x, y), self.s.get_at((x, y)))

    def guardar(self, nome):
        grande = pygame.transform.scale(self.s, (LADO * PIXEIS, LADO * PIXEIS))
        pygame.image.save(grande, os.path.join(AQUI, nome))


MODELOS = {}       # o nome do ficheiro -> a funcao que o desenha


def modelo(nome):
    def registar(funcao):
        MODELOS[nome] = funcao
        return funcao
    return registar


# =====================================================================
#                    OS BICHOS (Bicharada e Bicharada a Solta)
# De frente olham para a direita (o jogo vira-os quando e preciso). De
# costas e como se ve o teu, na batalha.
# =====================================================================

VERMELHO = (214, 52, 52)
CRISTA = (176, 24, 44)
AMARELO = (246, 196, 60)
PENAS = (40, 92, 96)


@modelo("galo.png")
def galo(t):
    t.forma(PENAS, [(3, 20), (1, 7), (6, 12)])                 # a cauda
    t.forma(escurecer(PENAS, 20), [(5, 21), (5, 5), (10, 13)])
    t.forma(PENAS, [(8, 22), (10, 8), (13, 15)])
    t.bola(VERMELHO, 7, 13, 18, 14)                            # o corpo
    t.oval(escurecer(VERMELHO, 35), 10, 17, 10, 7)             # a asa
    t.oval(VERMELHO, 17, 5, 10, 11)                            # a cabeca
    t.caixa(AMARELO, 12, 26, 2, 4)                             # as patas
    t.caixa(AMARELO, 18, 26, 2, 4)
    t.caixa(AMARELO, 11, 29, 5, 1)
    t.caixa(AMARELO, 17, 29, 5, 1)
    for x, y in ((18, 2), (21, 1), (24, 3)):                   # a crista
        t.oval(CRISTA, x, y, 4, 5)
    t.forma(AMARELO, [(26, 9), (31, 11), (26, 13)])            # o bico
    t.oval(CRISTA, 24, 13, 3, 5)                               # a barbela
    t.contornar()
    t.olho(21, 7, 1)


@modelo("galo-costas.png")
def galo_costas(t):
    t.oval(VERMELHO, 11, 3, 10, 10)                            # a cabeca, de tras
    for x, y in ((11, 0), (14, -1), (17, 0)):
        t.oval(CRISTA, x, y, 4, 5)
    t.bola(VERMELHO, 6, 11, 20, 16)
    for pontos, cor in (([(16, 26), (3, 10), (9, 9)], PENAS), ([(16, 26), (9, 6), (14, 6)], escurecer(PENAS, 20)),
                        ([(16, 26), (14, 5), (19, 5)], PENAS), ([(16, 26), (19, 6), (24, 7)], escurecer(PENAS, 20)),
                        ([(16, 26), (24, 9), (29, 11)], PENAS)):
        t.forma(cor, pontos)                                   # a cauda em leque
    t.caixa(AMARELO, 11, 27, 2, 3)
    t.caixa(AMARELO, 19, 27, 2, 3)
    t.caixa(AMARELO, 10, 29, 5, 1)
    t.caixa(AMARELO, 18, 29, 5, 1)
    t.contornar()


CASTANHA = (134, 78, 40)


def castanha_corpo(t):
    t.forma(escurecer(CASTANHA), [(16, 2), (5, 16), (27, 16)])
    t.forma(CASTANHA, [(16, 3), (7, 15), (25, 15)])
    t.bola(CASTANHA, 4, 9, 24, 20)
    t.oval((226, 190, 140), 8, 23, 16, 6)                      # a base clara


@modelo("castanha.png")
def castanha(t):
    castanha_corpo(t)
    t.forma((250, 226, 150), [(9, 12), (14, 6), (12, 14)])     # o golpe da castanha assada
    t.contornar()
    t.olhos(10, 18, 15, 1, 4)
    t.caixa(PRETO, 13, 21, 6, 1)
    t.ponto((255, 140, 40), 16, 0)                             # uma faisca
    t.ponto((255, 200, 60), 18, 1)


@modelo("castanha-costas.png")
def castanha_costas(t):
    castanha_corpo(t)
    t.forma((250, 226, 150), [(13, 8), (19, 5), (20, 15), (14, 17)])
    t.linha(escurecer(CASTANHA, 60), (9, 14), (12, 22))
    t.linha(escurecer(CASTANHA, 60), (22, 12), (23, 21))
    t.contornar()


SARDINHA = (96, 140, 190)
PRATA = (214, 226, 236)


@modelo("sardinhao.png")
def sardinhao(t):
    t.forma(escurecer(SARDINHA, 30), [(7, 16), (0, 8), (2, 16), (0, 24)])    # a cauda
    t.forma(escurecer(SARDINHA, 30), [(11, 11), (16, 5), (21, 10)])          # a barbatana de cima
    t.bola(SARDINHA, 5, 9, 24, 14)
    t.oval(PRATA, 7, 15, 20, 7)                                              # a barriga
    t.forma(escurecer(SARDINHA, 30), [(14, 20), (17, 25), (20, 20)])
    for x in (10, 13, 16, 19):                                               # as pintas
        t.ponto(escurecer(SARDINHA, 70), x, 12)
    t.linha(escurecer(SARDINHA, 60), (22, 11), (21, 20))                     # a guelra
    t.contornar()
    t.olho(24, 12, 1)
    t.caixa(PRETO, 27, 17, 2, 1)


@modelo("sardinhao-costas.png")
def sardinhao_costas(t):
    t.forma(escurecer(SARDINHA, 30), [(16, 22), (8, 31), (16, 28), (24, 31)])
    t.forma(escurecer(SARDINHA, 30), [(9, 14), (3, 19), (10, 20)])           # as barbatanas dos lados
    t.forma(escurecer(SARDINHA, 30), [(23, 14), (29, 19), (22, 20)])
    t.bola(SARDINHA, 9, 2, 14, 23)
    t.linha(escurecer(SARDINHA, 60), (16, 4), (16, 22))                      # a espinha
    for y in (8, 12, 16):
        t.ponto(escurecer(SARDINHA, 70), 13, y)
        t.ponto(escurecer(SARDINHA, 70), 19, y)
    t.contornar()


POLVO = (170, 80, 158)


def polvo_corpo(t, com_ventosas):
    for x, fim in ((6, 3), (10, 8), (19, 21), (23, 26)):                     # os tentaculos
        t.caixa(POLVO, x, 17, 4, 9, 2)
        t.caixa(POLVO, fim, 25, 5, 4, 2)
        if com_ventosas:
            t.ponto((246, 190, 220), x + 1, 23)
            t.ponto((246, 190, 220), fim + 2, 27)
    t.caixa(POLVO, 14, 18, 4, 11, 2)
    t.bola(POLVO, 5, 2, 22, 19)


@modelo("polvo.png")
def polvo(t):
    polvo_corpo(t, True)
    t.contornar()
    t.olhos(10, 18, 10, 1, 4)
    t.caixa(PRETO, 14, 17, 4, 1)


@modelo("polvo-costas.png")
def polvo_costas(t):
    polvo_corpo(t, False)
    for x, y in ((10, 7), (20, 6), (15, 12), (9, 14), (22, 13)):             # as manchas
        t.oval(clarear(POLVO, 45), x, y, 3, 3)
    t.contornar()


FOLHAS = (74, 150, 72)
TRONCO = (128, 96, 60)
CORTICA = (196, 110, 62)


def sobreiro_corpo(t):
    t.caixa(TRONCO, 11, 15, 10, 15, 2)
    t.caixa(CORTICA, 11, 23, 10, 6)                                          # o tronco descorticado
    t.caixa(escurecer(TRONCO), 9, 28, 4, 3, 1)                               # as raizes
    t.caixa(escurecer(TRONCO), 19, 28, 4, 3, 1)
    for x, y in ((3, 6), (17, 6), (9, 1)):                                   # a copa
        t.bola(FOLHAS, x, y, 13, 13)
    for x, y in ((8, 9), (20, 11), (14, 5), (24, 8), (6, 13)):
        t.ponto(escurecer(FOLHAS, 50), x, y)


@modelo("sobreirinho.png")
def sobreirinho(t):
    sobreiro_corpo(t)
    t.contornar()
    t.olhos(12, 17, 18, 1)
    t.caixa(PRETO, 14, 22, 4, 1)


@modelo("sobreirinho-costas.png")
def sobreirinho_costas(t):
    sobreiro_corpo(t)
    t.linha(escurecer(TRONCO, 40), (14, 16), (14, 22))
    t.linha(escurecer(TRONCO, 40), (18, 17), (18, 22))
    t.caixa(BRANCO, 14, 24, 3, 1)                                            # o numero pintado na cortica
    t.caixa(BRANCO, 16, 25, 1, 3)
    t.contornar()


COUVE = (64, 150, 78)


def couve_corpo(t):
    t.bola(escurecer(COUVE, 30), 3, 5, 26, 24)
    t.bola(COUVE, 4, 7, 14, 18)                                              # as folhas de fora
    t.bola(COUVE, 14, 7, 14, 18)
    t.bola(clarear(COUVE, 25), 9, 11, 14, 16)                                # a folha do meio


@modelo("couve.png")
def couve(t):
    couve_corpo(t)
    t.linha(clarear(COUVE, 80), (16, 13), (16, 16))
    t.contornar()
    t.olhos(11, 18, 17, 1)
    t.caixa(PRETO, 14, 23, 4, 1)


@modelo("couve-costas.png")
def couve_costas(t):
    couve_corpo(t)
    t.linha(clarear(COUVE, 80), (16, 12), (16, 26))                          # as nervuras
    for y in (15, 19, 23):
        t.linha(clarear(COUVE, 80), (16, y), (11, y - 3))
        t.linha(clarear(COUVE, 80), (16, y), (21, y - 3))
    t.contornar()


LINCE = (206, 158, 92)
PINTAS = (120, 78, 40)


@modelo("lince.png")
def lince(t):
    t.forma(LINCE, [(6, 13), (7, 2), (13, 9)])                               # as orelhas
    t.forma((240, 170, 170), [(8, 10), (8, 5), (11, 9)])
    t.forma(BRANCO, [(5, 19), (1, 26), (9, 25)])                             # as suicas
    t.bola(LINCE, 5, 8, 22, 20)
    t.oval(BRANCO, 11, 19, 10, 8)                                            # o focinho
    for x, y in ((9, 11), (12, 10)):
        t.ponto(PINTAS, x, y)
    t.espelhar()
    t.ponto(PRETO, 7, 1)                                                     # os pinceis das orelhas
    t.ponto(PRETO, 24, 1)
    t.contornar()
    t.caixa((120, 190, 90), 10, 14, 4, 3)                                    # os olhos verdes
    t.caixa((120, 190, 90), 18, 14, 4, 3)
    t.caixa(PRETO, 12, 14, 1, 3)
    t.caixa(PRETO, 19, 14, 1, 3)
    t.caixa((230, 130, 140), 15, 20, 2, 2)                                   # o nariz
    t.linha(PRETO, (14, 24), (17, 24))


@modelo("lince-costas.png")
def lince_costas(t):
    t.forma(PRETO, [(7, 12), (8, 2), (13, 8)])                               # as orelhas, por tras
    t.ponto(BRANCO, 9, 7)
    t.oval(LINCE, 8, 6, 8, 10)
    t.espelhar()
    t.bola(LINCE, 5, 12, 22, 18)                                             # as costas
    for x, y in ((10, 17), (15, 15), (20, 18), (12, 22), (18, 23), (8, 21), (23, 22)):
        t.caixa(PINTAS, x, y, 2, 2)
    t.caixa(LINCE, 22, 26, 6, 4, 2)                                          # a cauda curta
    t.caixa(PRETO, 26, 26, 3, 4, 1)
    t.contornar()


# =====================================================================
#                       TU (Bicharada a Solta)
# =====================================================================

CAMISOLA = (240, 200, 70)
CALCAS = (60, 96, 180)
CABELO = (96, 58, 34)


@modelo("jogador.png")
def jogador(t):
    t.caixa(CALCAS, 11, 23, 4, 6)
    t.caixa(CALCAS, 17, 23, 4, 6)
    t.caixa(PRETO, 10, 28, 5, 3, 1)                                          # os sapatos
    t.caixa(PRETO, 17, 28, 5, 3, 1)
    t.caixa(CAMISOLA, 10, 14, 12, 10, 2)
    t.caixa(escurecer(CAMISOLA, 30), 7, 15, 3, 7, 1)                         # os bracos
    t.caixa(escurecer(CAMISOLA, 30), 22, 15, 3, 7, 1)
    t.caixa(PELE, 7, 21, 3, 2)
    t.caixa(PELE, 22, 21, 3, 2)
    t.oval(PELE, 9, 2, 14, 13)                                               # a cabeca
    t.oval(CABELO, 9, 1, 14, 7)
    t.caixa(CABELO, 9, 4, 2, 5)
    t.caixa(CABELO, 21, 4, 2, 5)
    t.contornar()
    t.caixa(PRETO, 13, 8, 2, 3)
    t.caixa(PRETO, 17, 8, 2, 3)
    t.caixa(PELE_ESCURA, 14, 12, 4, 1)


@modelo("jogador-costas.png")
def jogador_costas(t):
    t.caixa(CALCAS, 11, 23, 4, 6)
    t.caixa(CALCAS, 17, 23, 4, 6)
    t.caixa(PRETO, 10, 28, 5, 3, 1)
    t.caixa(PRETO, 17, 28, 5, 3, 1)
    t.caixa(CAMISOLA, 10, 14, 12, 10, 2)
    t.caixa(escurecer(CAMISOLA, 30), 7, 15, 3, 7, 1)
    t.caixa(escurecer(CAMISOLA, 30), 22, 15, 3, 7, 1)
    t.caixa(PELE, 7, 21, 3, 2)
    t.caixa(PELE, 22, 21, 3, 2)
    t.caixa((170, 70, 50), 12, 15, 8, 8, 2)                                  # a mochila
    t.caixa((120, 44, 34), 12, 19, 8, 1)
    t.oval(CABELO, 9, 1, 14, 14)                                             # a cabeca, de tras
    t.caixa(PELE, 14, 13, 4, 2)
    t.contornar()


@modelo("jogador-lado.png")
def jogador_lado(t):
    t.caixa(CALCAS, 11, 23, 4, 6)                                            # uma perna atras, outra a frente
    t.caixa(escurecer(CALCAS, 25), 16, 23, 4, 5)
    t.caixa(PRETO, 11, 28, 6, 3, 1)
    t.caixa(PRETO, 16, 27, 6, 3, 1)
    t.caixa(CAMISOLA, 11, 14, 10, 10, 2)
    t.caixa(escurecer(CAMISOLA, 30), 15, 15, 3, 7, 1)                        # o braco
    t.caixa(PELE, 15, 21, 3, 2)
    t.oval(PELE, 10, 2, 13, 13)
    t.oval(CABELO, 9, 1, 12, 8)
    t.caixa(CABELO, 9, 4, 5, 7)
    t.caixa(PELE, 22, 8, 2, 2)                                               # o nariz
    t.contornar()
    t.caixa(PRETO, 19, 7, 2, 3)
    t.caixa(PELE_ESCURA, 20, 12, 3, 1)


# =====================================================================
#                              O CERCO
# =====================================================================

ACO = (150, 156, 170)
MADEIRA = (122, 84, 50)
PEDRA = (150, 150, 158)


def pessoa(t, roupa, x=10):
    # Um boneco de frente: pernas, tronco e cabeca. Devolve nada: desenha.
    t.caixa(escurecer(roupa, 60), x + 1, 23, 4, 6)
    t.caixa(escurecer(roupa, 60), x + 7, 23, 4, 6)
    t.caixa(PRETO, x, 28, 5, 3, 1)
    t.caixa(PRETO, x + 7, 28, 5, 3, 1)
    t.caixa(roupa, x, 13, 12, 11, 2)
    t.oval(PELE, x + 1, 3, 10, 11)


@modelo("soldado.png")
def soldado(t):
    t.linha(MADEIRA, (26, 2), (26, 29), 2)                                   # a lanca
    t.forma(ACO, [(27, 0), (24, 5), (29, 5)])
    pessoa(t, (200, 60, 60))
    t.oval(ACO, 10, 1, 12, 8)                                                # o capacete
    t.caixa(ACO, 15, 6, 2, 5)
    t.caixa(escurecer((200, 60, 60), 30), 22, 15, 3, 8, 1)
    t.bola((150, 104, 60), 3, 13, 11, 13)                                    # o escudo
    t.caixa(AMARELO, 7, 18, 3, 3)
    t.contornar()
    t.caixa(PRETO, 13, 8, 1, 2)
    t.caixa(PRETO, 18, 8, 1, 2)


@modelo("cavaleiro.png")
def cavaleiro(t):
    cavalo = (150, 100, 60)
    for x in (6, 10, 19, 23):                                                # as patas do cavalo
        t.caixa(escurecer(cavalo), x, 24, 3, 7)
    t.forma(escurecer(cavalo, 60), [(5, 17), (0, 23), (4, 24)])              # a cauda
    t.bola(cavalo, 4, 15, 22, 11)
    t.forma(cavalo, [(21, 18), (24, 7), (31, 12), (29, 16), (26, 20)])       # o pescoco e a cabeca
    t.linha(escurecer(cavalo, 60), (22, 10), (20, 17), 2)                    # a crina
    t.caixa((230, 140, 60), 11, 9, 8, 9, 2)                                  # o cavaleiro
    t.oval(ACO, 11, 2, 8, 8)
    t.forma((230, 60, 60), [(15, 2), (11, 0), (12, 4)])                      # o penacho
    t.linha(MADEIRA, (13, 13), (31, 6), 1)                                   # a lanca
    t.contornar()
    t.caixa(PRETO, 28, 11, 1, 2)
    t.caixa(PRETO, 16, 5, 2, 1)


@modelo("ariete.png")
def ariete(t):
    t.forma(escurecer(MADEIRA, 20), [(4, 14), (16, 3), (28, 14)])            # o telhado
    t.linha(clarear(MADEIRA, 30), (16, 4), (16, 13))
    t.linha(clarear(MADEIRA, 30), (10, 9), (10, 13))
    t.linha(clarear(MADEIRA, 30), (22, 9), (22, 13))
    t.caixa(escurecer(MADEIRA, 40), 5, 13, 2, 11)                            # os postes
    t.caixa(escurecer(MADEIRA, 40), 25, 13, 2, 11)
    t.caixa(MADEIRA, 1, 16, 26, 6, 2)                                        # o tronco
    t.caixa(clarear(MADEIRA, 30), 2, 17, 24, 1)
    t.caixa(ACO, 26, 14, 5, 10, 2)                                           # a cabeca de ferro
    t.caixa(escurecer(ACO, 40), 29, 16, 2, 6)
    for x in (5, 19):                                                        # as rodas
        t.oval(escurecer(MADEIRA, 50), x, 22, 9, 9)
        t.oval(MADEIRA, x + 2, 24, 5, 5)
    t.contornar()


@modelo("general.png")
def general(t):
    roxo = (120, 40, 140)
    t.forma(escurecer(roxo, 30), [(6, 14), (2, 30), (30, 30), (26, 14)])     # a capa
    pessoa(t, roxo)
    t.caixa(AMARELO, 10, 18, 12, 2)                                          # o cinto
    t.caixa(AMARELO, 15, 13, 2, 5)
    t.forma(AMARELO, [(10, 5), (10, 0), (13, 3), (16, 0), (19, 3), (22, 0), (22, 5)])    # a coroa
    t.linha(ACO, (26, 8), (26, 24), 2)                                       # a espada
    t.caixa(AMARELO, 24, 22, 6, 2)
    t.contornar()
    t.caixa(PRETO, 13, 8, 2, 2)
    t.caixa(PRETO, 18, 8, 2, 2)
    t.caixa(PRETO, 13, 12, 6, 1)


def torre_de_pedra(t):
    t.caixa(PEDRA, 5, 17, 22, 14, 1)
    t.caixa(escurecer(PEDRA, 30), 5, 27, 22, 4)
    for x in (5, 11, 17, 23):                                                # as ameias
        t.caixa(PEDRA, x, 14, 4, 4)
    for x, y in ((9, 21), (19, 23), (13, 26)):
        t.caixa(escurecer(PEDRA, 40), x, y, 4, 1)


@modelo("besteiro.png")
def besteiro(t):
    azul = (70, 110, 200)
    t.caixa(azul, 11, 9, 10, 9, 2)                                           # o besteiro, atras das ameias
    t.oval(PELE, 12, 2, 8, 8)
    t.oval(azul, 11, 0, 10, 6)                                               # o capuz
    torre_de_pedra(t)
    t.linha(MADEIRA, (6, 11), (26, 11), 2)                                   # a besta
    t.linha(MADEIRA, (16, 8), (16, 15), 2)
    t.linha(BRANCO, (6, 11), (16, 14))
    t.linha(BRANCO, (26, 11), (16, 14))
    t.contornar()
    t.caixa(PRETO, 14, 5, 1, 2)
    t.caixa(PRETO, 17, 5, 1, 2)


@modelo("trabuco.png")
def trabuco(t):
    t.linha(MADEIRA, (7, 29), (16, 12), 2)                                   # a armacao
    t.linha(MADEIRA, (25, 29), (16, 12), 2)
    t.caixa(escurecer(MADEIRA, 30), 4, 28, 24, 3, 1)
    t.linha(clarear(MADEIRA, 20), (3, 21), (29, 5), 2)                       # o braco
    t.caixa(PEDRA, 0, 19, 7, 7, 1)                                           # o contrapeso
    t.caixa(escurecer(PEDRA, 40), 0, 24, 7, 2)
    t.linha(BRANCO, (29, 5), (27, 11))                                       # a funda
    t.oval(escurecer(PEDRA, 20), 24, 10, 6, 6)                               # a pedra
    t.contornar()


@modelo("caldeirao.png")
def caldeirao(t):
    for pontos, cor in (([(8, 30), (11, 22), (14, 30)], (230, 80, 40)), ([(13, 30), (16, 21), (19, 30)], (250, 150, 40)),
                        ([(18, 30), (21, 22), (24, 30)], (230, 80, 40))):
        t.forma(cor, pontos)                                                 # o lume
    t.bola((60, 60, 72), 4, 9, 24, 19)                                       # o caldeirao
    t.caixa((60, 60, 72), 3, 9, 26, 4, 2)
    t.oval((236, 176, 48), 6, 8, 20, 6)                                      # o azeite a ferver
    for x, y in ((10, 6), (16, 4), (21, 6)):
        t.oval((250, 214, 110), x, y, 3, 3)
    t.contornar()
    t.ponto(BRANCO, 11, 7)
    t.ponto(BRANCO, 17, 5)


@modelo("padeira.png")
def padeira(t):
    vestido = (230, 220, 200)
    t.linha(MADEIRA, (26, 6), (26, 28), 2)                                   # a pa do forno
    t.caixa(clarear(MADEIRA, 30), 23, 1, 7, 8, 2)
    t.forma(vestido, [(9, 14), (6, 30), (26, 30), (23, 14)])                 # a saia
    t.caixa((150, 90, 70), 12, 17, 8, 12)                                    # o avental
    t.caixa(vestido, 10, 13, 12, 6, 2)
    t.caixa(vestido, 22, 14, 4, 4, 1)                                        # o braco que segura a pa
    t.caixa(PELE, 24, 13, 3, 3)
    t.oval(PELE, 11, 3, 10, 11)
    t.oval(BRANCO, 10, 1, 12, 7)                                             # o lenco
    t.caixa(BRANCO, 10, 4, 2, 6)
    t.caixa(BRANCO, 20, 4, 2, 6)
    t.contornar()
    t.caixa(PRETO, 13, 8, 2, 2)
    t.caixa(PRETO, 17, 8, 2, 2)
    t.caixa((200, 80, 80), 14, 12, 4, 1)


# =====================================================================
#                           MAOS AO AR!
# Olham para a direita: o jogo vira-os quando andam para a esquerda. O jogo
# estica cada imagem ate ao tamanho do inimigo.
# =====================================================================

@modelo("lesma.png")
def lesma(t):
    cor = (150, 210, 90)
    t.caixa(clarear(cor, 50), 1, 27, 28, 3, 1)                               # o rasto
    t.bola(cor, 2, 13, 26, 16)
    t.bola(escurecer(cor, 30), 5, 9, 14, 12)                                 # a corcunda
    t.caixa(cor, 22, 5, 2, 10)                                               # as antenas
    t.caixa(cor, 27, 6, 2, 9)
    t.oval(cor, 20, 2, 5, 5)
    t.oval(cor, 26, 3, 5, 5)
    t.contornar()
    t.caixa(PRETO, 22, 4, 2, 2)
    t.caixa(PRETO, 28, 5, 2, 2)
    t.caixa(PRETO, 23, 23, 5, 1)


@modelo("sapo.png")
def sapo(t):
    cor = (60, 170, 110)
    t.caixa(escurecer(cor, 30), 2, 23, 9, 6, 2)                              # as patas
    t.caixa(escurecer(cor, 30), 21, 23, 9, 6, 2)
    t.bola(cor, 3, 9, 26, 20)
    t.oval((226, 240, 200), 9, 19, 14, 9)                                    # a barriga
    t.oval(cor, 5, 3, 9, 9)                                                  # os olhos saidos
    t.oval(cor, 18, 3, 9, 9)
    t.contornar()
    t.olhos(7, 20, 5, 1, 5)
    t.linha(PRETO, (10, 17), (21, 17))


@modelo("morcego.png")
def morcego(t):
    cor = (150, 90, 190)
    asa = escurecer(cor, 40)
    t.forma(asa, [(13, 12), (1, 5), (0, 18), (4, 15), (7, 21), (10, 16), (13, 20)])    # uma asa
    t.forma(cor, [(12, 8), (10, 1), (15, 6)])                                # uma orelha
    t.espelhar()
    t.bola(cor, 10, 6, 12, 17)                                               # o corpo
    t.contornar()
    t.olhos(12, 17, 11, 0)
    t.caixa(BRANCO, 14, 17, 1, 2)                                            # os dentes
    t.caixa(BRANCO, 17, 17, 1, 2)


@modelo("ourico.png")
def ourico(t):
    cor = (200, 120, 70)
    picos = escurecer(cor, 80)
    for x in range(2, 22, 4):                                                # os picos
        t.forma(picos, [(x, 16), (x + 2, 4 + abs(10 - x) // 2), (x + 5, 16)])
    t.bola(picos, 1, 10, 24, 18)
    t.bola((236, 200, 160), 16, 15, 14, 13)                                  # a cara
    t.caixa(escurecer(cor, 40), 5, 26, 5, 4, 1)                              # as patas
    t.caixa(escurecer(cor, 40), 17, 26, 5, 4, 1)
    t.contornar()
    t.olho(21, 18, 1)
    t.caixa(PRETO, 28, 21, 3, 3, 1)                                          # o nariz


@modelo("javali.png")
def javali(t):
    cor = (120, 85, 70)
    for x in (5, 10, 19, 23):
        t.caixa(escurecer(cor, 40), x, 23, 4, 8, 1)                          # as patas
    t.bola(cor, 1, 9, 26, 18)
    for x in range(4, 20, 3):                                                # as cerdas do lombo
        t.forma(escurecer(cor, 55), [(x, 11), (x + 2, 5), (x + 4, 11)])
    t.bola(clarear(cor, 15), 17, 11, 14, 14)                                 # a cabeca
    t.caixa((200, 140, 130), 27, 17, 5, 6, 2)                                # o focinho
    t.forma(BRANCO, [(24, 23), (25, 17), (27, 23)])                          # o dente
    t.forma(escurecer(cor, 40), [(18, 12), (17, 6), (22, 11)])               # a orelha
    t.contornar()
    t.olho(22, 15, 1)
    t.linha(PRETO, (21, 13), (25, 14))                                       # a sobrancelha zangada
    t.ponto(PRETO, 30, 19)


@modelo("canhao.png")
def canhao(t):
    cor = (90, 95, 110)
    t.caixa(MADEIRA, 3, 21, 20, 5, 1)                                        # a carreta
    t.caixa(cor, 7, 9, 23, 10, 3)                                            # o cano
    t.caixa(clarear(cor, 35), 8, 10, 20, 2)
    t.caixa(escurecer(cor, 30), 27, 7, 4, 14, 1)                             # a boca
    t.caixa(escurecer(cor, 30), 5, 8, 4, 12, 2)                              # a culatra
    t.oval(escurecer(MADEIRA, 50), 6, 17, 14, 14)                            # a roda
    t.oval(MADEIRA, 9, 20, 8, 8)
    t.caixa(escurecer(MADEIRA, 50), 12, 18, 2, 12)
    t.caixa(escurecer(MADEIRA, 50), 7, 23, 12, 2)
    t.contornar()
    t.caixa(PRETO, 29, 10, 2, 8)


@modelo("rei-sucata.png")
def rei_sucata(t):
    cor = (190, 70, 90)
    t.caixa(ACO, 1, 14, 5, 12, 2)                                            # os bracos de cano
    t.caixa(ACO, 26, 14, 5, 12, 2)
    t.caixa(escurecer(ACO, 40), 0, 24, 7, 5, 1)
    t.caixa(escurecer(ACO, 40), 25, 24, 7, 5, 1)
    t.caixa(escurecer(cor, 40), 8, 26, 6, 5, 1)                              # os pes
    t.caixa(escurecer(cor, 40), 18, 26, 6, 5, 1)
    t.caixa(cor, 6, 15, 20, 13, 2)                                           # o tronco
    t.caixa(escurecer(cor, 30), 6, 24, 20, 4)
    t.caixa((60, 60, 72), 11, 18, 10, 6, 1)                                  # o painel
    t.caixa(cor, 7, 5, 18, 11, 2)                                            # a cabeca
    t.forma(AMARELO, [(8, 6), (8, 0), (12, 4), (16, 0), (20, 4), (24, 0), (24, 6)])     # a coroa
    t.caixa((150, 96, 60), 20, 9, 4, 4)                                      # um remendo de ferrugem
    t.contornar()
    t.caixa(AMARELO, 10, 8, 4, 3)                                            # os olhos acesos
    t.caixa(AMARELO, 17, 8, 4, 3)
    t.caixa(PRETO, 12, 9, 2, 2)
    t.caixa(PRETO, 19, 9, 2, 2)
    for x in (11, 14, 17, 20):                                               # a grelha da boca
        t.caixa(PRETO, x, 13, 1, 2)
    t.caixa((90, 230, 120), 13, 20, 2, 2)                                    # as luzes do painel
    t.caixa((240, 90, 70), 17, 20, 2, 2)


@modelo("faisca.png")
def faisca(t):
    amarelo = (246, 200, 50)
    t.caixa(PRETO, 15, 1, 2, 5)                                              # a antena
    t.caixa((90, 200, 250), 14, 0, 4, 3, 1)
    t.caixa(PRETO, 10, 26, 5, 5, 1)                                          # as pernas
    t.caixa(PRETO, 17, 26, 5, 5, 1)
    t.caixa(PRETO, 5, 17, 4, 8, 1)                                           # os bracos
    t.caixa(PRETO, 23, 17, 4, 8, 1)
    t.caixa(amarelo, 8, 16, 16, 11, 2)                                       # o tronco
    t.caixa(PRETO, 8, 21, 16, 2)                                             # a risca
    t.forma(PRETO, [(17, 17), (13, 21), (16, 21), (14, 26), (19, 20), (16, 20)])     # o raio
    t.caixa(amarelo, 7, 5, 18, 12, 3)                                        # a cabeca
    t.caixa(clarear(amarelo, 40), 9, 6, 12, 2)
    t.caixa(PRETO, 9, 9, 14, 6, 2)                                           # a viseira
    t.contornar()
    t.caixa((90, 230, 250), 12, 11, 3, 3)                                    # os olhos
    t.caixa((90, 230, 250), 19, 11, 3, 3)


# =====================================================================
#                            FADO//NEON
# Formas de neon: o meio escuro e a borda a brilhar.
# =====================================================================

def neon(t, cor, pontos, nucleo=True):
    t.forma(clarear(cor, 90), pontos)
    dentro = [(x + (1 if x < 16 else -1) * 2, y + (1 if y < 16 else -1) * 2) for x, y in pontos]
    t.forma(cor, pontos)
    t.forma((max(0, cor[0] // 5), max(0, cor[1] // 5), max(0, cor[2] // 5 + 12)), dentro)
    pygame.draw.polygon(t.s, clarear(cor, 110), pontos, 1)
    if nucleo:
        t.caixa(clarear(cor, 110), 14, 14, 4, 4, 1)
        t.caixa(BRANCO, 15, 15, 2, 2)


@modelo("corredor.png")
def corredor(t):
    rosa = (255, 60, 160)
    neon(t, rosa, [(29, 16), (6, 4), (11, 16), (6, 28)], False)             # uma seta, a correr para a direita
    t.caixa(BRANCO, 19, 15, 3, 3)
    for y in (9, 16, 23):                                                    # os riscos da velocidade
        t.caixa(clarear(rosa, 60), 1, y, 4, 1)


@modelo("atirador.png")
def atirador(t):
    laranja = (255, 150, 40)
    neon(t, laranja, [(4, 6), (22, 6), (22, 26), (4, 26)])
    t.caixa(clarear(laranja, 60), 20, 13, 11, 6)                             # o cano
    t.caixa((40, 24, 20), 22, 15, 8, 2)
    t.caixa(BRANCO, 29, 14, 2, 4)


@modelo("divisor.png")
def divisor(t):
    verde = (60, 240, 130)
    neon(t, verde, [(9, 2), (23, 2), (30, 16), (23, 30), (9, 30), (2, 16)], False)
    t.linha(clarear(verde, 110), (16, 3), (13, 12))                          # a racha por onde se divide
    t.linha(clarear(verde, 110), (13, 12), (19, 19))
    t.linha(clarear(verde, 110), (19, 19), (16, 29))
    t.caixa(BRANCO, 8, 14, 3, 3)                                             # os dois nucleos
    t.caixa(BRANCO, 21, 15, 3, 3)


@modelo("pequeno.png")
def pequeno(t):
    verde = (60, 240, 130)
    neon(t, verde, [(12, 7), (20, 7), (25, 16), (20, 25), (12, 25), (7, 16)])


@modelo("investida.png")
def investida(t):
    roxo = (180, 80, 255)
    t.forma(clarear(roxo, 90), [(20, 8), (31, 2), (25, 13)])                 # os cornos
    t.forma(clarear(roxo, 90), [(20, 24), (31, 30), (25, 19)])
    neon(t, roxo, [(3, 7), (22, 7), (28, 16), (22, 25), (3, 25)], False)
    t.caixa(BRANCO, 19, 12, 3, 2)                                            # os olhos zangados
    t.caixa(BRANCO, 19, 18, 3, 2)
    t.caixa(clarear(roxo, 60), 0, 15, 5, 2)


def fazer():
    pygame.init()
    pygame.display.set_mode((16, 16))
    telas = {}
    for nome, funcao in MODELOS.items():
        tela = Tela()
        funcao(tela)
        tela.guardar(nome)
        telas[nome] = tela
    return telas


if __name__ == "__main__":
    telas = fazer()
    print(len(telas), "modelos em", AQUI)
    if len(sys.argv) > 1:
        # Todos numa folha, com o nome por baixo, para os ver de uma vez.
        colunas = 8
        linhas = (len(telas) + colunas - 1) // colunas
        folha = pygame.Surface((colunas * 150, linhas * 158))
        folha.fill((52, 58, 78))
        letra = pygame.font.SysFont(None, 16)
        for numero, (nome, tela) in enumerate(telas.items()):
            x, y = numero % colunas * 150, numero // colunas * 158
            for linha in range(0, 144, 9):
                for coluna in range(0, 144, 9):
                    if (linha + coluna) // 9 % 2:
                        folha.fill((60, 66, 88), (x + 3 + coluna, y + 3 + linha, 9, 9))
            folha.blit(pygame.transform.scale(tela.s, (144, 144)), (x + 3, y + 3))
            folha.blit(letra.render(nome, True, (230, 230, 240)), (x + 4, y + 146))
        pygame.image.save(folha, sys.argv[1])
