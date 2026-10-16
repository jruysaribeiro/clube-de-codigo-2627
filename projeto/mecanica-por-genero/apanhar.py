# =====================================================================
# GENERO: APANHAR — recolher objetos espalhados pelo ecra.
# A tecnica: uma LISTA de objetos e a receita dos sobreviventes.
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
COR_MOEDA = (240, 200, 70)
TAMANHO = 48
MOEDA = 28
QUANTAS = 12
VELOCIDADE = 6

pygame.init()
ecra = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Genero: apanhar")
clock = pygame.time.Clock()
fonte = pygame.font.SysFont(None, 36)

jogador = pygame.Rect(LARGURA // 2, ALTURA // 2, TAMANHO, TAMANHO)
moedas = []
while len(moedas) < QUANTAS:
    x = random.randint(0, LARGURA - MOEDA)
    y = random.randint(0, ALTURA - MOEDA)
    moedas.append(pygame.Rect(x, y, MOEDA, MOEDA))
pontuacao = 0

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
    jogador.clamp_ip(ecra.get_rect())

    # A TECNICA: lista nova com quem fica, em vez de tirar da antiga.
    sobreviventes = []
    for moeda in moedas:
        if jogador.colliderect(moeda):
            pontuacao = pontuacao + 1
        else:
            sobreviventes.append(moeda)
    moedas = sobreviventes

    # ------------------------ 3. DESENHAR -------------------------
    ecra.fill(FUNDO)
    for moeda in moedas:
        pygame.draw.rect(ecra, COR_MOEDA, moeda)
    pygame.draw.rect(ecra, COR_JOGADOR, jogador)
    ecra.blit(fonte.render("Apanhadas: " + str(pontuacao), True, BRANCO), (20, 20))

    # ------------------------- 4. MOSTRAR -------------------------
    pygame.display.flip()

    # ------------------------- 5. ESPERAR -------------------------
    clock.tick(FPS)

pygame.quit()
