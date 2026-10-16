# =====================================================================
# GENERO: CHEGAR A UM ALVO — ir de A a B, com o caminho a complicar-se.
# A tecnica: uma condicao de vitoria, e o alvo a mudar de sitio para o
# jogo continuar. E o esqueleto de qualquer jogo de "entregas".
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
COR_ALVO = (90, 200, 120)
COR_BICHO = (220, 70, 70)
TAMANHO = 40
ALVO = 56
BICHO = 40
VELOCIDADE = 6

pygame.init()
ecra = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Genero: chegar ao alvo")
clock = pygame.time.Clock()
fonte = pygame.font.SysFont(None, 36)

jogador = pygame.Rect(60, ALTURA // 2, TAMANHO, TAMANHO)
alvo = pygame.Rect(700, ALTURA // 2, ALVO, ALVO)
entregas = 0
# Cada entrega feita acrescenta um bicho: e a dificuldade a crescer sem
# ser preciso relogio nenhum.
bichos = []

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

    for bicho in bichos:
        if bicho.x < jogador.x:
            bicho.x = bicho.x + 2
        if bicho.x > jogador.x:
            bicho.x = bicho.x - 2
        if bicho.y < jogador.y:
            bicho.y = bicho.y + 2
        if bicho.y > jogador.y:
            bicho.y = bicho.y - 2

    # A CONDICAO DE VITORIA. Chegou ao alvo: conta, e o alvo muda de sitio.
    if jogador.colliderect(alvo):
        entregas = entregas + 1
        alvo.x = random.randint(0, LARGURA - ALVO)
        alvo.y = random.randint(0, ALTURA - ALVO)
        bichos.append(pygame.Rect(random.randint(0, 700), 20, BICHO, BICHO))

    # ------------------------ 3. DESENHAR -------------------------
    ecra.fill(FUNDO)
    pygame.draw.rect(ecra, COR_ALVO, alvo)
    for bicho in bichos:
        pygame.draw.rect(ecra, COR_BICHO, bicho)
    pygame.draw.rect(ecra, COR_JOGADOR, jogador)
    ecra.blit(fonte.render("Entregas: " + str(entregas), True, BRANCO), (20, 20))

    # ------------------------- 4. MOSTRAR -------------------------
    pygame.display.flip()

    # ------------------------- 5. ESPERAR -------------------------
    clock.tick(FPS)

pygame.quit()
