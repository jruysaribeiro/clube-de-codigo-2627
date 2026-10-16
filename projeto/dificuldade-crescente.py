# =====================================================================
# DIFICULDADE CRESCENTE — sessao 13
# A alternativa simples aos niveis: nao ha niveis nenhuns, a velocidade
# e que sobe com o tempo. Duas linhas de codigo, e o jogo passa a ter
# uma curva. Para muitos jogos e melhor do que niveis a serio.
# =====================================================================

import random

import pygame

LARGURA = 800
ALTURA = 600
FPS = 60
FUNDO = (18, 18, 28)
BRANCO = (240, 240, 240)
COR_JOGADOR = (70, 130, 230)
COR_PEDRA = (220, 70, 70)
TAMANHO = 48
PEDRA = 32

# Estas tres constantes SAO a curva de dificuldade. Sao o unico sitio
# onde se mexe para o jogo ficar mais facil ou mais dificil.
QUEDA_INICIAL = 2.0
QUEDA_MAXIMA = 12.0
# Quanto a velocidade sobe por segundo. 0.25 e suave; 1.0 e brutal.
SUBIDA_POR_SEGUNDO = 0.25

pygame.init()
ecra = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Dificuldade crescente")
clock = pygame.time.Clock()
fonte = pygame.font.SysFont(None, 36)

jogador = pygame.Rect(LARGURA // 2, ALTURA - 70, TAMANHO, TAMANHO)
pedras = []
while len(pedras) < 6:
    x = random.randint(0, LARGURA - PEDRA)
    pedras.append(pygame.Rect(x, random.randint(-800, -PEDRA), PEDRA, PEDRA))

inicio = pygame.time.get_ticks()
queda = QUEDA_INICIAL

a_correr = True
while a_correr:

    # ------------------------- 1. EVENTOS -------------------------
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            a_correr = False

    teclas = pygame.key.get_pressed()

    # ------------------------- 2. LOGICA --------------------------
    if teclas[pygame.K_LEFT]:
        jogador.x = jogador.x - 6
    if teclas[pygame.K_RIGHT]:
        jogador.x = jogador.x + 6
    jogador.clamp_ip(ecra.get_rect())

    # AQUI ESTA A CURVA, e sao mesmo so estas duas linhas.
    segundos = (pygame.time.get_ticks() - inicio) // 1000
    queda = QUEDA_INICIAL + segundos * SUBIDA_POR_SEGUNDO

    # O tecto e obrigatorio. Sem ele, ao fim de dois minutos as pedras
    # andam tanto por ciclo que atravessam o jogador sem lhe tocar.
    if queda > QUEDA_MAXIMA:
        queda = QUEDA_MAXIMA

    for pedra in pedras:
        pedra.y = pedra.y + int(queda)
        if pedra.top > ALTURA:
            pedra.x = random.randint(0, LARGURA - PEDRA)
            pedra.bottom = 0

    # ------------------------ 3. DESENHAR -------------------------
    ecra.fill(FUNDO)
    for pedra in pedras:
        pygame.draw.rect(ecra, COR_PEDRA, pedra)
    pygame.draw.rect(ecra, COR_JOGADOR, jogador)
    texto = "Segundos: " + str(segundos) + "   Queda: " + str(round(queda, 1))
    ecra.blit(fonte.render(texto, True, BRANCO), (20, 20))

    # ------------------------- 4. MOSTRAR -------------------------
    pygame.display.flip()

    # ------------------------- 5. ESPERAR -------------------------
    clock.tick(FPS)

pygame.quit()
