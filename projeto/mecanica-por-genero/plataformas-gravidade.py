# =====================================================================
# GENERO: PLATAFORMAS — gravidade, chao e salto.
#
# ISTO E MUITO MAIS DIFICIL DO QUE TUDO O RESTO DO ANO. Nao e para
# descobrires sozinho: e para copiares, pores a funcionar, e so depois
# perceberes. Nao ha aqui vergonha nenhuma — toda a gente faz assim.
#
# As tres ideias, por ordem:
#
# 1. GRAVIDADE. O jogador tem uma velocidade vertical (velocidade_y) que
#    CRESCE um bocadinho em cada ciclo. Nao ha "cair": ha uma velocidade
#    que aumenta sempre, e uma posicao que a segue.
#
# 2. UM EIXO DE CADA VEZ. Mexe-se no x, resolve-se o x. Mexe-se no y,
#    resolve-se o y. Se mexeres nos dois ao mesmo tempo nunca consegues
#    saber se bateste no chao ou na parede, e ficas colado as coisas.
#
# 3. SO SE SALTA COM OS PES NO CHAO. Precisas de saber se estas apoiado,
#    e isso descobre-se DEPOIS de resolver o y: se estavas a descer e
#    bateste em alguma coisa, entao estas apoiado.
#
# O salto usa KEYDOWN (um acontecimento) e nao teclas[] (um estado). Se
# usasses teclas[], voavas: saltarias 60 vezes por segundo.
# =====================================================================

import pygame

LARGURA = 800
ALTURA = 600
FPS = 60
FUNDO = (18, 18, 28)
BRANCO = (240, 240, 240)
COR_JOGADOR = (70, 130, 230)
COR_CHAO = (110, 110, 130)
TAMANHO = 40
VELOCIDADE = 5

# Estas tres constantes SAO a sensacao do jogo. Mexe nelas.
# GRAVIDADE: quanto a velocidade de queda cresce por ciclo.
GRAVIDADE = 0.8
# FORCA_DO_SALTO: negativa, porque para cima o y DIMINUI.
FORCA_DO_SALTO = -15
# QUEDA_MAXIMA: sem tecto, ao fim de uma queda longa o jogador anda tanto
# por ciclo que atravessa o chao sem lhe tocar. Este limite evita isso.
QUEDA_MAXIMA = 18

pygame.init()
ecra = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Genero: plataformas")
clock = pygame.time.Clock()
fonte = pygame.font.SysFont(None, 30)

jogador = pygame.Rect(100, 100, TAMANHO, TAMANHO)
velocidade_y = 0.0
no_chao = False

plataformas = [
    pygame.Rect(0, ALTURA - 40, LARGURA, 40),
    pygame.Rect(120, 460, 200, 20),
    pygame.Rect(400, 380, 200, 20),
    pygame.Rect(180, 290, 160, 20),
    pygame.Rect(520, 200, 220, 20),
]

a_correr = True
while a_correr:

    # ------------------------- 1. EVENTOS -------------------------
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            a_correr = False
        # O salto e um ACONTECIMENTO, nao um estado. Por isso vive aqui.
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE and no_chao == True:
                velocidade_y = FORCA_DO_SALTO
                no_chao = False

    teclas = pygame.key.get_pressed()

    # ------------------------- 2. LOGICA --------------------------

    # --- PRIMEIRO O X, e resolve-se logo o x ---
    passo_x = 0
    if teclas[pygame.K_LEFT]:
        passo_x = -VELOCIDADE
    if teclas[pygame.K_RIGHT]:
        passo_x = VELOCIDADE
    jogador.x = jogador.x + passo_x
    for plataforma in plataformas:
        if jogador.colliderect(plataforma):
            # Bateu de lado: encosta-se a parede, do lado por onde vinha.
            if passo_x > 0:
                jogador.right = plataforma.left
            if passo_x < 0:
                jogador.left = plataforma.right

    # --- AGORA O Y: gravidade, movimento, e resolve-se o y ---
    velocidade_y = velocidade_y + GRAVIDADE
    if velocidade_y > QUEDA_MAXIMA:
        velocidade_y = QUEDA_MAXIMA
    jogador.y = jogador.y + int(velocidade_y)

    no_chao = False
    for plataforma in plataformas:
        if jogador.colliderect(plataforma):
            if velocidade_y > 0:
                # Vinha a descer: pousa em cima da plataforma.
                jogador.bottom = plataforma.top
                no_chao = True
            else:
                # Vinha a subir: bateu com a cabeca no tecto.
                jogador.top = plataforma.bottom
            # Bateu, seja de que lado for: a velocidade vertical zera.
            velocidade_y = 0.0

    # Caiu para fora do ecra: volta ao principio.
    if jogador.top > ALTURA:
        jogador.x = 100
        jogador.y = 100
        velocidade_y = 0.0

    # ------------------------ 3. DESENHAR -------------------------
    ecra.fill(FUNDO)
    for plataforma in plataformas:
        pygame.draw.rect(ecra, COR_CHAO, plataforma)
    pygame.draw.rect(ecra, COR_JOGADOR, jogador)
    ecra.blit(fonte.render("Setas para andar, ESPACO para saltar",
                           True, BRANCO), (20, 20))
    ecra.blit(fonte.render("no_chao = " + str(no_chao)
                           + "   velocidade_y = " + str(round(velocidade_y, 1)),
                           True, BRANCO), (20, 50))

    # ------------------------- 4. MOSTRAR -------------------------
    pygame.display.flip()

    # ------------------------- 5. ESPERAR -------------------------
    clock.tick(FPS)

pygame.quit()
