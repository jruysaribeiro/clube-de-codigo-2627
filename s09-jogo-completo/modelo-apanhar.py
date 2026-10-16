# MODELO 2 — APANHAR. Apanha todas as moedas antes de o tempo acabar.
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
VERDE = (90, 200, 120)
VELOCIDADE = 5
TAMANHO = 48
MOEDA = 32
QUANTAS_MOEDAS = 10
SEGUNDOS = 30
PASTA_ASSETS = Path(__file__).parent.parent / "comum" / "assets"

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

ecra = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Modelo — apanhar")
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


def comecar_jogo():
    global jogador, moedas, fim_do_tempo, pontuacao
    jogador = pygame.Rect(LARGURA // 2, ALTURA // 2, TAMANHO, TAMANHO)
    pontuacao = 0
    # Guardamos o INSTANTE em que o tempo acaba e depois so comparamos.
    fim_do_tempo = pygame.time.get_ticks() + SEGUNDOS * 1000
    moedas = []
    while len(moedas) < QUANTAS_MOEDAS:
        y = random.randint(0, ALTURA - MOEDA)
        moedas.append(pygame.Rect(random.randint(0, 760), y, MOEDA, MOEDA))


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
        # clamp_ip puxa o retangulo para dentro de outro: e a versao curta
        # dos quatro if da sessao 7.
        jogador.clamp_ip(ecra.get_rect())

        # RECEITA: nunca tires de uma lista enquanto a percorres.
        sobreviventes = []
        for moeda in moedas:
            if jogador.colliderect(moeda):
                pontuacao = pontuacao + 1
                tocar(som_ponto)
            else:
                sobreviventes.append(moeda)
        moedas = sobreviventes
        segundos = (fim_do_tempo - pygame.time.get_ticks()) // 1000
        if len(moedas) == 0 or segundos <= 0:
            estado = "fim"

    # ------------------------ 3. DESENHAR -------------------------
    ecra.fill(PRETO)
    if estado == "menu":
        mostrar_texto("APANHA TUDO", 180, 200, AMARELO, fonte_grande)
        mostrar_texto("10 moedas em 30 segundos. Espaco!", 190, 330, BRANCO, fonte)
    if estado == "jogo":
        for moeda in moedas:
            ecra.blit(imagem_moeda, moeda)
        ecra.blit(imagem_jogador, jogador)
        mostrar_texto("Moedas: " + str(pontuacao), 20, 20, BRANCO, fonte)
        mostrar_texto("Tempo: " + str(segundos), 640, 20, BRANCO, fonte)
    if estado == "fim":
        if len(moedas) == 0:
            mostrar_texto("GANHASTE!", 240, 190, VERDE, fonte_grande)
        else:
            mostrar_texto("ACABOU O TEMPO", 130, 190, AMARELO, fonte_grande)
        mostrar_texto("Moedas: " + str(pontuacao), 320, 300, BRANCO, fonte)
        mostrar_texto("R para jogar outra vez", 250, 350, BRANCO, fonte)

    # ------------------------- 4. MOSTRAR -------------------------
    pygame.display.flip()

    # ------------------------- 5. ESPERAR -------------------------
    clock.tick(FPS)

pygame.quit()
