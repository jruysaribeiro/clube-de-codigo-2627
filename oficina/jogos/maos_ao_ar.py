# O Maos ao Ar! na Oficina: que coisas se podem escolher, onde esta o
# codigo de cada uma, e o "palco" que mostra so essa coisa a funcionar.
#
# O palco nao e um jogo a parte: e o Maos ao Ar! verdadeiro a correr, ja
# dentro de um nivel, sem titulo, sem treino e sem se poder perder. Por
# isso tudo o que se ve e desenhado pelo codigo do proprio jogo.
#
# Alem de mudar o que la esta, aqui tambem se cria (novo), se apaga (apagar),
# se escolhe de uma lista (lista) e se marcam caixas (caixas): ver essas
# funcoes mais abaixo. Sao as mesmas ferramentas do bicharada.py.
#
# Na Oficina nao ha camara: joga-se com o teclado, no modo que o jogo ja
# tem para isso (o da tecla T). Para o jogo nem tentar ligar a camara, nem
# instalar o mediapipe, pomos a variavel MAOS_AO_AR_SO_TECLADO a "1" antes
# de ele arrancar (ver criar_palco, no fim, e SO_TECLADO no jogo).

import ast
import inspect
import os
import re

import blocos
from jogos import bicharada as base      # as ferramentas de mexer no ficheiro sao as mesmas

NOME = "Mãos ao Ar!"
FICHEIRO = "s14-maos-ao-ar/maos-ao-ar.py"
DESCRICAO = "Um jogo de plataformas. Aqui joga-se com o teclado."

# As instrucoes do jogo, que a pagina mostra a entrada dele:
#   "joga"    como se joga
#   "comeca"  por onde comecar, passo a passo: (o que fazer, o titulo da coisa
#             a abrir, ou None). Com titulo, o passo ganha um botao que a abre.
#   "podes"   o que aqui se pode fazer
#   "nao"     o que nao da, ou da asneira
INSTRUCOES = {
    "joga": "Aqui joga-se com o teclado, sem câmara. O Faísca anda sozinho: as setas viram-no, a seta para baixo "
            "pára-o, Espaço salta, Shift corre e X dispara. Chega à saída de cada nível. No último está o Rei Sucata.",
    "comeca": [
        ("Joga o nível 1 no «Jogar o jogo inteiro», para saberes o que há.", None),
        ("Abre o Faísca e muda-lhe as cores.", "O Faísca"),
        ("Abre «Os números do jogo» e dá-lhe um salto mais alto, ou mais vidas.", "Os números do jogo"),
        ("Abre o nível 1 e troca letras: põe moedas (o) e uma mola (M).", "1. Primeiros passos"),
        ("Abre a Lesma e muda-lhe a vida, a velocidade e a cor.", "Lesma"),
        ("Depois inventa: «+ Novo nível», «+ Novo inimigo», «+ Novo mundo», e as Regras do jogo.", None),
    ],
    "podes": [
        "Desenhar níveis com letras: chão, plataformas, molas, espinhos, lava, moedas e inimigos.",
        "Criar níveis, inimigos e mundos novos, e apagar os que não queres.",
        "Mudar o Faísca e os inimigos: as cores, a vida, a velocidade, o jeito de cada um.",
        "Dar uma imagem e um som teus ao Faísca, ao tiro e a cada inimigo.",
        "Afinar o jogo: a força do salto, a gravidade, as vidas, os textos.",
        "Mudar as regras, e escrever nos Acontecimentos o que acontece quando o Faísca salta, apanha uma moeda...",
    ],
    "nao": [
        "Num nível, todas as linhas têm de ter o mesmo número de letras, e são sempre 12 linhas.",
        "Um nível precisa de um P (onde o Faísca começa) e de um F (a saída).",
        "Para o nível se conseguir passar: a andar salta-se um buraco de 2 quadrados e a correr de 3; "
        "sobe-se no máximo 2 quadrados de cada vez, ou usa-se uma mola.",
        "Cada inimigo tem a sua letra. Uma letra que não é de nenhum inimigo não mostra nada.",
        "Na Oficina não há câmara nem gestos: isso é só no jogo a sério, fora daqui.",
    ],
}

# Uma frase por grupo, para a pagina do jogo dizer o que la ha.
SOBRE_OS_GRUPOS = {
    "Inimigos": "Vida, velocidade, tamanho, cor e jeito. Podes pôr uma imagem e um som teus.",
    "O herói": "As cores do Faísca e do tiro dele, ou uma imagem e sons teus.",
    "Mundos": "As cores de cada mundo, e se o céu tem estrelas.",
    "Afinar o jogo": "Os saltos, as velocidades, as vidas, as cores e os textos.",
    "Regras do jogo": "Aqui mudas a maneira como o jogo se comporta: é programar a sério.",
    "Acontecimentos": "Estão vazios: o que lá escreveres passa a acontecer nesse momento. É aqui que se inventa.",
    "Desenhos": "Como se desenham o Faísca, os inimigos, o mapa, as moedas, os corações e os tiros.",
    "Níveis": "Cada nível é desenhado com letras: muda uma letra e muda o nível.",
}

# Os grupos onde se pode criar uma coisa nova, e o que diz o botao.
CRIAVEIS = {"Inimigos": "Novo inimigo", "Mundos": "Novo mundo", "Níveis": "Novo nível"}

# Pedidos ja escritos para o ajudante, para se perceber o que se pode pedir.
# Nos niveis so ha perguntas: o ajudante engana-se a mexer em mapas de letras.
EXPLICA = "Explica-me esta função linha a linha"
QUE_POSSO = "O que posso fazer aqui?"
SUGESTOES = {
    "inimigo": ["Põe-no mais rápido e com mais vida", "Muda-lhe a cor para roxo", "O que quer dizer cada coisa da ficha?"],
    "heroi": ["Põe o Faísca verde, com o contorno verde-escuro", "Põe o Faísca cor-de-rosa",
              "Como é que ponho uma imagem minha no Faísca?"],
    "tiro": ["Muda a cor do tiro para vermelho", "Põe o tiro azul-claro", "Como é que ponho um som meu no tiro?"],
    "mundo": ["Põe o céu cor de laranja, como ao pôr do sol", "Faz este mundo de noite, com estrelas", "O que é cada cor?"],
    "numeros": ["Faz o Faísca saltar mais alto", "Põe os tiros mais rápidos e a irem mais longe",
                "O que quer dizer cada número?"],
    "cores": ["Muda a cor das moedas para verde", "Põe a lava roxa", "Como é que três números fazem uma cor?"],
    "textos": ["Muda o título do jogo para ROBOT AO AR!", "Inventa outro texto de vitória", "Para que serve cada texto?"],
    "nivel": ["O que quer dizer cada letra do mapa?", "Como é que ponho mais um inimigo neste nível?",
              "Porque é que as linhas têm de ter todas o mesmo tamanho?"],
    "saltar": ["Faz o Faísca saltar mais alto quando vai a correr", "Quero um salto duplo: poder saltar mais uma vez no ar",
               EXPLICA],
    "tocar_num_inimigo": ["Faz o Faísca ressaltar muito mais alto quando pisa um inimigo",
                          "Dá uma moeda por cada inimigo pisado", EXPLICA],
    "acertar_tiro": ["Faz cada tiro tirar 2 de vida", "Quero golpes críticos: às vezes o tiro tira 3 de vida", EXPLICA],
    "mexer_saltador": ["Faz o sapo saltar mais alto", "Faz o sapo fugir do Faísca em vez de ir atrás dele", EXPLICA],
    "mexer_voador": ["Faz o morcego voar mais longe para os lados", "Faz o morcego voar às voltas, num círculo", EXPLICA],
    "mexer_carregador": ["Faz o javali ver o Faísca de mais longe", "Faz o javali nunca ficar tonto", EXPLICA],
    "mexer_canhao": ["Faz o canhão disparar o dobro das vezes", "Faz o canhão disparar duas bolas, uma mais para cima",
                     EXPLICA],
    "tocar_na_mola": ["Faz a mola dar uma moeda de cada vez", "Faz a mola funcionar só de 2 em 2 vezes", EXPLICA],
    "contar_estrelas": ["Dá uma estrela a quem acabar em menos de 30 segundos",
                        "Para a estrela das moedas basta apanhar metade", EXPLICA],
    "mundo_do_nivel": ["Põe três níveis em cada mundo", "Faz os mundos rodarem: um nível em cada um", EXPLICA],
    "ao_comecar_nivel": ["Começa cada nível com o turbo ligado", "Põe uma moeda de prémio à frente do Faísca",
                         QUE_POSSO],
    "ao_acabar_nivel": ["Dá 10 moedas de prémio quando se ganham 3 estrelas", "Solta um fogo de artifício de faíscas",
                        QUE_POSSO],
    "ao_apanhar_coracao": ["Cada coração dá também 5 moedas", "Fica meio segundo invencível quando apanha um coração",
                           QUE_POSSO],
    "ao_disparar": ["Faz um tiro triplo", "Faz o Faísca dar um passo atrás com o coice do tiro", QUE_POSSO],
    "ao_partir_caixote": ["Sai uma moeda de dentro de cada caixote", "Conta os caixotes partidos e diz quantos já vão",
                          QUE_POSSO],
    "ao_saltar": ["Solta faíscas amarelas nos pés quando ele salta", "De 5 em 5 saltos, dá um salto gigante", QUE_POSSO],
    "ao_apanhar_moeda": ["Dá mais um coração de 10 em 10 moedas", "Solta muitas faíscas no sítio da moeda", QUE_POSSO],
    "ao_perder_coracao": ["Dá uma segunda oportunidade: se ficar com 0 corações volta a ter 1, uma vez por nível",
                          "Quando ele perde um coração, perde também 3 moedas", QUE_POSSO],
    "ao_derrotar_inimigo": ["Deixa uma moeda no sítio onde o inimigo caiu", "Dá um coração por cada 3 inimigos derrotados",
                            QUE_POSSO],
    "ao_carregar_tecla": ["A tecla B dá um super salto, mas só 3 vezes por nível", "A tecla G liga e desliga o turbo",
                          QUE_POSSO],
    "a_cada_frame": ["Faz um íman de moedas: as moedas perto do Faísca andam para ele",
                     "Faz o Faísca cair devagar, como um paraquedas", QUE_POSSO],
    "desenhar_robot": ["Põe um chapéu ao Faísca", "Faz o Faísca ficar vermelho quando só tem um coração",
                       "Explica-me este desenho linha a linha"],
    "desenhar_lesma": ["Dá dois olhos à lesma", "Pinta a casca da lesma de azul", "Explica-me este desenho linha a linha"],
    "desenhar_inimigo_novo": ["Dá-lhe dois olhos e uma boca", "Põe-lhe dois chifres",
                              "Explica-me este desenho linha a linha"],
    "desenhar_quadrado": ["Põe flores na relva", "Faz a lava verde", "Explica-me este desenho linha a linha"],
    "desenhar_moeda": ["Faz as moedas quadradas", "Faz as moedas subirem e descerem em vez de rodarem",
                       "Explica-me este desenho linha a linha"],
    "desenhar_coracao": ["Põe um brilho branco no coração", "Troca os corações por pilhas",
                         "Explica-me este desenho linha a linha"],
    "desenhar_tiro": ["Faz o tiro ser uma bola", "Põe um rasto atrás do tiro", "Explica-me este desenho linha a linha"],
}

# As letras que o mapa de um nivel conhece, fora as dos inimigos.
LETRAS_DO_MAPA = ".#=%BM^~ohPFc"
JEITOS = ["andar", "saltar", "voar", "carregar", "canhao", "chefe"]
# Os inimigos que o jogo desenha com desenhar_inimigo_novo: os que nao tem
# uma destas letras nem um destes jeitos (ver desenhar_inimigo, no jogo).
LETRAS_COM_DESENHO = "ae"
JEITOS_COM_DESENHO = ["saltar", "voar", "carregar", "canhao", "chefe"]
# Em que lista do jogo esta cada tipo de coisa.
LISTAS = {"inimigo": "INIMIGOS", "mundo": "MUNDOS", "nivel": "NIVEIS"}

# Os grupos de constantes que se abrem de uma vez: da primeira a ultima.
NUMEROS = ["VIDAS", "VEL_ANDAR", "VEL_CORRER", "GRAVIDADE", "FORCA_SALTO", "FORCA_MOLA",
           "TEMPO_ENTRE_TIROS", "VEL_TIRO", "ALCANCE_TIRO", "TEMPO_COIOTE", "TOLERANCIA_SALTO"]
CORES = ["BRANCO", "PRETO", "CINZA", "AMARELO", "VERMELHO", "VERDE", "AZUL", "LARANJA",
         "COR_HEROI", "COR_HEROI_ESCURA", "COR_TIRO", "COR_MOEDA", "COR_MADEIRA",
         "COR_PONTE_PODRE", "COR_LAVA", "COR_ESPINHO"]
TEXTOS = ["TITULO", "SUBTITULO", "NOME_DO_HEROI", "TEXTO_VITORIA"]
SONS = ["SOM_DO_SALTO", "SOM_DO_TIRO"]
GRUPOS = {
    "heroi": ["IMAGEM_DO_HEROI", "COR_HEROI", "COR_HEROI_ESCURA", "SOM_DO_SALTO"],
    "tiro": ["COR_TIRO", "SOM_DO_TIRO"],
    "numeros": NUMEROS,
    "cores": CORES,
    "textos": TEXTOS,
}
TITULOS = {"numeros": "Os números do jogo", "cores": "As cores", "textos": "Os textos", "tiro": "O tiro"}
# A constante que diz o nome do WAV de cada um destes.
SOM_DE = {"heroi": "SOM_DO_SALTO", "tiro": "SOM_DO_TIRO"}

# As regras: funcoes do jogo que se podem mudar. Para cada uma, o titulo que
# aparece na Oficina, e o que ela recebe (o jogo chama-a assim, por isso nao
# pode mudar).
REGRAS = {
    "saltar": ("Como o Faísca salta", []),
    "tocar_num_inimigo": ("Quando o Faísca toca num inimigo", ["inimigo", "por_cima"]),
    "acertar_tiro": ("Quando um tiro acerta num inimigo", ["inimigo", "tiro"]),
    "mexer_saltador": ("Como se mexe um inimigo que salta", ["inimigo", "velocidade"]),
    "mexer_voador": ("Como se mexe um inimigo que voa", ["inimigo", "velocidade"]),
    "mexer_carregador": ("Como se mexe um inimigo que carrega", ["inimigo", "velocidade"]),
    "mexer_canhao": ("Como dispara um canhão", ["inimigo", "velocidade"]),
    "tocar_na_mola": ("O que faz uma mola", []),
    "contar_estrelas": ("Quantas estrelas dá um nível", []),
    "mundo_do_nivel": ("Em que mundo se passa cada nível", ["numero"]),
}
INICIO_DAS_REGRAS = "# --- As regras do jogo ---"

# Os acontecimentos: funcoes que o jogo chama em certos momentos, e que vem
# vazias. E os desenhos. Tudo isto sao funcoes, como as regras.
ACONTECIMENTOS = {
    "ao_saltar": ("Quando o Faísca salta", []),
    "ao_apanhar_moeda": ("Quando apanha uma moeda", ["x", "y"]),
    "ao_perder_coracao": ("Quando perde um coração", []),
    "ao_derrotar_inimigo": ("Quando um inimigo é derrotado", ["inimigo"]),
    "ao_carregar_tecla": ("Quando se carrega numa tecla", ["tecla"]),
    "a_cada_frame": ("A cada frame", []),
    "ao_comecar_nivel": ("Quando um nível começa", []),
    "ao_acabar_nivel": ("Quando se acaba um nível", ["estrelas"]),
    "ao_apanhar_coracao": ("Quando apanha um coração", ["x", "y"]),
    "ao_disparar": ("Quando o Faísca dispara", ["tiro"]),
    "ao_partir_caixote": ("Quando um caixote se parte", ["coluna", "linha"]),
}
INICIO_DOS_ACONTECIMENTOS = "# --- Os acontecimentos ---"
DESENHOS = {
    "desenhar_robot": ("O desenho do Faísca", ["x", "y", "v"]),
    "desenhar_lesma": ("O desenho da Lesma", ["inimigo", "x", "y", "cor"]),
    "desenhar_inimigo_novo": ("O desenho de um inimigo novo", ["inimigo", "x", "y", "cor"]),
    "desenhar_quadrado": ("Os quadrados do mapa", ["letra", "coluna", "linha", "x", "y"]),
    "desenhar_moeda": ("O desenho de uma moeda", ["x", "y", "atraso"]),
    "desenhar_coracao": ("O desenho de um coração", ["x", "y", "tamanho", "cor"]),
    "desenhar_tiro": ("O desenho de um tiro", ["tiro", "x", "y"]),
}
INICIO_DOS_DESENHOS = "# --- Os desenhos ---"

# tipo da escolha -> (as funcoes desse tipo, o grupo onde aparecem, as
# explicacoes gerais que se juntam a ajuda de cada uma)
FUNCOES = {
    "regra": (REGRAS, "Regras do jogo", [INICIO_DAS_REGRAS]),
    "evento": (ACONTECIMENTOS, "Acontecimentos", [INICIO_DOS_ACONTECIMENTOS, INICIO_DAS_REGRAS]),
    "desenho": (DESENHOS, "Desenhos", [INICIO_DOS_DESENHOS]),
}

# Cada numero: (nome, minimo, maximo, tem de ser inteiro)
LIMITES = [
    ("VIDAS", 1, 10, True),
    ("VEL_ANDAR", 0, 40, False),
    ("VEL_CORRER", 0, 40, False),
    ("GRAVIDADE", 0.1, 5, False),
    ("FORCA_SALTO", 0, 40, False),
    ("FORCA_MOLA", 0, 60, False),
    ("TEMPO_ENTRE_TIROS", 1, 600, True),
    ("VEL_TIRO", 0, 100, False),
    ("ALCANCE_TIRO", 0, 300, False),
    ("TEMPO_COIOTE", 0, 600, False),
    ("TOLERANCIA_SALTO", 0, 600, False),
]

TECLAS = "O Faísca anda sozinho. Setas: virar. Seta para baixo: parar. Espaço: saltar. Shift: correr. X: disparar. "
DICAS = {
    "inimigo": TECLAS + "Ele está atrás de um caixote: salta-o, ou parte-o com um tiro. "
               "«Escolher o jeito» mostra as maneiras de ele se portar.",
    "heroi": TECLAS + "A imagem dele deve estar a olhar para a direita: o jogo vira-a quando ele anda para a esquerda.",
    "nivel": TECLAS + "Cada letra é um quadrado: muda uma e vê o nível mudar, no jogo e no mapa pequeno. "
             "As teclas Q e E levam o Faísca um ecrã para trás e para a frente; a tecla M esconde o mapa pequeno.",
    "mundo": TECLAS + "Estás no primeiro nível deste mundo, com as cores que escreveres. "
             "Q e E: andar um ecrã para trás e para a frente.",
    "numeros": TECLAS + "A pista tem buracos de 2 e de 3 quadrados, um muro de 2 e uma mola, "
               "para veres o que cada número muda. Q e E: andar um ecrã.",
    "cores": TECLAS + "Está aqui um bocadinho de tudo o que tem cor. A cor do tiro só se vê quando disparas.",
    "textos": "Vês o título como ele aparece no jogo; os outros dois textos estão na faixa de baixo. "
              "Aqui o jogo não começa.",
    "tiro": TECLAS + "A cor do tiro vê-se quando disparas (X). O som ouve-se no jogo inteiro.",
}
# As funcoes tem cada uma a sua dica, porque cada uma tem o seu palco.
JOGA_TU = ("Setas: virar. Seta para baixo: parar. Espaço: saltar. X: disparar. "
           "Clica no jogo para ele ouvir as teclas. ")
VAZIO = "Está vazio: tira o pass e escreve o que queres que aconteça. "
DICAS_DAS_FUNCOES = {
    "saltar": "Isto é uma regra do jogo: muda-a e o Faísca passa a saltar de outra maneira. "
              "Quando mudas o código ele dá um salto sozinho, para veres logo. " + JOGA_TU + "Q e E: andar um ecrã.",
    "tocar_num_inimigo": "Isto é uma regra do jogo. O Faísca vai contra os inimigos sozinho: vê o que acontece "
                         "de lado, e salta-lhes para cima (Espaço) para veres a diferença. Aqui os corações voltam sempre.",
    "acertar_tiro": "Isto é uma regra do jogo. Aqui o Faísca fica parado e dispara sozinho, para veres logo o que "
                    "faz um tiro certeiro. Com as setas carregadas ele anda. Os inimigos voltam quando caem todos.",
    "mexer_saltador": "Isto é uma regra do jogo: muda-a e os inimigos que saltam passam a mexer-se de outra maneira. "
                      + TECLAS + "O Faísca está atrás de um caixote.",
    "mexer_voador": "Isto é uma regra do jogo: muda-a e os inimigos que voam passam a mexer-se de outra maneira. "
                    + TECLAS + "O Faísca está atrás de um caixote.",
    "ao_saltar": VAZIO + "Quando mudas o código o Faísca volta ao início e dá um salto sozinho. " + JOGA_TU,
    "ao_apanhar_moeda": VAZIO + "Quando mudas o código o Faísca volta ao início e vai apanhar as três moedas. "
                        "As moedas voltam quando acabam. " + JOGA_TU,
    "ao_perder_coracao": VAZIO + "O Faísca anda sozinho contra a lesma e para a lava, por isso perde corações "
                         "depressa. Quando fica sem nenhum, voltam todos. " + JOGA_TU,
    "ao_derrotar_inimigo": VAZIO + "Aqui o Faísca dispara sozinho contra a lesma, e ela volta pouco depois de cair. "
                           + JOGA_TU,
    "ao_carregar_tecla": VAZIO + "Depois clica no jogo e carrega na tua tecla. " + JOGA_TU,
    "a_cada_frame": VAZIO + "Corre 60 vezes por segundo. A faixa de baixo mostra o que está na memoria. " + JOGA_TU,
    "mexer_carregador": "Isto é uma regra do jogo: muda-a e os inimigos que carregam passam a portar-se de outra "
                        "maneira. " + TECLAS + "O Faísca está atrás de um caixote.",
    "mexer_canhao": "Isto é uma regra do jogo: muda-a e os canhões passam a disparar de outra maneira. "
                    + TECLAS + "O Faísca está atrás de um caixote.",
    "tocar_na_mola": "Isto é uma regra do jogo. O Faísca vai sozinho contra a mola, e volta ao início de vez em "
                     "quando, para veres logo o que ela faz. " + JOGA_TU,
    "contar_estrelas": "Isto é uma regra do jogo. O Faísca vai sozinho até à saída, e o ecrã das estrelas mostra "
                       "quantas a tua regra dá. A faixa de baixo diz quantas dava agora. Depois recomeça. " + JOGA_TU,
    "mundo_do_nivel": "Isto é uma regra do jogo. A faixa de baixo diz que mundo calha a cada nível com a tua regra, "
                      "e o céu vai mostrando o mundo de cada um, à vez. " + JOGA_TU,
    "ao_comecar_nivel": VAZIO + "Aqui o nível recomeça sozinho de 5 em 5 segundos, para o veres acontecer. " + JOGA_TU,
    "ao_acabar_nivel": VAZIO + "O Faísca vai sozinho até à saída, e depois recomeça. " + JOGA_TU,
    "ao_apanhar_coracao": VAZIO + "O Faísca vai contra a lesma, perde um coração e apanha o que está mais à "
                          "frente. Depois recomeça. " + JOGA_TU,
    "ao_disparar": VAZIO + "Aqui o Faísca dispara sozinho, um tiro por segundo. " + JOGA_TU,
    "ao_partir_caixote": VAZIO + "Aqui o Faísca dispara sozinho contra os caixotes, e eles voltam pouco depois. "
                         + JOGA_TU,
    "desenhar_quadrado": "Isto desenha o chão, as plataformas, os caixotes, os espinhos, a lava e as molas: "
                         "está aqui um de cada. Muda o desenho e vês logo. " + TECLAS,
    "desenhar_moeda": "Isto é o desenho de uma moeda: muda-o e vês logo, no jogo e aumentado no canto.",
    "desenhar_coracao": "Isto é o desenho de um coração: muda-o e vês logo, nos corações do canto do ecrã, no que "
                        "está no nível e aumentado no canto.",
    "desenhar_tiro": "Isto é o desenho de um tiro: muda-o e vês logo, aumentado no canto e nos tiros que o Faísca "
                     "dispara sozinho.",
    "desenhar_robot": "Isto é o desenho do Faísca: muda-o e vês logo, no jogo e aumentado no canto. "
                      "Experimenta mudar um número, ou acrescentar um círculo. " + TECLAS,
    "desenhar_lesma": "Isto é o desenho da Lesma: muda-o e vês logo, no jogo e aumentado no canto. "
                      "Experimenta mudar um número, ou acrescentar um círculo.",
    "desenhar_inimigo_novo": "É assim que aparece um inimigo que criares com o botão Novo inimigo. "
                             "Muda o desenho e vês logo, no jogo e aumentado no canto.",
}
AJUDAS = {
    "numeros": "Os números que mandam no Faísca. As velocidades são em pixeis por frame "
               "(60 frames = um segundo) e cada quadrado do mapa tem 48 pixeis.",
    "textos": "O que o jogo escreve no ecrã. Os textos ficam entre aspas.",
}
# O que se junta a ajuda quando a coisa pode ter um som.
AJUDA_DO_SOM = ('O "som" é o nome de um ficheiro WAV. Com o botão do som, por cima do código, gravas ou escolhes '
                "um, e o jogo passa a tocá-lo em vez do som de sempre.")


# =====================================================================
#                    ONDE ESTA O CODIGO DE CADA COISA
# =====================================================================

def _valor(dicionario, chave):
    # Dentro de um {...} escrito no codigo, o valor simples (texto, numero,
    # True...) guardado em "chave". None se nao houver.
    if not isinstance(dicionario, ast.Dict):
        return None
    for k, v in zip(dicionario.keys, dicionario.values):
        if blocos.texto_constante(k) == chave and isinstance(v, ast.Constant):
            return v.value
    return None


def _fichas(arvore, nome):
    # As entradas de INIMIGOS, MUNDOS ou NIVEIS: [(chave, ficha, inicio, fim), ...].
    # Numa lista nao ha chave (fica None). Devolve [] se nao der para as separar.
    no = blocos.instrucao(arvore, nome)
    partes = blocos.entradas(no) if no is not None else None
    if not partes:
        return []
    if isinstance(no.value, ast.Dict):
        valores = no.value.values
    else:
        valores = no.value.elts
    return [(parte if isinstance(no.value, ast.Dict) else None, ficha, inicio, fim)
            for (parte, inicio, fim), ficha in zip(partes, valores)]


def _nome_do_nivel(fichas, i):
    # Como o jogo o mostra: se o primeiro nivel for o recreio ("treino":
    # True), esse e o 0 e os outros contam a partir do 1.
    numero = i + 1
    if _valor(fichas[0][1], "treino") is True:
        numero = i
    return str(numero) + ". " + str(_valor(fichas[i][1], "nome") or "Nível sem nome")


def _constantes(arvore, nomes):
    # As instrucoes "NOME = ..." que existem, das pedidas.
    nos = [blocos.instrucao(arvore, nome) for nome in nomes]
    return [no for no in nos if no is not None]


def _sem_tracos(texto):
    # Uma explicacao tirada do ficheiro, sem os tracos dos titulos.
    ajuda = []
    for linha in texto.split("\n"):
        if linha.startswith("---"):
            linha = linha.strip("- ")
        if linha != "" or (len(ajuda) > 0 and ajuda[-1] != ""):
            ajuda.append(linha)
    return "\n".join(ajuda).strip("\n")


def _ajuda(linhas, primeira_linha):
    # A explicacao que o ficheiro traz por cima de uma instrucao.
    return _sem_tracos(blocos.ajuda_acima(linhas, primeira_linha))


def escolhas(fonte):
    arvore = ast.parse(fonte)
    lista = []

    for i, (chave, ficha, _, _) in enumerate(_fichas(arvore, "INIMIGOS")):
        nome = _valor(ficha, "nome") or blocos.texto_constante(chave) or "Inimigo " + str(i + 1)
        lista.append({"id": "inimigo:" + str(i), "grupo": "Inimigos", "titulo": str(nome)})

    if len(_constantes(arvore, GRUPOS["heroi"])) > 0:
        no = blocos.instrucao(arvore, "NOME_DO_HEROI")
        nome = blocos.texto_constante(no.value) if no is not None else None
        lista.append({"id": "heroi", "grupo": "O herói", "titulo": "O " + (nome or "herói")})
    if len(_constantes(arvore, GRUPOS["tiro"])) > 0:
        lista.append({"id": "tiro", "grupo": "O herói", "titulo": TITULOS["tiro"]})

    for i, (_, ficha, _, _) in enumerate(_fichas(arvore, "MUNDOS")):
        nome = _valor(ficha, "nome") or "Mundo " + str(i + 1)
        lista.append({"id": "mundo:" + str(i), "grupo": "Mundos", "titulo": str(nome)})

    for tipo in ("numeros", "cores", "textos"):
        if len(_constantes(arvore, GRUPOS[tipo])) > 0:
            lista.append({"id": tipo, "grupo": "Afinar o jogo", "titulo": TITULOS[tipo]})

    for tipo in FUNCOES:
        funcoes, grupo, _ = FUNCOES[tipo]
        for nome in funcoes:
            if blocos.funcao(arvore, nome) is not None:
                lista.append({"id": tipo + ":" + nome, "grupo": grupo, "titulo": funcoes[nome][0]})

    fichas = _fichas(arvore, "NIVEIS")
    for i in range(len(fichas)):
        lista.append({"id": "nivel:" + str(i), "grupo": "Níveis", "titulo": _nome_do_nivel(fichas, i)})
    return lista


def regiao(fonte, escolha):
    # Devolve {"inicio", "fim", "ajuda", "titulo", "dica", "imagem", "som",
    # "sugestoes"} ou None. "imagem" e o nome do PNG que essa coisa usa (None
    # se nao usa nenhum): e com ele que a Oficina sabe onde guardar a imagem
    # que a crianca escolher. "som" e o mesmo, para o WAV.
    arvore = ast.parse(fonte)
    linhas = fonte.split("\n")
    tipo, _, numero = escolha.partition(":")
    if tipo in FUNCOES:
        # Uma regra, um acontecimento ou um desenho: e uma funcao inteira. A
        # ajuda junta o que o ficheiro diz sobre ela ao que se pode usar
        # dentro de qualquer funcao desse genero.
        funcoes, _, gerais = FUNCOES[tipo]
        no = blocos.funcao(arvore, numero) if numero in funcoes else None
        if no is None:
            return None
        ajuda = _ajuda(linhas, no.lineno)
        for inicio in gerais:
            geral = _sem_tracos(blocos.comentarios_a_partir_de(linhas, inicio))
            if geral and geral != ajuda:
                ajuda = ajuda + "\n\n" + geral
        return {"inicio": no.lineno, "fim": no.end_lineno, "ajuda": ajuda, "dica": DICAS_DAS_FUNCOES[numero],
                "titulo": funcoes[numero][0], "imagem": None, "som": None, "sugestoes": SUGESTOES[numero]}
    if tipo not in DICAS:
        return None
    resposta = {"dica": DICAS[tipo], "imagem": None, "som": None, "sugestoes": SUGESTOES[tipo]}

    if tipo in GRUPOS:
        # Varias constantes seguidas: da primeira linha a ultima.
        nos = _constantes(arvore, GRUPOS[tipo])
        if len(nos) == 0:
            return None
        inicio = min(no.lineno for no in nos)
        fim = max(no.end_lineno for no in nos)
        titulo = TITULOS.get(tipo)
        if tipo == "heroi":
            no = blocos.instrucao(arvore, "NOME_DO_HEROI")
            titulo = "O " + ((blocos.texto_constante(no.value) if no is not None else None) or "herói")
            no = blocos.instrucao(arvore, "IMAGEM_DO_HEROI")
            if no is not None:
                resposta["imagem"] = blocos.texto_constante(no.value)
        ajuda = AJUDAS.get(tipo) or _ajuda(linhas, inicio)
        if tipo in SOM_DE:
            no = blocos.instrucao(arvore, SOM_DE[tipo])
            if no is not None:
                resposta["som"] = blocos.texto_constante(no.value)
                ajuda = ajuda + "\n\n" + AJUDA_DO_SOM
        resposta.update(inicio=inicio, fim=fim, titulo=titulo, ajuda=ajuda)
        return resposta

    fichas = _fichas(arvore, LISTAS[tipo])
    if not numero.isdigit() or int(numero) >= len(fichas):
        return None
    chave, ficha, inicio, fim = fichas[int(numero)]
    if tipo == "nivel":
        titulo = _nome_do_nivel(fichas, int(numero))
    else:
        titulo = _valor(ficha, "nome") or blocos.texto_constante(chave) or escolha
    if tipo == "inimigo":
        resposta["imagem"] = blocos.valor_da_chave(ficha, "imagem")
        resposta["som"] = blocos.valor_da_chave(ficha, "som")
        resposta["lista"] = "Escolher o jeito"
    # O que dizem os botoes de apagar esta coisa, e se ha caixas para marcar
    # (ver apagar e caixas, mais abaixo).
    resposta["apagar"] = {"inimigo": "Apagar este inimigo", "mundo": "Apagar este mundo",
                          "nivel": "Apagar este nível"}[tipo]
    resposta["caixas"] = True
    no = blocos.instrucao(arvore, LISTAS[tipo])
    ajuda = _ajuda(linhas, no.lineno)
    # As letras que ha agora, a cabeca: a explicacao que o ficheiro traz so
    # conhece os inimigos que vinham com o jogo, e nao os que foram criados.
    inimigos = [(blocos.texto_constante(letra), _valor(dele, "nome") or "sem nome")
                for letra, dele, _, _ in _fichas(arvore, "INIMIGOS") if blocos.texto_constante(letra)]
    if tipo == "nivel" and inimigos:
        ajuda = ("OS INIMIGOS QUE HA AGORA, e a letra de cada um no mapa:\n"
                 + "\n".join("  " + letra + "   " + str(nome) for letra, nome in inimigos)
                 + "\nEscreve a letra de um no mapa, no sitio onde o queres.\n\nCOMO FUNCIONA UM NIVEL:\n" + ajuda)
    if tipo == "inimigo" and blocos.texto_constante(chave):
        letra = blocos.texto_constante(chave)
        onde = [_nome_do_nivel(_fichas(arvore, "NIVEIS"), i) for i, (_, nivel, _, _) in enumerate(_fichas(arvore, "NIVEIS"))
                if any(letra in fila.value for fila in _mapa(nivel) or [])]
        ajuda = ("A LETRA DESTE INIMIGO NO MAPA E: " + letra + "\n"
                 + ("Esta nos niveis: " + ", ".join(str(nome) for nome in onde[:8]) + (" ..." if len(onde) > 8 else "")
                    if onde else "Ainda nao esta em nenhum nivel: abre um nivel e escreve a letra " + letra + " onde o quiseres.")
                 + "\n\n" + ajuda)
    resposta.update(inicio=inicio, fim=fim, titulo=str(titulo), ajuda=ajuda)
    return resposta


# =====================================================================
#                        CRIAR UMA COISA NOVA
# =====================================================================
# Um inimigo novo e um nivel novo nascem como copia de um que ja la esta (o
# mais simples), com outro nome, e ficam no fim da lista. Devolve o ficheiro
# inteiro ja com a coisa nova, a escolha a abrir, e uma frase a contar o que
# se fez.

# As letras que um inimigo novo pode ter no mapa, por ordem de preferencia.
LETRAS_LIVRES = "nbdgikpqruvwyzfl"


def _nome_livre(base, existentes):
    nome = base
    numero = 2
    while nome in existentes:
        nome = base + " " + str(numero)
        numero = numero + 1
    return nome


def _ficheiro(nome):
    # "Inimigo novo 2" -> "inimigo-novo-2"
    return nome.lower().replace(" ", "-")


def _letras(linha, bytes_):
    # O Python conta as colunas em bytes: com acentos nao e o mesmo que letras.
    return len(linha.encode("utf-8")[:bytes_].decode("utf-8"))


def _mapa(ficha):
    # As linhas do "mapa" de um nivel, como estao escritas no codigo: a lista
    # dos textos entre aspas. None se nao der para as ler assim.
    if not isinstance(ficha, ast.Dict):
        return None
    for k, v in zip(ficha.keys, ficha.values):
        if blocos.texto_constante(k) == "mapa" and isinstance(v, ast.List):
            if all(blocos.texto_constante(fila) is not None for fila in v.elts):
                return v.elts
    return None


def _letras_usadas(arvore):
    # Todas as letras que aparecem nos mapas dos niveis.
    usadas = set()
    for _, ficha, _, _ in _fichas(arvore, "NIVEIS"):
        for fila in _mapa(ficha) or []:
            usadas.update(fila.value)
    return usadas


def _acrescentar(linhas, copia, ultima):
    # Poe as linhas da copia a seguir a ultima entrada da lista, com as
    # virgulas que forem precisas. Devolve o ficheiro inteiro.
    copia[-1] = copia[-1].rstrip()
    if not copia[-1].endswith(","):
        copia[-1] = copia[-1] + ","
    if not linhas[ultima - 1].rstrip().endswith(","):
        linhas[ultima - 1] = linhas[ultima - 1].rstrip() + ","
    return "\n".join(linhas[:ultima] + copia + linhas[ultima:])


def _por_no_mapa(fonte, letra):
    # Escreve a letra no chao do primeiro nivel, uns quadrados a frente do
    # Faisca: sem isto o inimigo novo existia mas nunca aparecia no jogo.
    # Devolve o ficheiro e o nome desse nivel (None se nao houve sitio).
    fichas = _fichas(ast.parse(fonte), "NIVEIS")
    filas = _mapa(fichas[0][1]) if fichas else None
    if not filas:
        return fonte, None
    textos = [fila.value for fila in filas]
    linhas = fonte.split("\n")
    for f in range(len(textos) - 1):
        if "P" not in textos[f]:
            continue
        for c in range(textos[f].index("P") + 12, len(textos[f]) - 1):
            livre = textos[f][c - 1:c + 2] == "..." and (f == 0 or textos[f - 1][c:c + 1] == ".")
            if not livre or textos[f + 1][c - 1:c + 2] != "###":
                continue
            # O sitio da letra na linha do ficheiro: a seguir as aspas.
            linha = linhas[filas[f].lineno - 1]
            aspas = _letras(linha, filas[f].col_offset)
            if filas[f].lineno != filas[f].end_lineno or linha[aspas + 1:aspas + 1 + len(textos[f])] != textos[f]:
                return fonte, None
            sitio = aspas + 1 + c
            linhas[filas[f].lineno - 1] = linha[:sitio] + letra + linha[sitio + 1:]
            return "\n".join(linhas), _valor(fichas[0][1], "nome") or "sem nome"
    return fonte, None


def _novo_inimigo(fonte):
    arvore = ast.parse(fonte)
    linhas = fonte.split("\n")
    fichas = _fichas(arvore, "INIMIGOS")
    if not fichas:
        raise ValueError("não encontrei os INIMIGOS no ficheiro.")
    ocupadas = _letras_usadas(arvore) | set(LETRAS_DO_MAPA)
    ocupadas.update(blocos.texto_constante(chave) or "" for chave, _, _, _ in fichas)
    livres = [letra for letra in LETRAS_LIVRES if letra not in ocupadas]
    if not livres:
        raise ValueError("já não há letras livres para mais um inimigo.")
    letra = livres[0]
    nome = _nome_livre("Inimigo novo", [_valor(ficha, "nome") for _, ficha, _, _ in fichas])

    # A copia: a ficha do primeiro, com a letra, o nome, a imagem e o som novos.
    chave, ficha, inicio, fim = fichas[0]
    antigo = _valor(ficha, "nome") or "primeiro"
    copia = linhas[inicio - 1:fim]
    onde = _letras(copia[0], chave.col_offset)
    ate = _letras(copia[0], chave.end_col_offset)
    copia[0] = copia[0][:onde] + '"' + letra + '"' + copia[0][ate:]
    texto = "\n".join(copia)
    texto = re.sub(r'"nome":\s*"[^"]*"', '"nome": "' + nome + '"', texto, count=1)
    corpo = blocos.corpo_livre("\n".join(linhas), _ficheiro(nome))      # ficheiros so dele
    texto = re.sub(r'"imagem":\s*"[^"]*"', '"imagem": "' + corpo + '.png"', texto)
    texto = re.sub(r'"som":\s*"[^"]*"', '"som": "' + corpo + '.wav"', texto)
    nova = _acrescentar(linhas, texto.split("\n"), fichas[-1][3])

    nova, nivel = _por_no_mapa(nova, letra)
    aviso = 'Criei o "' + nome + '", uma cópia de "' + str(antigo) + '", com a letra "' + letra + '". '
    if nivel is not None:
        aviso = aviso + 'Pus um no primeiro nível ("' + str(nivel) + '"), perto do início. '
    aviso = aviso + "Em Níveis, escreve " + letra + " no mapa onde quiseres mais."
    return nova, "inimigo:" + str(len(fichas)), aviso


def _novo_nivel(fonte):
    arvore = ast.parse(fonte)
    linhas = fonte.split("\n")
    fichas = _fichas(arvore, "NIVEIS")
    if not fichas:
        raise ValueError("não encontrei os NIVEIS no ficheiro.")
    # Copia-se o primeiro nivel a serio (o recreio nao conta).
    modelo = 0
    for i in range(len(fichas)):
        if _valor(fichas[i][1], "treino") is not True:
            modelo = i
            break
    _, ficha, inicio, fim = fichas[modelo]
    antigo = _valor(ficha, "nome") or "primeiro"
    nome = _nome_livre("Nível novo", [_valor(f, "nome") for _, f, _, _ in fichas])
    texto = "\n".join(linhas[inicio - 1:fim])
    texto = re.sub(r'"nome":\s*"[^"]*"', '"nome": "' + nome + '"', texto, count=1)
    texto = re.sub(r'"dica":\s*"[^"]*"', '"dica": "Um nível só teu. Muda-lhe as letras!"', texto, count=1)
    texto = re.sub(r'"treino":\s*True', '"treino": False', texto)
    ultimo = _valor(fichas[-1][1], "nome") or "último"
    nova = _acrescentar(linhas, texto.split("\n"), fichas[-1][3])
    numero = _nome_do_nivel(_fichas(ast.parse(nova), "NIVEIS"), len(fichas)).split(".")[0]
    aviso = ('Criei o "' + nome + '", uma cópia de "' + str(antigo) + '". É o nível ' + numero
             + ', o último, a seguir a "' + str(ultimo) + '". '
             "Em Jogar o jogo inteiro, escolhe-o no título com a seta para a direita.")
    return nova, "nivel:" + str(len(fichas)), aviso


def _novo_mundo(fonte):
    # Uma copia do primeiro mundo, com outro nome, no fim da lista. Os mundos
    # nao tem os niveis la dentro: e a regra mundo_do_nivel que diz que niveis
    # se passam em cada um (como esta, cinco em cada, por ordem).
    arvore = ast.parse(fonte)
    linhas = fonte.split("\n")
    fichas = _fichas(arvore, "MUNDOS")
    if not fichas:
        raise ValueError("não encontrei os MUNDOS no ficheiro.")
    _, ficha, inicio, fim = fichas[0]
    antigo = _valor(ficha, "nome") or "primeiro"
    nome = _nome_livre("Mundo novo", [_valor(f, "nome") for _, f, _, _ in fichas])
    texto = "\n".join(linhas[inicio - 1:fim])
    texto = re.sub(r'"nome":\s*"[^"]*"', '"nome": "' + nome + '"', texto, count=1)
    nova = _acrescentar(linhas, texto.split("\n"), fichas[-1][3])
    posicao = len(fichas)
    niveis = _fichas(arvore, "NIVEIS")
    quantos = len(niveis)
    if niveis and _valor(niveis[0][1], "treino") is True:
        quantos = quantos - 1
    aviso = ('Criei o "' + nome + '", uma cópia de "' + str(antigo) + '". É o mundo ' + str(posicao + 1)
             + ": com a regra de sempre, passam-se lá os níveis " + str(posicao * 5 + 1) + " a "
             + str(posicao * 5 + 5) + ". ")
    if quantos <= posicao * 5:
        aviso = (aviso + "Ainda só há " + str(quantos) + " níveis: cria mais, ou muda a regra "
                 "«Em que mundo se passa cada nível». Aqui, ao lado do código, já o vês.")
    else:
        aviso = aviso + "Muda-lhe o nome e as cores."
    return nova, "mundo:" + str(posicao), aviso


def novo(fonte, grupo):
    if grupo == "Inimigos":
        return _novo_inimigo(fonte)
    if grupo == "Níveis":
        return _novo_nivel(fonte)
    if grupo == "Mundos":
        return _novo_mundo(fonte)
    raise ValueError("aqui não dá para criar isso.")


# =====================================================================
#                          APAGAR UMA COISA
# =====================================================================
# Um inimigo, um mundo ou um nivel saem do jogo. Um inimigo sai tambem dos
# mapas dos niveis (fica ar onde ele estava). Tem de sobrar sempre o que o
# jogo precisa para correr. Devolve o ficheiro inteiro ja sem a coisa, e uma
# frase a contar o que se fez.

def _tirar_dos_mapas(arvore, linhas, letra):
    # As trocas a fazer (ver o _aplicar do bicharada.py) para a letra de um
    # inimigo passar a ar em todos os mapas, e quantas vezes la estava.
    trocas = []
    quantos = 0
    for _, ficha, _, _ in _fichas(arvore, "NIVEIS"):
        for fila in _mapa(ficha) or []:
            if letra not in fila.value or fila.lineno != fila.end_lineno:
                continue
            escrito = linhas[fila.lineno - 1]
            onde = _letras(escrito, fila.col_offset) + 1
            if escrito[onde:onde + len(fila.value)] != fila.value:
                continue
            quantos = quantos + fila.value.count(letra)
            trocas.append((fila.lineno, onde, onde + len(fila.value), fila.value.replace(letra, ".")))
    return trocas, quantos


def apagar(fonte, escolha):
    tipo, _, numero = escolha.partition(":")
    arvore = ast.parse(fonte)
    linhas = fonte.split("\n")
    fichas = _fichas(arvore, LISTAS[tipo]) if tipo in LISTAS else []
    if not numero.isdigit() or int(numero) >= len(fichas):
        raise ValueError("isso não se pode apagar.")
    indice = int(numero)
    chave, ficha, inicio, fim = fichas[indice]
    nome = str(_valor(ficha, "nome") or "sem nome")
    cortes = [(inicio, fim)]
    trocas = []

    if tipo == "inimigo":
        if len(fichas) < 2:
            raise ValueError("tem de haver pelo menos um inimigo.")
        letra = blocos.texto_constante(chave) or ""
        aviso = 'Apaguei o "' + nome + '" (a letra ' + letra + ")."
        if len(letra) == 1:
            trocas, quantos = _tirar_dos_mapas(arvore, linhas, letra)
            if quantos == 1:
                aviso = aviso + " Havia um num nível: ficou ar no lugar dele."
            elif quantos > 1:
                aviso = aviso + " Havia " + str(quantos) + " nos níveis: ficou ar no lugar deles."
        return base._aplicar(linhas, cortes, trocas), aviso

    if tipo == "mundo":
        if len(fichas) < 2:
            raise ValueError("tem de haver pelo menos um mundo.")
        aviso = ('Apaguei o mundo "' + nome + '". Os mundos a seguir passaram um lugar para trás, e os níveis '
                 "que lá se passavam ficam agora noutro mundo.")
        return base._aplicar(linhas, cortes, trocas), aviso

    a_serio = [i for i in range(len(fichas)) if _valor(fichas[i][1], "treino") is not True]
    if len(fichas) < 2 or a_serio == [indice]:
        raise ValueError("tem de ficar pelo menos um nível a sério (que não seja o recreio).")
    aviso = 'Apaguei o nível "' + nome + '".'
    if indice < len(fichas) - 1:
        aviso = aviso + " Os níveis a seguir passaram a ter o número abaixo, e podem ter mudado de mundo."
    return base._aplicar(linhas, cortes, trocas), aviso


# =====================================================================
#              O QUE SE ESCOLHE DE UMA LISTA, E O QUE SE MARCA
# =====================================================================
# Como no bicharada.py: trabalha-se sobre o codigo que esta no editor (a
# ficha da coisa), e devolve-se esse codigo ja mudado. O resto do caminho e
# o de sempre, como se a crianca o tivesse escrito.
#
# De uma lista escolhe-se o "jeito" de um inimigo. Numa caixa marca-se o que
# no codigo e True ou False.

NOMES_DOS_JEITOS = {
    "andar": "andar: vai e vem",
    "saltar": "saltar: dá saltos na tua direção",
    "voar": "voar: voa de um lado para o outro",
    "carregar": "carregar: se te vê, corre contra ti",
    "canhao": "canhao: fica parado e dispara bolas",
    "chefe": "chefe: como o Rei Sucata",
}
CAIXAS = {
    "inimigo": {"pisavel": "Pisa-se: cai quando o Faísca lhe salta em cima (sem isto, só a tiro)"},
    "mundo": {"estrelas": "O céu deste mundo tem estrelas"},
    "nivel": {"treino": "É um recreio: aqui não se perdem corações nem se ganham estrelas"},
}


def _ficha_do_codigo(codigo):
    # A ficha que esta no editor: o { } de um mundo ou de um nivel, ou o
    # "a": { } de um inimigo. Devolve (o no do dicionario, as linhas do texto
    # sem a virgula do fim, se a tinha, e quantas colunas a primeira linha
    # ficou desviada por causa do { que se lhe poe a volta para a ler).
    texto = codigo.rstrip()
    virgula = texto.endswith(",")
    if virgula:
        texto = texto[:-1]
    desvio = 0
    try:
        no = ast.parse(texto, mode="eval").body
    except SyntaxError:
        try:
            no = ast.parse("{" + texto + "}", mode="eval").body.values[0]
            desvio = 1
        except (SyntaxError, IndexError):
            raise ValueError("o código tem um erro: corrige-o primeiro, ou carrega em Repor o original.")
    if not isinstance(no, ast.Dict):
        raise ValueError("não percebi esta ficha: falta-lhe o { }?")
    return no, texto.split("\n"), virgula, desvio


def _no_da_chave(ficha, chave):
    for k, v in zip(ficha.keys, ficha.values):
        if blocos.texto_constante(k) == chave:
            return v
    return None


def _trocar_no(linhas, no, desvio, texto):
    # O que esta escrito num no (de uma linha so) passa a ser "texto".
    if no.lineno != no.end_lineno:
        raise ValueError("não percebi como isso está escrito.")
    tira = desvio if no.lineno == 1 else 0
    linha = linhas[no.lineno - 1]
    de = _letras(linha, no.col_offset - tira)
    ate = _letras(linha, no.end_col_offset - tira)
    linhas[no.lineno - 1] = linha[:de] + texto + linha[ate:]


def _de_volta(codigo, linhas, virgula):
    return {"codigo": "\n".join(linhas) + ("," if virgula else "") + codigo[len(codigo.rstrip()):]}


def lista(fonte, escolha, codigo, escolhidos=None):
    if escolha.partition(":")[0] != "inimigo":
        raise ValueError("aqui não há nada para escolher de uma lista.")
    ficha, linhas, virgula, desvio = _ficha_do_codigo(codigo)
    no = _no_da_chave(ficha, "jeito")
    if no is None:
        raise ValueError('não encontrei o "jeito" deste inimigo no código.')
    atual = no.value if isinstance(no, ast.Constant) else None
    nomes = [NOMES_DOS_JEITOS[jeito] for jeito in JEITOS]
    if escolhidos is None:
        quem = _valor(ficha, "nome") or "este inimigo"
        return {"titulo": "Como se porta " + str(quem) + "?", "opcoes": nomes,
                "escolhidos": [NOMES_DOS_JEITOS[atual]] if atual in JEITOS else [],
                "nota": "Carrega no jeito que queres. Só pode ter um: fica o último em que carregares."}
    feitas = [nome for nome in (escolhidos if isinstance(escolhidos, list) else []) if nome in nomes]
    if len(feitas) == 0:
        raise ValueError("um inimigo tem de ter um jeito: carrega num deles.")
    jeito = JEITOS[nomes.index(feitas[-1])]
    _trocar_no(linhas, no, desvio, '"' + jeito + '"')
    return _de_volta(codigo, linhas, virgula)


def caixas(fonte, escolha, codigo, chave=None, valor=None):
    tipo = escolha.partition(":")[0]
    if tipo not in CAIXAS:
        raise ValueError("aqui não há caixas para marcar.")
    ficha, linhas, virgula, desvio = _ficha_do_codigo(codigo)
    if chave is None:
        estado = []
        for qual, texto in CAIXAS[tipo].items():
            no = _no_da_chave(ficha, qual)
            estado.append({"chave": qual, "texto": texto,
                           "ligada": isinstance(no, ast.Constant) and no.value is True})
        return {"caixas": estado}
    if chave not in CAIXAS[tipo]:
        raise ValueError("essa caixa não existe.")
    escrito = "True" if valor else "False"
    no = _no_da_chave(ficha, chave)
    if no is not None:
        _trocar_no(linhas, no, desvio, escrito)
    elif valor:
        # Ainda nao esta na ficha: vai para uma linha nova, a seguir a
        # primeira coisa dela, alinhada com ela.
        primeira_chave = ficha.keys[0]
        primeira = ficha.values[0]
        tira = desvio if primeira_chave.lineno == 1 else 0
        margem = " " * _letras(linhas[primeira_chave.lineno - 1], primeira_chave.col_offset - tira)
        if not linhas[primeira.end_lineno - 1].rstrip().endswith(","):
            raise ValueError('não consegui acrescentar à ficha: escreve tu "' + chave + '": True, numa linha nova.')
        linhas[primeira.end_lineno:primeira.end_lineno] = [margem + '"' + chave + '": True,']
    return _de_volta(codigo, linhas, virgula)


# =====================================================================
#                 VER SE O QUE FOI ESCRITO FAZ SENTIDO
# =====================================================================
# Antes de uma mudanca entrar no jogo, passa por aqui. Devolve duas listas
# de frases: problemas (a mudanca nao entra) e avisos (entra, mas atencao).

def _numero(valor):
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


def _cor(valor):
    if not isinstance(valor, (tuple, list)) or len(valor) != 3:
        return False
    for parte in valor:
        if not isinstance(parte, int) or isinstance(parte, bool) or parte < 0 or parte > 255:
            return False
    return True


def _ver_cor(ficha, quem, chave, problemas):
    if chave not in ficha:
        problemas.append(quem + ': falta "' + chave + '".')
    elif not _cor(ficha[chave]):
        problemas.append(quem + ': "' + chave + '" são três números de 0 a 255, como (200, 60, 60).')


def _ver_numero(ficha, quem, chave, minimo, maximo, problemas):
    if chave not in ficha:
        problemas.append(quem + ': falta "' + chave + '".')
    elif not _numero(ficha[chave]):
        problemas.append(quem + ': "' + chave + '" tem de ser um número, sem aspas.')
    elif ficha[chave] < minimo or ficha[chave] > maximo:
        problemas.append(quem + ': "' + chave + '" tem de estar entre ' + str(minimo) + " e " + str(maximo) + ".")


def _ver_constantes(ns, problemas, avisos):
    for nome, minimo, maximo, inteiro in LIMITES:
        valor = ns.get(nome)
        if not _numero(valor):
            problemas.append(nome + " tem de ser um número, sem aspas.")
        elif inteiro and not isinstance(valor, int):
            problemas.append(nome + " tem de ser um número inteiro, sem ponto: " + str(int(valor)) + ", por exemplo.")
        elif valor < minimo or valor > maximo:
            problemas.append(nome + " tem de estar entre " + str(minimo) + " e " + str(maximo) + ".")
    if _numero(ns.get("VEL_ANDAR")) and _numero(ns.get("VEL_CORRER")) and ns["VEL_CORRER"] < ns["VEL_ANDAR"]:
        avisos.append("VEL_CORRER é menor que VEL_ANDAR: a correr, o Faísca fica mais lento do que a andar.")

    for nome in CORES:
        if not _cor(ns.get(nome)):
            problemas.append(nome + " tem de ser uma cor: três números de 0 a 255, como (200, 60, 60).")
    for nome in TEXTOS:
        if not isinstance(ns.get(nome), str):
            problemas.append(nome + " tem de ser um texto, entre aspas.")
    if not isinstance(ns.get("IMAGEM_DO_HEROI"), str):
        problemas.append('IMAGEM_DO_HEROI é o nome de um ficheiro, entre aspas, como "faisca.png".')
    for nome in SONS:
        if not isinstance(ns.get(nome), str):
            problemas.append(nome + ' é o nome de um ficheiro, entre aspas, como "salto.wav".')


def _ver_inimigos(ns, problemas, avisos):
    inimigos = ns.get("INIMIGOS")
    if not isinstance(inimigos, dict) or len(inimigos) == 0:
        problemas.append("Tem de haver pelo menos um inimigo.")
        return
    for letra, ficha in inimigos.items():
        if not isinstance(letra, str) or len(letra) != 1:
            problemas.append("A letra de um inimigo é uma letra só, entre aspas. Encontrei " + repr(letra) + ".")
            continue
        if letra in LETRAS_DO_MAPA or letra == " ":
            problemas.append('A letra "' + letra + '" já quer dizer outra coisa no mapa. Escolhe outra para o inimigo.')
            continue
        if not isinstance(ficha, dict):
            problemas.append('O inimigo "' + letra + '": a ficha tem de estar entre { }.')
            continue
        quem = ficha.get("nome")
        if not isinstance(quem, str):
            problemas.append('O inimigo "' + letra + '": o "nome" tem de ser um texto entre aspas.')
            quem = 'O inimigo "' + letra + '"'
        _ver_numero(ficha, quem, "vida", 1, 9999, problemas)
        _ver_numero(ficha, quem, "velocidade", 0, 30, problemas)
        _ver_numero(ficha, quem, "largura", 4, 240, problemas)
        _ver_numero(ficha, quem, "altura", 4, 240, problemas)
        _ver_cor(ficha, quem, "cor", problemas)
        if "pisavel" not in ficha:
            problemas.append(quem + ': falta "pisavel" (True ou False).')
        elif not isinstance(ficha["pisavel"], bool):
            avisos.append(quem + ': "pisavel" é True ou False, sem aspas.')
        if "jeito" not in ficha:
            problemas.append(quem + ': falta o "jeito".')
        elif ficha["jeito"] not in JEITOS:
            avisos.append(quem + ': o jogo não conhece o jeito ' + repr(ficha["jeito"]) + ". Fica parado. "
                          'Os jeitos são "' + '", "'.join(JEITOS) + '".')
        if "imagem" in ficha and not isinstance(ficha["imagem"], str):
            problemas.append(quem + ': a "imagem" é o nome de um ficheiro, entre aspas, como "lesma.png".')
        if "som" in ficha and not isinstance(ficha["som"], str):
            problemas.append(quem + ': o "som" é o nome de um ficheiro, entre aspas, como "lesma.wav".')


def _ver_letras_sem_dono(ns, avisos):
    # Letras que os niveis usam e que ja nao sao de nenhum inimigo (acontece
    # quando se muda a letra de um).
    inimigos = ns.get("INIMIGOS")
    if not isinstance(inimigos, dict):
        return
    orfas = []
    niveis = ns.get("NIVEIS")
    for dados in niveis if isinstance(niveis, list) else []:
        mapa = dados.get("mapa") if isinstance(dados, dict) else None
        for linha in mapa if isinstance(mapa, list) else []:
            for letra in linha if isinstance(linha, str) else "":
                if letra not in LETRAS_DO_MAPA and letra not in inimigos and letra not in orfas:
                    orfas.append(letra)
    if orfas:
        avisos.append("Os níveis usam letras que não são de nenhum inimigo: " + " ".join(sorted(orfas))
                      + ". Nesses sítios não aparece nada.")


def _ver_mundos(ns, problemas, avisos):
    mundos = ns.get("MUNDOS")
    if not isinstance(mundos, list) or len(mundos) == 0:
        problemas.append("Tem de haver pelo menos um mundo.")
        return
    numero = 0
    for ficha in mundos:
        numero = numero + 1
        if not isinstance(ficha, dict):
            problemas.append("O mundo " + str(numero) + " tem de estar entre { }.")
            continue
        quem = ficha.get("nome")
        if not isinstance(quem, str):
            problemas.append("O mundo " + str(numero) + ': o "nome" tem de ser um texto entre aspas.')
            quem = "O mundo " + str(numero)
        for chave in ("ceu_cima", "ceu_baixo", "terra", "relva", "montes"):
            _ver_cor(ficha, quem, chave, problemas)
        if "estrelas" not in ficha:
            problemas.append(quem + ': falta "estrelas" (True ou False).')
        elif not isinstance(ficha["estrelas"], bool):
            avisos.append(quem + ': "estrelas" é True ou False, sem aspas.')


def _ver_nivel(ns, indice, problemas, avisos):
    niveis = ns.get("NIVEIS")
    if not isinstance(niveis, list) or len(niveis) == 0:
        problemas.append("NIVEIS tem de ser uma lista com pelo menos um nível, entre [ ].")
        return
    if indice >= len(niveis):
        problemas.append("Este nível já não está na lista NIVEIS.")
        return
    dados = niveis[indice]
    if not isinstance(dados, dict):
        problemas.append("O nível tem de estar entre { }.")
        return
    if not isinstance(dados.get("nome"), str):
        problemas.append('Falta o "nome" do nível, um texto entre aspas.')
    if "dica" in dados and not isinstance(dados["dica"], str):
        problemas.append('A "dica" tem de ser um texto entre aspas.')
    if "treino" in dados and not isinstance(dados["treino"], bool):
        avisos.append('"treino" é True ou False, sem aspas.')
    placas = dados.get("placas", [])
    if not isinstance(placas, list):
        placas = [None]
    for placa in placas:
        certa = isinstance(placa, (tuple, list)) and len(placa) == 3
        if not certa or not _numero(placa[0]) or not _numero(placa[1]) or not isinstance(placa[2], str):
            problemas.append('As "placas" são uma lista, e cada placa é (coluna, linha, "texto"), como (11, 7, "Olá!").')
            break

    mapa = dados.get("mapa")
    if "mapa" not in dados:
        problemas.append('Falta o "mapa" do nível.')
        return
    if not isinstance(mapa, list) or len(mapa) == 0:
        problemas.append('O "mapa" tem de ser uma lista de linhas, entre [ ].')
        return
    for linha in mapa:
        if not isinstance(linha, str):
            problemas.append("Cada linha do mapa tem de estar entre aspas e acabar com uma vírgula.")
            return

    linhas_certas = ns.get("LINHAS", 12)
    if len(mapa) > linhas_certas:
        problemas.append("O mapa tem " + str(len(mapa)) + " linhas e só cabem " + str(linhas_certas)
                         + ". As de baixo ficavam de fora: apaga " + str(len(mapa) - linhas_certas) + ".")
    elif len(mapa) < linhas_certas:
        avisos.append("O mapa tem " + str(len(mapa)) + " linhas em vez de " + str(linhas_certas)
                      + ". O jogo põe ar por cima.")

    # Todas as linhas com o mesmo numero de letras. Diz-se quais nao tem.
    tamanhos = [len(linha) for linha in mapa]
    normal = max(set(tamanhos), key=tamanhos.count)
    diferentes = [i for i in range(len(mapa)) if tamanhos[i] != normal]
    if len(diferentes) == 1:
        i = diferentes[0]
        problemas.append("A linha " + str(i + 1) + " do mapa tem " + str(tamanhos[i]) + " letras e as outras têm "
                         + str(normal) + ". Têm de ter todas as mesmas.")
    elif len(diferentes) > 1:
        problemas.append("As linhas do mapa têm de ter todas o mesmo número de letras. Quase todas têm "
                         + str(normal) + ", mas as linhas " + ", ".join(str(i + 1) for i in diferentes[:8])
                         + (" e outras" if len(diferentes) > 8 else "") + " não.")
    if max(tamanhos) > 300:
        problemas.append("O mapa é comprido demais: " + str(max(tamanhos)) + " letras. O máximo é 300.")

    tudo = "".join(mapa)
    if tudo.count("P") == 0:
        problemas.append("Falta o P: o sítio onde o Faísca começa.")
    if tudo.count("P") > 1:
        problemas.append("Só pode haver um P (o Faísca só começa num sítio).")
    if tudo.count("F") == 0:
        problemas.append("Falta o F: a saída. Sem ela o nível não acaba.")
    if tudo.count("F") > 1:
        problemas.append("Só pode haver um F (uma saída).")

    inimigos = ns.get("INIMIGOS")
    if not isinstance(inimigos, dict):
        inimigos = {}
    conhecidas = LETRAS_DO_MAPA + "".join(letra for letra in inimigos if isinstance(letra, str))
    estranhas = sorted(set(tudo) - set(conhecidas))
    if estranhas:
        nomes = ["espaço" if letra == " " else letra for letra in estranhas]
        avisos.append("Letras que o nível não conhece (ficam ar): " + " ".join(nomes))
    if 0 < normal < 20:
        avisos.append("O ecrã mostra 20 letras de largura. O jogo enche o resto com ar.")


def _ver_funcoes(ns, problemas, avisos):
    # O jogo chama cada funcao pelo nome e da-lhe sempre as mesmas coisas.
    todas = {}
    for tipo in FUNCOES:
        todas.update(FUNCOES[tipo][0])
    for nome in todas:
        esperado = todas[nome][1]
        funcao = ns.get(nome)
        como = "def " + nome + "(" + ", ".join(esperado) + "):"
        if not inspect.isfunction(funcao):
            problemas.append('"' + nome + '" tem de ser uma função. A primeira linha é: ' + como)
            continue
        recebe = list(inspect.signature(funcao).parameters)
        if len(recebe) != len(esperado):
            problemas.append("A função " + nome + " tem de receber "
                             + (", ".join(esperado) if esperado else "nada, só ( )") + ", nem mais nem menos. "
                             "A primeira linha tem de ser: " + como)
    if not isinstance(ns.get("memoria"), dict):
        problemas.append('A "memoria" tem de continuar a ser um dicionário. Para a esvaziar usa memoria.clear().')


def _ver_mundo_do_nivel(ns, problemas, avisos):
    # A regra tem de dar a posicao de um mundo: um numero inteiro.
    mundos = ns.get("MUNDOS")
    quantos = len(mundos) if isinstance(mundos, list) else 0
    total = max(1, ns["total_de_niveis"]())
    fora = []
    for numero in range(0, total + 1):
        valor = ns["mundo_do_nivel"](numero)
        if not isinstance(valor, int) or isinstance(valor, bool):
            problemas.append("mundo_do_nivel tem de devolver um número inteiro (a posição do mundo na lista: 0 é o "
                             "primeiro). Para o nível " + str(numero) + " devolveu " + repr(valor)[:40]
                             + ". Para dividir sem vírgulas usa // em vez de /.")
            return
        if numero > 0 and (valor < 0 or valor >= quantos):
            fora.append(str(numero))
    if fora:
        avisos.append("Para " + ("o nível " if len(fora) == 1 else "os níveis ") + ", ".join(fora[:8])
                      + (" e outros" if len(fora) > 8 else "") + ", a regra dá um mundo que não há (só há "
                      + str(quantos) + "). O jogo usa o primeiro ou o último.")


def _ver_contar_estrelas(ns, problemas):
    # A regra tem de dar um numero de estrelas que caiba no ecra.
    nivel = ns.get("nivel")
    if not isinstance(nivel, dict) or "apanhadas" not in nivel:
        return
    valor = ns["contar_estrelas"]()
    if not isinstance(valor, int) or isinstance(valor, bool):
        problemas.append("contar_estrelas tem de devolver um número inteiro de estrelas: falta um return no fim, "
                         "ou devolve outra coisa? Devolveu " + repr(valor)[:40] + ".")
    elif valor < 0 or valor > 3:
        problemas.append("contar_estrelas tem de devolver de 0 a 3 estrelas (o ecrã só tem lugar para 3). "
                         "Devolveu " + str(valor) + ".")


# =====================================================================
#                      OS NIVEIS DE EXPERIENCIA
# =====================================================================
# Quando a coisa escolhida nao e um nivel, o Faisca precisa de um sitio
# para a mostrar. Estes niveis sao so do palco: nao estao no jogo.
# Escrevem-se sem o ar a direita; o encher() trata disso.

def encher(linhas, largura):
    return [linha.ljust(largura, ".") for linha in linhas]


def arena_do_inimigo(letra, ficha):
    # Um ecra so, com o inimigo sempre a vista. O Faisca fica atras de um
    # caixote, para nao ir a correr contra ele antes de se querer.
    jeito = ficha.get("jeito")
    fila = list(".P.B................")
    voo = list("....................")
    if jeito == "voar":
        voo[13] = letra
    elif jeito in ("canhao", "chefe") or ficha.get("largura", 0) > 60:
        fila[14] = letra
    else:
        fila[10] = letra
        fila[16] = letra
    mapa = encher([""] * 5, 20) + [
        "".join(voo),
        "....................",
        ".......===..........",
        "....................",
        "".join(fila),
        "####################",
        "####################",
    ]
    return {"nome": ficha.get("nome", letra), "dica": "", "mapa": mapa}


def letra_que_anda(ns):
    # Um inimigo simples para por nas pistas: o primeiro que so anda.
    for letra, ficha in ns["INIMIGOS"].items():
        if ficha.get("jeito") == "andar":
            return letra
    return "."


def montra(ns):
    # Um ecra so com um bocadinho de tudo o que tem cor.
    mapa = encher([
        "", "", "", "",
        ".........oo......h",
        ".........==",
        "",
        "",
        "",
        ".P.B..c.M.....^^..@.",
        "###########%%%######",
        "###########~~~######",
    ], 20)
    mapa[9] = mapa[9].replace("@", letra_que_anda(ns))
    return {"nome": "A montra", "dica": "", "mapa": mapa}


def pista(ns):
    # Para os numeros do jogo: um buraco de 2, um de 3, um muro de 2, uma
    # mola com uma plataforma 5 quadrados acima, um caixote e um inimigo.
    mapa = encher([
        "",
        "",
        "",
        "...................................ooo",
        "...................................===",
        "",
        "",
        "........................oo....................ooo",
        "..................##",
        ".P.B.....o.o......##..c.........M....@.....c..........h.",
        "########################..####################...#######",
        "########################~~####################~~~#######",
    ], 56)
    mapa[9] = mapa[9].replace("@", letra_que_anda(ns))
    return {"nome": "A pista de testes", "dica": "", "mapa": mapa}


def letra_com_jeito(ns, jeito):
    # O primeiro inimigo com esse jeito; se nao houver nenhum, o primeiro.
    for letra, ficha in ns["INIMIGOS"].items():
        if ficha.get("jeito") == jeito:
            return letra
    return list(ns["INIMIGOS"])[0]


def letras_do_chao(ns, primeiro):
    # Dois inimigos que andam pelo chao. primeiro="vida": os que aguentam
    # mais tiros (para se ver a vida a descer). primeiro="pisavel": um a que
    # se salta em cima e um a que nao. Se so houver um, vem duas vezes.
    fichas = ns["INIMIGOS"]
    letras = [letra for letra in fichas if fichas[letra].get("jeito") in ("andar", "carregar")]
    if len(letras) == 0:
        letras = [list(fichas)[0]]
    if primeiro == "vida":
        letras.sort(key=lambda letra: -fichas[letra].get("vida", 1))
    else:
        letras.sort(key=lambda letra: not fichas[letra].get("pisavel"))
        letras = [letras[0], letras[-1]]
    return [letras[0], letras[min(1, len(letras) - 1)]]


def letra_sem_desenho(ns):
    # Um inimigo que o jogo desenhe com desenhar_inimigo_novo. Se ainda nao
    # houver nenhum (ninguem criou um inimigo novo), inventa-se aqui um so
    # para a mostra: fica na memoria do jogo, nao no ficheiro.
    for letra, ficha in ns["INIMIGOS"].items():
        if letra not in LETRAS_COM_DESENHO and ficha.get("jeito") not in JEITOS_COM_DESENHO:
            return letra
    ns["INIMIGOS"]["?"] = {"nome": "Inimigo novo", "vida": 1, "velocidade": 1.0, "pisavel": True,
                           "jeito": "andar", "largura": 38, "altura": 28, "cor": (230, 120, 200)}
    return "?"


def arena_dos_toques(ns, letras):
    # Um ecra so, sem caixote: o Faisca vai direito aos inimigos.
    fila = list(".P..................")
    fila[8] = letras[0]
    fila[15] = letras[1]
    mapa = encher([""] * 7, 20) + [
        ".......===..........",
        "....................",
        "".join(fila),
        "####################",
        "####################",
    ]
    return {"nome": "A arena", "dica": "", "mapa": mapa}


def recreio_dos_acontecimentos(ns):
    # Um ecra so, onde acontece de tudo depressa: tres moedas logo a frente,
    # uma lesma a vir, lava para cair, e um coracao la em cima.
    mapa = encher([
        "", "", "", "", "", "",
        "..........ooo.......",
        "..........===......h",
        "",
        ".P..o.o.o@..........",
        "###############..###",
        "###############~~###",
    ], 20)
    mapa[9] = mapa[9].replace("@", letra_que_anda(ns))
    return {"nome": "O recreio dos acontecimentos", "dica": "", "mapa": mapa}


def arena_da_mola(ns):
    # Um ecra so: o Faisca vai direito a mola.
    mapa = encher([""] * 9, 20) + [
        ".P....M.............",
        "####################",
        "####################",
    ]
    return {"nome": "A mola", "dica": "", "mapa": mapa}


def arena_da_saida(ns):
    # Tres moedas e a saida logo ali: o nivel acaba em poucos segundos.
    mapa = encher([""] * 9, 20) + [
        ".P...o.o.o.....F....",
        "####################",
        "####################",
    ]
    return {"nome": "A saída", "dica": "", "mapa": mapa}


def arena_dos_coracoes(ns):
    # Uma lesma para o Faisca perder um coracao, e um coracao mais a frente.
    mapa = encher([""] * 9, 20) + [
        ".P.....@....h.......",
        "####################",
        "####################",
    ]
    mapa[9] = mapa[9].replace("@", letra_que_anda(ns))
    return {"nome": "O coração", "dica": "", "mapa": mapa}


def arena_dos_caixotes(ns):
    # Tres caixotes em fila, para partir a tiro.
    mapa = encher([""] * 9, 20) + [
        ".P...B....B....B....",
        "####################",
        "####################",
    ]
    return {"nome": "Os caixotes", "dica": "", "mapa": mapa}


# As funcoes cuja arena recomeca sozinha, e de quantos em quantos frames:
# o que elas mostram acontece uma vez e acaba (a mola, o coracao, os
# caixotes, o inicio do nivel).
RECOMECAR = {"tocar_na_mola": 260, "ao_apanhar_coracao": 420, "ao_partir_caixote": 420, "ao_comecar_nivel": 300}
# Com estas, o Faisca dispara sozinho, um tiro por segundo.
A_DISPARAR = ["acertar_tiro", "ao_derrotar_inimigo", "ao_disparar", "ao_partir_caixote", "desenhar_tiro"]
# Com estas, o nivel acaba (o Faisca chega a saida) e recomeca pouco depois.
ATE_A_SAIDA = ["contar_estrelas", "ao_acabar_nivel"]


# As teclas que o palco carrega pelo jogador (para o Faisca disparar ou
# ficar parado sozinho). O jogo pergunta ao pygame que teclas estao em
# baixo; aqui responde-se com as verdadeiras mais estas.
teclas_a_mais = set()
teclas_verdadeiras = None        # o pygame.key.get_pressed de antes de mexermos


class TeclasComAjuda:
    def __init__(self, verdadeiras):
        self.verdadeiras = verdadeiras

    def __getitem__(self, tecla):
        return tecla in teclas_a_mais or self.verdadeiras[tecla]


def ajudar_nas_teclas(pygame):
    global teclas_verdadeiras
    if teclas_verdadeiras is None:
        teclas_verdadeiras = pygame.key.get_pressed
        pygame.key.get_pressed = lambda: TeclasComAjuda(teclas_verdadeiras())


# =====================================================================
#                              O PALCO
# =====================================================================

class Palco:

    def __init__(self, escolha):
        tipo, _, numero = escolha.partition(":")
        self.tipo = tipo
        self.numero = int(numero) if numero.isdigit() else 0
        self.letra = None            # a letra da faixa de baixo
        self.mapa_pequeno = None     # o nivel inteiro em ponto pequeno
        self.escala = 8
        self.carregadas = {}         # as teclas Q e E no frame anterior
        self.quantos = None          # quantas entradas tem a lista da coisa escolhida
        self.com_mapa = True         # a tecla M esconde e mostra o mapa pequeno
        # Uma regra, um acontecimento ou um desenho: qual e a funcao.
        self.funcao = numero if tipo in FUNCOES and numero in FUNCOES[tipo][0] else None
        self.a_letra_da_arena = None # o inimigo que esta na arena dessa funcao
        self.guardado = None         # as moedas e os inimigos da arena, para voltarem
        self.sem_moedas = 0          # ha quantos frames nao ha moedas, nem inimigos
        self.sem_inimigos = 0
        self.desde_a_mudanca = 0     # frames desde que o codigo mudou
        self.feito = 0               # ha quantos frames o nivel da arena esta acabado
        self.nivel_a_vista = None    # na regra dos mundos: o nivel cujo mundo se esta a mostrar
        if tipo in FUNCOES:
            # Uma funcao nova so mostra o que vale quando chega a vez de ser
            # usada (o salto, o tiro a acertar): prova-se mais tempo.
            self.quadros_de_prova = 150

    def verificar(self, ns):
        problemas = []
        avisos = []
        _ver_constantes(ns, problemas, avisos)
        _ver_inimigos(ns, problemas, avisos)
        _ver_mundos(ns, problemas, avisos)
        _ver_funcoes(ns, problemas, avisos)
        if self.tipo == "nivel":
            _ver_nivel(ns, self.numero, problemas, avisos)
        if self.tipo == "inimigo":
            _ver_letras_sem_dono(ns, avisos)
        # As regras que devolvem uma resposta: tem de ser uma que o jogo perceba.
        if not problemas and self.funcao == "mundo_do_nivel":
            _ver_mundo_do_nivel(ns, problemas, avisos)
        if not problemas and self.funcao == "contar_estrelas":
            _ver_contar_estrelas(ns, problemas)
        # Apagar a ficha inteira deixava o palco a mostrar a ficha seguinte.
        lista = ns.get(LISTAS.get(self.tipo))
        if self.quantos is not None and isinstance(lista, (list, dict)) and len(lista) < self.quantos:
            problemas.append("Apagaste a ficha inteira, e assim esta coisa desaparecia do jogo. "
                             "Tem de ficar pelo menos o que está entre { }.")
        return problemas, avisos

    def contar(self, ns):
        if self.tipo in LISTAS:
            self.quantos = len(ns[LISTAS[self.tipo]])

    # --- Montar o nivel que mostra a coisa ---

    def montar(self, ns):
        nivel = ns["nivel"]
        if self.tipo == "nivel":
            ns["comecar_nivel"](min(self.numero, len(ns["NIVEIS"]) - 1))
        elif self.tipo == "mundo":
            # O primeiro nivel que se passa nesse mundo (decide a regra do jogo).
            indice = 0
            for i in range(len(ns["NIVEIS"])):
                if ns["mundo_do_nivel"](ns["numero_do_nivel"](i)) == self.numero:
                    indice = i
                    break
            ns["comecar_nivel"](indice)
            nivel["mundo"] = self.o_mundo(ns)
        elif self.tipo == "inimigo":
            letra = self.a_letra(ns)
            self.montar_arena(ns, arena_do_inimigo(letra, ns["INIMIGOS"][letra]))
        elif self.tipo == "numeros":
            self.montar_arena(ns, pista(ns))
        elif self.funcao is not None:
            self.montar_arena(ns, self.arena_da_funcao(ns))
        else:
            self.montar_arena(ns, montra(ns))
        nivel["da_oficina"] = True       # o jogo apaga isto se carregar outro nivel
        self.mapa_pequeno = None
        self.contar(ns)
        if self.funcao is not None:
            # Nestas arenas as moedas e os inimigos voltam depois de acabarem.
            self.guardado = {
                "inicio": nivel["ponto"],
                "moedas": [moeda.copy() for moeda in nivel["moedas"]],
                "inimigos": [(inimigo["letra"], inimigo["x0"], inimigo["y0"]) for inimigo in nivel["inimigos"]],
            }
            self.sem_moedas = 0
            self.sem_inimigos = 0

    def arena_da_funcao(self, ns):
        # O sitio onde se ve o que cada funcao faz.
        self.a_letra_da_arena = None
        if self.funcao in ATE_A_SAIDA:
            return arena_da_saida(ns)
        if self.funcao == "ao_apanhar_coracao":
            return arena_dos_coracoes(ns)
        if self.funcao == "ao_partir_caixote":
            return arena_dos_caixotes(ns)
        if self.funcao == "tocar_na_mola":
            return arena_da_mola(ns)
        if self.tipo == "evento":
            return recreio_dos_acontecimentos(ns)
        if self.funcao == "tocar_num_inimigo":
            return arena_dos_toques(ns, letras_do_chao(ns, "pisavel"))
        if self.funcao == "acertar_tiro":
            return arena_dos_toques(ns, letras_do_chao(ns, "vida"))
        jeitos = {"mexer_saltador": "saltar", "mexer_voador": "voar", "mexer_carregador": "carregar",
                  "mexer_canhao": "canhao"}
        if self.funcao in jeitos:
            letra = letra_com_jeito(ns, jeitos[self.funcao])
        elif self.funcao == "desenhar_lesma":
            letra = "a" if "a" in ns["INIMIGOS"] else list(ns["INIMIGOS"])[0]
        elif self.funcao == "desenhar_inimigo_novo":
            letra = letra_sem_desenho(ns)
        elif self.funcao in ("desenhar_robot", "desenhar_quadrado", "desenhar_moeda", "desenhar_coracao",
                             "desenhar_tiro", "mundo_do_nivel"):
            return montra(ns)
        else:
            return pista(ns)
        self.a_letra_da_arena = letra
        return arena_do_inimigo(letra, ns["INIMIGOS"][letra])

    def repor_arena(self, ns, moedas, inimigos):
        # As moedas e os inimigos da arena voltam ao sitio onde nasceram.
        nivel = ns["nivel"]
        if moedas:
            nivel["moedas"] = [moeda.copy() for moeda in self.guardado["moedas"]]
            self.sem_moedas = 0
        if inimigos:
            nivel["inimigos"] = []
            for letra, x, y in self.guardado["inimigos"]:
                if letra in ns["INIMIGOS"]:
                    inimigo = ns["criar_inimigo"](letra, 0, 0)
                    inimigo["x"] = inimigo["x0"] = x
                    inimigo["y"] = inimigo["y0"] = y
                    nivel["inimigos"].append(inimigo)
            self.sem_inimigos = 0

    def recomecar(self, ns):
        # Carrega a arena outra vez, de raiz. A memoria fica como estava (o
        # jogo esvazia-a quando um nivel comeca), menos no "quando um nivel
        # comeca", onde e isso mesmo que se quer ver.
        guardada = dict(ns["memoria"])
        self.montar(ns)
        if self.funcao != "ao_comecar_nivel":
            ns["memoria"].clear()
            ns["memoria"].update(guardada)
        self.feito = 0

    def mundo_a_vista(self, ns):
        # Na regra dos mundos: de 2,5 em 2,5 segundos, o ceu passa a ser o do
        # mundo do nivel seguinte, tal como a regra o decide. Devolve o numero
        # desse nivel.
        total = max(1, ns["total_de_niveis"]())
        numero = (self.desde_a_mudanca // 150) % total + 1
        if numero != self.nivel_a_vista:
            self.nivel_a_vista = numero
            ns["nivel"]["mundo"] = self.mundo_da_regra(ns, numero)
            ns["nivel"].pop("ceu", None)         # o jogo volta a pintar o ceu
        return numero

    def mundo_da_regra(self, ns, numero):
        posicao = ns["mundo_do_nivel"](numero)
        if not isinstance(posicao, int):
            posicao = 0
        return ns["MUNDOS"][max(0, min(posicao, len(ns["MUNDOS"]) - 1))]

    def voltar_ao_inicio(self, ns):
        # O Faisca volta ao principio da arena, com tudo no sitio: assim o
        # que se acabou de escrever acontece logo, sem se ter de esperar.
        nivel = ns["nivel"]
        heroi = ns["heroi"]
        inicio = self.guardado["inicio"]
        ns["repor_heroi"](inicio[0], inicio[1])
        heroi["congelado"] = 10          # quase sem esperar: quer-se ver ja
        heroi["virado"] = 1
        heroi["invencivel"] = 0
        heroi["vidas"] = ns["VIDAS"]
        nivel["ponto"] = inicio
        nivel["tiros"] = []
        nivel["balas"] = []
        self.repor_arena(ns, True, True)

    def manter_arena(self, ns, pygame):
        # Todos os frames, nas arenas das funcoes: repor o que acabou, e
        # carregar nas teclas que o palco carrega pelo jogador.
        nivel = ns["nivel"]
        self.desde_a_mudanca = self.desde_a_mudanca + 1
        de_quantos = RECOMECAR.get(self.funcao)
        if de_quantos and self.desde_a_mudanca % de_quantos == de_quantos - 1:
            if self.funcao == "tocar_na_mola":
                self.voltar_ao_inicio(ns)
            else:
                self.recomecar(ns)
            nivel = ns["nivel"]
        if self.funcao in ATE_A_SAIDA and ns["jogo"]["fase"] == "nivel_feito":
            # O nivel acabou: fica-se a ver as estrelas um bocado, e recomeca.
            self.feito = self.feito + 1
            if self.feito > 170:
                self.recomecar(ns)
            return
        if len(self.guardado["moedas"]) > 0 and len(nivel["moedas"]) == 0:
            self.sem_moedas = self.sem_moedas + 1
            if self.sem_moedas > 120:
                self.repor_arena(ns, True, False)
        if len(self.guardado["inimigos"]) > 0 and len(nivel["inimigos"]) == 0:
            self.sem_inimigos = self.sem_inimigos + 1
            if self.sem_inimigos > 90:
                self.repor_arena(ns, False, True)

        ajudar_nas_teclas(pygame)
        teclas_a_mais.clear()
        if ns["jogo"]["fase"] != "jogar":
            return
        if self.funcao in A_DISPARAR:
            # Dispara sozinho, um tiro por segundo.
            if self.desde_a_mudanca % 60 > 54:
                teclas_a_mais.add(pygame.K_x)
        if self.funcao == "acertar_tiro":
            # E fica parado, a nao ser que se carregue numa seta.
            teclas = teclas_verdadeiras()
            if not teclas[pygame.K_LEFT] and not teclas[pygame.K_RIGHT]:
                teclas_a_mais.add(pygame.K_DOWN)
        if self.funcao in ("saltar", "ao_saltar") and self.desde_a_mudanca == 45:
            # Um salto sozinho, pouco depois de o codigo mudar.
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE, unicode=" ", mod=0, scancode=0))

    def montar_arena(self, ns, dados):
        # O jogo so sabe carregar niveis da lista NIVEIS: empresta-se-lhe
        # uma lista so com o nosso, e devolve-se logo a verdadeira.
        verdadeiros = ns["NIVEIS"]
        ns["NIVEIS"] = [dados]
        try:
            ns["comecar_nivel"](0)
        finally:
            ns["NIVEIS"] = verdadeiros

    def a_letra(self, ns):
        letras = list(ns["INIMIGOS"])
        return letras[min(self.numero, len(letras) - 1)]

    def o_mundo(self, ns):
        return ns["MUNDOS"][min(self.numero, len(ns["MUNDOS"]) - 1)]

    def ao_mudar(self, ns):
        # O codigo mudou. As constantes o jogo vai busca-las sempre que
        # precisa; o que foi feito com os valores antigos (o nivel carregado,
        # os inimigos, o ceu) tem de ser feito outra vez.
        nivel = ns["nivel"]
        heroi = ns["heroi"]
        if not nivel.get("da_oficina"):
            return
        self.contar(ns)
        if self.funcao is not None:
            # Uma funcao nova: o jogo passa a chama-la sozinho. A memoria
            # comeca vazia, para nao ficar la nada do codigo antigo.
            self.desde_a_mudanca = 0
            self.nivel_a_vista = None
            ns["memoria"].clear()
            if self.funcao in ATE_A_SAIDA or self.funcao in ("ao_apanhar_coracao", "ao_partir_caixote",
                                                             "ao_comecar_nivel"):
                self.montar(ns)              # de raiz: o que la havia ja se gastou
                self.feito = 0
            elif self.tipo == "evento" or self.funcao in ("tocar_num_inimigo", "acertar_tiro", "tocar_na_mola"):
                self.voltar_ao_inicio(ns)
            return
        if self.tipo == "mundo":
            nivel["mundo"] = self.o_mundo(ns)
            nivel.pop("ceu", None)           # o jogo volta a pintar o ceu
        if self.tipo in ("nivel", "inimigo"):
            # Carrega-se de novo, mas o Faisca fica onde estava: se voltasse
            # ao inicio, nao se via a letra que se mudou la a frente.
            x = heroi["x"]
            y = heroi["y"]
            virado = heroi["virado"]
            camara_x = nivel["camara_x"]
            tempo = nivel["tempo"]
            dica = nivel["dica"]
            self.montar(ns)
            if nivel["dica"] == dica:
                nivel["tempo"] = tempo       # senao a dica do nivel voltava a aparecer por cima
            for subida in range(ns["LINHAS"]):
                if x + heroi["l"] <= nivel["largura"] and not ns["bate_em_solido"](x, y, heroi["l"], heroi["a"]):
                    heroi["x"] = x
                    heroi["y"] = y
                    heroi["virado"] = virado
                    heroi["congelado"] = 0
                    nivel["camara_x"] = camara_x
                    break
                y = y - ns["TILE"]           # ficou dentro de uma parede nova: sobe

    def levar(self, ns, ecras):
        # As teclas Q e E: o Faisca aparece um ecra mais atras ou mais a
        # frente, no primeiro sitio com chao que se encontrar por la.
        nivel = ns["nivel"]
        heroi = ns["heroi"]
        tile = ns["TILE"]
        alvo = int(heroi["x"] // tile) + ecras * 16
        alvo = max(1, min(alvo, nivel["colunas"] - 2))
        for desvio in range(nivel["colunas"]):
            for coluna in (alvo + desvio, alvo - desvio):
                if coluna < 0 or coluna >= nivel["colunas"]:
                    continue
                for linha in range(ns["LINHAS"] - 1, 0, -1):
                    livre = ns["letra_em"](coluna, linha) == "." and ns["letra_em"](coluna, linha - 1) == "."
                    x = coluna * tile + 9
                    y = (linha + 1) * tile - heroi["a"]
                    na_saida = nivel["saida"] is not None and nivel["saida"].colliderect((x, y, heroi["l"], heroi["a"]))
                    if livre and ns["ha_chao"](coluna, linha + 1) and not na_saida:
                        ns["repor_heroi"](x, y)
                        heroi["congelado"] = 0
                        nivel["ponto"] = (x, y)      # se cair, volta para aqui
                        nivel["camara_x"] = x - ns["LARGURA"] * 0.4
                        return

    # --- Todos os frames ---

    def quadro(self, ns, pygame):
        jogo = ns["jogo"]
        nivel = ns["nivel"]
        heroi = ns["heroi"]
        if self.letra is None:
            self.letra = pygame.font.SysFont(None, 22)

        # Sem camara: o modo "so teclado" do jogo, e o treino dos gestos dado.
        jogo["modo_teclado"] = True
        jogo["treinou"] = True

        # O jogo fica sempre dentro do nosso nivel: sem titulo, sem treino.
        # Se ele carregou outro (passou-se o nivel, Esc...), volta-se ao nosso.
        outro_ecra = False
        if not nivel.get("da_oficina") or jogo["fase"] not in ("jogar", "pausa", "nivel_feito", "perdeu"):
            self.montar(ns)
            outro_ecra = True

        # Os coracoes sao os do jogo: perdem-se, e quem fica sem nenhum
        # perde. Ai a demonstracao comeca outra vez, do principio.
        if jogo["fase"] == "perdeu":
            self.montar(ns)
            jogo["fase"] = "jogar"
            nivel = ns["nivel"]
            heroi = ns["heroi"]
            heroi["vidas"] = ns["VIDAS"]
            outro_ecra = True
        if self.funcao is not None and self.guardado is not None:
            self.manter_arena(ns, pygame)

        if outro_ecra:
            # O jogo ja tinha desenhado este frame (o titulo, o "Quase!"...):
            # desenha-se por cima o nivel, para esse ecra nem se chegar a ver.
            parado = {"direcao": 0, "andar": False, "correr": False, "saltar": False, "disparar": False}
            ns["desenhar_jogo"](ns["ler_mao"](), parado)
        if self.tipo == "textos":
            jogo["fase"] = "pausa"       # parado por baixo; por cima, o titulo
            ns["desenhar_titulo"](ns["ler_mao"]())

        if self.tipo in ("nivel", "mundo", "numeros") or self.funcao == "saltar":
            teclas = pygame.key.get_pressed()
            for tecla, ecras in ((pygame.K_q, -1), (pygame.K_e, 1), (pygame.K_m, 0)):
                if teclas[tecla] and not self.carregadas.get(tecla) and jogo["fase"] == "jogar":
                    if ecras == 0:
                        self.com_mapa = not self.com_mapa
                    else:
                        self.levar(ns, ecras)
                self.carregadas[tecla] = teclas[tecla]

        self.desenhar(ns, pygame)

    def desenhar(self, ns, pygame):
        nivel = ns["nivel"]
        texto = ""
        if self.tipo == "inimigo":
            letra = self.a_letra(ns)
            ficha = ns["INIMIGOS"][letra]
            texto = ficha["nome"] + ' (a letra "' + letra + '"):   vida ' + str(ficha["vida"])
            texto = texto + "   velocidade " + str(ficha["velocidade"]) + "   jeito " + str(ficha["jeito"])
            if ficha["pisavel"]:
                texto = texto + "   salta-se-lhe em cima"
            else:
                texto = texto + "   não se pisa: só a tiro"
            vivos = [inimigo for inimigo in nivel["inimigos"] if inimigo["letra"] == letra]
            if len(vivos) == 0 and len(nivel["particulas"]) == 0:
                self.ao_mudar(ns)            # morreram todos: vem outros
                ns["heroi"]["invencivel"] = 110
            self.lupa(ns, pygame, letra)
        elif self.tipo == "numeros":
            tile = ns["TILE"]
            no_ar = 2 * ns["FORCA_SALTO"] / ns["GRAVIDADE"]      # frames que um salto dura
            texto = "Em quadrados:   salto " + self.quadrados(ns["FORCA_SALTO"] ** 2 / (2 * ns["GRAVIDADE"]) / tile)
            texto = texto + " de altura   passa um buraco de " + self.quadrados(no_ar * ns["VEL_ANDAR"] / tile)
            texto = texto + " a andar e de " + self.quadrados(no_ar * ns["VEL_CORRER"] / tile) + " a correr"
            texto = texto + "   mola " + self.quadrados(ns["FORCA_MOLA"] ** 2 / (2 * ns["GRAVIDADE"]) / tile)
            texto = texto + " de altura   tiro chega a " + self.quadrados(ns["VEL_TIRO"] * ns["ALCANCE_TIRO"] / tile)
        elif self.tipo == "textos":
            texto = "Quando perdes:  O " + ns["NOME_DO_HEROI"] + " ficou sem corações.      No fim:  " + ns["TEXTO_VITORIA"]
        elif self.tipo == "nivel" and self.com_mapa and ns["jogo"]["fase"] == "jogar":
            self.desenhar_mapa_pequeno(ns, pygame)
        elif self.tipo == "regra":
            texto = "Regra:   " + REGRAS[self.funcao][0] + "   (a função " + self.funcao + ")"
            if self.funcao == "contar_estrelas" and ns["jogo"]["fase"] == "jogar":
                texto = texto + "      Se chegasse agora à saída: " + str(ns["contar_estrelas"]()) + " estrelas"
            if self.funcao == "mundo_do_nivel":
                numero = self.mundo_a_vista(ns)
                texto = ("Nível " + str(numero) + ": «" + str(nivel["mundo"].get("nome")) + "».     "
                         + self.niveis_por_mundo(ns))
        elif self.tipo == "evento":
            texto = "Acontecimento:   " + ACONTECIMENTOS[self.funcao][0] + "   (a função " + self.funcao + ")"
            texto = texto + "      memoria = " + repr(ns["memoria"])[:70]
        elif self.tipo == "desenho":
            texto = "Desenho:   " + DESENHOS[self.funcao][0] + "   (a função " + self.funcao + ")"
            if self.funcao == "desenhar_robot":
                self.lupa_do_heroi(ns, pygame)
            elif self.funcao == "desenhar_moeda":
                self.lupa_de(ns, pygame, lambda: ns["desenhar_moeda"](24, 24, 0))
            elif self.funcao == "desenhar_coracao":
                self.lupa_de(ns, pygame, lambda: ns["desenhar_coracao"](12, 12, 24, ns["VERMELHO"]))
            elif self.funcao == "desenhar_tiro":
                self.lupa_de(ns, pygame, lambda: ns["desenhar_tiro"]({"x": 24, "y": 24, "vx": 11, "vida": 30}, 24, 24))
            elif self.a_letra_da_arena in ns["INIMIGOS"]:
                self.lupa(ns, pygame, self.a_letra_da_arena)

        if texto != "":
            ecra = ns["janela"]["ecra"]
            fundo = ns["ALTURA"] - 30
            pygame.draw.rect(ecra, (30, 30, 48), (0, fundo, ns["LARGURA"], 30))
            pygame.draw.rect(ecra, ns["AMARELO"], (0, fundo, 6, 30))
            ecra.blit(self.letra.render(texto, True, (245, 245, 245)), (18, fundo + 8))

    def quadrados(self, quantos):
        return str(round(quantos, 1))

    def niveis_por_mundo(self, ns):
        # "1 a 5: O Prado   6 a 10: A Gruta": os niveis seguidos que a regra
        # poe no mesmo mundo, juntos.
        partes = []
        primeiro = 1
        total = max(1, ns["total_de_niveis"]())
        for numero in range(1, total + 1):
            mundo = self.mundo_da_regra(ns, numero)
            seguinte = self.mundo_da_regra(ns, numero + 1) if numero < total else None
            if seguinte is not mundo:
                quais = str(primeiro) if primeiro == numero else str(primeiro) + " a " + str(numero)
                partes.append(quais + ": " + str(mundo.get("nome")))
                primeiro = numero + 1
        return "   ".join(partes)[:96]

    def lupa_de(self, ns, pygame, desenhar):
        # Uma coisa pequena (uma moeda, um coracao, um tiro) desenhada numa
        # folha com a funcao do proprio jogo, e mostrada aumentada no canto.
        folha = pygame.Surface((48, 48))
        folha.fill(ns["nivel"]["mundo"]["ceu_baixo"])
        ecra = ns["janela"]["ecra"]
        ns["janela"]["ecra"] = folha
        try:
            desenhar()
        finally:
            ns["janela"]["ecra"] = ecra
        self.mostrar_lupa(ns, pygame, folha)

    def lupa(self, ns, pygame, letra):
        # Desenha o inimigo numa folha pequena, com a funcao do proprio
        # jogo, e mostra essa folha aumentada no canto.
        ficha = ns["INIMIGOS"][letra]
        lado = int(max(ficha["largura"], ficha["altura"])) + 28
        folha = pygame.Surface((lado, lado))
        folha.fill(ns["nivel"]["mundo"]["ceu_baixo"])
        modelo = ns["criar_inimigo"](letra, 0, 0)
        modelo["x"] = (lado - ficha["largura"]) // 2
        modelo["y"] = (lado - ficha["altura"]) // 2 + 4
        modelo["t"] = ns["jogo"]["frame"]
        modelo["no_chao"] = True
        ecra = ns["janela"]["ecra"]
        ns["janela"]["ecra"] = folha
        try:
            ns["desenhar_inimigo"](modelo, 0)
        finally:
            ns["janela"]["ecra"] = ecra
        self.mostrar_lupa(ns, pygame, folha)

    def lupa_do_heroi(self, ns, pygame):
        # O mesmo para o Faisca, com a funcao que o desenha com formas.
        folha = pygame.Surface((64, 64))
        folha.fill(ns["nivel"]["mundo"]["ceu_baixo"])
        ecra = ns["janela"]["ecra"]
        ns["janela"]["ecra"] = folha
        try:
            ns["desenhar_robot"](17, 16, ns["heroi"]["virado"])
        finally:
            ns["janela"]["ecra"] = ecra
        self.mostrar_lupa(ns, pygame, folha)

    def mostrar_lupa(self, ns, pygame, folha):
        ecra = ns["janela"]["ecra"]
        grande = pygame.transform.scale(folha, (110, 110))
        caixa = pygame.Rect(ns["LARGURA"] - 126, 84, 114, 114)
        pygame.draw.rect(ecra, (30, 30, 48), caixa.inflate(6, 6), border_radius=6)
        ecra.blit(grande, (caixa.x + 2, caixa.y + 2))
        pygame.draw.rect(ecra, ns["AMARELO"], caixa.inflate(6, 6), 2, border_radius=6)

    def desenhar_mapa_pequeno(self, ns, pygame):
        # O nivel inteiro, como esta escrito, com um quadradinho por letra.
        # Assim ve-se logo a letra que se mudou, mesmo longe do Faisca.
        nivel = ns["nivel"]
        heroi = ns["heroi"]
        if self.mapa_pequeno is None:
            self.mapa_pequeno = self.fazer_mapa_pequeno(ns, pygame)
        ecra = ns["janela"]["ecra"]
        escala = self.escala
        x0 = (ns["LARGURA"] - self.mapa_pequeno.get_width()) // 2
        y0 = 118
        ecra.blit(self.mapa_pequeno, (x0, y0))
        # o bocado que esta no ecra, e o Faisca
        vista = pygame.Rect(x0 + int(nivel["camara_x"] / ns["TILE"] * escala), y0,
                            ns["LARGURA"] // ns["TILE"] * escala, self.mapa_pequeno.get_height())
        pygame.draw.rect(ecra, (245, 245, 245), vista, 1)
        pygame.draw.rect(ecra, ns["COR_HEROI"], (x0 + int(heroi["x"] / ns["TILE"] * escala) - 1,
                                                 y0 + int(heroi["y"] / ns["TILE"] * escala), escala, escala))

    def fazer_mapa_pequeno(self, ns, pygame):
        nivel = ns["nivel"]
        mapa = ns["NIVEIS"][ns["jogo"]["indice"]]["mapa"]
        mundo = nivel["mundo"]
        self.escala = max(2, min(8, ns["LARGURA"] // nivel["colunas"]))
        escala = self.escala
        cores = {
            "#": mundo["terra"], "=": ns["COR_MADEIRA"], "%": ns["COR_PONTE_PODRE"], "B": ns["COR_MADEIRA"],
            "M": ns["VERMELHO"], "^": ns["COR_ESPINHO"], "~": ns["COR_LAVA"], "o": ns["COR_MOEDA"],
            "h": ns["VERMELHO"], "P": ns["COR_HEROI"], "F": ns["VERDE"], "c": ns["BRANCO"],
        }
        for letra, ficha in ns["INIMIGOS"].items():
            cores[letra] = ficha["cor"]
        folha = pygame.Surface((nivel["colunas"] * escala, ns["LINHAS"] * escala), pygame.SRCALPHA)
        folha.fill((10, 10, 25, 170))
        topo = ns["LINHAS"] - len(mapa)      # mapas com menos linhas ficam em baixo
        for linha in range(len(mapa)):
            for coluna in range(len(mapa[linha])):
                cor = cores.get(mapa[linha][coluna])
                if cor is not None and 0 <= topo + linha < ns["LINHAS"]:
                    pygame.draw.rect(folha, cor, (coluna * escala, (topo + linha) * escala, escala, escala))
        return folha


def antes_de_jogar():
    # Isto corre antes do codigo do jogo: e aqui que se lhe diz "so teclado".
    os.environ["MAOS_AO_AR_SO_TECLADO"] = "1"


def criar_palco(escolha):
    antes_de_jogar()
    return Palco(escolha)
