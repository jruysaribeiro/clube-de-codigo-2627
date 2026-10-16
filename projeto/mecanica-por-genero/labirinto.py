# =====================================================================
# GENERO: LABIRINTO — paredes que nao se atravessam.
#
# A tecnica, e e a unica que resulta bem sem matematica nenhuma:
#   MOVE-SE PRIMEIRO E DESFAZ-SE DEPOIS.
# Mexe-se so no x; se ficou dentro de uma parede, desfaz-se o x. Depois
# mexe-se so no y; se ficou dentro de uma parede, desfaz-se o y.
#
# Tem de ser um eixo de cada vez. Se mexeres nos dois e depois desfizeres
# os dois, ficas colado as paredes e nao consegues deslizar ao longo delas.
#
# Estes ficheiros usam so retangulos coloridos, sem imagens nem sons: cada
# um demonstra UMA tecnica e mais nada. Para os juntares ao teu jogo,
# comeca pelo comum/esqueleto.py e traz para la so o bloco que precisas.
# =====================================================================

import pygame

LARGURA = 800
ALTURA = 600
FPS = 60
FUNDO = (18, 18, 28)
BRANCO = (240, 240, 240)
COR_JOGADOR = (70, 130, 230)
COR_PAREDE = (110, 110, 130)
COR_SAIDA = (90, 200, 120)
TAMANHO = 36
VELOCIDADE = 5

pygame.init()
ecra = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Genero: labirinto")
clock = pygame.time.Clock()
fonte = pygame.font.SysFont(None, 36)

jogador = pygame.Rect(60, 60, TAMANHO, TAMANHO)
saida = pygame.Rect(700, 500, 60, 60)

# As paredes sao so uma lista de retangulos. Mexe nos numeros e tens
# outro labirinto — nao ha mais nada a mudar no ficheiro.
paredes = [
    pygame.Rect(0, 0, LARGURA, 20),
    pygame.Rect(0, ALTURA - 20, LARGURA, 20),
    pygame.Rect(0, 0, 20, ALTURA),
    pygame.Rect(LARGURA - 20, 0, 20, ALTURA),
    pygame.Rect(150, 20, 20, 380),
    pygame.Rect(300, 200, 20, 380),
    pygame.Rect(450, 20, 20, 380),
    pygame.Rect(600, 200, 20, 300),
    pygame.Rect(150, 380, 320, 20),
]

a_correr = True
while a_correr:

    # ------------------------- 1. EVENTOS -------------------------
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            a_correr = False

    teclas = pygame.key.get_pressed()

    # ------------------------- 2. LOGICA --------------------------
    # --- primeiro so o x ---
    passo_x = 0
    if teclas[pygame.K_LEFT]:
        passo_x = -VELOCIDADE
    if teclas[pygame.K_RIGHT]:
        passo_x = VELOCIDADE
    jogador.x = jogador.x + passo_x
    for parede in paredes:
        if jogador.colliderect(parede):
            jogador.x = jogador.x - passo_x

    # --- agora so o y ---
    passo_y = 0
    if teclas[pygame.K_UP]:
        passo_y = -VELOCIDADE
    if teclas[pygame.K_DOWN]:
        passo_y = VELOCIDADE
    jogador.y = jogador.y + passo_y
    for parede in paredes:
        if jogador.colliderect(parede):
            jogador.y = jogador.y - passo_y

    # ------------------------ 3. DESENHAR -------------------------
    ecra.fill(FUNDO)
    pygame.draw.rect(ecra, COR_SAIDA, saida)
    for parede in paredes:
        pygame.draw.rect(ecra, COR_PAREDE, parede)
    pygame.draw.rect(ecra, COR_JOGADOR, jogador)
    if jogador.colliderect(saida):
        ecra.blit(fonte.render("CHEGASTE A SAIDA!", True, COR_SAIDA), (250, 40))

    # ------------------------- 4. MOSTRAR -------------------------
    pygame.display.flip()

    # ------------------------- 5. ESPERAR -------------------------
    clock.tick(FPS)

pygame.quit()
