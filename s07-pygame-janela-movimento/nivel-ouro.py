# =====================================================================
# Sessao 7 — 🥇 OURO
# Dois jogadores, com movimentos de tipos diferentes:
#   Setas: aceleracao e atrito. Arranca devagar e derrapa.
#   WASD:  velocidade constante, como na solucao.
# Joga com os dois e sente a diferenca. Nao ha resposta certa.
# =====================================================================

import random
from pathlib import Path

import pygame

LARGURA = 800
ALTURA = 600
FPS = 60

PRETO = (18, 18, 28)
BRANCO = (240, 240, 240)
AZUL = (70, 130, 230)
VERDE = (90, 200, 120)
AMARELO = (240, 200, 70)

VELOCIDADE = 6
TAMANHO = 48

# Quanto a velocidade sobe em cada ciclo, com a tecla carregada.
ACELERACAO = 0.6
# Quanto sobra da velocidade em cada ciclo: 0.92 = fica com 92%, perde 8%.
# Baixa para 0.80 e ele trava logo; sobe para 0.99 e patina no gelo.
ATRITO = 0.92

PASTA_ASSETS = Path(__file__).parent.parent / "comum" / "assets"

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

ecra = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Ouro — aceleracao e dois jogadores")
clock = pygame.time.Clock()
fonte = pygame.font.SysFont(None, 36)
fonte_grande = pygame.font.SysFont(None, 72)


def carregar_imagem(nome, largura, altura, cor):
    caminho = PASTA_ASSETS / "imagens" / nome
    if caminho.exists():
        imagem = pygame.image.load(caminho).convert_alpha()
        return pygame.transform.scale(imagem, (largura, altura))
    substituto = pygame.Surface((largura, altura))
    substituto.fill(cor)
    return substituto


def mostrar_texto(texto, x, y, cor, letra):
    desenho = letra.render(texto, True, cor)
    ecra.blit(desenho, (x, y))


imagem_jogador = carregar_imagem("jogador.png", TAMANHO, TAMANHO, AZUL)
imagem_jogador2 = carregar_imagem("jogador2.png", TAMANHO, TAMANHO, VERDE)

jogador = pygame.Rect(0, 0, TAMANHO, TAMANHO)
jogador2 = pygame.Rect(0, 0, TAMANHO, TAMANHO)
velocidade_x = 0.0
velocidade_y = 0.0


def comecar_jogo():
    global jogador, jogador2, velocidade_x, velocidade_y
    jogador = pygame.Rect(250, ALTURA // 2, TAMANHO, TAMANHO)
    jogador2 = pygame.Rect(500, ALTURA // 2, TAMANHO, TAMANHO)
    velocidade_x = 0.0
    velocidade_y = 0.0


comecar_jogo()

estado = "menu"
a_correr = True

while a_correr:

    # ------------------------- 1. EVENTOS -------------------------
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            a_correr = False
        if evento.type == pygame.KEYDOWN:
            if estado == "menu" and evento.key == pygame.K_SPACE:
                comecar_jogo()
                estado = "jogo"
            if estado == "jogo" and evento.key == pygame.K_ESCAPE:
                estado = "fim"
            if estado == "fim" and evento.key == pygame.K_r:
                comecar_jogo()
                estado = "jogo"

    teclas = pygame.key.get_pressed()

    # ------------------------- 2. LOGICA --------------------------
    if estado == "jogo":
        # Jogador 1: as teclas ja nao mexem na posicao. Mexem na VELOCIDADE,
        # e e a velocidade que mexe na posicao. E essa a diferenca toda.
        if teclas[pygame.K_LEFT]:
            velocidade_x = velocidade_x - ACELERACAO
        if teclas[pygame.K_RIGHT]:
            velocidade_x = velocidade_x + ACELERACAO
        if teclas[pygame.K_UP]:
            velocidade_y = velocidade_y - ACELERACAO
        if teclas[pygame.K_DOWN]:
            velocidade_y = velocidade_y + ACELERACAO

        # Sem esta parte ele nunca mais parava: ia somando para sempre.
        velocidade_x = velocidade_x * ATRITO
        velocidade_y = velocidade_y * ATRITO

        # O Rect so guarda numeros inteiros, por isso o int() aqui.
        jogador.x = jogador.x + int(velocidade_x)
        jogador.y = jogador.y + int(velocidade_y)

        # Jogador 2: o movimento simples da solucao, para comparar.
        if teclas[pygame.K_a]:
            jogador2.x = jogador2.x - VELOCIDADE
        if teclas[pygame.K_d]:
            jogador2.x = jogador2.x + VELOCIDADE
        if teclas[pygame.K_w]:
            jogador2.y = jogador2.y - VELOCIDADE
        if teclas[pygame.K_s]:
            jogador2.y = jogador2.y + VELOCIDADE

    # ------------------------ 3. DESENHAR -------------------------
    ecra.fill(PRETO)
    if estado == "menu":
        mostrar_texto("DOIS JOGADORES", 160, 200, AMARELO, fonte_grande)
        mostrar_texto("Setas: derrapa.  WASD: nao derrapa.", 170, 320, BRANCO, fonte)
        mostrar_texto("Espaco para comecar", 270, 370, BRANCO, fonte)
    if estado == "jogo":
        ecra.blit(imagem_jogador, jogador)
        ecra.blit(imagem_jogador2, jogador2)
    if estado == "fim":
        mostrar_texto("FIM", 330, 210, AMARELO, fonte_grande)
        mostrar_texto("R para jogar outra vez", 250, 350, BRANCO, fonte)

    # ------------------------- 4. MOSTRAR -------------------------
    pygame.display.flip()

    # ------------------------- 5. ESPERAR -------------------------
    clock.tick(FPS)

pygame.quit()
