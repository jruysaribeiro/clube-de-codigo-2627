# =====================================================================
# MODO FEIRA — sessao 16
# Os requisitos do Demo Day. Um jogo em cima de uma mesa, com pessoas
# que nunca o viram, que nao leem instrucoes e que vao embora a meio.
#
#   1. RECOMECAR COM UMA TECLA, sem fechar a janela.
#   2. VOLTAR SOZINHO AO MENU ao fim de 10 segundos sem ninguem mexer.
#   3. SEM CONSOLA VISIVEL: zero print() neste ficheiro. Nenhum.
#   4. SOBREVIVER a alguem carregar em todas as teclas ao mesmo tempo.
#
# Le o modo-feira-NOTAS.md: metade destes requisitos nao e codigo.
# =====================================================================

import random

import pygame

LARGURA = 800
ALTURA = 600
FPS = 60
FUNDO = (18, 18, 28)
BRANCO = (240, 240, 240)
AMARELO = (240, 200, 70)
COR_JOGADOR = (70, 130, 230)
COR_MOEDA = (240, 200, 70)
TAMANHO = 48
MOEDA = 32
VELOCIDADE = 6

# Requisito 2: ao fim de quantos segundos parado se volta ao menu.
SEGUNDOS_ATE_AO_MENU = 10

pygame.init()
ecra = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("O nosso jogo")
clock = pygame.time.Clock()
fonte = pygame.font.SysFont(None, 36)
fonte_grande = pygame.font.SysFont(None, 72)

jogador = pygame.Rect(0, 0, TAMANHO, TAMANHO)
moeda = pygame.Rect(0, 0, MOEDA, MOEDA)
pontuacao = 0
ultimo_toque = 0


def comecar_jogo():
    global jogador, moeda, pontuacao
    jogador = pygame.Rect(LARGURA // 2, ALTURA // 2, TAMANHO, TAMANHO)
    moeda = pygame.Rect(random.randint(0, LARGURA - MOEDA),
                        random.randint(0, ALTURA - MOEDA), MOEDA, MOEDA)
    pontuacao = 0


comecar_jogo()
ultimo_toque = pygame.time.get_ticks()
estado = "menu"

a_correr = True
while a_correr:

    # ------------------------- 1. EVENTOS -------------------------
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            a_correr = False

        # Requisito 4: qualquer tecla conta como sinal de vida, seja ela
        # qual for. Nao ha aqui nenhuma lista de teclas permitidas, por
        # isso nao ha nenhuma tecla que possa partir isto.
        if evento.type == pygame.KEYDOWN:
            ultimo_toque = pygame.time.get_ticks()

            # Requisito 1: uma tecla so, e a mesma nos dois ecras.
            if estado == "menu" or estado == "fim":
                if evento.key == pygame.K_SPACE or evento.key == pygame.K_r:
                    comecar_jogo()
                    estado = "jogo"

    teclas = pygame.key.get_pressed()

    # ------------------------- 2. LOGICA --------------------------
    if estado == "jogo":
        # Carregar nas quatro setas ao mesmo tempo nao parte nada: as
        # somas anulam-se e o jogador fica quieto. E o que se quer.
        if teclas[pygame.K_LEFT]:
            jogador.x = jogador.x - VELOCIDADE
        if teclas[pygame.K_RIGHT]:
            jogador.x = jogador.x + VELOCIDADE
        if teclas[pygame.K_UP]:
            jogador.y = jogador.y - VELOCIDADE
        if teclas[pygame.K_DOWN]:
            jogador.y = jogador.y + VELOCIDADE
        jogador.clamp_ip(ecra.get_rect())

        if jogador.colliderect(moeda):
            pontuacao = pontuacao + 1
            moeda.x = random.randint(0, LARGURA - MOEDA)
            moeda.y = random.randint(0, ALTURA - MOEDA)
            ultimo_toque = pygame.time.get_ticks()

        if pontuacao >= 10:
            estado = "fim"

        # Requisito 2: ninguem mexe ha muito tempo? Volta ao menu, para o
        # jogo seguinte comecar do principio e nao a meio do anterior.
        parado = pygame.time.get_ticks() - ultimo_toque
        if parado > SEGUNDOS_ATE_AO_MENU * 1000:
            comecar_jogo()
            estado = "menu"

    if estado == "fim":
        parado = pygame.time.get_ticks() - ultimo_toque
        if parado > SEGUNDOS_ATE_AO_MENU * 1000:
            comecar_jogo()
            estado = "menu"

    # ------------------------ 3. DESENHAR -------------------------
    ecra.fill(FUNDO)
    if estado == "menu":
        ecra.blit(fonte_grande.render("O NOSSO JOGO", True, AMARELO), (150, 180))
        ecra.blit(fonte.render("Setas para andar", True, BRANCO), (300, 320))
        ecra.blit(fonte.render("ESPACO para jogar", True, BRANCO), (290, 360))
    if estado == "jogo":
        pygame.draw.rect(ecra, COR_MOEDA, moeda)
        pygame.draw.rect(ecra, COR_JOGADOR, jogador)
        ecra.blit(fonte.render("Moedas: " + str(pontuacao) + " / 10",
                               True, BRANCO), (20, 20))
    if estado == "fim":
        ecra.blit(fonte_grande.render("GANHASTE!", True, AMARELO), (230, 180))
        ecra.blit(fonte.render("ESPACO para jogar outra vez", True, BRANCO),
                  (220, 340))

    # ------------------------- 4. MOSTRAR -------------------------
    pygame.display.flip()

    # ------------------------- 5. ESPERAR -------------------------
    clock.tick(FPS)

pygame.quit()
