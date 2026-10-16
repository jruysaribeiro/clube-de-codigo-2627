# =====================================================================
# MVP MINIMO — sessao 11
# O minimo absoluto que ja e um jogo: uma janela, uma personagem, e
# movimento que nao sai do ecra. Mais nada.
#
# E ESTE o ficheiro que a tua equipa copia para arrancar. Copia-o para a
# pasta da equipa com o nome do vosso jogo e comeca a mexer.
#
# Quando o vosso jogo ja tiver um fim e um recomeco, mudem-se para o
# comum/esqueleto.py, que tem menu, fim e reinicio ja feitos.
# =====================================================================

import pygame

LARGURA = 800
ALTURA = 600
FPS = 60
FUNDO = (18, 18, 28)
COR_JOGADOR = (70, 130, 230)
VELOCIDADE = 5
TAMANHO = 48

pygame.init()
ecra = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("O nosso jogo")
clock = pygame.time.Clock()

jogador = pygame.Rect(LARGURA // 2, ALTURA // 2, TAMANHO, TAMANHO)

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
    if teclas[pygame.K_UP]:
        jogador.y = jogador.y - VELOCIDADE
    if teclas[pygame.K_DOWN]:
        jogador.y = jogador.y + VELOCIDADE

    # Puxa o jogador para dentro do ecra, se ele tiver saido.
    jogador.clamp_ip(ecra.get_rect())

    # ------------------------ 3. DESENHAR -------------------------
    ecra.fill(FUNDO)
    pygame.draw.rect(ecra, COR_JOGADOR, jogador)

    # ------------------------- 4. MOSTRAR -------------------------
    pygame.display.flip()

    # ------------------------- 5. ESPERAR -------------------------
    clock.tick(FPS)

pygame.quit()
