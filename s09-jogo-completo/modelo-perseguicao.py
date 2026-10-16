# MODELO 1 — PERSEGUICAO. Um bicho persegue-te; aguenta o maximo de tempo.
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
VERMELHO = (220, 70, 70)
VELOCIDADE = 5
TAMANHO = 48
BICHO = 44
BICHO_VELOCIDADE = 3
PASTA_ASSETS = Path(__file__).parent.parent / "comum" / "assets"

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

ecra = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Modelo — perseguicao")
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
imagem_bicho = carregar_imagem("inimigo.png", BICHO, BICHO, VERMELHO)
som_fim = carregar_som("fim.wav")

# Quem cria as variaveis do jogo e o comecar_jogo(), aqui em baixo.
def comecar_jogo():
    global jogador, bicho, inicio, pontuacao
    jogador = pygame.Rect(LARGURA // 2, ALTURA // 2, TAMANHO, TAMANHO)
    bicho = pygame.Rect(40, 40, BICHO, BICHO)
    inicio = pygame.time.get_ticks()
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
        # clamp_ip puxa o retangulo para dentro de outro. E a versao curta
        # dos quatro if que escreveste na sessao 7.
        jogador.clamp_ip(ecra.get_rect())

        # O bicho nao sabe o caminho: so sabe de que lado tu estas e da um
        # passo nessa direcao. Feito 60 vezes por segundo, parece esperto.
        if bicho.x < jogador.x:
            bicho.x = bicho.x + BICHO_VELOCIDADE
        if bicho.x > jogador.x:
            bicho.x = bicho.x - BICHO_VELOCIDADE
        if bicho.y < jogador.y:
            bicho.y = bicho.y + BICHO_VELOCIDADE
        if bicho.y > jogador.y:
            bicho.y = bicho.y - BICHO_VELOCIDADE

        # Os pontos sao os segundos que aguentaste.
        pontuacao = (pygame.time.get_ticks() - inicio) // 1000
        if jogador.colliderect(bicho):
            tocar(som_fim)
            estado = "fim"

    # ------------------------ 3. DESENHAR -------------------------
    ecra.fill(PRETO)
    if estado == "menu":
        mostrar_texto("FOGE!", 310, 200, AMARELO, fonte_grande)
        mostrar_texto("Setas para fugir.", 300, 320, BRANCO, fonte)
        mostrar_texto("Espaco para comecar", 270, 360, BRANCO, fonte)
    if estado == "jogo":
        ecra.blit(imagem_bicho, bicho)
        ecra.blit(imagem_jogador, jogador)
        mostrar_texto("Segundos: " + str(pontuacao), 20, 20, BRANCO, fonte)
    if estado == "fim":
        mostrar_texto("APANHOU-TE", 200, 200, AMARELO, fonte_grande)
        segundos_texto = "Aguentaste " + str(pontuacao) + " segundos"
        mostrar_texto(segundos_texto, 240, 300, BRANCO, fonte)
        mostrar_texto("R para jogar outra vez", 250, 350, BRANCO, fonte)

    # ------------------------- 4. MOSTRAR -------------------------
    pygame.display.flip()

    # ------------------------- 5. ESPERAR -------------------------
    clock.tick(FPS)

pygame.quit()
