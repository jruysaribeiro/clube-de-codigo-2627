# =====================================================================
# Sessao 7 — ESQUELETO. Corre-me com:  python3 esqueleto.py
# Vais reencontrar este ficheiro em TODAS as sessoes ate ao fim do ano, por
# isso vale a pena le-lo todo uma vez, com calma, antes de mexer.
# O ciclo do jogo tem cinco blocos, sempre por esta ordem:
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
        # Se a seta da esquerda estiver carregada agora, o teclas[] que a
        # linha de cima te deu faz teclas[pygame.K_LEFT] valer True.
        # TODO: o quadrado esta parado. O que tem de mudar de ciclo para
        #       ciclo, para ele parecer que anda?

        # TODO: ele tem um jogador.x e um jogador.y. Qual deles muda para o
        #       lado? Para a esquerda, fica maior ou mais pequeno? E cuidado,
        #       porque no ecra o y CRESCE para baixo, nao para cima.
        pass

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
