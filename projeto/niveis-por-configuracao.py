# =====================================================================
# NIVEIS POR CONFIGURACAO — sessao 13
#
# A ideia grande: DADOS contra LOGICA.
#
# Os niveis nao sao codigo. Sao uma LISTA de configuracoes, e ha um so
# bloco de codigo que sabe ler qualquer uma delas. Para acrescentar um
# nivel novo escreve-se mais uma linha na lista — e mais nada.
#
# Compara com a alternativa: um if para o nivel 1, outro para o 2, outro
# para o 3... Com cinco niveis ficam duzentas linhas quase iguais, e uma
# correcao tem de ser feita cinco vezes.
# =====================================================================

import random

import pygame

LARGURA = 800
ALTURA = 600
FPS = 60
FUNDO = (18, 18, 28)
BRANCO = (240, 240, 240)
COR_JOGADOR = (70, 130, 230)
COR_MOEDA = (240, 200, 70)
TAMANHO = 48
MOEDA = 28

# ------------------------- OS NIVEIS -------------------------
# Um dicionario e uma lista de pares nome: valor. Le-se "o nome desta
# coisa e X". Aqui cada dicionario descreve um nivel inteiro.
#
# Para acrescentar o nivel 5, escreve mais uma linha. Nao mexes em mais
# nada no ficheiro inteiro. E esse o objetivo.
NIVEIS = [
    {"nome": "Aquecimento", "moedas": 3, "velocidade": 7, "cor": (40, 60, 40)},
    {"nome": "A serio", "moedas": 6, "velocidade": 6, "cor": (60, 40, 70)},
    {"nome": "Depressa", "moedas": 9, "velocidade": 5, "cor": (70, 45, 30)},
    {"nome": "Ultimo", "moedas": 12, "velocidade": 4, "cor": (80, 30, 30)},
]

pygame.init()
ecra = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Niveis por configuracao")
clock = pygame.time.Clock()
fonte = pygame.font.SysFont(None, 36)
fonte_grande = pygame.font.SysFont(None, 72)

numero_do_nivel = 0
jogador = pygame.Rect(0, 0, TAMANHO, TAMANHO)
moedas = []
nivel = NIVEIS[0]


# UM SO bloco de codigo, que sabe montar QUALQUER nivel da lista.
def montar_nivel(indice):
    global jogador, moedas, nivel
    nivel = NIVEIS[indice]
    jogador = pygame.Rect(LARGURA // 2, ALTURA // 2, TAMANHO, TAMANHO)
    moedas = []
    while len(moedas) < nivel["moedas"]:
        x = random.randint(0, LARGURA - MOEDA)
        y = random.randint(0, ALTURA - MOEDA)
        moedas.append(pygame.Rect(x, y, MOEDA, MOEDA))


montar_nivel(0)
acabou = False

a_correr = True
while a_correr:

    # ------------------------- 1. EVENTOS -------------------------
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            a_correr = False

    teclas = pygame.key.get_pressed()

    # ------------------------- 2. LOGICA --------------------------
    if acabou == False:
        # A velocidade nao esta escrita aqui: vem do nivel.
        if teclas[pygame.K_LEFT]:
            jogador.x = jogador.x - nivel["velocidade"]
        if teclas[pygame.K_RIGHT]:
            jogador.x = jogador.x + nivel["velocidade"]
        if teclas[pygame.K_UP]:
            jogador.y = jogador.y - nivel["velocidade"]
        if teclas[pygame.K_DOWN]:
            jogador.y = jogador.y + nivel["velocidade"]
        jogador.clamp_ip(ecra.get_rect())

        sobreviventes = []
        for moeda in moedas:
            if jogador.colliderect(moeda) == False:
                sobreviventes.append(moeda)
        moedas = sobreviventes

        if len(moedas) == 0:
            numero_do_nivel = numero_do_nivel + 1
            if numero_do_nivel < len(NIVEIS):
                montar_nivel(numero_do_nivel)
            else:
                acabou = True

    # ------------------------ 3. DESENHAR -------------------------
    # Ate a cor do fundo vem do nivel.
    ecra.fill(nivel["cor"])
    if acabou == True:
        ecra.blit(fonte_grande.render("ACABASTE TUDO", True, BRANCO), (140, 250))
    else:
        for moeda in moedas:
            pygame.draw.rect(ecra, COR_MOEDA, moeda)
        pygame.draw.rect(ecra, COR_JOGADOR, jogador)
        texto = "Nivel " + str(numero_do_nivel + 1) + ": " + nivel["nome"]
        ecra.blit(fonte.render(texto, True, BRANCO), (20, 20))
        faltam = "Faltam " + str(len(moedas))
        ecra.blit(fonte.render(faltam, True, BRANCO), (620, 20))

    # ------------------------- 4. MOSTRAR -------------------------
    pygame.display.flip()

    # ------------------------- 5. ESPERAR -------------------------
    clock.tick(FPS)

pygame.quit()
