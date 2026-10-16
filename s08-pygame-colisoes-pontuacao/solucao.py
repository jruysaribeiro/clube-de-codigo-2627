# Sessao 8 — SOLUCAO — apanhar uma moeda e contar pontos
# O esqueleto de sempre, sem os comentarios de tutorial da sessao 7.

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

VELOCIDADE = 5
TAMANHO = 48
MOEDA = 32

PASTA_ASSETS = Path(__file__).parent.parent / "comum" / "assets"

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

ecra = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Sessao 8 — colisoes")
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
imagem_moeda = carregar_imagem("moeda.png", MOEDA, MOEDA, AMARELO)
som_ponto = carregar_som("ponto.wav")

jogador = pygame.Rect(0, 0, TAMANHO, TAMANHO)
moeda = pygame.Rect(0, 0, MOEDA, MOEDA)
pontuacao = 0


# O "- MOEDA" e para ela nao ficar meia de fora pela direita ou por baixo.
def mudar_moeda_de_sitio():
    global moeda
    moeda.x = random.randint(0, LARGURA - MOEDA)
    moeda.y = random.randint(0, ALTURA - MOEDA)


def comecar_jogo():
    global jogador, pontuacao
    jogador = pygame.Rect(LARGURA // 2, ALTURA // 2, TAMANHO, TAMANHO)
    pontuacao = 0
    mudar_moeda_de_sitio()


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

        # colliderect() responde a uma pergunta so: estes dois retangulos
        # estao sobrepostos AGORA? Nao interessa de que lado se tocaram.
        if jogador.colliderect(moeda):
            pontuacao = pontuacao + 1
            tocar(som_ponto)
            mudar_moeda_de_sitio()

    # ------------------------ 3. DESENHAR -------------------------
    ecra.fill(PRETO)
    if estado == "menu":
        mostrar_texto("APANHA A MOEDA", 150, 210, AMARELO, fonte_grande)
        mostrar_texto("Espaco para comecar", 270, 330, BRANCO, fonte)
    if estado == "jogo":
        ecra.blit(imagem_moeda, moeda)
        ecra.blit(imagem_jogador, jogador)
        mostrar_texto("Pontos: " + str(pontuacao), 20, 20, BRANCO, fonte)
        # Tira o # das duas linhas seguintes para veres as caixas da
        # colisao a vermelho. Depois volta a por, senao fica feio.
        # pygame.draw.rect(ecra, (255, 0, 0), jogador, 2)
        # pygame.draw.rect(ecra, (255, 0, 0), moeda, 2)
    if estado == "fim":
        mostrar_texto("FIM", 330, 210, AMARELO, fonte_grande)
        mostrar_texto("Pontos: " + str(pontuacao), 320, 300, BRANCO, fonte)
        mostrar_texto("R para jogar outra vez", 250, 350, BRANCO, fonte)

    # ------------------------- 4. MOSTRAR -------------------------
    pygame.display.flip()

    # ------------------------- 5. ESPERAR -------------------------
    clock.tick(FPS)

pygame.quit()
