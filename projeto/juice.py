# =====================================================================
# JUICE — sessao 14
# "Juice" e o nome que se da aos efeitos que nao mudam nada nas regras
# do jogo, mas mudam tudo na sensacao de o jogar.
#
# Aqui estao dois, os mais baratos que existem. Cinco linhas cada.
#   1. O ECRA A TREMER meio segundo quando levas dano.
#   2. O OBJETO A CRESCER 20% no instante em que e apanhado.
#
# Carrega em D para levar dano e em A para apanhar. Experimenta primeiro
# com os efeitos desligados (tecla E) para sentires a diferenca.
# =====================================================================

import random

import pygame

LARGURA = 800
ALTURA = 600
FPS = 60
FUNDO = (18, 18, 28)
BRANCO = (240, 240, 240)
COR_JOGADOR = (70, 130, 230)
COR_MOEDA = (240, 200, 70)
MOEDA = 40

# Quantos ciclos dura o tremor. 30 ciclos a 60 FPS = meio segundo.
TREMOR_CICLOS = 30
# Quantos pixels o ecra salta, no maximo, para cada lado.
TREMOR_FORCA = 8
# Quantos ciclos o objeto fica crescido, e quanto cresce.
CRESCER_CICLOS = 10
CRESCER_PIXEIS = 8

pygame.init()
ecra = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Juice")
clock = pygame.time.Clock()
fonte = pygame.font.SysFont(None, 32)

jogador = pygame.Rect(200, 300, 48, 48)
moeda = pygame.Rect(500, 300, MOEDA, MOEDA)

# Sao contadores: valem zero quando nao ha efeito nenhum a acontecer, e
# vao descendo ate zero enquanto o efeito dura. E so isto.
tremor = 0
crescer = 0
efeitos_ligados = True

a_correr = True
while a_correr:

    # ------------------------- 1. EVENTOS -------------------------
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            a_correr = False
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_d:
                tremor = TREMOR_CICLOS      # <-- EFEITO 1: comeca o tremor
            if evento.key == pygame.K_a:
                crescer = CRESCER_CICLOS    # <-- EFEITO 2: comeca o crescer
            if evento.key == pygame.K_e:
                efeitos_ligados = not efeitos_ligados

    # ------------------------- 2. LOGICA --------------------------
    if tremor > 0:
        tremor = tremor - 1
    if crescer > 0:
        crescer = crescer - 1

    # ------------------------ 3. DESENHAR -------------------------
    ecra.fill(FUNDO)

    # EFEITO 1 — o tremor. Nao se mexe no jogo: mexe-se em TUDO o que se
    # desenha, ao mesmo tempo, uns pixels a sorte para cada lado.
    salto_x = 0
    salto_y = 0
    if tremor > 0 and efeitos_ligados == True:
        salto_x = random.randint(-TREMOR_FORCA, TREMOR_FORCA)
        salto_y = random.randint(-TREMOR_FORCA, TREMOR_FORCA)

    pygame.draw.rect(ecra, COR_JOGADOR, jogador.move(salto_x, salto_y))

    # EFEITO 2 — o crescer. inflate() devolve um retangulo maior a volta
    # do mesmo centro. Enquanto o contador nao chegar a zero, a moeda e
    # desenhada maior do que e.
    moeda_a_desenhar = moeda
    if crescer > 0 and efeitos_ligados == True:
        moeda_a_desenhar = moeda.inflate(CRESCER_PIXEIS, CRESCER_PIXEIS)
    pygame.draw.rect(ecra, COR_MOEDA, moeda_a_desenhar.move(salto_x, salto_y))

    ecra.blit(fonte.render("D: dano    A: apanhar    E: ligar/desligar efeitos",
                           True, BRANCO), (20, 20))
    estado_texto = "Efeitos: LIGADOS"
    if efeitos_ligados == False:
        estado_texto = "Efeitos: DESLIGADOS"
    ecra.blit(fonte.render(estado_texto, True, BRANCO), (20, 55))

    # ------------------------- 4. MOSTRAR -------------------------
    pygame.display.flip()

    # ------------------------- 5. ESPERAR -------------------------
    clock.tick(FPS)

pygame.quit()
