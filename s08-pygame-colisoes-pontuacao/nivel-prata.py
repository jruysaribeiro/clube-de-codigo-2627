# Sessao 8 — 🥈 PRATA — varias moedas numa lista, pontuacao no ecra, e a
# RECEITA de tirar coisas de uma lista sem estragar tudo (ver a logica).

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
QUANTAS_MOEDAS = 8

PASTA_ASSETS = Path(__file__).parent.parent / "comum" / "assets"

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

ecra = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Prata — varias moedas")
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
moedas = []
pontuacao = 0


def comecar_jogo():
    global jogador, moedas, pontuacao
    jogador = pygame.Rect(LARGURA // 2, ALTURA // 2, TAMANHO, TAMANHO)
    pontuacao = 0
    # Cada moeda e um pygame.Rect igual ao jogador, so mais pequeno.
    moedas = []
    while len(moedas) < QUANTAS_MOEDAS:
        x = random.randint(0, LARGURA - MOEDA)
        y = random.randint(0, ALTURA - MOEDA)
        moedas.append(pygame.Rect(x, y, MOEDA, MOEDA))


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

        # RECEITA: nunca tires nada de uma lista enquanto a percorres.
        # Faz uma lista NOVA so com os que ficam, e troca uma pela outra.
        sobreviventes = []
        for moeda in moedas:
            if jogador.colliderect(moeda):
                pontuacao = pontuacao + 1
                tocar(som_ponto)
            else:
                sobreviventes.append(moeda)
        moedas = sobreviventes
        if len(moedas) == 0:
            estado = "fim"

    # ------------------------ 3. DESENHAR -------------------------
    ecra.fill(PRETO)
    if estado == "menu":
        mostrar_texto("APANHA AS MOEDAS", 110, 210, AMARELO, fonte_grande)
        mostrar_texto("Espaco para comecar", 270, 330, BRANCO, fonte)
    if estado == "jogo":
        for moeda in moedas:
            ecra.blit(imagem_moeda, moeda)
        ecra.blit(imagem_jogador, jogador)
        mostrar_texto("Pontos: " + str(pontuacao), 20, 20, BRANCO, fonte)
    if estado == "fim":
        mostrar_texto("APANHASTE TUDO", 130, 210, AMARELO, fonte_grande)
        mostrar_texto("R para jogar outra vez", 250, 330, BRANCO, fonte)

    # ------------------------- 4. MOSTRAR -------------------------
    pygame.display.flip()

    # ------------------------- 5. ESPERAR -------------------------
    clock.tick(FPS)

pygame.quit()
