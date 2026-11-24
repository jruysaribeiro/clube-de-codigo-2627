# S15 — BICHARADA A SOLTA
# Batalhas por turnos, a moda do Pokemon, com bichos muito portugueses e um
# mundo por onde se anda. O mundo e feito de zonas,
# cada uma do tamanho do ecra: quando sais por um lado de uma, entras na do
# lado. Ha edificios onde se entra pela porta. Na erva alta saltam bichos a
# solta, os treinadores estao espalhados pelas zonas, e a casa da avo cura a
# equipa.
#
# ESTE FICHEIRO E UMA BASE, NAO UM JOGO ACABADO.
# As zonas, os tipos, os ataques, os bichos e os treinadores sao todos DADOS,
# aqui em cima. Para mudares uma zona mudas letras em ZONAS; para inventares
# um bicho novo escreves mais um dicionario em BICHOS. O resto do ficheiro
# sabe ler o que la puseres.
#
#   Setas            andar pelo mapa, e mexer nos menus
#   Enter / Espaco   escolher, e passar o texto a frente
#   Esc / Backspace  voltar atras, e sair da loja
#
# Comecas sem bichos e sem redes. Fala com o Mestre Zacarias (anda contra
# ele): da-te uma rede. Com ela vais a erva alta apanhar o teu primeiro bicho.
# Quando voltares, ele faz-te uma luta de treino. So com um bicho e que os
# treinadores aceitam lutar. Todos tem coisas para dizer, e alguns fazem
# perguntas.
#
# Para desafiares um treinador, anda contra ele. Para descansares, anda
# contra a casa da avo. Para comprares sopas e redes, anda contra o balcao da
# mercearia. Com uma rede apanhas um bicho a solta, e ele fica na tua equipa.
#
# Zero assets: os bichos sao formas com olhos. Se puseres um PNG com o nome
# que esta em "imagem" na pasta comum/assets/imagens/, aparece a imagem.
# Com os sons e igual: um WAV com o nome que esta em "som", na pasta
# comum/assets/sons/, passa a ouvir-se.

import math
import random
from pathlib import Path

import pygame

# --- Constantes: e aqui que se mexe primeiro ---
LARGURA = 800
ALTURA = 600
FPS = 60

NIVEL_INICIAL = 5        # o nivel do primeiro bicho que apanhas
SOPAS_NA_MOCHILA = 3     # a sopa da avo cura metade da vida. A avo enche-te a mochila
EQUIPA_MAXIMA = 6        # quantos bichos cabem na equipa, com os que apanhares
REDES_INICIAIS = 0       # as redes com que comecas: cada uma e uma tentativa de apanhar
MOEDAS_INICIAIS = 30     # as moedas com que comecas. Ganham-se mais nas batalhas
QUADRADO = 40            # o tamanho de um quadrado do mapa, em pixeis
ZONA_COLUNAS = 20        # quantos quadrados cabem no ecra, de lado a lado
ZONA_LINHAS = 14         # e de cima a baixo
SORTE_NA_ERVA = 15       # em cada 100 passos na erva alta, em quantos salta um bicho

RELVA = (120, 190, 100)
ERVA_ALTA = (60, 140, 70)
AGUA = (70, 140, 230)
TRONCO = (110, 75, 45)
COPA = (40, 110, 60)
PAREDE = (235, 220, 190)
TELHADO = (200, 80, 60)
SOALHO = (200, 165, 115)

PRETO = (18, 18, 28)
BRANCO = (240, 240, 240)
CINZA = (130, 130, 145)
AMARELO = (240, 200, 70)
VERDE = (80, 200, 100)
VERMELHO = (220, 70, 60)
PAINEL = (30, 30, 48)

PASTA_ASSETS = Path(__file__).parent.parent / "comum" / "assets"


# =====================================================================
#                              OS DADOS
# =====================================================================

# --- As zonas ---
# O mundo e feito de zonas. Cada zona enche o ecra: 20 letras em cada linha,
# e 14 linhas. Cada letra e um quadrado. CA FORA, as letras sao estas:
#   .   relva: anda-se a vontade
#   e   erva alta: anda-se, e de vez em quando salta de la um bicho a solta
#   A   arvore: nao se passa
#   ~   agua: nao se passa
#   #   parede: nao se passa. Com ela se fazem as casas, vistas de fora
#   H   uma casa da avo: anda contra ela para curar a equipa e encher as sopas
#   P   a partida: onde comecas (so um, no mundo todo)
#   1 a 9   um treinador: o 1 e o primeiro da lista TREINADORES, o 2 e o
#           segundo, e por ai fora. Anda contra ele para o desafiares.
#   M, ou outra letra que esteja em PORTAS: uma porta (ve mais abaixo)
# Uma letra que o jogo nao conheca fica relva.
# AS SAIDAS: para se passar de uma zona para a do lado, tem de haver relva
# (ou erva) na borda das duas, no mesmo sitio. Aqui as saidas para os lados
# estao nas linhas 7 e 8 (a contar de cima), e as de cima e de baixo nas duas
# colunas do meio.

# --- Os interiores ---
# O interior de um edificio tambem e uma zona, com 20 letras em cada linha e
# 14 linhas. LA DENTRO as letras sao outras:
#   _   soalho: o chao. Anda-se a vontade
#   t   tapete: anda-se por cima
#   #   parede: nao se passa
#   j   janela: uma parede com vidro. Nao se passa
#   m   mesa: nao se passa
#   b   banco: nao se passa
#   l   estante com livros: nao se passa
#   c   cama: nao se passa
#   v   vaso com uma planta: nao se passa
#   $   o balcao de uma loja: anda contra ele para comprares (ve a LOJA)
#       (um espaco) nada: fica preto, e nao se passa. E o que ha a volta da sala
#   1 a 9   um treinador: anda contra ele para falares com ele
#   M, ou outra letra que esteja em PORTAS: a porta por onde se sai
# Para uma coisa nova (um piano, uma lareira) escolhe uma letra que ainda nao
# uses: desenha-a em desenhar_quadrado e, se nao for para passar por cima,
# junta-a ao pode_andar.
ZONAS = {
    "serra": [
        "AAAAAAAAAAAAAAAAAAAA",
        "A...AA.......eeee..A",
        "A...AA.......eeee..A",
        "A............eeee..A",
        "A..eee....AA.......A",
        "A..eee....AA.......A",
        "A..eee..............",
        "A...................",
        "A......AAA.........A",
        "A......AAA....~~...A",
        "A.............~~...A",
        "A..AA..............A",
        "A..AA..............A",
        "AAAAAAAAA..AAAAAAAAA",
    ],
    "montado": [
        "AAAAAAAAAAAAAAAAAAAA",
        "A..A....A.....A....A",
        "A.......eee........A",
        "A..A....eee...A.H..A",
        "A.......eee........A",
        "A....A.......A.....A",
        ".................4..",
        "....................",
        "A....A.......A.....A",
        "A..eee.............A",
        "A..eee....A....A...A",
        "A..eee.............A",
        "A.......A.....A....A",
        "AAAAAAAAA..AAAAAAAAA",
    ],
    "feira": [
        "AAAAAAAAAAAAAAAAAAAA",
        "A..................A",
        "A...AA......AA.....A",
        "A...AA......AA.....A",
        "A..................A",
        "A..................A",
        "..............5....A",
        "...................A",
        "A..................A",
        "A...AA......AA.....A",
        "A...AA......AA.....A",
        "A..................A",
        "A..................A",
        "AAAAAAAAAAAAAAAAAAAA",
    ],
    "aldeia": [
        "AAAAAAAAA..AAAAAAAAA",
        "A..................A",
        "A..H....###........A",
        "A..P.1..#M#..eee...A",
        "A............eee...A",
        "A............eee...A",
        "A...................",
        "A...................",
        "A..AAA.............A",
        "A..A~A.......AA....A",
        "A..AAA.......AA....A",
        "A..................A",
        "A..................A",
        "AAAAAAAAA..AAAAAAAAA",
    ],
    "ribeira": [
        "AAAAAAAAA..AAAAAAAAA",
        "A............~~....A",
        "A..eee.......~~....A",
        "A..eee.......~~....A",
        "A..eee........~~...A",
        "A.............~~...A",
        "....................",
        "....................",
        "A.............~~...A",
        "A....AA.......~~...A",
        "A....AA......~~....A",
        "A............~~.eeeA",
        "A............~~.eeeA",
        "AAAAAAAAA..AAAAAAAAA",
    ],
    "pinhal": [
        "AAAAAAAAAAAAAAAAAAAA",
        "A.A...A....A...A...A",
        "A....eeee......eee.A",
        "A.A..eeee..A...eee.A",
        "A....eeee......eee.A",
        "A.......A....A.....A",
        "....................",
        "....................",
        "A..A.......A.......A",
        "A.....eeee.....A...A",
        "A..A..eeee.........A",
        "A.....eeee...A.....A",
        "A..A...............A",
        "AAAAAAAAA..AAAAAAAAA",
    ],
    "horta": [
        "AAAAAAAAA..AAAAAAAAA",
        "A..................A",
        "A..eeee....eeee....A",
        "A..eeee....eeee....A",
        "A..................A",
        "A..................A",
        "A...................",
        "A...................",
        "A..................A",
        "A..eeee....AAA.....A",
        "A..eeee....A~A.....A",
        "A..........AAA.....A",
        "A..................A",
        "AAAAAAAAAAAAAAAAAAAA",
    ],
    "praia": [
        "AAAAAAAAA..AAAAAAAAA",
        "A..................A",
        "A..H...............A",
        "A............eee...A",
        "A............eee...A",
        "A..................A",
        "....................",
        ".........3..........",
        "A..................A",
        "A....~~~......~~~..A",
        "A..~~~~~~~..~~~~~~~A",
        "A~~~~~~~~~~~~~~~~~~A",
        "~~~~~~~~~~~~~~~~~~~~",
        "~~~~~~~~~~~~~~~~~~~~",
    ],
    "farol": [
        "AAAAAAAAA..AAAAAAAAA",
        "A..................A",
        "A......eeee........A",
        "A......eeee....AA..A",
        "A......eeee....AA..A",
        "A..................A",
        "..................~~",
        ".................~~~",
        "A...............~~~~",
        "A..~~.........~~~~~~",
        "A~~~~~~.....~~~~~~~~",
        "~~~~~~~~~~~~~~~~~~~~",
        "~~~~~~~~~~~~~~~~~~~~",
        "~~~~~~~~~~~~~~~~~~~~",
    ],
    "mercearia": [
        "                    ",
        "                    ",
        "                    ",
        "     ##j####j##     ",
        "     #lll___vl#     ",
        "     #___2____#     ",
        "     #_##$#___#     ",
        "     #________#     ",
        "     #_m____b_#     ",
        "     #___tt___#     ",
        "     ####M#####     ",
        "                    ",
        "                    ",
        "                    ",
    ],
}

# --- O mundo ---
# Como as zonas se juntam: cada linha daqui e uma fila de zonas, da esquerda
# para a direita, e as filas vao de cima para baixo. Quem sai pela direita
# da "aldeia" entra na "ribeira"; quem sai por baixo entra na "horta".
# Onde nao houver zona (ou com "" no lugar dela) nao se passa.
# Uma zona que nao esteja aqui e o interior de um edificio: so se la chega
# por uma porta.
MUNDO = [
    ["serra", "montado", "feira"],
    ["aldeia", "ribeira", "pinhal"],
    ["horta", "praia", "farol"],
]

# --- As portas ---
# Cada porta e uma letra, e leva ao interior de um edificio, que e uma zona
# como as outras. Le-se: "a letra M e a porta da mercearia".
# A mesma letra escreve-se em dois sitios: ca fora, na parede do edificio, e
# la dentro, na parede do interior. Quem pisa uma, aparece ao lado da outra.
# Para fazeres um edificio novo: uma zona nova em ZONAS (o interior), uma
# linha aqui com uma letra que ainda nao uses, e essa letra nos dois sitios.
PORTAS = {
    "M": "mercearia",
}

# --- A loja ---
# O que se vende ao balcao (a letra $ no mapa), e por quantas moedas. O que
# cada coisa FAZ quando a compras esta na funcao receber_compra, mais abaixo:
# para venderes uma coisa nova, uma linha aqui e um "elif" la.
LOJA = {
    "Sopa": {"preco": 15},
    "Rede": {"preco": 25},
}

# --- Os tipos ---
# Cada tipo tem uma cor, que aparece nos menus e nos bichos.
CORES_TIPO = {
    "normal": (170, 165, 150),
    "fogo": (235, 110, 50),
    "agua": (70, 140, 230),
    "planta": (90, 180, 80),
}

# O tipo que todos podem aprender: um bicho so sabe ataques do tipo dele e
# deste. (E a Oficina que o verifica, quando mudas um bicho ou um ataque.)
TIPO_NORMAL = "normal"

# Le-se: "um ataque de FOGO contra um bicho de PLANTA faz o dobro".
# O que nao estiver aqui faz o normal (1.0). Para acrescentar um tipo novo
# (eletrico? pedra? fantasma?) poe-lhe uma cor em CORES_TIPO e uma linha
# aqui a dizer contra quem e forte e contra quem e fraco.
EFICACIA = {
    "fogo": {"planta": 2.0, "agua": 0.5, "fogo": 0.5},
    "agua": {"fogo": 2.0, "planta": 0.5, "agua": 0.5},
    "planta": {"agua": 2.0, "fogo": 0.5, "planta": 0.5},
}

# --- Os ataques ---
# poder:    quanto magoa (0 nos ataques que nao fazem dano)
# precisao: de 0 a 100, a probabilidade de acertar
# efeito:   "dano", "cura", "sobe_ataque", "sobe_defesa",
#           "baixa_ataque" ou "baixa_defesa"
# som:      (so se quiseres) o nome de um WAV, assim: "som": "bicada.wav".
#           Se ele existir em comum/assets/sons/, ouve-se quando o ataque
#           e usado.
ATAQUES = {
    "Investida": {"tipo": "normal", "poder": 40, "precisao": 100, "efeito": "dano"},
    "Arranhão": {"tipo": "normal", "poder": 40, "precisao": 100, "efeito": "dano"},
    "Bicada": {"tipo": "normal", "poder": 35, "precisao": 100, "efeito": "dano"},
    "Patada": {"tipo": "normal", "poder": 50, "precisao": 95, "efeito": "dano"},
    "Salto Felino": {"tipo": "normal", "poder": 65, "precisao": 85, "efeito": "dano"},
    "Rugido": {"tipo": "normal", "poder": 0, "precisao": 100, "efeito": "baixa_ataque"},
    "Cocoricó": {"tipo": "normal", "poder": 0, "precisao": 100, "efeito": "sobe_ataque"},
    "Casca Dura": {"tipo": "normal", "poder": 0, "precisao": 100, "efeito": "sobe_defesa"},
    "Escamas": {"tipo": "normal", "poder": 0, "precisao": 100, "efeito": "sobe_defesa"},
    "Crista em Brasa": {"tipo": "fogo", "poder": 55, "precisao": 95, "efeito": "dano"},
    "Fumarada": {"tipo": "fogo", "poder": 45, "precisao": 100, "efeito": "dano"},
    "Estalido": {"tipo": "fogo", "poder": 75, "precisao": 80, "efeito": "dano"},
    "Esguicho": {"tipo": "agua", "poder": 40, "precisao": 100, "efeito": "dano"},
    "Tentáculo": {"tipo": "agua", "poder": 55, "precisao": 95, "efeito": "dano"},
    "Onda da Nazaré": {"tipo": "agua", "poder": 85, "precisao": 70, "efeito": "dano"},
    "Tinta de Choco": {"tipo": "agua", "poder": 0, "precisao": 100, "efeito": "baixa_defesa"},
    "Chicote de Cortiça": {"tipo": "planta", "poder": 45, "precisao": 100, "efeito": "dano"},
    "Folha de Couve": {"tipo": "planta", "poder": 55, "precisao": 95, "efeito": "dano"},
    "Bolotada": {"tipo": "planta", "poder": 70, "precisao": 85, "efeito": "dano"},
    "Seiva": {"tipo": "planta", "poder": 0, "precisao": 100, "efeito": "cura"},
}

# --- Os bichos ---
# Os numeros sao os valores BASE, ao nivel 1. Cada nivel acima soma 10%.
# ataques:  os que o bicho sabe desde o inicio (pelo menos um). Um bicho so
#           sabe ataques do tipo dele ou do tipo "normal": um bicho de fogo
#           nao aprende ataques de agua
# aprende:  (so se quiseres) os que passa a saber quando chega a um nivel:
#           {"Estalido": 9} quer dizer "aprende o Estalido ao nivel 9". Um
#           bicho que ja aparece com esse nivel ja o sabe. No menu da batalha
#           cabem 4: se souber mais, ficam os 4 ultimos que aprendeu.
# forma: "circulo", "quadrado", "triangulo" ou "gota"
# imagem:         o nome de um PNG com o bicho visto de frente: e como se ve
#                 quando e o adversario, e nos menus
# imagem_costas:  o bicho visto de costas: e como se ve o TEU, na batalha
#                 (Se o PNG existir em comum/assets/imagens/, aparece a imagem;
#                 se nao, o bicho e desenhado com a forma e a cor dele.)
# som:   o nome de um WAV. Se ele existir em comum/assets/sons/, ouve-se
#        quando o bicho entra em campo.
# Para inventares um bicho: copia um destes, muda-lhe o nome e os numeros.
# Regra de equilibrio: vida + ataque + defesa + velocidade da a volta de 85.
BICHOS = {
    "Galo de Barcelos": {
        "tipo": "fogo", "vida": 45, "ataque": 15, "defesa": 10, "velocidade": 14,
        "ataques": ["Bicada", "Cocoricó"],
        "aprende": {"Crista em Brasa": 6, "Estalido": 9},
        "cor": (200, 45, 45), "forma": "triangulo", "imagem": "galo.png", "imagem_costas": "galo-costas.png",
        "som": "galo.wav",
    },
    "Castanha Assada": {
        "tipo": "fogo", "vida": 55, "ataque": 12, "defesa": 13, "velocidade": 7,
        "ataques": ["Investida", "Casca Dura"],
        "aprende": {"Fumarada": 4, "Estalido": 8},
        "cor": (130, 70, 35), "forma": "gota", "imagem": "castanha.png", "imagem_costas": "castanha-costas.png",
        "som": "castanha.wav",
    },
    "Sardinhão": {
        "tipo": "agua", "vida": 48, "ataque": 13, "defesa": 10, "velocidade": 15,
        "ataques": ["Investida", "Escamas"],
        "aprende": {"Esguicho": 4, "Onda da Nazaré": 8},
        "cor": (120, 160, 200), "forma": "gota", "imagem": "sardinhao.png", "imagem_costas": "sardinhao-costas.png",
        "som": "sardinhao.wav",
    },
    "Polvo Lagareiro": {
        "tipo": "agua", "vida": 60, "ataque": 11, "defesa": 13, "velocidade": 6,
        "ataques": ["Patada", "Tinta de Choco"],
        "aprende": {"Esguicho": 4, "Tentáculo": 7},
        "cor": (170, 80, 150), "forma": "circulo", "imagem": "polvo.png", "imagem_costas": "polvo-costas.png",
        "som": "polvo.wav",
    },
    "Sobreirinho": {
        "tipo": "planta", "vida": 58, "ataque": 11, "defesa": 15, "velocidade": 5,
        "ataques": ["Chicote de Cortiça", "Casca Dura"],
        "aprende": {"Seiva": 5, "Bolotada": 8},
        "cor": (120, 100, 50), "forma": "quadrado", "imagem": "sobreirinho.png", "imagem_costas": "sobreirinho-costas.png",
        "som": "sobreirinho.wav",
    },
    "Couve Galega": {
        "tipo": "planta", "vida": 50, "ataque": 13, "defesa": 11, "velocidade": 11,
        "ataques": ["Investida", "Seiva"],
        "aprende": {"Folha de Couve": 4, "Bolotada": 8},
        "cor": (60, 150, 70), "forma": "circulo", "imagem": "couve.png", "imagem_costas": "couve-costas.png",
        "som": "couve.wav",
    },
    "Lince Ibérico": {
        "tipo": "normal", "vida": 46, "ataque": 15, "defesa": 9, "velocidade": 16,
        "ataques": ["Arranhão", "Rugido"],
        "aprende": {"Patada": 5, "Salto Felino": 8},
        "cor": (205, 155, 85), "forma": "quadrado", "imagem": "lince.png", "imagem_costas": "lince-costas.png",
        "som": "lince.wav",
    },
}

# --- Tu ---
# O teu boneco, no mapa. As tres imagens sao PNG em comum/assets/imagens/:
# quando existem, aparecem; quando nao, o boneco e desenhado com formas.
#   cor             a cor da camisola do boneco desenhado
#   imagem          de frente (quando andas para baixo)
#   imagem_costas   de costas (quando andas para cima)
#   imagem_lado     de lado, a olhar para a DIREITA (para a esquerda, o jogo
#                   vira-a ao contrario)
JOGADOR = {
    "cor": (240, 200, 70),
    "imagem": "jogador.png",
    "imagem_costas": "jogador-costas.png",
    "imagem_lado": "jogador-lado.png",
}

# --- Os treinadores ---
# Estao no mapa: o primeiro desta lista e o 1, o segundo e o 2... Para falares
# com um, anda contra ele: diz as falas dele e depois desafia-te. Podes
# desafia-los pela ordem que quiseres, mas os ultimos sao mais fortes.
# Ganhas a todos os que estao no mapa, ganhas a feira.
#   frase         o grito dele, quando a batalha comeca
#   cor_fundo     a cor do campo de batalha, e da camisola dele no mapa
#   equipa        os bichos que leva, pela ordem em que entram
#   falas         (so se quiseres) o que diz antes da luta: uma lista de
#                 textos, que passam com Enter
#   falas_depois  (so se quiseres) o que diz quando ja lhe ganhaste
#   da_rede       True se e ele que da a primeira rede. Enquanto nao tiveres
#                 nenhum bicho, em vez de lutar diz as falas_rede e da-te uma
#                 rede. Quando voltares com um bicho, luta como os outros.
#   falas_rede    o que diz quando da a rede
# UMA PERGUNTA: no meio das falas pode ir uma pergunta, com as respostas a
# escolha e o que ele diz a cada uma:
#   {"pergunta": "Queres lutar?",
#    "respostas": {"Sim": "Entao prepara-te!", "Nao": "Fica para a proxima."},
#    "sem_luta": "Nao"}
# "sem_luta" (so se quiseres) e a resposta que acaba a conversa sem batalha.
TREINADORES = [
    {
        "nome": "Mestre Zacarias",
        "da_rede": True,
        "falas_rede": [
            "Olá! Andas à procura de bichos?",
            "Eu já não tenho idade para andar pela erva alta.",
            "Toma esta rede. Apanha o teu primeiro bicho e volta cá!",
        ],
        "falas": [
            "Ah, já tens um bicho! Deixa ver o que ele vale.",
            "É só um treino, não te assustes.",
        ],
        "frase": "Devagar se vai ao longe!",
        "falas_depois": [
            "Muito bem! Estás pronto para a feira.",
            "Na mercearia vendem redes e sopas. E a avó cura os bichos.",
        ],
        "cor_fundo": (190, 170, 220),
        "equipa": [
            {"bicho": "Couve Galega", "nivel": 3},
        ],
    },
    {
        "nome": "Tia da Mercearia",
        "falas": [
            "Bom dia! As compras são ali ao balcão.",
            {"pergunta": "Ou vens para lutar comigo?",
             "respostas": {"Sim": "Então prepara-te!", "Agora não": "Faz bem. Compra uma sopa primeiro."},
             "sem_luta": "Agora não"},
        ],
        "frase": "Os meus bichos comem melhor do que tu!",
        "falas_depois": ["Ganhaste-me bem ganho. Leva cumprimentos à tua avó."],
        "cor_fundo": (150, 200, 230),
        "equipa": [
            {"bicho": "Couve Galega", "nivel": 3},
            {"bicho": "Castanha Assada", "nivel": 4},
        ],
    },
    {
        "nome": "Pescador da Póvoa",
        "falas": ["Chiu... espantas-me o peixe.", "Bom, já que aqui estás..."],
        "frase": "Cheira a maresia... e a vitória!",
        "falas_depois": ["O mar hoje não está para mim."],
        "cor_fundo": (110, 170, 210),
        "equipa": [
            {"bicho": "Sardinhão", "nivel": 5},
            {"bicho": "Polvo Lagareiro", "nivel": 6},
        ],
    },
    {
        "nome": "Guarda Florestal",
        "falas": ["Alto! Para a feira só passa quem me ganhar."],
        "frase": "Ninguém passa pelo meu montado.",
        "falas_depois": ["Podes passar. A feira é já ali."],
        "cor_fundo": (170, 200, 150),
        "equipa": [
            {"bicho": "Sobreirinho", "nivel": 6},
            {"bicho": "Lince Ibérico", "nivel": 6},
            {"bicho": "Couve Galega", "nivel": 7},
        ],
    },
    {
        "nome": "Campeã da Feira",
        "falas": [
            "Então és tu que andas a ganhar a toda a gente.",
            {"pergunta": "Tens a certeza de que queres lutar comigo?",
             "respostas": {"Tenho!": "Gosto de quem não tem medo.", "Ainda não": "Treina mais um bocado e volta."},
             "sem_luta": "Ainda não"},
        ],
        "frase": "Três anos invicta. Hoje não vai ser diferente.",
        "falas_depois": ["A feira tem uma campeã nova. Parabéns!"],
        "cor_fundo": (230, 170, 140),
        "equipa": [
            {"bicho": "Galo de Barcelos", "nivel": 7},
            {"bicho": "Sardinhão", "nivel": 8},
            {"bicho": "Sobreirinho", "nivel": 8},
        ],
    },
]

# Quando o adversario e um bicho a solta, e este o "treinador" dele: assim
# treinador()["nome"] funciona em todas as batalhas.
BICHO_A_SOLTA = {
    "nome": "Bicho à solta",
    "frase": "",
    "cor_fundo": (165, 210, 150),
    "equipa": [],
}


# =====================================================================
#                          PYGAME E UTILITARIOS
# =====================================================================

pygame.init()
ecra = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Bicharada à Solta")
clock = pygame.time.Clock()
fonte_pequena = pygame.font.SysFont(None, 24)
fonte = pygame.font.SysFont(None, 32)
fonte_grande = pygame.font.SysFont(None, 80)

# Guardamos aqui as imagens ja carregadas, para nao ler o disco 60 vezes
# por segundo. None quer dizer "procurei e nao ha".
imagens_carregadas = {}


def obter_imagem(nome_ficheiro, tamanho):
    chave = nome_ficheiro + str(tamanho)
    if chave not in imagens_carregadas:
        caminho = PASTA_ASSETS / "imagens" / nome_ficheiro
        if caminho.exists():
            imagem = pygame.image.load(caminho).convert_alpha()
            imagens_carregadas[chave] = pygame.transform.scale(imagem, (tamanho, tamanho))
        else:
            imagens_carregadas[chave] = None
    return imagens_carregadas[chave]


# Com os sons e igual: ficam aqui depois de lidos, e None quer dizer "nao ha".
sons_carregados = {}


def tocar_som(nome_ficheiro):
    # Toca o som com esse nome, se ele existir em comum/assets/sons/.
    if nome_ficheiro not in sons_carregados:
        caminho = PASTA_ASSETS / "sons" / nome_ficheiro
        som = None
        if caminho.is_file() and pygame.mixer.get_init():
            try:
                som = pygame.mixer.Sound(str(caminho))
            except pygame.error:
                som = None       # o ficheiro existe mas nao e um som que se perceba
        sons_carregados[nome_ficheiro] = som
    if sons_carregados[nome_ficheiro] is not None:
        sons_carregados[nome_ficheiro].play()


def som_do_bicho(bicho):
    # A "voz" do bicho: ouve-se quando ele entra em campo.
    dados = BICHOS[bicho["nome"]]
    if "som" in dados:
        tocar_som(dados["som"])


def mostrar_texto(texto, x, y, cor, letra):
    desenho = letra.render(texto, True, cor)
    ecra.blit(desenho, (x, y))


def escurecer(cor, quanto):
    return (int(cor[0] * quanto), int(cor[1] * quanto), int(cor[2] * quanto))


# =====================================================================
#                          AS REGRAS DO JOGO
# =====================================================================

# --- As regras do jogo ---
# Ha onze funcoes neste ficheiro que sao as REGRAS. Cinco sao da batalha:
# quanto magoa um ataque (calcular_dano), quando sai um golpe critico
# (golpe_critico), quanta experiencia e precisa para subir de nivel
# (xp_para_subir), quem ataca primeiro (quem_ataca_primeiro) e que ataque o
# inimigo escolhe (escolher_ataque_inimigo). Tres sao do mapa: onde se pode
# andar (pode_andar), quando salta um bicho da erva (ha_batalha_na_erva) e
# que bicho salta (escolher_bicho_selvagem). E tres sao das redes e das
# moedas: quando se consegue apanhar um bicho (consegue_apanhar), quantas
# moedas da uma batalha (premio_da_batalha) e o que se recebe ao comprar
# (receber_compra). Mudar uma delas muda a maneira como o jogo se comporta.
#
# Dentro delas podes usar tudo o que o jogo tem. Um bicho em batalha e um
# dicionario:
#   bicho["nome"], bicho["tipo"], bicho["nivel"], bicho["xp"]
#   bicho["vida"], bicho["vida_max"]    a vida que lhe resta, e a maxima
#   bicho["ataque"], bicho["defesa"], bicho["velocidade"]    ja com o nivel
#   bicho["mod_ataque"], bicho["mod_defesa"]    comecam em 1.0; o Cocorico,
#                                       o Rugido e outros fazem-nos mudar
# E ha mais:
#   minha_equipa[ativo_meu]             o teu bicho que esta em campo
#   equipa_inimiga[ativo_inimigo]       o bicho inimigo que esta em campo
#   BICHOS[bicho["nome"]]               a ficha dele, la em cima ("tipo"...)
#   ataques_de(bicho)                   os nomes dos ataques que ele sabe agora
#   ATAQUES[nome]                       a ficha de um ataque ("tipo", "poder",
#                                       "precisao", "efeito")
#   eficacia(tipo_do_ataque, tipo_do_alvo)    2.0, 0.5 ou 1.0, pela tabela EFICACIA
#   random.randint(1, 6)                um numero inteiro ao calhas, de 1 a 6
#   random.uniform(0.5, 1.5)            um numero com virgula ao calhas
#   dizer("ola")                        poe um texto no painel de baixo (na
#                                       batalha) ou numa caixa (no mapa)
# E do mapa:
#   jogador["zona"]                     o nome da zona onde estas ("aldeia",
#                                       "mercearia"...)
#   jogador["coluna"], jogador["linha"]    onde estas nessa zona (0, 0 e o
#                                       canto de cima, a esquerda, do ecra)
#   jogador["passos"]                   quantos passos ja deste
#   letra_do_mapa(coluna, linha)        a letra que esta nesse quadrado da
#                                       zona onde estas
#   ir_para(zona, coluna, linha)        poe-te noutro sitio, de repente
#   minha_equipa                        a lista dos teus bichos
#   batalha_selvagem                    True se a batalha e contra um bicho a
#                                       solta, False se e contra um treinador
#   treinadores_vencidos                a lista dos que ja venceste (0 e o
#                                       primeiro treinador, 1 o segundo...)
#   sopas, redes, moedas                o que levas na mochila
# Para mudar as sopas dentro de uma funcao, a primeira linha dela tem de ser
# "global sopas" (e o mesmo com as redes e as moedas: "global sopas, moedas").

def valor_no_nivel(base, nivel):
    # Cada nivel acima do 1 soma 10% do valor base.
    return int(base * (1 + (nivel - 1) * 0.1))


def calcular_valores(bicho):
    base = BICHOS[bicho["nome"]]
    bicho["vida_max"] = valor_no_nivel(base["vida"], bicho["nivel"]) + 10
    bicho["ataque"] = valor_no_nivel(base["ataque"], bicho["nivel"])
    bicho["defesa"] = valor_no_nivel(base["defesa"], bicho["nivel"])
    bicho["velocidade"] = valor_no_nivel(base["velocidade"], bicho["nivel"])


def criar_bicho(nome, nivel):
    # Os dados em BICHOS sao o "molde". Na batalha usamos uma copia, com a
    # vida que lhe resta, o nivel, a experiencia, etc.
    bicho = {
        "nome": nome,
        "tipo": BICHOS[nome]["tipo"],
        "nivel": nivel,
        "xp": 0,
        "mod_ataque": 1.0,
        "mod_defesa": 1.0,
        "anunciado": False,   # ja dissemos "desmaiou"?
        "tremor": 0,          # quantos frames ainda treme depois de levar
    }
    calcular_valores(bicho)
    bicho["vida"] = bicho["vida_max"]
    bicho["vida_mostrada"] = bicho["vida"]
    return bicho


def curar_tudo(equipa):
    for bicho in equipa:
        bicho["vida"] = bicho["vida_max"]
        bicho["mod_ataque"] = 1.0
        bicho["mod_defesa"] = 1.0
        bicho["anunciado"] = False


def ataques_de(bicho):
    # Os ataques que um bicho sabe AGORA, pela ordem em que aparecem no menu:
    # os de "ataques" e, dos de "aprende", aqueles para que ja tem nivel. No
    # menu cabem 4: se souber mais, ficam os 4 ultimos.
    dados = BICHOS[bicho["nome"]]
    sabe = list(dados["ataques"])
    if "aprende" in dados:
        for nome in dados["aprende"]:
            if bicho["nivel"] >= dados["aprende"][nome] and nome not in sabe:
                sabe.append(nome)
    return sabe[-4:]


def nivel_mais_alto(equipa):
    # O nivel do bicho mais forte de uma equipa.
    maior = 1
    for bicho in equipa:
        if bicho["nivel"] > maior:
            maior = bicho["nivel"]
    return maior


def eficacia(tipo_ataque, tipo_alvo):
    if tipo_ataque in EFICACIA:
        if tipo_alvo in EFICACIA[tipo_ataque]:
            return EFICACIA[tipo_ataque][tipo_alvo]
    return 1.0


# QUANTO MAGOA UM ATAQUE
# Recebe quem ataca, quem leva e o NOME do ataque. Devolve quanta vida o
# golpe tira (um numero inteiro). Como esta: o poder do ataque, vezes o
# ataque de um a dividir pela defesa do outro, e depois o nivel, o tipo e
# um bocadinho de sorte.
#   dados["poder"], dados["tipo"]    vem da ficha do ataque, em ATAQUES
# Ideias: um bicho com pouca vida bater mais forte (furia); tirar a sorte,
# para o mesmo ataque tirar sempre o mesmo; bater mais em bichos mais lentos.
def calcular_dano(atacante, alvo, ataque):
    dados = ATAQUES[ataque]
    ataque_real = atacante["ataque"] * atacante["mod_ataque"]
    defesa_real = alvo["defesa"] * alvo["mod_defesa"]
    dano = dados["poder"] * ataque_real / defesa_real * 0.35
    # Quem esta em nivel mais alto bate mais forte.
    dano = dano * (atacante["nivel"] + 5) / 10
    dano = dano * eficacia(dados["tipo"], alvo["tipo"])
    # Um bicho que usa um ataque do seu proprio tipo bate 25% mais.
    if dados["tipo"] == atacante["tipo"]:
        dano = dano * 1.25
    # Um bocadinho de sorte, para nenhuma batalha ser igual a outra.
    dano = dano * random.uniform(0.85, 1.0)
    return int(dano) + 1


# QUANDO SAI UM GOLPE CRITICO
# Corre cada vez que um ataque acerta. Recebe quem ataca e quem leva, e
# devolve True se o golpe for critico (tira mais metade do dano) ou False se
# nao for. Como esta: e sorte, 1 vez em cada 16.
# Ideias: sair mais vezes (1 em cada 4); os bichos mais rapidos do que o alvo
# terem mais sorte; critico garantido quando quem ataca tem pouca vida.
def golpe_critico(atacante, alvo):
    return random.randint(1, 16) == 1


def proximo_vivo(equipa):
    # Devolve a posicao do primeiro bicho com vida, ou -1 se nao houver.
    indice = 0
    while indice < len(equipa):
        if equipa[indice]["vida"] > 0:
            return indice
        indice = indice + 1
    return -1


# QUANTA EXPERIENCIA E PRECISA PARA SUBIR DE NIVEL
# Recebe um bicho e devolve quantos pontos de experiencia (XP) ele precisa
# de juntar para passar ao nivel seguinte. Como esta: 10 por cada nivel que
# ja tem (ao nivel 5 precisa de 50). Vencer um bicho da 12 de XP por cada
# nivel dele. Tem de devolver sempre mais que zero, senao o bicho nunca mais
# parava de subir.
# Ideias: subir mais depressa (5 por nivel); os primeiros niveis faceis e os
# ultimos dificeis; os bichos de planta crescerem mais depressa.
def xp_para_subir(bicho):
    return bicho["nivel"] * 10


# =====================================================================
#                          O ESTADO DO JOGO
# =====================================================================

estado = "menu"          # menu, mundo, conversa, loja, encontro, batalha, vitoria, derrota
fase = "texto"           # dentro da batalha: texto, menu, ataques, equipa
cursor = 0               # qual opcao do menu esta escolhida

nomes_dos_bichos = list(BICHOS.keys())

minha_equipa = []
equipa_inimiga = []
ativo_meu = 0
ativo_inimigo = 0
indice_treinador = 0
sopas = SOPAS_NA_MOCHILA
redes = REDES_INICIAIS
moedas = MOEDAS_INICIAIS
cursor_loja = 0          # qual coisa da loja esta escolhida
troca_obrigatoria = False

# No mapa: onde estas, para onde olhas e quantos passos ja deste.
jogador = {"zona": "", "coluna": 1, "linha": 1, "olha": "baixo", "passos": 0}
# Onde acordas se a equipa toda desmaiar: o ultimo sitio onde descansaste.
descanso = {"zona": "", "coluna": 1, "linha": 1}
# Por que porta entraste em cada edificio, para saires pela mesma:
# entradas["M"] = ("aldeia", 9, 3)
entradas = {}
redes_dadas = []             # os treinadores que ja te deram a rede deles (0 e o primeiro...)
# A conversa que esta a decorrer: o que ainda falta dizer (textos, e
# perguntas), quem fala, e o que acontece quando acabar ("luta", "rede" ou "").
conversa = []
quem_fala = ""
depois_da_conversa = ""
treinadores_vencidos = []    # 0 e o primeiro treinador, 1 o segundo...
por_vencer = 0               # quantos treinadores do mundo ainda faltam
batalha_selvagem = False     # a batalha e contra um bicho a solta?
bicho_a_solta = None         # o bicho que saltou da erva
a_fugir = False
aviso = ""                   # o texto da caixa que aparece no mapa
espera_do_passo = 0          # frames ate ao proximo passo com a seta carregada

# Os textos que aparecem no painel de baixo, um de cada vez.
mensagens = []
# As acoes que ainda faltam neste turno, pela ordem em que acontecem.
# Cada acao e um dicionario, por exemplo:
#   {"quem": "jogador", "tipo": "atacar", "ataque": "Bicada"}
fila_acoes = []

OPCOES_MENU = ["Lutar", "Equipa", "Sopa", "Apanhar", "Fugir"]


def opcoes_do_menu():
    # O que se pode escolher no menu da batalha. Contra um treinador nao ha
    # "Apanhar": os bichos dele nao se apanham.
    opcoes = []
    for opcao in OPCOES_MENU:
        if opcao == "Apanhar" and not batalha_selvagem:
            continue
        opcoes.append(opcao)
    return opcoes


def dizer(texto):
    # Numa batalha: poe um texto no painel de baixo, a seguir aos que la
    # estiverem, e o jogador passa-o com Enter. No mapa: mostra o texto numa
    # caixa, ate ao passo seguinte.
    global fase, aviso
    if estado == "batalha":
        mensagens.append(texto)
        fase = "texto"
    else:
        aviso = texto


def treinador():
    # Contra quem e a batalha.
    if batalha_selvagem:
        return BICHO_A_SOLTA
    return TREINADORES[indice_treinador]


def comecar_jogo():
    # Do principio: sem bichos, e tudo o resto como no inicio.
    global minha_equipa
    minha_equipa = []
    memoria.clear()
    comecar_mundo()


def comecar_batalha():
    # Contra o treinador que esta em indice_treinador ou, se batalha_selvagem
    # for True, contra o bicho_a_solta.
    global estado, fase, equipa_inimiga, ativo_meu, ativo_inimigo
    global mensagens, fila_acoes, troca_obrigatoria, a_fugir
    estado = "batalha"
    equipa_inimiga = []
    if batalha_selvagem:
        equipa_inimiga.append(bicho_a_solta)
    else:
        for membro in treinador()["equipa"]:
            equipa_inimiga.append(criar_bicho(membro["bicho"], membro["nivel"]))
    # A vida fica como estava: so a casa da avo cura. O ataque e a defesa,
    # que alguns ataques fazem subir e descer, voltam ao normal.
    for bicho in minha_equipa:
        bicho["mod_ataque"] = 1.0
        bicho["mod_defesa"] = 1.0
    ativo_meu = max(0, proximo_vivo(minha_equipa))
    ativo_inimigo = 0
    troca_obrigatoria = False
    a_fugir = False
    fila_acoes = []
    eu = minha_equipa[ativo_meu]
    if batalha_selvagem:
        mensagens = [
            "Salta da erva um " + equipa_inimiga[0]["nome"] + " à solta!",
            "Vai, " + eu["nome"] + "!",
        ]
    else:
        mensagens = [
            treinador()["nome"] + " desafia-te!",
            "«" + treinador()["frase"] + "»",
            treinador()["nome"] + " manda " + equipa_inimiga[0]["nome"] + "!",
            "Vai, " + eu["nome"] + "!",
        ]
    fase = "texto"
    som_do_bicho(equipa_inimiga[0])
    som_do_bicho(eu)
    ao_comecar_batalha()


def voltar_ao_mundo():
    # Acaba a batalha, de qualquer maneira, e volta ao mapa.
    global estado, batalha_selvagem, a_fugir
    estado = "mundo"
    batalha_selvagem = False
    a_fugir = False


def ganhar_batalha():
    global estado, por_vencer
    era_selvagem = batalha_selvagem
    nome = treinador()["nome"]
    voltar_ao_mundo()
    if era_selvagem:
        return
    if indice_treinador not in treinadores_vencidos:
        treinadores_vencidos.append(indice_treinador)
    # (Conta-se so aqui e ao comecar, e nao a cada frame: e preciso
    # percorrer o mundo todo.)
    por_vencer = treinadores_por_vencer()
    faltam = por_vencer
    if faltam == 0:
        estado = "vitoria"
    elif faltam == 1:
        dizer("Ganhaste a " + nome + "! Só falta um treinador.")
    else:
        dizer("Ganhaste a " + nome + "! Faltam " + str(faltam) + " treinadores.")


def acordar_em_casa():
    # A equipa toda desmaiou: acordas onde descansaste pela ultima vez, com
    # os bichos curados. Os treinadores que ja venceste continuam vencidos.
    global sopas
    voltar_ao_mundo()
    curar_tudo(minha_equipa)
    sopas = SOPAS_NA_MOCHILA
    ir_para(descanso["zona"], descanso["coluna"], descanso["linha"])
    jogador["olha"] = "baixo"
    dizer("A avó foi buscar-te. A equipa está curada: tenta outra vez!")


# =====================================================================
#                              O MAPA
# =====================================================================

def letra_da_zona(nome, coluna, linha):
    # A letra de um quadrado de uma zona. Fora da zona (ou se a zona nao
    # existir) e tudo arvores.
    if nome not in ZONAS:
        return "A"
    zona = ZONAS[nome]
    if linha < 0 or linha >= ZONA_LINHAS or linha >= len(zona):
        return "A"
    if coluna < 0 or coluna >= ZONA_COLUNAS or coluna >= len(zona[linha]):
        return "A"
    return zona[linha][coluna]


def letra_do_mapa(coluna, linha):
    # A letra de um quadrado da zona onde estas.
    return letra_da_zona(jogador["zona"], coluna, linha)


def zona_ao_lado(nome, passo_coluna, passo_linha):
    # O nome da zona que fica desse lado no MUNDO, ou "" se nao ha nenhuma.
    # zona_ao_lado("aldeia", 1, 0) e a que fica a direita da aldeia.
    for fila in range(len(MUNDO)):
        for lugar in range(len(MUNDO[fila])):
            if MUNDO[fila][lugar] == nome:
                fila = fila + passo_linha
                lugar = lugar + passo_coluna
                if fila < 0 or fila >= len(MUNDO) or lugar < 0 or lugar >= len(MUNDO[fila]):
                    return ""
                if MUNDO[fila][lugar] not in ZONAS:
                    return ""
                return MUNDO[fila][lugar]
    return ""


def quadrado_ao_lado(nome, coluna, linha, passo_coluna, passo_linha):
    # Para onde se vai com um passo: (zona, coluna, linha). Quem sai por um
    # lado do ecra entra na zona ao lado, pelo lado contrario. Se la nao
    # houver zona, a zona vem "".
    coluna = coluna + passo_coluna
    linha = linha + passo_linha
    if 0 <= coluna < ZONA_COLUNAS and 0 <= linha < ZONA_LINHAS:
        return nome, coluna, linha
    return zona_ao_lado(nome, passo_coluna, passo_linha), coluna % ZONA_COLUNAS, linha % ZONA_LINHAS


def encontrar_letra(letra, nomes):
    # Onde esta uma letra, procurando nas zonas com esses nomes: devolve
    # (zona, coluna, linha) do primeiro quadrado, ou ("", 0, 0) se nao ha.
    for nome in nomes:
        for linha in range(ZONA_LINHAS):
            for coluna in range(ZONA_COLUNAS):
                if letra_da_zona(nome, coluna, linha) == letra:
                    return nome, coluna, linha
    return "", 0, 0


def treinador_do_quadrado(letra):
    # Que treinador esta num quadrado: 0 para o "1", 1 para o "2"... ou -1
    # se a letra nao e de nenhum treinador que exista.
    if letra in "123456789" and int(letra) <= len(TREINADORES):
        return int(letra) - 1
    return -1


def encontrar_partida():
    # Onde esta o P: (zona, coluna, linha). Sem P, o primeiro bocado de relva.
    for procurada in ["P", "."]:
        zona, coluna, linha = encontrar_letra(procurada, list(ZONAS))
        if zona != "":
            return zona, coluna, linha
    return list(ZONAS)[0], 0, 0


def treinadores_por_vencer():
    # Quantos treinadores ainda nao venceste, em todas as zonas.
    faltam = []
    for nome in ZONAS:
        for linha in range(ZONA_LINHAS):
            for coluna in range(ZONA_COLUNAS):
                numero = treinador_do_quadrado(letra_da_zona(nome, coluna, linha))
                if numero != -1 and numero not in treinadores_vencidos and numero not in faltam:
                    faltam.append(numero)
    return len(faltam)


def ir_para(zona, coluna, linha):
    # Poe-te noutro sitio, de repente.
    jogador["zona"] = zona
    jogador["coluna"] = coluna
    jogador["linha"] = linha


def comecar_mundo():
    # Poe-te na partida, com a mochila do inicio e nenhum treinador vencido.
    global sopas, redes, moedas, por_vencer
    voltar_ao_mundo()
    zona, coluna, linha = encontrar_partida()
    ir_para(zona, coluna, linha)
    jogador["olha"] = "baixo"
    jogador["passos"] = 0
    descanso["zona"] = zona
    descanso["coluna"] = coluna
    descanso["linha"] = linha
    entradas.clear()
    redes_dadas.clear()
    treinadores_vencidos.clear()
    por_vencer = treinadores_por_vencer()
    sopas = SOPAS_NA_MOCHILA
    redes = REDES_INICIAIS
    moedas = MOEDAS_INICIAIS
    dizer("Anda com as setas. Para falares com alguém, vai contra essa pessoa.")


def chao_livre(letra):
    # Um quadrado onde se pode ficar parado: da para andar la, e nao e uma
    # porta, nem a casa da avo, nem um treinador.
    if letra in PORTAS or letra == "H" or letra == "$":
        return False
    if treinador_do_quadrado(letra) != -1:
        return False
    return pode_andar(letra)


def passar_a_porta(letra):
    # Pisaste uma porta: apareces ao lado da porta igual, do outro lado.
    # De fora vai-se para dentro; de dentro volta-se a porta por onde se
    # entrou (ou, se nao se entrou por nenhuma, a primeira que houver ca fora).
    dentro = PORTAS[letra]
    if jogador["zona"] != dentro:
        entradas[letra] = (jogador["zona"], jogador["coluna"], jogador["linha"])
        zona, coluna, linha = encontrar_letra(letra, [dentro])
    elif letra in entradas:
        zona, coluna, linha = entradas[letra]
    else:
        fora = []
        for nome in ZONAS:
            if nome != dentro:
                fora.append(nome)
        zona, coluna, linha = encontrar_letra(letra, fora)
    if zona == "":
        return       # a porta nao tem outro lado: fica-se onde se esta
    # Um passo para o lado, para nao ficares em cima da porta: primeiro
    # tenta-se para baixo, depois para cima, e depois para os lados.
    for passo in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        if chao_livre(letra_da_zona(zona, coluna + passo[0], linha + passo[1])):
            coluna = coluna + passo[0]
            linha = linha + passo[1]
            break
    ir_para(zona, coluna, linha)


# ONDE SE PODE ANDAR
# Recebe a letra de um quadrado do mapa e devolve True se da para andar para
# la, ou False se nao da. Como esta: nao se passa nas arvores (A), na agua
# (~), nas paredes (#), no nada (um espaco) nem, dentro dos edificios, nas
# janelas (j), mesas (m), bancos (b), estantes (l), camas (c) e vasos (v). (A casa da avo, o balcao da
# loja e os treinadores nao passam por aqui: contra eles vai-se sempre de
# encontro. E na erva alta so se entra com um bicho ou uma rede.)
# Ideias: nadar, isto e, passar na agua se levares na equipa um bicho do tipo
# "agua"; uma letra nova para uma cerca; uma ponte "=" por cima da agua.
def pode_andar(letra):
    if letra == "A" or letra == "~" or letra == "#" or letra == " ":
        return False
    if letra in "jmblcv":
        return False
    return True


# QUANDO SALTA UM BICHO DA ERVA
# Corre a cada passo que das na erva alta (a letra e). Devolve True se desse
# passo salta um bicho a solta, ou False se nao salta nada. Como esta: e
# sorte, SORTE_NA_ERVA vezes em cada 100.
# Ideias: saltar sempre; nunca saltar dois bichos seguidos (guarda na memoria
# o passo do ultimo); quanto mais passos ja deste, mais bichos saltam.
def ha_batalha_na_erva():
    return random.randint(1, 100) <= SORTE_NA_ERVA


# QUE BICHO SALTA DA ERVA
# Devolve o bicho a solta, feito com criar_bicho(nome, nivel). Como esta: um
# bicho qualquer de BICHOS, um a tres niveis abaixo do teu bicho mais forte.
# Enquanto nao tens nenhum, vem ao NIVEL_INICIAL: e o teu primeiro bicho.
# Ideias: so bichos de agua na praia (if jogador["zona"] == "praia"); bichos
# mais fortes na serra; um bicho raro, que so salta 1 vez em cada 20.
def escolher_bicho_selvagem():
    nome = random.choice(list(BICHOS.keys()))
    if len(minha_equipa) == 0:
        return criar_bicho(nome, NIVEL_INICIAL)
    nivel = nivel_mais_alto(minha_equipa) - random.randint(1, 3)
    if nivel < 1:
        nivel = 1
    return criar_bicho(nome, nivel)


# QUANDO SE CONSEGUE APANHAR UM BICHO
# Corre quando atiras uma rede a um bicho a solta. Recebe esse bicho e devolve
# True se ficou apanhado, ou False se se escapou (a rede gasta-se na mesma).
# Como esta: enquanto nao tens nenhum bicho, apanha-se sempre (nao tens com
# que lutar). Depois, um bicho com a vida toda escapa-se sempre: e preciso
# magoa-lo um bocadinho primeiro. Ja magoado e sorte, e quanto menos vida
# tiver, mais facil e: 40 em cada 100 mal lhe tocaste, quase 100 em cada 100
# quando esta quase a desmaiar.
# Ideias: apanhar sempre; so se apanha um bicho com menos de metade da vida;
# os bichos de nivel mais alto que os teus serem mais dificeis.
def consegue_apanhar(bicho):
    if len(minha_equipa) == 0:
        return True
    if bicho["vida"] == bicho["vida_max"]:
        return False
    falta = 1 - bicho["vida"] / bicho["vida_max"]
    return random.randint(1, 100) <= 40 + 60 * falta


# QUANTAS MOEDAS DA UMA BATALHA
# Corre quando ganhas uma batalha. Recebe a equipa que venceste (uma lista de
# bichos) e selvagem, que e True se era um bicho a solta. Devolve as moedas
# que ganhas. Como esta: um bicho a solta da 2 moedas por cada nivel dele; um
# treinador da 5 por cada nivel de cada bicho que levava.
# Ideias: os treinadores pagarem o dobro; nao ganhar nada com bichos a solta;
# um premio de sorte, entre 1 e 50.
def premio_da_batalha(equipa, selvagem):
    niveis = 0
    for bicho in equipa:
        niveis = niveis + bicho["nivel"]
    if selvagem:
        return niveis * 2
    return niveis * 5


# O QUE SE RECEBE AO COMPRAR
# Corre quando compras uma coisa na loja, ja com as moedas pagas. nome: o
# nome dela, como esta escrito na LOJA.
# Ideias: uma coisa nova. Poe "Pomada": {"preco": 40} na LOJA e aqui um
# elif nome == "Pomada": que cure a equipa toda (curar_tudo(minha_equipa));
# ou um "Bolo" que de 20 de experiencia ao teu primeiro bicho.
def receber_compra(nome):
    global sopas, redes
    if nome == "Sopa":
        sopas = sopas + 1
    elif nome == "Rede":
        redes = redes + 1


def abrir_loja():
    global estado, cursor_loja, aviso
    estado = "loja"
    cursor_loja = 0
    aviso = ""


def fechar_loja():
    global estado
    estado = "mundo"


def comprar(nome):
    # Paga e recebe, se as moedas chegarem. Diz como correu.
    global moedas
    preco = LOJA[nome]["preco"]
    if moedas < preco:
        return "Não tens moedas que cheguem para: " + nome
    moedas = moedas - preco
    receber_compra(nome)
    return "Compraste: " + nome


def tecla_na_loja(tecla):
    global cursor_loja, aviso
    nomes = list(LOJA.keys())
    if tecla == pygame.K_ESCAPE or tecla == pygame.K_BACKSPACE or len(nomes) == 0:
        fechar_loja()
        return
    if tecla == pygame.K_UP:
        cursor_loja = (cursor_loja - 1) % len(nomes)
    if tecla == pygame.K_DOWN:
        cursor_loja = (cursor_loja + 1) % len(nomes)
    if tecla == pygame.K_RETURN or tecla == pygame.K_SPACE:
        aviso = comprar(nomes[cursor_loja % len(nomes)])


def descansar():
    # Em casa da avo: cura a equipa, enche as sopas, e passa a ser aqui que
    # acordas se a equipa desmaiar.
    global sopas
    curar_tudo(minha_equipa)
    sopas = SOPAS_NA_MOCHILA
    descanso["zona"] = jogador["zona"]
    descanso["coluna"] = jogador["coluna"]
    descanso["linha"] = jogador["linha"]
    dizer("A avó deu sopa a todos. A equipa está curada!")
    ao_descansar()


def comecar_conversa(nome, falas, a_seguir):
    # Alguem fala contigo: as falas aparecem uma de cada vez, e passam com
    # Enter. a_seguir diz o que acontece no fim: "luta" (comeca a batalha
    # contra o treinador de indice_treinador), "rede" (recebes uma) ou "".
    global estado, conversa, quem_fala, depois_da_conversa, cursor, aviso
    conversa = list(falas)
    quem_fala = nome
    depois_da_conversa = a_seguir
    cursor = 0
    aviso = ""
    if len(conversa) == 0:
        acabar_conversa()
    else:
        estado = "conversa"


def acabar_conversa():
    global estado
    estado = "mundo"
    if depois_da_conversa == "luta":
        comecar_batalha()
    elif depois_da_conversa == "rede":
        receber_compra("Rede")
        dizer("Recebeste uma rede! Na erva alta, atira-a a um bicho à solta.")


def tecla_na_conversa(tecla):
    global cursor, depois_da_conversa
    if tecla == pygame.K_ESCAPE or tecla == pygame.K_BACKSPACE:
        # Virar costas a meio: a conversa acaba, sem luta e sem prendas.
        depois_da_conversa = ""
        conversa.clear()
        acabar_conversa()
        return
    confirmar = tecla == pygame.K_RETURN or tecla == pygame.K_SPACE
    fala = conversa[0]
    if isinstance(fala, str):
        if confirmar:
            conversa.pop(0)
            if len(conversa) == 0:
                acabar_conversa()
        return
    # E uma pergunta: as setas escolhem a resposta, Enter responde.
    respostas = list(fala["respostas"].keys())
    if tecla == pygame.K_UP:
        cursor = (cursor - 1) % len(respostas)
    if tecla == pygame.K_DOWN:
        cursor = (cursor + 1) % len(respostas)
    if confirmar:
        resposta = respostas[cursor]
        conversa.pop(0)
        cursor = 0
        if "sem_luta" in fala and fala["sem_luta"] == resposta:
            depois_da_conversa = ""
        # O que ele diz a essa resposta e a fala que vem a seguir.
        conversa.insert(0, fala["respostas"][resposta])
        ao_responder(quem_fala, fala["pergunta"], resposta)


def falas_de(ficha, chave, se_nao_houver):
    # As falas que estao na ficha de um treinador com esse nome ("falas",
    # "falas_rede"...), ou as que se dao aqui se ele nao as tiver.
    if chave in ficha:
        return ficha[chave]
    return se_nao_houver


def desafiar(numero):
    # Foste contra um treinador: ele fala contigo e depois, conforme o caso,
    # da-te uma rede, luta, ou fica so pela conversa.
    global indice_treinador, batalha_selvagem
    ficha = TREINADORES[numero]
    indice_treinador = numero
    batalha_selvagem = False

    if len(minha_equipa) == 0:
        # Sem bichos nao ha luta. Quem da a rede, da-a (e da outra a quem
        # ficou sem redes antes de apanhar o primeiro bicho).
        if "da_rede" in ficha and ficha["da_rede"]:
            if numero not in redes_dadas or redes == 0:
                if numero not in redes_dadas:
                    redes_dadas.append(numero)
                falas = falas_de(ficha, "falas_rede", ["Toma esta rede, e vai apanhar o teu primeiro bicho!"])
                comecar_conversa(ficha["nome"], falas, "rede")
            else:
                comecar_conversa(ficha["nome"], ["Vai à erva alta com a rede que te dei!"], "")
        else:
            comecar_conversa(ficha["nome"], ["Sem bichos não há luta. Apanha um primeiro!"], "")
        return

    if numero in treinadores_vencidos:
        comecar_conversa(ficha["nome"], falas_de(ficha, "falas_depois", ["Já me ganhaste. Boa sorte!"]), "")
        return
    comecar_conversa(ficha["nome"], falas_de(ficha, "falas", []), "luta")


def encontrar_bicho():
    # Saltou um bicho da erva: comeca uma batalha contra ele. Sem bichos nao
    # ha batalha: e um encontro, em que so se pode atirar a rede ou fugir.
    global batalha_selvagem, bicho_a_solta, estado, cursor, aviso
    bicho_a_solta = escolher_bicho_selvagem()
    if len(minha_equipa) == 0:
        estado = "encontro"
        cursor = 0
        aviso = "Salta da erva um " + bicho_a_solta["nome"] + " à solta!"
        som_do_bicho(bicho_a_solta)
        return
    batalha_selvagem = True
    comecar_batalha()


def tecla_no_encontro(tecla):
    # O encontro com um bicho a solta quando ainda nao tens bichos.
    global cursor, redes, aviso
    if tecla == pygame.K_UP or tecla == pygame.K_DOWN:
        cursor = 1 - cursor
    if tecla == pygame.K_ESCAPE or tecla == pygame.K_BACKSPACE:
        voltar_ao_mundo()
        aviso = "Fugiste a sete pés!"
        return
    if tecla != pygame.K_RETURN and tecla != pygame.K_SPACE:
        return
    if cursor == 1:
        voltar_ao_mundo()
        aviso = "Fugiste a sete pés!"
    elif redes == 0:
        aviso = "Não tens redes! Quem te deu a primeira dá-te outra."
    else:
        redes = redes - 1
        if consegue_apanhar(bicho_a_solta):
            minha_equipa.append(bicho_a_solta)
            voltar_ao_mundo()
            aviso = "Apanhaste-o! " + bicho_a_solta["nome"] + " é o teu primeiro bicho."
            ao_apanhar(bicho_a_solta)
        elif redes == 0:
            voltar_ao_mundo()
            aviso = "Escapou-se da rede, e era a última. Fugiu para a erva."
        else:
            aviso = "Escapou-se da rede! Tenta outra vez."


def andar(passo_coluna, passo_linha):
    # Tenta dar um passo: andar(1, 0) e para a direita, andar(0, -1) e para
    # cima. O que acontece depende da letra do quadrado para onde vais.
    global aviso
    if passo_coluna == 1:
        jogador["olha"] = "direita"
    elif passo_coluna == -1:
        jogador["olha"] = "esquerda"
    elif passo_linha == 1:
        jogador["olha"] = "baixo"
    else:
        jogador["olha"] = "cima"
    zona, coluna, linha = quadrado_ao_lado(jogador["zona"], jogador["coluna"], jogador["linha"],
                                           passo_coluna, passo_linha)
    letra = letra_da_zona(zona, coluna, linha)

    if treinador_do_quadrado(letra) != -1:
        desafiar(treinador_do_quadrado(letra))
        return
    if letra == "H":
        descansar()
        return
    if letra == "$":
        abrir_loja()
        return
    if not pode_andar(letra):
        return
    if letra == "e" and len(minha_equipa) == 0 and redes == 0:
        dizer("Sem bichos nem redes, a erva alta é perigosa. Fala primeiro com quem te dê uma rede.")
        return

    antes = jogador["zona"]
    ir_para(zona, coluna, linha)
    jogador["passos"] = jogador["passos"] + 1
    aviso = ""
    if letra in PORTAS and PORTAS[letra] in ZONAS:
        passar_a_porta(letra)
    # Mudaste de zona, por um lado do ecra ou por uma porta? E a zona nova
    # que o desenhar_mundo passa a mostrar.
    if jogador["zona"] != antes:
        dizer("Entraste em: " + jogador["zona"])
    ao_dar_passo(letra)
    if estado == "mundo" and letra == "e" and ha_batalha_na_erva():
        encontrar_bicho()


def tecla_no_mundo(tecla):
    # Um passo logo que se carrega na seta. Com a seta carregada, os passos
    # seguintes sao dados pelo andar_com_as_setas.
    global espera_do_passo
    if tecla == pygame.K_LEFT:
        andar(-1, 0)
    elif tecla == pygame.K_RIGHT:
        andar(1, 0)
    elif tecla == pygame.K_UP:
        andar(0, -1)
    elif tecla == pygame.K_DOWN:
        andar(0, 1)
    else:
        return
    espera_do_passo = 12


def andar_com_as_setas():
    # Corre a cada frame, no mapa: com uma seta carregada, da um passo de 9
    # em 9 frames.
    global espera_do_passo
    if espera_do_passo > 0:
        espera_do_passo = espera_do_passo - 1
        return
    teclas = pygame.key.get_pressed()
    if teclas[pygame.K_LEFT]:
        andar(-1, 0)
    elif teclas[pygame.K_RIGHT]:
        andar(1, 0)
    elif teclas[pygame.K_UP]:
        andar(0, -1)
    elif teclas[pygame.K_DOWN]:
        andar(0, 1)
    else:
        return
    espera_do_passo = 9


# =====================================================================
#                          ACONTECIMENTOS
# =====================================================================

# --- Os acontecimentos ---
# O jogo chama cada uma destas funcoes quando acontece o que o nome diz.
# Estao vazias (so tem "pass"): o que la escreveres passa a acontecer nesse
# momento. E aqui que se INVENTA: um bicho vampiro, um premio, um truque.
#
# Alem do que as regras do jogo podem usar (ver mais acima), tens:
#   memoria                 um dicionario so teu, para guardares o que
#                           quiseres de um turno para o outro:
#                           memoria["vitorias"] = 3
#                           (fica vazio cada vez que o jogo recomeca)
#   dizer("Boa!")           numa batalha, poe um texto no painel de baixo, a
#                           seguir aos que la estiverem; passa-se com Enter.
#                           No mapa, mostra o texto numa caixa
#   voltar_ao_mundo()       acaba a batalha ali mesmo e volta ao mapa
#   bicho in minha_equipa   e verdade se o bicho e teu, e nao do inimigo
#   bicho["vida"] = min(bicho["vida_max"], bicho["vida"] + 10)
#                           cura 10 de vida, sem passar da vida maxima
#   ganhar_xp(bicho, 20)    da 20 de experiencia a um bicho teu
#   sopas, redes, moedas    o que levas na mochila. Para os MUDAR, a
#                           primeira linha da funcao tem de ser "global sopas"
#                           (ou "global redes", ou "global moedas")
memoria = {}


# QUANDO COMECA UMA BATALHA
# Corre no inicio de cada batalha, com as duas equipas ja prontas.
# batalha_selvagem e True se e contra um bicho a solta. Se e contra um
# treinador, treinador()["nome"] diz contra quem, e indice_treinador diz qual
# deles e: 0 no primeiro, 1 no segundo, e por ai fora.
# Ideias: dizer uma frase tua antes da luta; levar uma sopa a mais contra o
# segundo treinador; o teu bicho entrar com o ataque mais forte (mod_ataque
# a 1.25) contra os bichos a solta.
def ao_comecar_batalha():
    pass


# QUANDO UM ATAQUE ACERTA
# atacante: quem atacou. alvo: quem levou. dano: quanta vida o golpe tirou
# (a vida do alvo ja desceu). So corre nos ataques que fazem dano.
# Ideias: um bicho vampiro, que recupera metade do dano que faz; dizer
# "Que pancada!" quando o golpe tira mais de 20; o alvo ficar um bocadinho
# mais fraco de cada vez que leva (mod_defesa a descer).
def ao_acertar(atacante, alvo, dano):
    pass


# QUANDO UM BICHO DESMAIA
# desmaiado: o bicho que ficou sem vida. vencedor: o que o deitou abaixo
# (o que estava em campo do outro lado). Corre para os teus e para os do
# inimigo.
# Ideias: o vencedor recuperar 10 de vida; contar na memoria quantos bichos
# ja deitaste abaixo, e dizer o numero; o desmaiado despedir-se com uma frase.
def ao_desmaiar(desmaiado, vencedor):
    pass


# QUANDO UM BICHO TEU SOBE DE NIVEL
# bicho: o que acabou de subir. bicho["nivel"] ja e o nivel novo.
# Ideias: ficar com a vida toda (bicho["vida"] = bicho["vida_max"]); ganhar
# uma sopa; dizer uma frase de festa quando chega ao nivel 10.
def ao_subir_de_nivel(bicho):
    pass


# QUANDO GANHAS UMA BATALHA
# Corre quando o ultimo bicho do adversario desmaia (o de um treinador, ou o
# bicho a solta), antes de voltares ao mapa.
# Ideias: um premio (o teu bicho em campo ganha 30 de experiencia a mais);
# contar as vitorias na memoria e dizer quantas ja vao; o treinador dizer uma
# frase de mau perdedor.
def ao_ganhar_batalha():
    pass


# QUANDO SE CARREGA NUMA TECLA
# tecla: a tecla em que se carregou. pygame.K_s e a tecla S, pygame.K_c a C.
# Corre no mapa e nas batalhas: estado diz onde estas ("mundo" ou "batalha").
# (As setas, Enter, Espaco, Esc e Backspace ja fazem coisas no jogo.)
# Ideias: a tecla S da mais uma sopa (batota!); a tecla C cura o teu bicho,
# mas so uma vez por jogo (usa a memoria para te lembrares se ja foi usada).
# No mapa: a tecla M mostrar as moedas com o dizer().
def ao_carregar_tecla(tecla):
    pass


# QUANDO RESPONDES A UMA PERGUNTA
# Corre quando escolhes uma resposta numa conversa. nome: quem perguntou.
# pergunta: o que perguntou. resposta: o que respondeste (como esta escrito
# nas "respostas" dele).
# Ideias: a Tia da Mercearia dar-te uma sopa se disseres que nao queres
# lutar; perder 5 moedas por uma resposta malcriada; guardar na memoria o
# que respondeste, para outro treinador falar disso mais tarde.
def ao_responder(nome, pergunta, resposta):
    pass


# QUANDO APANHAS UM BICHO
# bicho: o que acabou de ficar na rede. Ja esta na tua equipa (e o ultimo:
# minha_equipa[-1]), com a vida que lhe restava.
# Ideias: ficar logo com a vida toda; dizer uma frase de boas-vindas; contar
# na memoria quantos ja apanhaste; ganhar 10 moedas por cada um.
def ao_apanhar(bicho):
    pass


# QUANDO DAS UM PASSO
# Corre a cada passo no mapa, ja no quadrado novo. letra: a letra desse
# quadrado ("." e relva, "e" e erva alta...). jogador["passos"] diz quantos
# ja deste, e jogador["zona"] em que zona estas.
# Ideias: uma letra nova no mapa, por exemplo "s" para uma sopa perdida no
# chao (if letra == "s"); os bichos cansarem-se, e perderem 1 de vida a cada
# 20 passos; dizer "Cheira a maresia..." quando chegas perto da agua.
def ao_dar_passo(letra):
    pass


# QUANDO DESCANSAS EM CASA DA AVO
# Corre depois de a avo curar a equipa e encher as sopas.
# Ideias: a avo dar uma sopa a mais; a avo dizer outra coisa; o teu primeiro
# bicho ganhar 10 de experiencia por cada visita.
def ao_descansar():
    pass


# A CADA FRAME
# Corre 60 vezes por segundo enquanto andas pelo mapa (nas batalhas nao).
# Ideias: um relogio (soma 1 a memoria["frames"] e, de 60 em 60, passou um
# segundo); os bichos irem recuperando vida devagarinho enquanto andas.
def a_cada_frame():
    pass


# =====================================================================
#                          O TURNO, PASSO A PASSO
#
# Um turno e uma fila de acoes. Executamos uma, mostramos as mensagens
# que ela deixou, e so depois de o jogador carregar em Enter passamos a
# seguinte. Quando a fila acaba, vemos quem desmaiou.
# =====================================================================

# QUE ATAQUE O INIMIGO ESCOLHE
# Nao recebe nada, e devolve o NOME de um dos ataques do bicho inimigo que
# esta em campo. Como esta: da pontos a cada ataque (os que magoam mais
# valem mais, e curar vale muito quando ele tem pouca vida), junta-lhes
# alguma sorte e escolhe o que ficou com mais pontos.
# Ideias: escolher ao calhas, com random.choice(ataques_de(inimigo));
# escolher sempre o que magoa mais, sem sorte nenhuma; curar-se mais cedo.
def escolher_ataque_inimigo():
    inimigo = equipa_inimiga[ativo_inimigo]
    eu = minha_equipa[ativo_meu]
    melhor = ""
    melhor_pontos = -1
    for nome in ataques_de(inimigo):
        dados = ATAQUES[nome]
        if dados["efeito"] == "dano":
            pontos = dados["poder"] * eficacia(dados["tipo"], eu["tipo"])
            pontos = pontos * dados["precisao"] / 100
        elif dados["efeito"] == "cura":
            pontos = 10
            if inimigo["vida"] < inimigo["vida_max"] * 0.4:
                pontos = 50
        else:
            pontos = 25
        # A sorte faz o inimigo nao ser previsivel de mais.
        pontos = pontos * random.uniform(0.6, 1.4)
        if pontos > melhor_pontos:
            melhor_pontos = pontos
            melhor = nome
    return melhor


# QUEM ATACA PRIMEIRO
# Corre quando os dois bichos vao atacar no mesmo turno. Recebe o teu bicho
# e o do inimigo, e devolve "jogador" (o teu vai primeiro) ou "inimigo".
# Como esta: vai primeiro o mais rapido; se forem iguais, e a sorte.
# (Trocar de bicho e comer sopa vem sempre antes dos ataques.)
# Ideias: ir primeiro o que tem menos vida; ser sempre ao calhas; o teu bicho
# ir sempre primeiro no primeiro turno (conta os turnos na memoria).
def quem_ataca_primeiro(eu, inimigo):
    if eu["velocidade"] > inimigo["velocidade"]:
        return "jogador"
    if eu["velocidade"] < inimigo["velocidade"]:
        return "inimigo"
    if random.randint(0, 1) == 0:
        return "jogador"
    return "inimigo"


def jogador_escolheu(acao_jogador):
    global fila_acoes
    acao_inimigo = {"quem": "inimigo", "tipo": "atacar", "ataque": escolher_ataque_inimigo()}
    eu = minha_equipa[ativo_meu]
    inimigo = equipa_inimiga[ativo_inimigo]
    # Trocar de bicho, comer sopa e atirar a rede vem sempre antes dos
    # ataques. Entre dois ataques, decide a regra quem_ataca_primeiro.
    if acao_jogador["tipo"] != "atacar":
        fila_acoes = [acao_jogador, acao_inimigo]
    elif quem_ataca_primeiro(eu, inimigo) == "jogador":
        fila_acoes = [acao_jogador, acao_inimigo]
    else:
        fila_acoes = [acao_inimigo, acao_jogador]
    continuar()


def mudar_modificador(bicho, chave, fator, nome_do_valor):
    novo = bicho[chave] * fator
    if novo > 2.01 or novo < 0.49:
        mensagens.append("O " + nome_do_valor + " de " + bicho["nome"] + " já não muda mais!")
        return
    bicho[chave] = novo
    if fator > 1:
        mensagens.append("O " + nome_do_valor + " de " + bicho["nome"] + " subiu!")
    else:
        mensagens.append("O " + nome_do_valor + " de " + bicho["nome"] + " desceu!")


def usar_ataque(atacante, alvo, nome):
    dados = ATAQUES[nome]
    mensagens.append(atacante["nome"] + " usa " + nome + "!")
    if "som" in dados:
        tocar_som(dados["som"])
    if random.randint(1, 100) > dados["precisao"]:
        mensagens.append("Mas falhou!")
        return
    efeito = dados["efeito"]
    if efeito == "dano":
        dano = calcular_dano(atacante, alvo, nome)
        if golpe_critico(atacante, alvo):
            dano = int(dano * 1.5)
            mensagens.append("Golpe crítico!")
        alvo["vida"] = max(0, alvo["vida"] - dano)
        alvo["tremor"] = 24
        multiplicador = eficacia(dados["tipo"], alvo["tipo"])
        if multiplicador > 1:
            mensagens.append("É super eficaz!")
        if multiplicador < 1:
            mensagens.append("Não é muito eficaz...")
        ao_acertar(atacante, alvo, dano)
    elif efeito == "cura":
        cura = atacante["vida_max"] * 40 // 100
        atacante["vida"] = min(atacante["vida_max"], atacante["vida"] + cura)
        mensagens.append(atacante["nome"] + " recuperou vida.")
    elif efeito == "sobe_ataque":
        mudar_modificador(atacante, "mod_ataque", 1.25, "ataque")
    elif efeito == "sobe_defesa":
        mudar_modificador(atacante, "mod_defesa", 1.25, "defesa")
    elif efeito == "baixa_ataque":
        mudar_modificador(alvo, "mod_ataque", 0.8, "ataque")
    elif efeito == "baixa_defesa":
        mudar_modificador(alvo, "mod_defesa", 0.8, "defesa")


def executar(acao):
    global ativo_meu, ativo_inimigo, sopas, redes, a_fugir
    if acao["quem"] == "jogador":
        atacante = minha_equipa[ativo_meu]
        alvo = equipa_inimiga[ativo_inimigo]
    else:
        atacante = equipa_inimiga[ativo_inimigo]
        alvo = minha_equipa[ativo_meu]

    if acao["tipo"] == "atacar":
        # Quem desmaiou antes de chegar a sua vez ja nao ataca.
        if atacante["vida"] > 0 and alvo["vida"] > 0:
            usar_ataque(atacante, alvo, acao["ataque"])
    elif acao["tipo"] == "trocar":
        mensagens.append("Volta, " + atacante["nome"] + "!")
        atacante["mod_ataque"] = 1.0
        atacante["mod_defesa"] = 1.0
        ativo_meu = acao["indice"]
        mensagens.append("Vai, " + minha_equipa[ativo_meu]["nome"] + "!")
        som_do_bicho(minha_equipa[ativo_meu])
    elif acao["tipo"] == "entrar_inimigo":
        ativo_inimigo = acao["indice"]
        mensagens.append(treinador()["nome"] + " manda " + equipa_inimiga[ativo_inimigo]["nome"] + "!")
        som_do_bicho(equipa_inimiga[ativo_inimigo])
    elif acao["tipo"] == "apanhar":
        redes = redes - 1
        mensagens.append("Atiras a rede a " + alvo["nome"] + "...")
        if consegue_apanhar(alvo):
            mensagens.append("Apanhaste-o! " + alvo["nome"] + " fica na tua equipa.")
            minha_equipa.append(alvo)
            # A batalha acaba aqui: o que faltava do turno ja nao acontece, e
            # o fim_do_turno ve o a_fugir e volta ao mapa.
            fila_acoes.clear()
            a_fugir = True
            ao_apanhar(alvo)
        else:
            mensagens.append("Escapou-se da rede!")
            if alvo["vida"] == alvo["vida_max"]:
                mensagens.append("Ainda tem a força toda: magoa-o um bocadinho primeiro.")
    elif acao["tipo"] == "sopa":
        sopas = sopas - 1
        cura = atacante["vida_max"] // 2
        atacante["vida"] = min(atacante["vida_max"], atacante["vida"] + cura)
        mensagens.append(atacante["nome"] + " comeu a sopa da avó. Que conforto.")


def ganhar_xp(bicho, quanto):
    bicho["xp"] = bicho["xp"] + quanto
    mensagens.append(bicho["nome"] + " ganhou " + str(quanto) + " de experiência.")
    while bicho["xp"] >= xp_para_subir(bicho):
        bicho["xp"] = bicho["xp"] - xp_para_subir(bicho)
        # Subir de nivel aumenta tudo, mas mantem a vida que ja se perdeu.
        perdida = bicho["vida_max"] - bicho["vida"]
        bicho["nivel"] = bicho["nivel"] + 1
        calcular_valores(bicho)
        bicho["vida"] = max(1, bicho["vida_max"] - perdida)
        mensagens.append(bicho["nome"] + " subiu para o nível " + str(bicho["nivel"]) + "!")
        # Ha algum ataque que ele aprenda exatamente neste nivel?
        dados = BICHOS[bicho["nome"]]
        if "aprende" in dados:
            for nome in dados["aprende"]:
                if dados["aprende"][nome] == bicho["nivel"]:
                    mensagens.append(bicho["nome"] + " aprendeu " + nome + "!")
        ao_subir_de_nivel(bicho)


def fim_do_turno():
    global fase, estado, troca_obrigatoria, cursor, moedas
    if a_fugir:
        voltar_ao_mundo()
        return
    inimigo = equipa_inimiga[ativo_inimigo]
    eu = minha_equipa[ativo_meu]

    if inimigo["vida"] <= 0:
        if not inimigo["anunciado"]:
            inimigo["anunciado"] = True
            mensagens.append(inimigo["nome"] + " desmaiou!")
            ao_desmaiar(inimigo, eu)
            ganhar_xp(eu, inimigo["nivel"] * 12)
            if proximo_vivo(equipa_inimiga) == -1:
                premio = int(premio_da_batalha(equipa_inimiga, batalha_selvagem))
                if premio > 0:
                    moedas = moedas + premio
                    mensagens.append("Ganhaste " + str(premio) + " moedas.")
                ao_ganhar_batalha()
            fase = "texto"
            return
        seguinte = proximo_vivo(equipa_inimiga)
        if seguinte == -1:
            ganhar_batalha()
            return
        fila_acoes.append({"quem": "inimigo", "tipo": "entrar_inimigo", "indice": seguinte})
        continuar()
        return

    if eu["vida"] <= 0:
        if not eu["anunciado"]:
            eu["anunciado"] = True
            mensagens.append(eu["nome"] + " desmaiou!")
            ao_desmaiar(eu, inimigo)
            fase = "texto"
            return
        if proximo_vivo(minha_equipa) == -1:
            estado = "derrota"
            return
        troca_obrigatoria = True
        fase = "equipa"
        cursor = proximo_vivo(minha_equipa)
        return

    fase = "menu"
    cursor = 0


def continuar():
    global fase
    while len(fila_acoes) > 0:
        executar(fila_acoes.pop(0))
        if len(mensagens) > 0:
            fase = "texto"
            return
    fim_do_turno()


def mexer_barras():
    # Corre a cada frame: as barras de vida descem (ou sobem) devagar ate a
    # vida verdadeira, e os bichos deixam de tremer.
    # (Esta numa funcao, e nao solto no ciclo do jogo, para o "bicho" daqui
    # nao ficar a existir no resto do ficheiro: quem escrevesse "bicho" numa
    # funcao sua, por engano, ficava com um bicho qualquer em vez de um erro.)
    for bicho in minha_equipa + equipa_inimiga:
        passo = bicho["vida_max"] / 50
        if bicho["vida_mostrada"] > bicho["vida"]:
            bicho["vida_mostrada"] = max(bicho["vida"], bicho["vida_mostrada"] - passo)
        if bicho["vida_mostrada"] < bicho["vida"]:
            bicho["vida_mostrada"] = min(bicho["vida"], bicho["vida_mostrada"] + passo)
        if bicho["tremor"] > 0:
            bicho["tremor"] = bicho["tremor"] - 1


def barras_paradas():
    # Enquanto alguma barra de vida esta a descer, nao passamos o texto.
    for bicho in minha_equipa + equipa_inimiga:
        if abs(bicho["vida_mostrada"] - bicho["vida"]) > 0.5:
            return False
    return True


# =====================================================================
#                          AS TECLAS DA BATALHA
# =====================================================================

def tecla_na_batalha(tecla):
    global fase, cursor, troca_obrigatoria, ativo_meu, a_fugir
    confirmar = tecla == pygame.K_RETURN or tecla == pygame.K_SPACE
    voltar = tecla == pygame.K_ESCAPE or tecla == pygame.K_BACKSPACE
    eu = minha_equipa[ativo_meu]

    if fase == "texto":
        if confirmar and barras_paradas():
            mensagens.pop(0)
            if len(mensagens) == 0:
                continuar()
        return

    if fase == "menu":
        quantas = len(opcoes_do_menu())
    elif fase == "ataques":
        quantas = len(ataques_de(eu))
    else:
        quantas = len(minha_equipa)
    if tecla == pygame.K_UP:
        cursor = (cursor - 1) % quantas
    if tecla == pygame.K_DOWN:
        cursor = (cursor + 1) % quantas

    if fase == "menu" and confirmar:
        escolha = opcoes_do_menu()[cursor]
        if escolha == "Lutar":
            fase = "ataques"
            cursor = 0
        elif escolha == "Equipa":
            fase = "equipa"
            cursor = ativo_meu
        elif escolha == "Sopa":
            if sopas == 0:
                mensagens.append("Já não há sopa. A avó vai ficar triste.")
                fase = "texto"
            elif eu["vida"] == eu["vida_max"]:
                mensagens.append(eu["nome"] + " já está de barriga cheia.")
                fase = "texto"
            else:
                jogador_escolheu({"quem": "jogador", "tipo": "sopa"})
        elif escolha == "Apanhar":
            # (So aparece contra um bicho a solta.) E preciso uma rede, e
            # haver lugar na equipa.
            if redes == 0:
                mensagens.append("Já não tens redes. Vendem-se na mercearia.")
                fase = "texto"
            elif len(minha_equipa) >= EQUIPA_MAXIMA:
                mensagens.append("A tua equipa está cheia: não cabe mais nenhum.")
                fase = "texto"
            else:
                jogador_escolheu({"quem": "jogador", "tipo": "apanhar"})
        elif escolha == "Fugir":
            # So se foge de um bicho a solta. Depois de lido o texto, o
            # fim_do_turno ve o a_fugir e volta ao mapa.
            if batalha_selvagem:
                mensagens.append("Fugiste a sete pés!")
                a_fugir = True
            else:
                mensagens.append("De um treinador não se foge!")
            fase = "texto"

    elif fase == "ataques":
        if voltar:
            fase = "menu"
            cursor = 0
        elif confirmar:
            nome = ataques_de(eu)[cursor]
            jogador_escolheu({"quem": "jogador", "tipo": "atacar", "ataque": nome})

    elif fase == "equipa":
        if voltar and not troca_obrigatoria:
            fase = "menu"
            cursor = 1
        elif confirmar:
            escolhido = minha_equipa[cursor]
            if escolhido["vida"] <= 0 or cursor == ativo_meu:
                return
            if troca_obrigatoria:
                # O anterior desmaiou: trocar nao gasta o turno.
                troca_obrigatoria = False
                ativo_meu = cursor
                mensagens.append("Vai, " + escolhido["nome"] + "!")
                som_do_bicho(escolhido)
                fase = "texto"
            else:
                jogador_escolheu({"quem": "jogador", "tipo": "trocar", "indice": cursor})


# =====================================================================
#                          DESENHAR
# =====================================================================

# --- Os desenhos ---
# As funcoes que se seguem desenham um bicho (o corpo e os olhos) e a barra
# de vida. Desenha-se com formas do pygame, sempre no "ecra":
#   pygame.draw.circle(ecra, cor, (x, y), raio)
#   pygame.draw.ellipse(ecra, cor, (x, y, largura, altura))
#   pygame.draw.rect(ecra, cor, (x, y, largura, altura))
#   pygame.draw.line(ecra, cor, (x1, y1), (x2, y2), grossura)
#   pygame.draw.polygon(ecra, cor, [(x1, y1), (x2, y2), (x3, y3)])
# O x cresce para a direita e o y cresce para BAIXO. Uma cor sao tres
# numeros (vermelho, verde, azul), de 0 a 255. O que se desenha depois fica
# por cima do que se desenhou antes. escurecer(cor, 0.5) da a mesma cor, mais
# escura.
#   cx, cy       o centro do bicho, em pixeis
#   tamanho      a largura (e a altura) do bicho. O mesmo bicho e desenhado
#                grande na batalha e pequeno nos menus, por isso faz as
#                contas com o tamanho (tamanho // 4) em vez de numeros fixos
#   bicho["nome"], bicho["tipo"], bicho["vida"], bicho["vida_max"]
#   BICHOS[bicho["nome"]]    a ficha dele, la em cima ("forma", "cor"...)
# Nos desenhos do mapa (um quadrado, tu, um treinador):
#   x, y         o canto de cima, a esquerda, do quadrado onde se desenha
#   QUADRADO     o lado do quadrado, em pixeis. O meio dele e
#                (x + QUADRADO // 2, y + QUADRADO // 2)

# O BICHO INTEIRO
# Faz o bicho respirar e tremer, e depois mostra a imagem dele ou, se nao
# houver imagem, manda desenhar o corpo e os olhos.
#   olha_para         1 se o bicho olha para a direita, -1 para a esquerda
#   bicho["tremor"]   os frames que ainda treme depois de levar um golpe
# Ideias: respirar mais depressa; saltar em vez de tremer; ficar mais
# pequeno quando tem pouca vida.
def desenhar_bicho(bicho, cx, cy, tamanho, olha_para):
    if bicho["vida_mostrada"] <= 0.5:
        return
    dados = BICHOS[bicho["nome"]]
    # Respira: sobe e desce devagar.
    cy = cy + int(math.sin(pygame.time.get_ticks() / 300 + cx) * 3)
    if bicho["tremor"] > 0:
        cx = cx + random.randint(-6, 6)

    imagem = obter_imagem(dados["imagem"], tamanho)
    if imagem is not None:
        if olha_para == -1:
            imagem = pygame.transform.flip(imagem, True, False)
        ecra.blit(imagem, (cx - tamanho // 2, cy - tamanho // 2))
        return

    cor = dados["cor"]
    # Pisca a branco nos primeiros frames depois de levar um golpe.
    if bicho["tremor"] > 0 and bicho["tremor"] % 6 < 3:
        cor = BRANCO
    desenhar_corpo(bicho, cor, cx, cy, tamanho)
    desenhar_olhos(bicho, cx, cy, tamanho, olha_para)


# O TEU BICHO, VISTO DE COSTAS
# E assim que se desenha o teu bicho na batalha: ele olha para o adversario,
# e tu ves-lhe as costas. Mostra a imagem_costas dele; se nao houver, a
# imagem de frente; se tambem nao houver, o corpo sem olhos, com uma risca
# nas costas.
# Ideias: uma cauda; duas riscas em vez de uma; as costas mais escuras.
def desenhar_bicho_de_costas(bicho, cx, cy, tamanho):
    if bicho["vida_mostrada"] <= 0.5:
        return
    dados = BICHOS[bicho["nome"]]
    cy = cy + int(math.sin(pygame.time.get_ticks() / 300 + cx) * 3)
    if bicho["tremor"] > 0:
        cx = cx + random.randint(-6, 6)

    imagem = None
    if "imagem_costas" in dados:
        imagem = obter_imagem(dados["imagem_costas"], tamanho)
    if imagem is None:
        imagem = obter_imagem(dados["imagem"], tamanho)
    if imagem is not None:
        ecra.blit(imagem, (cx - tamanho // 2, cy - tamanho // 2))
        return

    cor = dados["cor"]
    if bicho["tremor"] > 0 and bicho["tremor"] % 6 < 3:
        cor = BRANCO
    desenhar_corpo(bicho, cor, cx, cy, tamanho)
    pygame.draw.line(ecra, escurecer(dados["cor"], 0.55), (cx, cy - tamanho // 5), (cx, cy + tamanho // 4), 5)


# O CORPO DE UM BICHO
# Desenha a forma que esta na ficha do bicho ("circulo", "quadrado",
# "triangulo" ou "gota"), com um contorno mais escuro.
#   cor      a cor com que se pinta (a do bicho, ou branco quando leva um golpe)
#   corpo    um retangulo do tamanho do bicho: corpo.top e o cimo,
#            corpo.bottom o fundo, corpo.left e corpo.right os lados
# Ideias: uma forma nova (um "losango", para usares na ficha de um bicho);
# uma crista ou um chapeu por cima do corpo; uma boca; riscas.
def desenhar_corpo(bicho, cor, cx, cy, tamanho):
    dados = BICHOS[bicho["nome"]]
    contorno = escurecer(dados["cor"], 0.55)
    corpo = pygame.Rect(0, 0, tamanho, tamanho)
    corpo.center = (cx, cy)

    if dados["forma"] == "circulo":
        pygame.draw.ellipse(ecra, cor, corpo)
        pygame.draw.ellipse(ecra, contorno, corpo, 4)
    elif dados["forma"] == "quadrado":
        pygame.draw.rect(ecra, cor, corpo, border_radius=tamanho // 5)
        pygame.draw.rect(ecra, contorno, corpo, 4, border_radius=tamanho // 5)
    elif dados["forma"] == "triangulo":
        pontos = [(cx, corpo.top), (corpo.right, corpo.bottom), (corpo.left, corpo.bottom)]
        pygame.draw.polygon(ecra, cor, pontos)
        pygame.draw.polygon(ecra, contorno, pontos, 4)
    elif dados["forma"] == "gota":
        raio = tamanho * 2 // 5
        centro_baixo = (cx, corpo.bottom - raio)
        bico = [(cx, corpo.top), (cx + raio, centro_baixo[1]), (cx - raio, centro_baixo[1])]
        pygame.draw.circle(ecra, cor, centro_baixo, raio)
        pygame.draw.polygon(ecra, cor, bico)
        pygame.draw.circle(ecra, contorno, centro_baixo, raio, 4)


# OS OLHOS DE UM BICHO
# Dois circulos brancos, cada um com a pupila virada para o outro bicho.
#   olha_para    1 se o bicho olha para a direita, -1 para a esquerda
# Ideias: olhos maiores; olhos zangados quando tem pouca vida (uma linha por
# cima de cada olho); um olho so, ao meio, como um ciclope.
def desenhar_olhos(bicho, cx, cy, tamanho, olha_para):
    olho_y = cy + tamanho // 10
    raio_olho = tamanho // 9
    for lado in [-1, 1]:
        olho_x = cx + lado * tamanho // 5
        pygame.draw.circle(ecra, BRANCO, (olho_x, olho_y), raio_olho)
        pygame.draw.circle(ecra, PRETO, (olho_x + olha_para * raio_olho // 2, olho_y), raio_olho // 2)


# A BARRA DE VIDA
# x, y: o canto de cima, a esquerda. largura: o comprimento da barra cheia.
# fracao vai de 0 (sem vida) a 1 (vida toda). A barra e verde, passa a
# amarela abaixo de metade e a vermelha quando esta quase no fim.
# Ideias: outras cores; uma barra mais grossa; piscar quando esta vermelha.
def desenhar_barra_vida(bicho, x, y, largura):
    fracao = bicho["vida_mostrada"] / bicho["vida_max"]
    cor = VERDE
    if fracao < 0.5:
        cor = AMARELO
    if fracao < 0.2:
        cor = VERMELHO
    pygame.draw.rect(ecra, PRETO, (x, y, largura, 12), border_radius=6)
    pygame.draw.rect(ecra, cor, (x, y, int(largura * fracao), 12), border_radius=6)


# UM QUADRADO DO MAPA
# letra: a letra desse quadrado, na zona. Primeiro pinta-se o chao (relva, ou
# soalho por baixo das coisas de dentro de um edificio) e depois, por cima, o
# que a letra disser: erva alta, uma arvore, agua, a casa da avo, uma parede,
# uma porta, uma mesa, uma estante... (Tu e os treinadores sao desenhados
# depois, por outras funcoes.)
# Ideias: outras cores (um mapa de neve, ou de deserto); flores na relva; o
# desenho de uma letra nova que tenhas inventado (if letra == "s").
def desenhar_quadrado(letra, x, y):
    meio = x + QUADRADO // 2
    pygame.draw.rect(ecra, RELVA, (x, y, QUADRADO, QUADRADO))
    if letra in "_tmblcv$":
        # O que esta dentro de um edificio tem soalho por baixo.
        pygame.draw.rect(ecra, SOALHO, (x, y, QUADRADO, QUADRADO))
        pygame.draw.line(ecra, escurecer(SOALHO, 0.85), (x, y + 20), (x + QUADRADO, y + 20), 1)
    if letra == "e":
        pygame.draw.rect(ecra, ERVA_ALTA, (x, y, QUADRADO, QUADRADO))
        # Tres tufos, cada um com duas folhas.
        for tufo in [x + 8, x + 20, x + 32]:
            pygame.draw.line(ecra, RELVA, (tufo, y + 32), (tufo - 4, y + 14), 3)
            pygame.draw.line(ecra, RELVA, (tufo, y + 32), (tufo + 4, y + 10), 3)
    elif letra == "A":
        pygame.draw.rect(ecra, TRONCO, (meio - 4, y + 22, 8, 16))
        pygame.draw.circle(ecra, COPA, (meio, y + 16), 15)
        pygame.draw.circle(ecra, escurecer(COPA, 0.8), (meio, y + 16), 15, 3)
    elif letra == "~":
        pygame.draw.rect(ecra, AGUA, (x, y, QUADRADO, QUADRADO))
        # Duas ondas, que andam para a direita e voltam ao inicio.
        desvio = pygame.time.get_ticks() // 200 % 8
        pygame.draw.line(ecra, BRANCO, (x + 4 + desvio, y + 12), (x + 16 + desvio, y + 12), 2)
        pygame.draw.line(ecra, BRANCO, (x + 16 + desvio, y + 28), (x + 28 + desvio, y + 28), 2)
    elif letra == "H":
        pygame.draw.rect(ecra, PAREDE, (x + 5, y + 18, 30, 20))
        pygame.draw.polygon(ecra, TELHADO, [(x + 1, y + 20), (meio, y + 2), (x + 39, y + 20)])
        pygame.draw.rect(ecra, TRONCO, (meio - 4, y + 26, 8, 12))
    elif letra == "#":
        pygame.draw.rect(ecra, PAREDE, (x, y, QUADRADO, QUADRADO))
        pygame.draw.rect(ecra, escurecer(PAREDE, 0.7), (x, y, QUADRADO, QUADRADO), 2)
        pygame.draw.line(ecra, escurecer(PAREDE, 0.7), (x, y + 20), (x + QUADRADO, y + 20), 2)
    elif letra == "t":
        pygame.draw.rect(ecra, TELHADO, (x + 2, y + 2, 36, 36), border_radius=4)
        pygame.draw.rect(ecra, AMARELO, (x + 6, y + 6, 28, 28), 2, border_radius=3)
    elif letra == "j":
        pygame.draw.rect(ecra, PAREDE, (x, y, QUADRADO, QUADRADO))
        pygame.draw.rect(ecra, escurecer(PAREDE, 0.7), (x, y, QUADRADO, QUADRADO), 2)
        pygame.draw.rect(ecra, AGUA, (x + 8, y + 8, 24, 22))
        pygame.draw.line(ecra, BRANCO, (meio, y + 8), (meio, y + 29), 2)
        pygame.draw.line(ecra, BRANCO, (x + 8, y + 19), (x + 31, y + 19), 2)
    elif letra == "m":
        pygame.draw.rect(ecra, escurecer(TRONCO, 0.7), (x + 6, y + 28, 4, 9))
        pygame.draw.rect(ecra, escurecer(TRONCO, 0.7), (x + 30, y + 28, 4, 9))
        pygame.draw.rect(ecra, TRONCO, (x + 3, y + 8, 34, 22), border_radius=4)
        pygame.draw.rect(ecra, escurecer(TRONCO, 0.7), (x + 3, y + 8, 34, 22), 2, border_radius=4)
    elif letra == "b":
        pygame.draw.rect(ecra, escurecer(TRONCO, 0.7), (x + 13, y + 22, 3, 12))
        pygame.draw.rect(ecra, escurecer(TRONCO, 0.7), (x + 24, y + 22, 3, 12))
        pygame.draw.ellipse(ecra, TRONCO, (x + 9, y + 12, 22, 14))
        pygame.draw.ellipse(ecra, escurecer(TRONCO, 0.7), (x + 9, y + 12, 22, 14), 2)
    elif letra == "l":
        pygame.draw.rect(ecra, escurecer(TRONCO, 0.75), (x + 2, y + 2, 36, 36))
        # Duas prateleiras, cada uma com cinco livros de cores diferentes.
        for prateleira in [y + 5, y + 21]:
            cores = [VERMELHO, AGUA, AMARELO, VERDE, PAREDE]
            for numero in range(5):
                pygame.draw.rect(ecra, cores[numero], (x + 5 + numero * 6, prateleira, 5, 13))
    elif letra == "c":
        pygame.draw.rect(ecra, TRONCO, (x + 4, y + 2, 32, 36), border_radius=4)
        pygame.draw.rect(ecra, AGUA, (x + 6, y + 14, 28, 22), border_radius=3)
        pygame.draw.rect(ecra, BRANCO, (x + 9, y + 4, 22, 9), border_radius=3)
    elif letra == "v":
        pygame.draw.circle(ecra, COPA, (meio, y + 13), 10)
        pygame.draw.circle(ecra, ERVA_ALTA, (meio - 4, y + 10), 5)
        pygame.draw.polygon(ecra, TELHADO, [(x + 11, y + 22), (x + 29, y + 22), (x + 26, y + 37), (x + 14, y + 37)])
    elif letra == " ":
        pygame.draw.rect(ecra, PRETO, (x, y, QUADRADO, QUADRADO))
    elif letra == "$":
        pygame.draw.rect(ecra, TRONCO, (x, y + 6, QUADRADO, 28))
        pygame.draw.circle(ecra, AMARELO, (meio, y + 20), 9)
        pygame.draw.circle(ecra, escurecer(AMARELO, 0.6), (meio, y + 20), 9, 2)
    elif letra in PORTAS:
        pygame.draw.rect(ecra, PAREDE, (x, y, QUADRADO, QUADRADO))
        pygame.draw.rect(ecra, TRONCO, (x + 8, y + 4, 24, 36))
        pygame.draw.circle(ecra, AMARELO, (x + 26, y + 24), 3)


# TU, NO MAPA
# olha_para: "cima", "baixo", "esquerda" ou "direita". Como esta: mostra a
# imagem do JOGADOR para esse lado (de frente, de costas ou de lado). Se ela
# nao existir, desenha um corpo com a "cor" do JOGADOR, uma cabeca, e dois
# olhos virados para onde vais (de costas nao se veem).
# Ideias: outra cor de camisola; um chapeu; o teu primeiro bicho a andar
# atras de ti, pequenino (desenhar_bicho(minha_equipa[0], x, y, 20, 1)).
def desenhar_jogador(x, y, olha_para):
    chave = "imagem"
    if olha_para == "cima":
        chave = "imagem_costas"
    if olha_para == "esquerda" or olha_para == "direita":
        chave = "imagem_lado"
    if chave in JOGADOR:
        imagem = obter_imagem(JOGADOR[chave], QUADRADO)
        if imagem is not None:
            if olha_para == "esquerda":
                imagem = pygame.transform.flip(imagem, True, False)
            ecra.blit(imagem, (x, y))
            return

    meio = x + QUADRADO // 2
    pygame.draw.rect(ecra, JOGADOR["cor"], (meio - 9, y + 20, 18, 17), border_radius=5)
    pygame.draw.circle(ecra, PAREDE, (meio, y + 13), 10)
    pygame.draw.circle(ecra, PRETO, (meio, y + 13), 10, 2)
    if olha_para == "cima":
        return
    desvio = 0
    if olha_para == "esquerda":
        desvio = -4
    if olha_para == "direita":
        desvio = 4
    pygame.draw.circle(ecra, PRETO, (meio - 4 + desvio, y + 13), 2)
    pygame.draw.circle(ecra, PRETO, (meio + 4 + desvio, y + 13), 2)


# UM TREINADOR, NO MAPA
# treinador: a ficha dele, de TREINADORES. vencido: True se ja lhe ganhaste.
# Como esta: a camisola tem a cor_fundo dele, e um ponto de exclamacao por
# cima enquanto nao o venceres. Vencido, fica cinzento.
# Ideias: uma coroa na ultima treinadora (if treinador["nome"] == ...); um
# desenho diferente para cada um; os vencidos ficarem deitados.
def desenhar_treinador(treinador, x, y, vencido):
    meio = x + QUADRADO // 2
    cor = escurecer(treinador["cor_fundo"], 0.8)
    if vencido:
        cor = CINZA
    pygame.draw.rect(ecra, cor, (meio - 9, y + 20, 18, 17), border_radius=5)
    pygame.draw.circle(ecra, PAREDE, (meio, y + 13), 10)
    pygame.draw.circle(ecra, PRETO, (meio, y + 13), 10, 2)
    pygame.draw.circle(ecra, PRETO, (meio - 4, y + 13), 2)
    pygame.draw.circle(ecra, PRETO, (meio + 4, y + 13), 2)
    if not vencido:
        pygame.draw.rect(ecra, VERMELHO, (meio + 9, y, 4, 9))
        pygame.draw.rect(ecra, VERMELHO, (meio + 9, y + 11, 4, 4))


def partir_texto(texto, letras):
    # Parte um texto comprido em linhas com esse numero de letras, no maximo,
    # sem cortar palavras a meio.
    linhas = []
    linha = ""
    for palavra in texto.split(" "):
        if linha != "" and len(linha) + 1 + len(palavra) > letras:
            linhas.append(linha)
            linha = palavra
        elif linha == "":
            linha = palavra
        else:
            linha = linha + " " + palavra
    linhas.append(linha)
    return linhas


def desenhar_aviso():
    # A caixa com o que foi dito, por cima do mapa. Cresce para cima quando o
    # texto precisa de mais linhas.
    if aviso == "":
        return
    linhas = partir_texto(aviso, 62)
    altura = 22 + 28 * len(linhas)
    y = 552 - altura
    pygame.draw.rect(ecra, PAINEL, (20, y, LARGURA - 40, altura), border_radius=12)
    pygame.draw.rect(ecra, BRANCO, (20, y, LARGURA - 40, altura), 3, border_radius=12)
    for linha in linhas:
        mostrar_texto(linha, 38, y + 12, BRANCO, fonte)
        y = y + 28


def desenhar_conversa():
    # A conversa aparece por cima do mapa: quem fala, o que diz e, se for
    # uma pergunta, as respostas a escolha.
    desenhar_mundo()
    if len(conversa) == 0:
        return
    fala = conversa[0]
    respostas = []
    if isinstance(fala, str):
        texto = fala
    else:
        texto = fala["pergunta"]
        respostas = list(fala["respostas"].keys())
    linhas = partir_texto(texto, 62)
    altura = 52 + 28 * len(linhas) + 32 * len(respostas)
    y = 552 - altura
    pygame.draw.rect(ecra, PAINEL, (20, y, LARGURA - 40, altura), border_radius=12)
    pygame.draw.rect(ecra, BRANCO, (20, y, LARGURA - 40, altura), 3, border_radius=12)
    mostrar_texto(quem_fala, 38, y + 12, AMARELO, fonte_pequena)
    y = y + 36
    for linha in linhas:
        mostrar_texto(linha, 38, y, BRANCO, fonte)
        y = y + 28
    indice = 0
    for resposta in respostas:
        cor = BRANCO
        if indice == cursor:
            cor = AMARELO
            mostrar_texto(">", 60, y + 4, AMARELO, fonte)
        mostrar_texto(resposta, 84, y + 4, cor, fonte)
        y = y + 32
        indice = indice + 1
    if len(respostas) == 0 and pygame.time.get_ticks() // 400 % 2 == 0:
        pygame.draw.polygon(ecra, AMARELO, [(748, 528), (768, 528), (758, 540)])


def desenhar_encontro():
    # Um bicho a solta e tu sem bichos: a rede, ou as pernas.
    ecra.fill(BICHO_A_SOLTA["cor_fundo"])
    pygame.draw.rect(ecra, escurecer(BICHO_A_SOLTA["cor_fundo"], 0.75), (0, 250, LARGURA, 190))
    pygame.draw.ellipse(ecra, escurecer(BICHO_A_SOLTA["cor_fundo"], 0.55), (285, 265, 230, 55))
    desenhar_bicho(bicho_a_solta, 400, 230, 130, -1)
    desenhar_caixa_bicho(bicho_a_solta, 40, 40, False)
    desenhar_painel()
    y = 470
    for linha in partir_texto(aviso, 34)[:3]:
        mostrar_texto(linha, 34, y, BRANCO, fonte)
        y = y + 30
    opcoes = ["Atirar a rede (" + str(redes) + ")", "Fugir"]
    indice = 0
    for opcao in opcoes:
        cor = BRANCO
        if indice == cursor:
            cor = AMARELO
            mostrar_texto(">", 496, 478 + indice * 40, AMARELO, fonte)
        mostrar_texto(opcao, 520, 478 + indice * 40, cor, fonte)
        indice = indice + 1


def desenhar_mundo():
    # So se desenha a zona onde estas: e o ecra inteiro.
    ecra.fill(PRETO)
    for linha in range(ZONA_LINHAS):
        for coluna in range(ZONA_COLUNAS):
            letra = letra_do_mapa(coluna, linha)
            x = coluna * QUADRADO
            y = linha * QUADRADO
            numero = treinador_do_quadrado(letra)
            if numero != -1:
                # Por baixo de um treinador vai o chao que ele tiver ao lado:
                # soalho dentro de um edificio, relva ca fora.
                letra = "."
                if letra_do_mapa(coluna - 1, linha) == "_":
                    letra = "_"
            desenhar_quadrado(letra, x, y)
            if numero != -1:
                desenhar_treinador(TREINADORES[numero], x, y, numero in treinadores_vencidos)
    desenhar_jogador(jogador["coluna"] * QUADRADO, jogador["linha"] * QUADRADO, jogador["olha"])

    if estado == "mundo":
        desenhar_aviso()

    # A faixa de baixo: os treinadores que faltam, a equipa e as sopas.
    pygame.draw.rect(ecra, PAINEL, (0, ALTURA - 40, LARGURA, 40))
    mostrar_texto(jogador["zona"], 14, ALTURA - 28, AMARELO, fonte_pequena)
    mostrar_texto("Por vencer: " + str(por_vencer), 120, ALTURA - 28, BRANCO, fonte_pequena)
    # A vida de cada bicho da equipa, em barras pequenas.
    x = 245
    for bicho in minha_equipa[:EQUIPA_MAXIMA]:
        desenhar_barra_vida(bicho, x, ALTURA - 26, 36)
        x = x + 42
    mochila = "Sopas " + str(sopas) + "   Redes " + str(redes) + "   Moedas " + str(moedas)
    mostrar_texto(mochila, 520, ALTURA - 28, BRANCO, fonte_pequena)


def desenhar_loja():
    # A loja aparece por cima do mapa. (O aviso, aqui, e a frase da compra:
    # vai dentro da loja, e nao na caixa do mapa.)
    desenhar_mundo()
    pygame.draw.rect(ecra, PAINEL, (160, 110, 480, 330), border_radius=14)
    pygame.draw.rect(ecra, BRANCO, (160, 110, 480, 330), 3, border_radius=14)
    mostrar_texto("Loja", 190, 130, AMARELO, fonte)
    mostrar_texto("Tens " + str(moedas) + " moedas", 420, 134, BRANCO, fonte_pequena)
    y = 185
    indice = 0
    for nome in LOJA:
        cor = BRANCO
        if indice == cursor_loja:
            cor = AMARELO
            mostrar_texto(">", 190, y, AMARELO, fonte)
        mostrar_texto(nome, 215, y, cor, fonte)
        mostrar_texto(str(LOJA[nome]["preco"]) + " moedas", 480, y + 4, cor, fonte_pequena)
        y = y + 36
        indice = indice + 1
    if len(LOJA) == 0:
        mostrar_texto("Hoje não há nada à venda.", 190, y, CINZA, fonte)
    mostrar_texto(aviso, 190, 375, VERDE, fonte_pequena)
    mostrar_texto("Enter: comprar  ·  Esc: sair", 190, 405, CINZA, fonte_pequena)


def desenhar_caixa_bicho(bicho, x, y, com_numeros):
    altura = 70
    if com_numeros:
        altura = 95
    pygame.draw.rect(ecra, PAINEL, (x, y, 300, altura), border_radius=10)
    pygame.draw.rect(ecra, BRANCO, (x, y, 300, altura), 2, border_radius=10)
    mostrar_texto(bicho["nome"], x + 14, y + 10, BRANCO, fonte)
    mostrar_texto("Nv " + str(bicho["nivel"]), x + 235, y + 12, AMARELO, fonte_pequena)
    cor_tipo = CORES_TIPO[bicho["tipo"]]
    pygame.draw.rect(ecra, cor_tipo, (x + 14, y + 38, 70, 18), border_radius=9)
    mostrar_texto(bicho["tipo"], x + 22, y + 40, PRETO, fonte_pequena)
    desenhar_barra_vida(bicho, x + 95, y + 42, 190)
    if com_numeros:
        vida = str(int(bicho["vida_mostrada"] + 0.5)) + " / " + str(bicho["vida_max"])
        mostrar_texto(vida, x + 180, y + 64, BRANCO, fonte_pequena)
        mostrar_texto("XP " + str(bicho["xp"]) + "/" + str(xp_para_subir(bicho)), x + 14, y + 64, CINZA, fonte_pequena)


def desenhar_painel():
    pygame.draw.rect(ecra, PAINEL, (0, 440, LARGURA, 160))
    pygame.draw.rect(ecra, BRANCO, (8, 448, LARGURA - 16, 144), 3, border_radius=12)


def desenhar_batalha():
    eu = minha_equipa[ativo_meu]
    inimigo = equipa_inimiga[ativo_inimigo]

    ecra.fill(treinador()["cor_fundo"])
    pygame.draw.rect(ecra, escurecer(treinador()["cor_fundo"], 0.75), (0, 250, LARGURA, 190))
    pygame.draw.ellipse(ecra, escurecer(treinador()["cor_fundo"], 0.55), (480, 205, 230, 55))
    pygame.draw.ellipse(ecra, escurecer(treinador()["cor_fundo"], 0.55), (70, 385, 280, 60))

    desenhar_bicho(inimigo, 595, 180, 110, -1)
    desenhar_bicho_de_costas(eu, 210, 340, 150)
    desenhar_caixa_bicho(inimigo, 40, 40, False)
    desenhar_caixa_bicho(eu, 460, 300, True)

    desenhar_painel()
    if fase == "texto":
        if len(mensagens) > 0:
            mostrar_texto(mensagens[0], 34, 475, BRANCO, fonte)
            if barras_paradas() and pygame.time.get_ticks() // 400 % 2 == 0:
                pygame.draw.polygon(ecra, AMARELO, [(748, 560), (768, 560), (758, 572)])

    elif fase == "menu":
        mostrar_texto("O que faz " + eu["nome"] + "?", 34, 475, BRANCO, fonte)
        # As opcoes em duas colunas, tres em cada uma.
        indice = 0
        for opcao in opcoes_do_menu():
            texto = opcao
            if opcao == "Sopa":
                texto = "Sopa (" + str(sopas) + ")"
            if opcao == "Apanhar":
                texto = "Apanhar (" + str(redes) + ")"
            x = 440 + (indice // 3) * 165
            y = 468 + (indice % 3) * 36
            cor = BRANCO
            if indice == cursor:
                cor = AMARELO
                mostrar_texto(">", x - 24, y, AMARELO, fonte)
            mostrar_texto(texto, x, y, cor, fonte)
            indice = indice + 1

    elif fase == "ataques":
        nomes = ataques_de(eu)
        y = 460
        indice = 0
        for nome in nomes:
            cor = BRANCO
            if indice == cursor:
                cor = AMARELO
                mostrar_texto(">", 22, y, AMARELO, fonte)
            pygame.draw.circle(ecra, CORES_TIPO[ATAQUES[nome]["tipo"]], (52, y + 10), 7)
            mostrar_texto(nome, 66, y, cor, fonte)
            y = y + 32
            indice = indice + 1
        # A ficha do ataque escolhido, do lado direito.
        dados = ATAQUES[nomes[cursor]]
        mostrar_texto("Tipo: " + dados["tipo"], 440, 462, BRANCO, fonte_pequena)
        if dados["efeito"] == "dano":
            mostrar_texto("Poder: " + str(dados["poder"]), 440, 488, BRANCO, fonte_pequena)
        else:
            mostrar_texto("Efeito: " + dados["efeito"].replace("_", " "), 440, 488, BRANCO, fonte_pequena)
        mostrar_texto("Precisão: " + str(dados["precisao"]), 440, 514, BRANCO, fonte_pequena)
        if dados["efeito"] == "dano":
            multiplicador = eficacia(dados["tipo"], inimigo["tipo"])
            if multiplicador > 1:
                mostrar_texto("Super eficaz contra " + inimigo["nome"] + "!", 440, 545, VERDE, fonte_pequena)
            if multiplicador < 1:
                mostrar_texto("Pouco eficaz contra " + inimigo["nome"] + ".", 440, 545, VERMELHO, fonte_pequena)
        mostrar_texto("Esc: voltar", 680, 568, CINZA, fonte_pequena)

    elif fase == "equipa":
        desenhar_lista_equipa()
        dica = "Enter: entra este · Esc: voltar (trocar gasta o turno)"
        if troca_obrigatoria:
            dica = "Enter: entra este"
        mostrar_texto(dica, 34, 500, CINZA, fonte)


def desenhar_lista_equipa():
    pygame.draw.rect(ecra, PAINEL, (100, 90, 600, 380), border_radius=14)
    pygame.draw.rect(ecra, BRANCO, (100, 90, 600, 380), 3, border_radius=14)
    titulo = "Quem entra?"
    if troca_obrigatoria:
        titulo = "Quem entra? (tens de escolher)"
    mostrar_texto(titulo, 130, 110, AMARELO, fonte)
    # Ate tres bichos, cada um tem 100 pixeis de altura. Com mais (os que
    # apanhaste), apertam-se: cabem seis, com 50 cada um.
    passo = 100
    if len(minha_equipa) > 3:
        passo = 50
    y = 160
    if passo == 50:
        y = 152
    indice = 0
    for bicho in minha_equipa:
        if indice == cursor:
            pygame.draw.rect(ecra, (60, 60, 90), (115, y - 4, 570, passo - 6), border_radius=10)
        desenhar_bicho(bicho, 170, y + passo // 2 - 8, passo * 3 // 5, 1)
        cor = BRANCO
        if bicho["vida"] <= 0:
            cor = CINZA
        mostrar_texto(bicho["nome"] + "  Nv " + str(bicho["nivel"]), 230, y, cor, fonte)
        desenhar_barra_vida(bicho, 230, y + passo - 22, 250)
        mostrar_texto(str(bicho["vida"]) + " / " + str(bicho["vida_max"]), 500, y + passo - 26, cor, fonte_pequena)
        if bicho["vida"] <= 0:
            mostrar_texto("desmaiado", 590, y + passo - 26, VERMELHO, fonte_pequena)
        elif indice == ativo_meu:
            mostrar_texto("em campo", 590, y + passo - 26, AMARELO, fonte_pequena)
        y = y + passo
        indice = indice + 1


# =====================================================================
#                          O CICLO DO JOGO
# =====================================================================

a_correr = True
while a_correr:

    # ------------------------- 1. EVENTOS -------------------------
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            a_correr = False
        if evento.type == pygame.KEYDOWN:
            confirmar = evento.key == pygame.K_RETURN or evento.key == pygame.K_SPACE
            if estado == "menu" and confirmar:
                comecar_jogo()
            elif estado == "mundo":
                tecla_no_mundo(evento.key)
                ao_carregar_tecla(evento.key)
            elif estado == "conversa":
                tecla_na_conversa(evento.key)
            elif estado == "loja":
                tecla_na_loja(evento.key)
            elif estado == "encontro":
                tecla_no_encontro(evento.key)
            elif estado == "batalha":
                tecla_na_batalha(evento.key)
                ao_carregar_tecla(evento.key)
            elif estado == "derrota" and confirmar:
                acordar_em_casa()
            elif estado == "vitoria" and evento.key == pygame.K_r:
                comecar_jogo()

    # ------------------------- 2. LOGICA --------------------------
    if estado == "mundo":
        andar_com_as_setas()
    # (Outra vez o if: o passo pode ter comecado uma batalha.)
    if estado == "mundo":
        a_cada_frame()

    mexer_barras()

    # ------------------------ 3. DESENHAR -------------------------
    if estado == "menu":
        ecra.fill(PRETO)
        mostrar_texto("BICHARADA À SOLTA", 120, 170, AMARELO, fonte_grande)
        mostrar_texto("Os bichos mais portugueses do mundo andam por aí", 135, 260, BRANCO, fonte)
        # Os dois primeiros bichos de BICHOS, sejam eles quais forem.
        modelo = criar_bicho(nomes_dos_bichos[0], NIVEL_INICIAL)
        desenhar_bicho(modelo, 300, 380, 90, 1)
        modelo = criar_bicho(nomes_dos_bichos[1], NIVEL_INICIAL)
        desenhar_bicho(modelo, 500, 380, 90, -1)
        mostrar_texto("Enter para começar", 290, 490, CINZA, fonte)
    elif estado == "encontro":
        desenhar_encontro()
    elif estado == "mundo":
        desenhar_mundo()
    elif estado == "conversa":
        desenhar_conversa()
    elif estado == "loja":
        desenhar_loja()
    elif estado == "batalha":
        desenhar_batalha()
    elif estado == "vitoria":
        ecra.fill(PRETO)
        mostrar_texto("CAMPEÃ(O) DA FEIRA!", 90, 200, AMARELO, fonte_grande)
        mostrar_texto("Ganhaste a todos os treinadores.", 220, 300, BRANCO, fonte)
        mostrar_texto("R para jogar outra vez", 270, 380, CINZA, fonte)
    elif estado == "derrota":
        ecra.fill(PRETO)
        mostrar_texto("A tua equipa desmaiou...", 120, 200, VERMELHO, fonte_grande)
        if batalha_selvagem:
            mostrar_texto("Perdeste contra um bicho à solta.", 220, 300, BRANCO, fonte)
        else:
            mostrar_texto("Perdeste contra " + treinador()["nome"] + ".", 230, 300, BRANCO, fonte)
        mostrar_texto("Enter para acordar em casa da avó", 215, 380, CINZA, fonte)

    # ------------------------- 4. MOSTRAR -------------------------
    pygame.display.flip()

    # ------------------------- 5. ESPERAR -------------------------
    clock.tick(FPS)

pygame.quit()
