# =====================================================================
# HUD — sessao 13
# HUD e o nome que se da a informacao desenhada POR CIMA do jogo:
# pontuacao, vidas, nivel, tempo. Nao faz parte do mundo do jogo, faz
# parte do ecra.
#
# Regras que valem para qualquer HUD:
#   1. desenha-se SEMPRE em ultimo, senao fica tapado pelo jogo;
#   2. a informacao mais importante fica no canto superior esquerdo,
#      que e para onde os olhos vao primeiro;
#   3. tudo o que e numero tem de passar por str() antes de ser texto.
# =====================================================================

import pygame

LARGURA = 800
ALTURA = 600
FPS = 60
FUNDO = (18, 18, 28)
BRANCO = (240, 240, 240)
VERMELHO = (220, 70, 70)
AMARELO = (240, 200, 70)
VERDE = (90, 200, 120)
COR_JOGADOR = (70, 130, 230)

pygame.init()
ecra = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("HUD")
clock = pygame.time.Clock()
fonte = pygame.font.SysFont(None, 32)

jogador = pygame.Rect(370, 270, 48, 48)
pontuacao = 0
vidas = 3
numero_do_nivel = 1


def mostrar_texto(texto, x, y, cor):
    desenho = fonte.render(texto, True, cor)
    ecra.blit(desenho, (x, y))


# Uma barra de vida desenhada com dois retangulos: um escuro por baixo,
# que e o maximo, e um colorido por cima, que e o que resta.
def barra(x, y, largura, altura, valor, maximo, cor):
    pygame.draw.rect(ecra, (60, 60, 70), (x, y, largura, altura))
    cheio = int(largura * valor / maximo)
    if cheio > 0:
        pygame.draw.rect(ecra, cor, (x, y, cheio, altura))


a_correr = True
while a_correr:

    # ------------------------- 1. EVENTOS -------------------------
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            a_correr = False
        # Teclas so para experimentares o HUD sem teres de jogar nada.
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_p:
                pontuacao = pontuacao + 10
            if evento.key == pygame.K_v and vidas > 0:
                vidas = vidas - 1
            if evento.key == pygame.K_n:
                numero_do_nivel = numero_do_nivel + 1

    # ------------------------- 2. LOGICA --------------------------
    # (num jogo a serio, o jogo acontecia aqui)

    # ------------------------ 3. DESENHAR -------------------------
    ecra.fill(FUNDO)
    pygame.draw.rect(ecra, COR_JOGADOR, jogador)

    # --- O HUD, sempre no fim de tudo o resto ---
    mostrar_texto("Pontos: " + str(pontuacao), 20, 20, BRANCO)
    mostrar_texto("Nivel " + str(numero_do_nivel), 360, 20, AMARELO)

    # Vidas em simbolos em vez de numeros: le-se muito mais depressa a
    # meio de um jogo do que "Vidas: 3".
    mostrar_texto("Vidas:", 600, 20, BRANCO)
    coracao = 0
    while coracao < vidas:
        pygame.draw.rect(ecra, VERMELHO, (680 + coracao * 30, 20, 22, 22))
        coracao = coracao + 1

    barra(20, 60, 200, 18, vidas, 3, VERDE)
    mostrar_texto("P: pontos   V: perder vida   N: nivel", 20, ALTURA - 40, BRANCO)

    # ------------------------- 4. MOSTRAR -------------------------
    pygame.display.flip()

    # ------------------------- 5. ESPERAR -------------------------
    clock.tick(FPS)

pygame.quit()
