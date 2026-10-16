# Sessao 8 — 🥇 OURO — bichos que andam sozinhos e tiram vidas. Sobreviver
# vale pontos. Versao reduzida: ver "Aviso de ambito" no NOTAS.md.

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
BICHO = 40
BICHO_VELOCIDADE = 4
QUANTOS_BICHOS = 5
VIDAS_INICIAIS = 3
PASTA_ASSETS = Path(__file__).parent.parent / "comum" / "assets"
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

ecra = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Ouro — vidas e bichos que andam")
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
som_dano = carregar_som("dano.wav")

# Quem cria as variaveis do jogo e o comecar_jogo(), aqui em baixo.
def comecar_jogo():
    global jogador, bichos, pontuacao, vidas
    jogador = pygame.Rect(LARGURA // 2, ALTURA // 2, TAMANHO, TAMANHO)
    pontuacao = 0
    vidas = VIDAS_INICIAIS
    # Comecam todos fora do ecra, a esquerda, para entrarem aos poucos.
    bichos = []
    while len(bichos) < QUANTOS_BICHOS:
        y = random.randint(0, ALTURA - BICHO)
        bichos.append(pygame.Rect(random.randint(-600, 0), y, BICHO, BICHO))


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

        for bicho in bichos:
            bicho.x = bicho.x + BICHO_VELOCIDADE
            # Chegou ao fim do ecra sem te apanhar: um ponto, e volta atras.
            if bicho.left > LARGURA:
                bicho.right = random.randint(-500, 0)
                bicho.y = random.randint(0, ALTURA - BICHO)
                pontuacao = pontuacao + 1
            if jogador.colliderect(bicho):
                vidas = vidas - 1
                tocar(som_dano)
                # Sem isto perdias as 3 vidas de uma vez: no ciclo seguinte
                # continuavas sobreposto ao mesmo bicho.
                jogador.x = LARGURA // 2
                jogador.y = ALTURA // 2

        if vidas <= 0:
            estado = "fim"

    # ------------------------ 3. DESENHAR -------------------------
    ecra.fill(PRETO)
    if estado == "menu":
        mostrar_texto("SOBREVIVE", 240, 200, AMARELO, fonte_grande)
        mostrar_texto("Espaco para comecar", 270, 330, BRANCO, fonte)
    if estado == "jogo":
        for bicho in bichos:
            ecra.blit(imagem_bicho, bicho)
        ecra.blit(imagem_jogador, jogador)
        mostrar_texto("Pontos: " + str(pontuacao), 20, 20, BRANCO, fonte)
        mostrar_texto("Vidas: " + str(vidas), 640, 20, VERMELHO, fonte)
    if estado == "fim":
        mostrar_texto("FIM", 330, 200, AMARELO, fonte_grande)
        mostrar_texto("Pontos: " + str(pontuacao), 320, 300, BRANCO, fonte)
        mostrar_texto("R para jogar outra vez", 250, 340, BRANCO, fonte)

    # ------------------------- 4. MOSTRAR -------------------------
    pygame.display.flip()

    # ------------------------- 5. ESPERAR -------------------------
    clock.tick(FPS)

pygame.quit()
