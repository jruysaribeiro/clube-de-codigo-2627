# MODELO 3 — ESQUIVAR. Caem pedras. Nao lhes toques.
# Os tres modelos desta pasta tem a mesma forma: quem leu um le os outros.

import random
from pathlib import Path

import pygame

# --- Constantes: e aqui que se mexe primeiro ---
LARGURA = 800
ALTURA = 600
FPS = 60
PRETO = (18, 18, 28)
BRANCO = (240, 240, 240)
AZUL = (70, 130, 230)
AMARELO = (240, 200, 70)
CINZENTO = (150, 150, 160)
VELOCIDADE = 5
TAMANHO = 48
PEDRA = 36
QUANTAS_PEDRAS = 7
QUEDA = 5
PASTA_ASSETS = Path(__file__).parent.parent / "comum" / "assets"

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

ecra = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Modelo — esquivar")
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

imagem_jogador = carregar_imagem("jogador.png", TAMANHO, TAMANHO, AZUL)
imagem_pedra = carregar_imagem("inimigo.png", PEDRA, PEDRA, CINZENTO)
som_fim = carregar_som("fim.wav")

# Quem cria as variaveis do jogo e o comecar_jogo(), aqui em baixo.
def comecar_jogo():
    global jogador, pedras, pontuacao
    # So se anda para os lados: o jogador fica sempre em baixo.
    jogador = pygame.Rect(LARGURA // 2, ALTURA - 70, TAMANHO, TAMANHO)
    pontuacao = 0
    # Comecam todas acima do ecra, a alturas diferentes, para virem aos poucos.
    pedras = []
    while len(pedras) < QUANTAS_PEDRAS:
        x = random.randint(0, LARGURA - PEDRA)
        y = random.randint(-900, -PEDRA)
        pedras.append(pygame.Rect(x, y, PEDRA, PEDRA))


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
        # clamp_ip puxa o retangulo para dentro de outro. E a versao curta
        # dos quatro if que escreveste na sessao 7.
        jogador.clamp_ip(ecra.get_rect())

        for pedra in pedras:
            pedra.y = pedra.y + QUEDA
            # Passou ao lado: vale um ponto e volta para cima, noutro sitio.
            if pedra.top > ALTURA:
                pedra.x = random.randint(0, LARGURA - PEDRA)
                pedra.bottom = 0
                pontuacao = pontuacao + 1
            if jogador.colliderect(pedra):
                tocar(som_fim)
                estado = "fim"

    # ------------------------ 3. DESENHAR -------------------------
    ecra.fill(PRETO)
    if estado == "menu":
        mostrar_texto("ESQUIVA-TE", 220, 200, AMARELO, fonte_grande)
        mostrar_texto("Esquerda e direita para fugir.", 220, 320, BRANCO, fonte)
        mostrar_texto("Espaco para comecar", 270, 360, BRANCO, fonte)
    if estado == "jogo":
        for pedra in pedras:
            ecra.blit(imagem_pedra, pedra)
        ecra.blit(imagem_jogador, jogador)
        mostrar_texto("Pontos: " + str(pontuacao), 20, 20, BRANCO, fonte)
    if estado == "fim":
        mostrar_texto("APANHASTE UMA", 130, 200, AMARELO, fonte_grande)
        mostrar_texto("Pontos: " + str(pontuacao), 320, 300, BRANCO, fonte)
        mostrar_texto("R para jogar outra vez", 250, 350, BRANCO, fonte)

    # ------------------------- 4. MOSTRAR -------------------------
    pygame.display.flip()

    # ------------------------- 5. ESPERAR -------------------------
    clock.tick(FPS)

pygame.quit()
