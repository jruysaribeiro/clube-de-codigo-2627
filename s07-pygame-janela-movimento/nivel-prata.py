# =====================================================================
# Sessao 7 — 🥈 PRATA
# Duas coisas novas em relacao a solucao:
#   1. o jogador nao sai do ecra (procura "PRATA 1" mais abaixo)
#   2. o quadrado passa a ser uma imagem  (procura "PRATA 2")
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
AMARELO = (240, 200, 70)

VELOCIDADE = 6
TAMANHO = 64

PASTA_ASSETS = Path(__file__).parent.parent / "comum" / "assets"

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

ecra = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Prata — limites e imagem")
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


def carregar_som(nome):
    caminho = PASTA_ASSETS / "sons" / nome
    if caminho.exists():
        return pygame.mixer.Sound(caminho)
    return None


def tocar(som):
    if som is not None:
        som.play()


def mostrar_texto(texto, x, y, cor, letra):
    desenho = letra.render(texto, True, cor)
    ecra.blit(desenho, (x, y))


# PRATA 2: a imagem ja vinha carregada de origem. Poe um jogador.png em
# comum/assets/imagens/ e ele aparece aqui em vez do quadrado azul, sem
# mexer numa unica linha de codigo. Foi para isto que a funcao ficou assim.
imagem_jogador = carregar_imagem("jogador.png", TAMANHO, TAMANHO, AZUL)
som_ponto = carregar_som("ponto.wav")

jogador = pygame.Rect(0, 0, TAMANHO, TAMANHO)
pontuacao = 0


def comecar_jogo():
    global jogador, pontuacao
    jogador = pygame.Rect(LARGURA // 2, ALTURA // 2, TAMANHO, TAMANHO)
    pontuacao = 0


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
        if teclas[pygame.K_LEFT]:
            jogador.x = jogador.x - VELOCIDADE
        if teclas[pygame.K_RIGHT]:
            jogador.x = jogador.x + VELOCIDADE
        if teclas[pygame.K_UP]:
            jogador.y = jogador.y - VELOCIDADE
        if teclas[pygame.K_DOWN]:
            jogador.y = jogador.y + VELOCIDADE

        # PRATA 1: deixamos o jogador sair e depois puxamo-lo para tras.
        # Em vez de impedir o movimento, corrigimo-lo. Da muito menos
        # trabalho, e o resultado no ecra e exatamente o mesmo.
        if jogador.left < 0:
            jogador.left = 0
        if jogador.right > LARGURA:
            jogador.right = LARGURA
        if jogador.top < 0:
            jogador.top = 0
        if jogador.bottom > ALTURA:
            jogador.bottom = ALTURA

    # ------------------------ 3. DESENHAR -------------------------
    ecra.fill(PRETO)
    if estado == "menu":
        mostrar_texto("O MEU JOGO", 230, 210, AMARELO, fonte_grande)
        mostrar_texto("Espaco para comecar", 270, 330, BRANCO, fonte)
    if estado == "jogo":
        ecra.blit(imagem_jogador, jogador)
        mostrar_texto("Pontos: " + str(pontuacao), 20, 20, BRANCO, fonte)
    if estado == "fim":
        mostrar_texto("FIM", 330, 210, AMARELO, fonte_grande)
        mostrar_texto("Pontos: " + str(pontuacao), 320, 300, BRANCO, fonte)
        mostrar_texto("R para jogar outra vez", 250, 350, BRANCO, fonte)

    # ------------------------- 4. MOSTRAR -------------------------
    pygame.display.flip()

    # ------------------------- 5. ESPERAR -------------------------
    clock.tick(FPS)

pygame.quit()
