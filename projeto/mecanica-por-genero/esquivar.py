# =====================================================================
# GENERO: ESQUIVAR — objetos que caem e nao se pode tocar.
# A tecnica: reciclar objetos. Nao se criam nem se destroem — quando
# saem por baixo, voltam para cima noutro sitio. A lista tem sempre o
# mesmo tamanho, e o jogo nunca fica lento.
#
# Estes ficheiros usam so retangulos coloridos, sem imagens nem sons: cada
# um demonstra UMA tecnica e mais nada. Para os juntares ao teu jogo,
# comeca pelo comum/esqueleto.py e traz para la so o bloco que precisas.
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
PEDRA = 34
QUANTAS = 8
QUEDA = 6
VELOCIDADE = 7

pygame.init()
ecra = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Genero: esquivar")
clock = pygame.time.Clock()
fonte = pygame.font.SysFont(None, 36)

jogador = pygame.Rect(LARGURA // 2, ALTURA - 70, TAMANHO, TAMANHO)
pedras = []
while len(pedras) < QUANTAS:
    x = random.randint(0, LARGURA - PEDRA)
    pedras.append(pygame.Rect(x, random.randint(-900, -PEDRA), PEDRA, PEDRA))
pontuacao = 0
tocado = False

a_correr = True
while a_correr:

    # ------------------------- 1. EVENTOS -------------------------
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            a_correr = False

    teclas = pygame.key.get_pressed()

    # ------------------------- 2. LOGICA --------------------------
    if teclas[pygame.K_LEFT]:
        jogador.x = jogador.x - VELOCIDADE
    if teclas[pygame.K_RIGHT]:
        jogador.x = jogador.x + VELOCIDADE
    jogador.clamp_ip(ecra.get_rect())

    # A TECNICA: reciclar em vez de criar e destruir.
    for pedra in pedras:
        pedra.y = pedra.y + QUEDA
        if pedra.top > ALTURA:
            pedra.x = random.randint(0, LARGURA - PEDRA)
            pedra.bottom = 0
            pontuacao = pontuacao + 1
        if jogador.colliderect(pedra):
            tocado = True

    # ------------------------ 3. DESENHAR -------------------------
    ecra.fill(FUNDO)
    for pedra in pedras:
        pygame.draw.rect(ecra, COR_PEDRA, pedra)
    pygame.draw.rect(ecra, COR_JOGADOR, jogador)
    texto = "Esquivadas: " + str(pontuacao)
    if tocado == True:
        texto = texto + "   (ja foste tocado)"
    ecra.blit(fonte.render(texto, True, BRANCO), (20, 20))

    # ------------------------- 4. MOSTRAR -------------------------
    pygame.display.flip()

    # ------------------------- 5. ESPERAR -------------------------
    clock.tick(FPS)

pygame.quit()
