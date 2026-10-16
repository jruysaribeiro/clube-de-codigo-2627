# =====================================================================
# ESQUELETO — Clube de Codigo 2026/27
# O mesmo ficheiro nas sessoes 7, 8, 9 e nas oito sessoes de projeto.
# Le-o com atencao uma vez; dai em diante so acrescentas linhas dentro
# dos blocos que ja aqui estao. O ciclo do jogo tem cinco, por esta ordem:
#     EVENTOS -> LOGICA -> DESENHAR -> MOSTRAR -> ESPERAR
# =====================================================================

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

# O caminho dos assets e calculado a partir da pasta deste ficheiro. Com
# "assets/imagens" o programa so funcionaria com o terminal aberto
# exatamente na pasta certa, e essa e a avaria que mais tempo rouba na sala.
PASTA_ASSETS = Path(__file__).parent.parent / "comum" / "assets"

# O mixer tem de ser afinado ANTES do pygame.init(). Ao contrario, fica com
# um buffer enorme e o som chega meio segundo depois da acao.
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

ecra = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Clube de Codigo")
clock = pygame.time.Clock()
fonte = pygame.font.SysFont(None, 36)
fonte_grande = pygame.font.SysFont(None, 72)


def carregar_imagem(nome, largura, altura, cor):
    # Sem o ficheiro devolvemos um retangulo da cor pedida: o jogo continua
    # a correr em qualquer computador, mesmo sem a pasta de imagens.
    caminho = PASTA_ASSETS / "imagens" / nome
    if caminho.exists():
        imagem = pygame.image.load(caminho).convert_alpha()
        return pygame.transform.scale(imagem, (largura, altura))
    substituto = pygame.Surface((largura, altura))
    substituto.fill(cor)
    return substituto


def carregar_som(nome):
    # Devolve None quando o ficheiro nao existe. O jogo fica em silencio,
    # mas nao rebenta a meio da aula.
    caminho = PASTA_ASSETS / "sons" / nome
    if caminho.exists():
        return pygame.mixer.Sound(caminho)
    return None


def tocar(som):
    # Chamamos esta em vez de som.play(), porque o som pode ser None.
    if som is not None:
        som.play()


def mostrar_texto(texto, x, y, cor, letra):
    desenho = letra.render(texto, True, cor)
    ecra.blit(desenho, (x, y))


imagem_jogador = carregar_imagem("jogador.png", TAMANHO, TAMANHO, AZUL)
som_ponto = carregar_som("ponto.wav")

jogador = pygame.Rect(0, 0, TAMANHO, TAMANHO)
pontuacao = 0


def comecar_jogo():
    # "global" avisa o Python de que queremos mexer nas variaveis la de
    # fora e nao criar variaveis novas so para dentro desta funcao.
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
            # Mais tarde trocas esta condicao por "quando as vidas acabam".
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
    # Ate aqui desenhamos numa folha invisivel. E esta linha que a poe no
    # ecra. Sem ela fica tudo preto e o Python nao se queixa de nada.
    pygame.display.flip()

    # ------------------------- 5. ESPERAR -------------------------
    # Trava o jogo nos 60 desenhos por segundo. Sem isto, o mesmo jogo
    # corre a velocidades diferentes em computadores diferentes.
    clock.tick(FPS)

pygame.quit()
