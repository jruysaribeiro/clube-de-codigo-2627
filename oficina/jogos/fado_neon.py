# O FADO//NEON na Oficina: que coisas se podem escolher, onde esta o codigo
# de cada uma, e o "palco" que mostra so essa coisa a funcionar.
#
# O palco nao e um jogo a parte: e o FADO//NEON verdadeiro a correr, sem
# menu e sem perder, e nos a mandarmos vir o que interessa (um inimigo, o
# chefe, as cartas...). Tudo o que se ve e desenhado pelo proprio jogo.
#
# Este jogo guarda tudo num objeto (o Jogo) que e feito dentro do main(),
# e copia os numeros quando cria as coisas: um inimigo fica com a vida que
# estava em PERFIS quando nasceu. Por isso, quando o codigo muda, o palco
# volta a criar o que foi feito com os numeros antigos (ver ao_mudar).
#
# As regras, os acontecimentos e os desenhos sao funcoes encostadas a margem,
# que as classes do jogo chamam pelo nome: essas trocam-se sem refazer nada.

import ast
import inspect
import json
import math
import re
import sys

import blocos
from jogos import bicharada as base

NOME = "FADO//NEON"
FICHEIRO = "s10-jogo-do-ano/fado-neon.py"
DESCRICAO = "Um roguelite de saudade e neon. Jogo do Ano 2026."

# As instrucoes do jogo, que a pagina mostra a entrada dele:
#   "joga"    como se joga
#   "comeca"  por onde comecar, passo a passo: (o que fazer, o titulo da coisa
#             a abrir, ou None). Com titulo, o passo ganha um botao que a abre.
#   "podes"   o que aqui se pode fazer
#   "nao"     o que nao da, ou da asneira
INSTRUCOES = {
    "joga": "WASD anda e as setas disparam. Espaço é a investida e E é o laser, quando o farol estiver cheio. "
            "Entre as ondas escolhes uma carta com 1, 2 ou 3. Ganhas se sobreviveres a 10 ondas; o Saudosista "
            "aparece na 5 e na 10.",
    "comeca": [
        ("Joga até à onda 2 ou 3 no «Jogar o jogo inteiro», para saberes o que há.", None),
        ("Abre «Vidas e velocidade» e dá-te mais vidas.", "Vidas e velocidade"),
        ("Abre «Os teus tiros» e põe-nos mais rápidos, ou mais fortes.", "Os teus tiros"),
        ("Abre o corredor e muda-lhe o tamanho, a vida e a cor.", "corredor"),
        ("Abre as «Frases das ondas» e escreve as tuas.", "Frases das ondas"),
        ("Depois inventa: «+ Novo inimigo», «+ Nova carta», e as Regras do jogo.", None),
    ],
    "podes": [
        "Mudar os inimigos e o chefe: a vida, a velocidade, a cor, se disparam, os ataques do Saudosista.",
        "Criar inimigos novos, com uma imagem e um som teus.",
        "Criar cartas novas e ondas especiais, com os inimigos que tu mandares.",
        "Mudar as frases que o jogo diz, as críticas do menu e os créditos.",
        "Ligar e desligar coisas em «Como o jogo arranca», com as caixas.",
        "Mudar as regras, e escrever nos Acontecimentos o que acontece quando um inimigo morre, quando disparas...",
    ],
    "nao": [
        "Números gigantes (milhares de inimigos, tamanhos enormes) deixam o jogo lento ou preso. Sobe aos poucos.",
        "Uma cor são sempre três números entre 0 e 255, entre parênteses.",
        "Uma carta nova ainda não faz nada: o que ela faz escreve-se nas Regras do jogo, em «O que cada carta faz».",
        "Um inimigo novo só se vê quando chegar a vez dele: a Oficina diz em que onda aparece.",
    ],
}

# Uma frase por grupo, para a pagina do jogo dizer o que la ha.
SOBRE_OS_GRUPOS = {
    "Inimigos": "Tamanho, vida, velocidade, cor, se disparam. Podes pôr uma imagem e um som teus. "
                "E o Saudosista: a vida dele, os ataques e quem ele chama.",
    "Tu": "As tuas vidas, os tiros, a investida e o laser.",
    "Ondas": "Quantas ondas há, como vão ficando mais difíceis, como o jogo arranca, "
             "e as ondas especiais, com os inimigos que tu mandares.",
    "Cartas": "As melhorias que aparecem entre as ondas.",
    "Textos": "As frases que o jogo diz.",
    "Regras do jogo": "Aqui mudas a maneira como o jogo se comporta: é programar a sério.",
    "Acontecimentos": "Estão vazios: o que lá escreveres passa a acontecer nesse momento. É aqui que se inventa.",
    "Desenhos": "Como se desenha um inimigo, a tua nave, as balas, o que fica no chão e os avisos, "
                "com polígonos, círculos e linhas.",
}

# Os grupos onde se pode criar uma coisa nova, e o que diz o botao.
CRIAVEIS = {"Inimigos": "Novo inimigo", "Ondas": "Nova onda especial", "Cartas": "Nova carta",
            "Textos": "Nova frase"}

# Pedidos ja escritos para o ajudante, para se perceber o que se pode pedir.
EXPLICA = "Explica-me esta função linha a linha"
QUE_FAZER = "O que posso fazer aqui?"
SUGESTOES = {
    "inimigo": ["Põe-no mais rápido mas com menos vida", "Muda-lhe a cor para amarelo e dá-lhe 5 lados",
                "O que quer dizer cada número?"],
    "chefe": ["Põe o Saudosista com metade da vida", "Faz o Saudosista aguentar o dobro", "O que muda este número?"],
    "ataques": ["Faz o Saudosista só usar a espiral e os anéis", "Põe o farol em primeiro lugar",
                "O que faz cada ataque?"],
    "invocados": ["Faz o Saudosista chamar só atiradores", "Faz sair um divisor uma vez em cada quatro",
                  "Porque é que o corredor está lá duas vezes?"],
    "arranque": ["Põe o tiro automático ligado desde o início", "Desliga o brilho e as riscas",
                 "O que faz cada uma destas coisas?"],
    "onda": ["Faz esta onda só de atiradores, seis de cada", "Põe esta onda mais difícil",
             "O que quer dizer de_cada?"],
    "vidas": ["Dá-me 8 corações", "Põe-me a andar mais depressa", "O que quer dizer cada número?"],
    "tiros": ["Faz-me disparar muito mais depressa", "Faz metade dos meus tiros serem críticos",
              "O que quer dizer cada número?"],
    "dash": ["Quero investir sem ter de esperar", "Faz-me piscar mais tempo depois de levar dano",
             "O que quer dizer cada número?"],
    "laser": ["Faz o laser durar 4 segundos", "Faz o laser encher com 5 mortes", "O que quer dizer cada número?"],
    "jogo": ["Faz um jogo rápido, só com 3 ondas", "Põe o Saudosista a aparecer logo na onda 2",
             "O que quer dizer cada número?"],
    "ondas": ["Põe o dobro dos inimigos em cada onda", "Faz os inimigos não ficarem mais fortes de onda para onda",
              "Como é que o jogo decide quantos inimigos vêm?"],
    "carta": ["Muda o nome e a descrição desta carta para ficarem mais engraçados", "Faz esta carta ser lendária",
              "O que quer dizer cada coisa desta linha?"],
    "frases": ["Junta três frases novas sobre Lisboa", "Põe as frases mais assustadoras", "Onde aparecem estas frases?"],
    "criticas": ["Junta uma crítica nova que dá 0/10 ao jogo", "Junta uma crítica da minha avó",
                 "Onde aparecem estas críticas?"],
    "creditos": ["Junta uma linha a agradecer à minha turma", "Junta uma linha a dizer quem fez os inimigos",
                 "Quando é que os créditos aparecem?"],
    "conquistas": ["Muda os textos para ficarem mais engraçados", "Muda o título da conquista \"morte\" para \"Ups\"",
                   "Porque é que o nome da esquerda não se pode mudar?"],
    "mover_inimigo": ["Faz os inimigos fugirem de mim quando têm menos de metade da vida",
                      "Faz os corredores virem aos ziguezagues", EXPLICA],
    "magoar_inimigo": ["O divisor tem um escudo: só leva metade do dano", "Dá-me 1 ponto por cada golpe que acerta",
                       EXPLICA],
    "disparar_balas": ["Faz-me disparar também para trás", "Faz todas as balas baterem uma vez nas paredes", EXPLICA],
    "rebentar_inimigo": ["Faz o divisor partir-se em quatro", "Faz o atirador deixar sempre um coração", EXPLICA],
    "aplicar_carta": ["Faz a Guitarra dar +2 projéteis de cada vez", "Faz o Café Duplo também me pôr a andar mais rápido",
                      "Explica-me o que faz cada carta"],
    "ao_comecar_onda": ["Dá-me um coração de 2 em 2 ondas", "Mostra um texto por cima de mim com o número da onda", QUE_FAZER],
    "ao_morrer_inimigo": ["Quando um inimigo morre, rebenta e magoa os que estão perto",
                          "De 10 em 10 mortes ganho um coração", QUE_FAZER],
    "ao_perder_coracao": ["Quando perco um coração, todos os inimigos levam 30 de dano",
                          "Quando perco um coração, o laser fica cheio", QUE_FAZER],
    "ao_disparar": ["Cada tiro meu sai também para trás", "De 10 em 10 tiros, disparo para os quatro lados", QUE_FAZER],
    "ao_carregar_tecla": ["A tecla X magoa todos os inimigos, mas só uma vez por onda", "A tecla G dá-me um coração", QUE_FAZER],
    "a_cada_frame": ["Dá-me 10 pontos por cada segundo que passa", "Os inimigos perdem vida aos poucos", QUE_FAZER],
    "desenhar_inimigo": ["Dá um olho ao inimigo", "Põe uma barra de vida por cima do inimigo",
                         "Explica-me este desenho linha a linha"],
    "desenhar_jogador": ["Faz a minha nave maior", "Põe a nave vermelha quando só me resta um coração",
                         "Explica-me este desenho linha a linha"],
    "desenhar_bala": ["Faz as balas redondas e maiores", "Dá uma cauda mais comprida às balas",
                      "Explica-me este desenho linha a linha"],
    "inimigos_da_onda": ["Faz as ondas pares só de atiradores", "Põe o dobro dos inimigos de 3 em 3 ondas", EXPLICA],
    "disparo_do_inimigo": ["Faz os inimigos dispararem em círculo, para todos os lados",
                           "Cada inimigo dispara balas da cor dele", EXPLICA],
    "pontos_por_morte": ["Faz os atiradores valerem 100 pontos", "Dá pontos a dobrar depois da onda 5", EXPLICA],
    "apanhar_recompensa": ["Faz as notas encherem um bocadinho o laser",
                           "Um coração que já não cabe vale 200 pontos", EXPLICA],
    "escolher_cartas": ["Faz aparecerem só duas cartas", "Nunca me ofereças uma carta que eu já tenha", EXPLICA],
    "ao_escolher_carta": ["Cada carta que escolho dá-me também 100 pontos",
                          "Escreve o nome da carta por cima de mim", QUE_FAZER],
    "ao_acabar_onda": ["Dá-me 50 pontos por cada coração que me resta no fim da onda",
                       "Enche-me o laser no fim de cada onda", QUE_FAZER],
    "ao_investir": ["Quando invisto, deixo uma explosão no sítio de onde saí",
                    "Quando invisto, disparo para trás", QUE_FAZER],
    "ao_disparar_laser": ["Quando ligo o laser fico 2 segundos sem levar dano",
                          "Quando ligo o laser, todos os inimigos levam 20 de dano", QUE_FAZER],
    "desenhar_bala_inimiga": ["Faz as balas inimigas quadradas", "Põe as balas inimigas maiores, para se verem bem",
                              "Explica-me este desenho linha a linha"],
    "desenhar_recompensa": ["Faz as notas redondas e maiores", "Põe os corações cor-de-rosa",
                            "Explica-me este desenho linha a linha"],
    "desenhar_aviso": ["Faz o aviso maior", "Escreve o nome do inimigo que vem aí",
                       "Explica-me este desenho linha a linha"],
}

# As regras: funcoes do jogo que se podem mudar. Para cada uma, o titulo que
# aparece na Oficina, e o que ela recebe (o jogo chama-a assim, por isso nao
# pode mudar).
REGRAS = {
    "mover_inimigo": ("Como anda cada inimigo", ["inimigo", "direcao", "distancia", "dt"]),
    "magoar_inimigo": ("O que acontece a um inimigo atingido", ["inimigo", "dano", "direcao", "critico"]),
    "disparar_balas": ("Como saem os teus tiros", ["angulo"]),
    "rebentar_inimigo": ("O que um inimigo deixa ao rebentar", ["inimigo"]),
    "aplicar_carta": ("O que cada carta faz", ["carta", "jogador"]),
    "inimigos_da_onda": ("Que inimigos vêm em cada onda", ["numero"]),
    "disparo_do_inimigo": ("Como dispara um inimigo", ["inimigo", "direcao"]),
    "pontos_por_morte": ("Quantos pontos vale um inimigo", ["inimigo"]),
    "apanhar_recompensa": ("O que te dá o que apanhas do chão", ["recompensa"]),
    "escolher_cartas": ("Que cartas aparecem", ["jogador"]),
}
INICIO_DAS_REGRAS = "# --- As regras do jogo ---"

# Os acontecimentos: funcoes que o jogo chama em certos momentos, e que vem
# vazias. E os desenhos. Tudo isto sao funcoes, como as regras.
ACONTECIMENTOS = {
    "ao_comecar_onda": ("Quando começa uma onda", ["numero"]),
    "ao_morrer_inimigo": ("Quando um inimigo morre", ["inimigo"]),
    "ao_perder_coracao": ("Quando perdes um coração", []),
    "ao_disparar": ("Quando disparas", ["angulo"]),
    "ao_carregar_tecla": ("Quando se carrega numa tecla", ["tecla"]),
    "a_cada_frame": ("A cada frame", ["dt"]),
    "ao_escolher_carta": ("Quando escolhes uma carta", ["carta"]),
    "ao_acabar_onda": ("Quando acaba uma onda", ["numero"]),
    "ao_investir": ("Quando investes", []),
    "ao_disparar_laser": ("Quando ligas o laser", []),
}
INICIO_DOS_ACONTECIMENTOS = "# --- Os acontecimentos ---"
DESENHOS = {
    "desenhar_inimigo": ("O desenho de um inimigo", ["cena", "inimigo", "p"]),
    "desenhar_jogador": ("O desenho da tua nave", ["cena", "jogador", "p"]),
    "desenhar_bala": ("O desenho de uma bala tua", ["cena", "bala", "p"]),
    "desenhar_bala_inimiga": ("O desenho de uma bala inimiga", ["cena", "bala", "p"]),
    "desenhar_recompensa": ("O desenho do que os inimigos deixam", ["cena", "recompensa", "p"]),
    "desenhar_aviso": ("O desenho do aviso de que vem aí um inimigo", ["cena", "aviso", "p"]),
}
INICIO_DOS_DESENHOS = "# --- Os desenhos ---"

# tipo da escolha -> (as funcoes desse tipo, o grupo onde aparecem, as
# explicacoes gerais que se juntam a ajuda de cada uma)
FUNCOES = {
    "regra": (REGRAS, "Regras do jogo", [INICIO_DAS_REGRAS]),
    "evento": (ACONTECIMENTOS, "Acontecimentos", [INICIO_DOS_ACONTECIMENTOS, INICIO_DAS_REGRAS]),
    "desenho": (DESENHOS, "Desenhos", [INICIO_DOS_DESENHOS]),
}

# Os bocados que sao so numeros: cada escolha mostra umas quantas linhas
# "NOME = numero" seguidas, com a explicacao que o ficheiro ja traz por
# baixo de cada uma.
BLOCOS = {
    "vidas": ["VIDAS_JOGADOR", "VELOCIDADE_JOGADOR"],
    "tiros": ["DANO_BALA", "TEMPO_ENTRE_TIROS", "VELOCIDADE_BALA", "CHANCE_CRITICO", "DANO_CRITICO"],
    "dash": ["RECARGA_INVESTIDA", "INVULNERAVEL_DEPOIS_DE_DANO"],
    "laser": ["DURACAO_LASER", "CARGA_LASER_POR_MORTE", "CHANCE_CORACAO"],
    "jogo": ["ONDAS_TOTAIS", "ONDA_DO_CHEFE"],
    "ondas": ["ORCAMENTO_BASE", "ORCAMENTO_POR_ONDA", "VIDA_EXTRA_POR_ONDA",
              "VELOCIDADE_EXTRA_POR_ONDA", "VELOCIDADE_EXTRA_MAXIMA"],
    "chefe": ["VIDA_CHEFE"],
}

# O bocado das coisas de ligar e desligar: "NOME = True" ou "NOME = False".
# Na Oficina cada uma tem uma caixa para marcar (ver caixas).
ARRANQUE = {
    "TIRO_AUTOMATICO": "Começas com o tiro automático ligado (tecla T)",
    "MUSICA_LIGADA": "O jogo arranca com música (tecla M)",
    "BRILHO_NEON": "O brilho de néon à volta de tudo (tecla B)",
    "ECRA_ANTIGO": "As riscas de televisão antiga (tecla C)",
}

# Os bocados que sao uma lista de nomes, que na Oficina se escolhem de uma
# lista (ver lista): tipo -> o nome da lista no ficheiro.
LISTAS = {
    "ataques": "PADROES_DO_CHEFE",
    "invocados": "INVOCADOS_PELO_CHEFE",
}
# Os ataques que o Saudosista sabe fazer (estao escritos na classe Chefe).
ATAQUES_DO_CHEFE = ["espiral", "farol", "aneis", "rajada", "invocar"]
# Os palcos em que esta o Saudosista.
COM_CHEFE = ["chefe", "ataques", "invocados"]
# Os palcos em que o jogo inteiro se joga sozinho, desde a onda 1 (ou, numa
# onda especial, sempre nessa onda).
JOGO_INTEIRO = ["jogo", "ondas", "arranque", "onda"]

# Os bocados que sao uma lista (ou um dicionario) de textos.
TEXTOS = {
    "frases": "FRASES_ONDA",
    "criticas": "CRITICAS",
    "creditos": "CREDITOS",
    "conquistas": "CONQUISTAS",
}

# O que aparece na lista de escolhas, pela ordem em que aparece.
TITULOS = [
    ("chefe", "Inimigos", "O Saudosista (o chefe)"),
    ("ataques", "Inimigos", "Os ataques do Saudosista"),
    ("invocados", "Inimigos", "Quem o Saudosista chama"),
    ("vidas", "Tu", "Vidas e velocidade"),
    ("tiros", "Tu", "Os teus tiros"),
    ("dash", "Tu", "Investida e dano"),
    ("laser", "Tu", "Laser e corações"),
    ("jogo", "Ondas", "Quantas ondas"),
    ("ondas", "Ondas", "Quantos inimigos"),
    ("arranque", "Ondas", "Como o jogo arranca"),
    ("frases", "Textos", "Frases das ondas"),
    ("criticas", "Textos", "Críticas do menu"),
    ("creditos", "Textos", "Créditos"),
    ("conquistas", "Textos", "Conquistas"),
]

# Cada numero: (o mais pequeno que pode ser, o maior, tem de ser inteiro?).
# Os maximos nao sao para estragar a brincadeira: acima deles o jogo fica
# preso a fazer contas ou a desenhar.
NUMEROS = {
    "ONDAS_TOTAIS": (1, 999, True),
    "ONDA_DO_CHEFE": (1, 999, True),
    "VIDAS_JOGADOR": (1, 30, True),
    "VELOCIDADE_JOGADOR": (0, 5000, False),
    "DANO_BALA": (0, 100000, False),
    "TEMPO_ENTRE_TIROS": (0, 60, False),
    "VELOCIDADE_BALA": (1, 20000, False),
    "CHANCE_CRITICO": (0, 1, False),
    "DANO_CRITICO": (0, 1000, False),
    "RECARGA_INVESTIDA": (0, 60, False),
    "INVULNERAVEL_DEPOIS_DE_DANO": (0, 60, False),
    "DURACAO_LASER": (0, 60, False),
    "CARGA_LASER_POR_MORTE": (0, 1, False),
    "CHANCE_CORACAO": (0, 1, False),
    "ORCAMENTO_BASE": (0, 300, False),
    "ORCAMENTO_POR_ONDA": (0, 100, False),
    "VIDA_EXTRA_POR_ONDA": (0, 100, False),
    "VELOCIDADE_EXTRA_POR_ONDA": (0, 100, False),
    "VELOCIDADE_EXTRA_MAXIMA": (0, 100, False),
    "VIDA_CHEFE": (1, 1000000, False),
}

# Os nomes de inimigo de que o resto do jogo precisa, e porque.
INIMIGOS_PRECISOS = {
    "corredor": "o chefe é feito a partir dele",
    "pequeno": "é o que sai de um divisor quando rebenta",
}

# As cartas a que a funcao aplicar_carta() do jogo sabe dar um efeito, tal
# como ela vem. (Se a funcao la estiver, pergunta-se a ela: ver _ids_com_efeito.)
CARTAS_COM_EFEITO = ["guitarra", "cafe", "calcada", "eletrico", "nata", "saudade", "gaivota",
                     "bacalhau", "vira", "azulejo", "sardinha", "ginjinha", "fado", "bugio"]

# As conquistas por que o jogo chama, pelo nome.
CONQUISTAS_PRECISAS = ["abrir", "sangue", "combo10", "combo25", "dash", "chefe", "morte",
                       "auto", "nata", "onda10", "raspao", "laser", "vitoria"]

# Que inimigos vem ao palco quando a coisa escolhida nao e um inimigo.
ELENCO = {
    "vidas": ["corredor"],
    "dash": ["corredor", "investida"],
    "tiros": ["divisor", "corredor", "atirador"],
    "laser": ["corredor", "corredor", "atirador"],
    "carta": ["corredor", "atirador", "corredor", "divisor"],
}
# Onde o tiro automatico comeca ligado (a tecla T liga e desliga).
COM_TIRO_AUTOMATICO = ["inimigo", "chefe", "ataques", "invocados", "tiros", "laser", "jogo", "ondas", "onda",
                       "carta"]
# Onde o jogador pode perder coracoes (quando ficam a zero, volta a nascer).
PODE_LEVAR_DANO = ["vidas", "dash", "tiros", "laser"]

JOGAR = "Clica no jogo para jogares: WASD anda, as setas disparam, Espaço investe, E é o laser."

DICAS = {
    "inimigo": "Estão sempre a chegar mais destes, e tu disparas sozinho (a tecla T desliga isso). "
               "No palco não perdes vidas. " + JOGAR,
    "chefe": "O Saudosista está sempre na arena: quando cai, vem outro. Disparas sozinho e "
             "não perdes vidas. A barra lá em cima é a vida dele.",
    "ataques": "O Saudosista está sempre na arena, a fazer os ataques pela ordem da lista: a faixa lá em "
               "baixo diz qual é o de agora. «Escolher os ataques» mostra os cinco que ele sabe fazer.",
    "invocados": "O Saudosista está sempre na arena e aqui só faz o ataque de chamar inimigos, para veres "
                 "quem vem. «Escolher os inimigos» mostra os que existem.",
    "arranque": "É o jogo inteiro, desde a onda 1, a arrancar como aqui disseres: marca e desmarca as caixas "
                "por cima do código. Sem o tiro automático ninguém dispara por ti: clica no jogo e joga. "
                "No palco não perdes vidas.",
    "onda": "É esta onda, a jogar-se sozinha, outra vez e outra vez: conta os inimigos que chegam. "
            "«Escolher os inimigos» mostra os que existem. No palco não perdes vidas.",
    "vidas": "Os corredores vêm bater-te para veres os corações a ir; quando acabam, nasces "
             "outra vez. " + JOGAR,
    "tiros": "Disparas sozinho contra o que vier (a tecla T desliga isso). Os números "
             "amarelos com ! são os tiros críticos.",
    "dash": "Clica no jogo e carrega em Espaço para investir: o anel à tua volta é a "
            "recarga. Deixa que te batam para veres quanto tempo ficas a piscar.",
    "laser": "A barra do laser começa cheia e o laser dispara sozinho. Depois repara em "
             "quantos inimigos é preciso para ela voltar a encher.",
    "jogo": "É o jogo inteiro a jogar-se sozinho, desde a onda 1, e tu não perdes vidas. "
            "Quando mudas um número, recomeça. " + JOGAR,
    "ondas": "É o jogo inteiro a jogar-se sozinho, desde a onda 1: conta os inimigos que "
             "chegam. Quando mudas um número, recomeça.",
    "carta": "A tua carta é a do meio. Escolhe-a (tecla 2, ou um clique) para a "
             "experimentares uns segundos; depois as cartas voltam.",
    "frases": "As frases aparecem uma a uma, por baixo do número da onda. "
              "No jogo a sério sai uma ao calhas.",
    "criticas": "É o menu do jogo: as críticas passam lá em baixo. "
                "A que mudares aparece logo.",
    "creditos": "É o ecrã de quem ganha o jogo, com os créditos a subir. "
                "A linha que mudares vem logo para o meio.",
    "conquistas": "As conquistas aparecem uma a uma, à direita. No jogo a sério cada uma "
                  "aparece quando a ganhas.",
    "regra": "Isto é uma regra do jogo: muda-a e o jogo passa a comportar-se de outra maneira. "
             "Há inimigos de todos sempre a chegar e tu disparas sozinho, para veres logo a diferença. " + JOGAR,
    "evento": "O jogo joga-se sozinho, onda atrás de onda, para veres o teu acontecimento a acontecer. "
              "Tira o pass e escreve o que queres que aconteça. A faixa lá em baixo mostra a tua memoria.",
    "desenho": "Isto é o desenho: muda-o e vês logo, no jogo e aumentado no canto. "
               "Experimenta mudar um número, ou acrescentar um círculo.",
}
# As funcoes cujo palco e diferente do das outras do mesmo genero.
DICAS_DAS_FUNCOES = {
    "aplicar_carta": "Escolhe uma carta (teclas 1 2 3, ou um clique) para veres o que ela te faz: os teus "
                     "números estão na faixa lá em baixo. Passados uns segundos vêm outras três cartas.",
    "ao_comecar_onda": "O jogo joga-se sozinho. Cada vez que mudas o código a onda começa outra vez, "
                       "para veres logo o teu acontecimento. A faixa lá em baixo mostra a tua memoria e em "
                       "que onda vais. Aqui não se morre: com um coração só, deixas de levar dano.",
    "ao_perder_coracao": "Aqui não disparas sozinho (a tecla T liga isso), para os inimigos te acertarem. "
                         "Cada vez que mudas o código levas um golpe, para veres logo o que acontece.",
    "ao_carregar_tecla": "O jogo joga-se sozinho. Clica no jogo e carrega na tua tecla para experimentares. "
                         "A faixa lá em baixo mostra a tua memoria.",
    "inimigos_da_onda": "É o jogo inteiro a jogar-se sozinho. Cada vez que mudas o código a onda começa outra vez, "
                        "com os inimigos que a tua regra mandar: a faixa lá em baixo diz quais são.",
    "escolher_cartas": "É o jogo inteiro a jogar-se sozinho. Cada vez que mudas o código aparecem as cartas que a "
                       "tua regra escolher: a faixa lá em baixo diz quais são.",
    "disparo_do_inimigo": "Há atiradores sempre a chegar e tu não perdes vidas, para veres bem as balas deles. "
                          "Disparas sozinho (a tecla T desliga isso).",
    "ao_escolher_carta": "O jogo joga-se sozinho. Cada vez que mudas o código aparecem as cartas, e passado um "
                         "bocadinho uma é escolhida, para veres logo o teu acontecimento.",
    "ao_acabar_onda": "O jogo joga-se sozinho. Cada vez que mudas o código a onda acaba ali mesmo, "
                      "para veres logo o teu acontecimento. A faixa lá em baixo mostra a tua memoria.",
    "ao_investir": "O jogo joga-se sozinho, e a nave investe de dois em dois segundos (ou quando carregares "
                   "em Espaço). A faixa lá em baixo mostra a tua memoria.",
    "ao_disparar_laser": "O jogo joga-se sozinho, e o laser está sempre a encher e a disparar. "
                         "A faixa lá em baixo mostra a tua memoria.",
}

# A explicacao ao lado do codigo, para os bocados em que o ficheiro do jogo
# nao traz nenhuma por cima.
AJUDA_NUMEROS = ("A explicação de cada número está por baixo dele.\n"
                 "MAIS  -> o que acontece se o número subir\n"
                 "MENOS -> o que acontece se o número descer\n"
                 "Os tempos estão em segundos (0.5 = meio segundo), as velocidades em\n"
                 "píxeis por segundo (o ecrã tem 960 de largura) e as percentagens\n"
                 "escrevem-se de 0 a 1 (0.05 = 5%).\n"
                 "Muda só o número: o nome e o = ficam como estão.")
AJUDA_ARRANQUE = ("Cada uma destas coisas está ligada (True) ou desligada (False).\n"
                  "Podes marcar e desmarcar as caixas por cima do código, ou escrever\n"
                  "True e False à mão: com maiúscula no início e sem aspas.\n"
                  "A meio do jogo, cada uma tem uma tecla que a troca.")
AJUDAS = {
    "frases": "Uma frase por linha, entre aspas e com uma vírgula no fim.\n"
              "Podes mudar as que há, apagar ou juntar mais.",
    "criticas": "Uma crítica por linha, entre aspas e com uma vírgula no fim.\n"
                "Passam no menu do jogo, uma de cada vez.",
    "creditos": "Uma linha dos créditos por cada linha, entre aspas e com vírgula.\n"
                'Uma linha vazia ("") deixa um espaço.',
    "conquistas": 'Cada conquista é   "nome": ("título", "texto"),\n'
                  "Muda o título e o texto à vontade. O nome fica como está: é por ele\n"
                  "que o jogo chama a conquista.",
}


# =====================================================================
#                    ONDE ESTA O CODIGO DE CADA COISA
# =====================================================================

def _nome_da_carta(elemento):
    # Uma carta e ("id", "nome", "descricao", raridade, unica).
    if isinstance(elemento, ast.Tuple) and len(elemento.elts) > 1:
        return blocos.texto_constante(elemento.elts[1])
    return None


def _linhas_do_bloco(arvore, linhas, nomes):
    # Da primeira instrucao "NOME = ..." do bloco ate a ultima, mais os
    # comentarios colados por baixo dela (neste jogo a explicacao de cada
    # numero vem depois dele). Devolve (inicio, fim), ou None se nao houver.
    nos = [blocos.instrucao(arvore, nome) for nome in nomes]
    nos = [no for no in nos if no is not None]
    if len(nos) == 0:
        return None
    inicio = min(no.lineno for no in nos)
    fim = max(no.end_lineno for no in nos)
    while fim < len(linhas) and linhas[fim].lstrip().startswith("#"):
        fim = fim + 1
    return (inicio, fim)


def _existe(arvore, tipo):
    # Ha no ficheiro o bocado deste tipo (uns numeros, uns textos, uma lista)?
    if tipo in BLOCOS:
        return any(blocos.instrucao(arvore, nome) is not None for nome in BLOCOS[tipo])
    if tipo == "arranque":
        return any(blocos.instrucao(arvore, nome) is not None for nome in ARRANQUE)
    if tipo in LISTAS:
        return blocos.instrucao(arvore, LISTAS[tipo]) is not None
    return blocos.instrucao(arvore, TEXTOS[tipo]) is not None


def _ondas_especiais(arvore):
    # As ondas de ONDAS_ESPECIAIS: [(numero da onda, a ficha, primeira linha,
    # ultima linha), ...], pela ordem em que estao escritas.
    no = blocos.instrucao(arvore, "ONDAS_ESPECIAIS")
    if no is None or not isinstance(no.value, ast.Dict):
        return []
    ondas = []
    for (chave, primeira, ultima), ficha in zip(blocos.entradas(no) or [], no.value.values):
        numero = chave.value if isinstance(chave, ast.Constant) else None
        ondas.append((numero, ficha, primeira, ultima))
    return ondas


def escolhas(fonte):
    arvore = ast.parse(fonte)
    lista = []

    no = blocos.instrucao(arvore, "PERFIS")
    partes = blocos.entradas(no) if no is not None else None
    if partes:
        for i, (chave, _, _) in enumerate(partes):
            nome = blocos.texto_constante(chave) or "Inimigo " + str(i + 1)
            lista.append({"id": "inimigo:" + str(i), "grupo": "Inimigos", "titulo": nome})

    for tipo, grupo, titulo in TITULOS:
        if _existe(arvore, tipo):
            lista.append({"id": tipo, "grupo": grupo, "titulo": titulo})

    for i, (numero, _, _, _) in enumerate(_ondas_especiais(arvore)):
        lista.append({"id": "onda:" + str(i), "grupo": "Ondas", "titulo": "Onda " + str(numero) + " (especial)"})

    no = blocos.instrucao(arvore, "MELHORIAS")
    partes = blocos.entradas(no) if no is not None else None
    if partes:
        for i, (elemento, _, _) in enumerate(partes):
            nome = _nome_da_carta(elemento) or "Carta " + str(i + 1)
            lista.append({"id": "carta:" + str(i), "grupo": "Cartas", "titulo": nome})

    for tipo in FUNCOES:
        funcoes, grupo, _ = FUNCOES[tipo]
        for nome in funcoes:
            if blocos.funcao(arvore, nome) is not None:
                lista.append({"id": tipo + ":" + nome, "grupo": grupo, "titulo": funcoes[nome][0]})

    # Os grupos ficam juntos, pela ordem em que apareceram pela primeira vez.
    ordem = []
    for escolha in lista:
        if escolha["grupo"] not in ordem:
            ordem.append(escolha["grupo"])
    lista.sort(key=lambda escolha: ordem.index(escolha["grupo"]))
    return lista


def regiao(fonte, escolha):
    # Devolve {"inicio", "fim", "ajuda", "titulo", "dica", "imagem", "som",
    # "sugestoes"} ou None. "imagem" e o nome do PNG que essa coisa usa (None
    # se nao usa nenhum), e "som" o do WAV: neste jogo so os inimigos de
    # PERFIS e que os tem. Pode levar ainda "apagar" e "lista" (o que dizem
    # esses botoes na Oficina) e "caixas" (ha caixas para marcar).
    arvore = ast.parse(fonte)
    linhas = fonte.split("\n")
    tipo, _, numero = escolha.partition(":")
    if tipo not in DICAS:
        return None
    if tipo in FUNCOES:
        # Uma regra, um acontecimento ou um desenho: e uma funcao inteira. A
        # ajuda junta o que o ficheiro diz sobre ela ao que se pode usar
        # dentro de qualquer funcao desse genero.
        funcoes, _, gerais = FUNCOES[tipo]
        no = blocos.funcao(arvore, numero) if numero in funcoes else None
        if no is None:
            return None
        ajuda = blocos.ajuda_acima(linhas, no.lineno)
        for inicio in gerais:
            geral = blocos.comentarios_a_partir_de(linhas, inicio)
            if geral and geral != ajuda:
                ajuda = ajuda + "\n\n" + geral
        return {"inicio": no.lineno, "fim": no.end_lineno, "ajuda": ajuda,
                "dica": DICAS_DAS_FUNCOES.get(numero, DICAS[tipo]), "titulo": funcoes[numero][0],
                "imagem": None, "som": None, "sugestoes": SUGESTOES[numero]}
    resposta = {"dica": DICAS[tipo], "imagem": None, "som": None, "sugestoes": SUGESTOES[tipo]}

    if tipo in BLOCOS:
        limites = _linhas_do_bloco(arvore, linhas, BLOCOS[tipo])
        if limites is None:
            return None
        titulo = [t for t in TITULOS if t[0] == tipo][0][2]
        resposta.update(inicio=limites[0], fim=limites[1], titulo=titulo, ajuda=AJUDA_NUMEROS)
        return resposta

    if tipo in TEXTOS:
        no = blocos.instrucao(arvore, TEXTOS[tipo])
        if no is None:
            return None
        titulo = [t for t in TITULOS if t[0] == tipo][0][2]
        ajuda = blocos.ajuda_acima(linhas, no.lineno) or AJUDAS[tipo]
        resposta.update(inicio=no.lineno, fim=no.end_lineno, titulo=titulo, ajuda=ajuda)
        return resposta

    if tipo == "arranque":
        limites = _linhas_do_bloco(arvore, linhas, list(ARRANQUE))
        if limites is None:
            return None
        resposta.update(inicio=limites[0], fim=limites[1], titulo="Como o jogo arranca", ajuda=AJUDA_ARRANQUE,
                        caixas=True)
        return resposta

    if tipo in LISTAS:
        # Uma lista de nomes, que se escolhem de uma lista.
        no = blocos.instrucao(arvore, LISTAS[tipo])
        if no is None:
            return None
        titulo = [t for t in TITULOS if t[0] == tipo][0][2]
        resposta.update(inicio=no.lineno, fim=no.end_lineno, titulo=titulo,
                        ajuda=blocos.ajuda_acima(linhas, no.lineno),
                        lista="Escolher os ataques" if tipo == "ataques" else "Escolher os inimigos")
        return resposta

    if tipo == "onda":
        ondas = _ondas_especiais(arvore)
        if not numero.isdigit() or int(numero) >= len(ondas):
            return None
        qual, _, inicio, fim = ondas[int(numero)]
        no = blocos.instrucao(arvore, "ONDAS_ESPECIAIS")
        resposta.update(inicio=inicio, fim=fim, titulo="Onda " + str(qual) + " (especial)",
                        ajuda=blocos.ajuda_acima(linhas, no.lineno), lista="Escolher os inimigos",
                        apagar="Apagar esta onda especial")
        return resposta

    # Um inimigo ou uma carta: uma entrada so, dentro de PERFIS ou MELHORIAS.
    no = blocos.instrucao(arvore, "PERFIS" if tipo == "inimigo" else "MELHORIAS")
    if no is None:
        return None
    partes = blocos.entradas(no)
    if not partes or not numero.isdigit() or int(numero) >= len(partes):
        return None
    parte, inicio, fim = partes[int(numero)]
    if tipo == "inimigo":
        titulo = blocos.texto_constante(parte)
        ficha = blocos.valor_da_entrada(no, int(numero))
        resposta["imagem"] = blocos.valor_da_chave(ficha, "imagem")
        resposta["som"] = blocos.valor_da_chave(ficha, "som")
        if titulo not in INIMIGOS_PRECISOS:
            resposta["apagar"] = "Apagar este inimigo"
    else:
        titulo = _nome_da_carta(parte)
        resposta["apagar"] = "Apagar esta carta"
    resposta["caixas"] = True
    resposta.update(inicio=inicio, fim=fim, titulo=titulo or escolha,
                    ajuda=blocos.ajuda_acima(linhas, no.lineno))
    return resposta


# =====================================================================
#                        CRIAR UMA COISA NOVA
# =====================================================================
# Um inimigo novo ou uma carta nova nascem como copia do mais simples que
# la esta (o corredor, o Cafe Duplo), com outro nome, e ficam no fim da
# lista. Devolve o ficheiro inteiro ja com a coisa nova, a escolha a abrir,
# e uma frase a contar o que se fez.

def _nome_livre(base, existentes, espaco=""):
    nome = base
    numero = 2
    while nome in existentes:
        nome = base + espaco + str(numero)
        numero = numero + 1
    return nome


def _por_virgula(linhas, ultima):
    # A linha onde acaba a ultima entrada tem de acabar numa virgula, para
    # se poder escrever outra entrada a seguir.
    if not linhas[ultima - 1].rstrip().endswith(","):
        linhas[ultima - 1] = linhas[ultima - 1].rstrip() + ","


def _novo_inimigo(fonte):
    arvore = ast.parse(fonte)
    linhas = fonte.split("\n")
    no = blocos.instrucao(arvore, "PERFIS")
    partes = blocos.entradas(no) if no is not None else None
    if not partes:
        raise ValueError("não encontrei os PERFIS no ficheiro.")
    nomes = [blocos.texto_constante(chave) for chave, _, _ in partes]
    # Copia-se o corredor, que e o mais simples. Se ja nao houver, o primeiro.
    qual = nomes.index("corredor") if "corredor" in nomes else 0
    antigo = nomes[qual]
    if antigo is None:
        raise ValueError("não percebi o nome do primeiro inimigo.")
    _, inicio, fim = partes[qual]
    ultima = partes[-1][2]
    nome = _nome_livre("novo", nomes)

    texto = "\n".join(linhas[inicio - 1:fim])
    texto = texto.replace('"' + antigo + '"', '"' + nome + '"', 1)
    corpo = blocos.corpo_livre("\n".join(linhas), nome)      # ficheiros so dele
    texto = re.sub(r'"imagem": "[^"]*"', '"imagem": "' + corpo + '.png"', texto)
    texto = re.sub(r'"som": "[^"]*"', '"som": "' + corpo + '.wav"', texto)
    # Para aparecer logo na onda 1 do jogo, e para nao se confundir com o
    # outro: fica amarelo.
    texto = re.sub(r'"desde_onda": \w+', '"desde_onda": 1', texto)
    texto = re.sub(r'"custo": 0\b', '"custo": 1', texto)
    texto = re.sub(r'"cor": (\([^)]*\)|\w+)', '"cor": AMARELO', texto)
    if not texto.rstrip().endswith(","):
        texto = texto.rstrip() + ","
    # As linhas de baixo da ficha vinham alinhadas pelo nome antigo.
    copia = texto.split("\n")
    for i in range(1, len(copia)):
        if len(nome) >= len(antigo):
            copia[i] = " " * (len(nome) - len(antigo)) + copia[i]
        elif copia[i].startswith(" " * (len(antigo) - len(nome) + 4)):
            copia[i] = copia[i][len(antigo) - len(nome):]
    _por_virgula(linhas, ultima)
    nova = "\n".join(linhas[:ultima] + copia + linhas[ultima:])
    aviso = ('Criei o "' + nome + '", igual ao ' + antigo + " mas amarelo. Aparece logo na onda 1. "
             'Muda-lhe o nome e os números. Ele corre para ti: para andar de outra maneira, vê "Como anda '
             'cada inimigo" nas Regras do jogo.')
    return nova, "inimigo:" + str(len(partes)), aviso


def _ramo_da_carta(funcao, ident):
    # Dentro de aplicar_carta(), a cadeia de if / elif. Devolve (as linhas
    # onde esta o que a carta "ident" faz, a linha onde acaba a cadeia, a
    # margem do if), ou None se a funcao ja nao for uma cadeia dessas.
    if funcao is None or len(funcao.body) == 0 or not isinstance(funcao.body[-1], ast.If):
        return None
    no = funcao.body[-1]
    margem = no.col_offset
    corpo = None
    while True:
        teste = no.test
        if (isinstance(teste, ast.Compare) and len(teste.comparators) == 1
                and blocos.texto_constante(teste.comparators[0]) == ident):
            corpo = (no.body[0].lineno, no.body[-1].end_lineno)
        if len(no.orelse) == 1 and isinstance(no.orelse[0], ast.If):
            no = no.orelse[0]
        elif len(no.orelse) == 0:
            break
        else:
            return None         # acaba num "else": nao se pode por um elif depois
    if corpo is None:
        return None
    return corpo, no.end_lineno, margem


def _nova_carta(fonte):
    arvore = ast.parse(fonte)
    linhas = fonte.split("\n")
    no = blocos.instrucao(arvore, "MELHORIAS")
    partes = blocos.entradas(no) if no is not None else None
    if not partes:
        raise ValueError("não encontrei as MELHORIAS no ficheiro.")
    cartas = []
    for elemento, _, _ in partes:
        try:
            carta = ast.literal_eval(elemento)
        except ValueError:
            carta = None
        if not isinstance(carta, tuple) or len(carta) != 5 or not isinstance(carta[0], str):
            raise ValueError("há uma carta em MELHORIAS que não percebi. Arranja-a primeiro.")
        cartas.append(carta)
    ids = [carta[0] for carta in cartas]
    # Copia-se o Cafe Duplo, que so muda um numero. Se ja nao houver, a primeira.
    qual = ids.index("cafe") if "cafe" in ids else 0
    antiga = cartas[qual]
    ident = _nome_livre("carta_nova", ids)
    nome = _nome_livre("Carta nova", [carta[1] for carta in cartas], " ")
    ultima = partes[-1][2]
    primeira = linhas[partes[0][1] - 1]
    margem = primeira[:len(primeira) - len(primeira.lstrip())]
    linha = (margem + "(" + json.dumps(ident) + ", " + json.dumps(nome, ensure_ascii=False) + ", "
             + json.dumps(antiga[2], ensure_ascii=False) + ", " + repr(antiga[3]) + ", " + repr(antiga[4]) + "),")

    # O que a carta faz: mais um "elif" no fim de aplicar_carta(), igual ao
    # da carta copiada. (Primeiro este, que fica mais abaixo no ficheiro:
    # assim as linhas das MELHORIAS ainda sao as mesmas.)
    ramo = _ramo_da_carta(blocos.funcao(arvore, "aplicar_carta"), antiga[0])
    if ramo is not None and ramo[1] > ultima:
        corpo, fim, espacos = ramo
        elif_novo = [" " * espacos + "elif carta == " + json.dumps(ident) + ":"] + linhas[corpo[0] - 1:corpo[1]]
        linhas = linhas[:fim] + elif_novo + linhas[fim:]
    else:
        ramo = None
    _por_virgula(linhas, ultima)
    linhas = linhas[:ultima] + [linha] + linhas[ultima:]

    aviso = 'Criei a carta "' + nome + '", igual à "' + str(antiga[1]) + '". Muda-lhe o nome e a descrição. '
    if ramo is not None:
        aviso = aviso + 'O que ela faz está nas Regras do jogo, em "O que cada carta faz": é o último elif.'
    else:
        aviso = aviso + ('Ainda não faz nada: escreve o que ela faz nas Regras do jogo, em "O que cada '
                         'carta faz", com um elif carta == "' + ident + '":')
    return "\n".join(linhas), "carta:" + str(len(partes)), aviso


def _valor(arvore, nome):
    # O valor de "NOME = ..." escrito no ficheiro, ou None se nao se percebe
    # (os PERFIS, por exemplo, que usam os nomes das cores).
    no = blocos.instrucao(arvore, nome)
    try:
        return ast.literal_eval(no.value)
    except (ValueError, SyntaxError, AttributeError, TypeError):
        return None


def _nomes_dos_inimigos(arvore):
    no = blocos.instrucao(arvore, "PERFIS")
    partes = blocos.entradas(no) if no is not None else None
    return [blocos.texto_constante(chave) for chave, _, _ in partes or [] if blocos.texto_constante(chave)]


def _nova_onda(fonte):
    # Uma onda especial nova: a primeira onda que ainda nao e especial nem e
    # do Saudosista, com tres de cada um dos dois primeiros inimigos.
    arvore = ast.parse(fonte)
    linhas = fonte.split("\n")
    no = blocos.instrucao(arvore, "ONDAS_ESPECIAIS")
    if no is None or not isinstance(no.value, ast.Dict):
        raise ValueError("não encontrei as ONDAS_ESPECIAIS no ficheiro.")
    ondas = _ondas_especiais(arvore)
    if len(ondas) != len(no.value.keys):
        raise ValueError("não percebi como estão escritas as ONDAS_ESPECIAIS: põe cada onda na sua linha.")
    usadas = [numero for numero, _, _, _ in ondas]
    do_chefe = _valor(arvore, "ONDA_DO_CHEFE")
    do_chefe = do_chefe if isinstance(do_chefe, int) and do_chefe > 0 else 5
    numero = 2
    while numero in usadas or numero % do_chefe == 0:
        numero = numero + 1
    nomes = _nomes_dos_inimigos(arvore)[:2] or ["corredor"]
    nova = ("    " + str(numero) + ': {"inimigos": [' + ", ".join(json.dumps(nome, ensure_ascii=False) for nome in nomes)
            + '], "de_cada": 3},')
    if ondas:
        ultima = ondas[-1][3]
        _por_virgula(linhas, ultima)
        linhas[ultima:ultima] = [nova]
    elif no.lineno == no.end_lineno:
        linhas[no.lineno - 1:no.lineno] = ["ONDAS_ESPECIAIS = {", nova, "}"]
    else:
        linhas[no.end_lineno - 1:no.end_lineno - 1] = [nova]       # antes da linha que fecha
    aviso = ("Criei a onda " + str(numero) + " especial: em vez dos inimigos do orçamento, vêm 3 de cada um dos "
             "que lá estão. Escolhe os inimigos e muda o número da onda e o de_cada.")
    return "\n".join(linhas), "onda:" + str(len(ondas)), aviso


def _nova_frase(fonte):
    arvore = ast.parse(fonte)
    linhas = fonte.split("\n")
    no = blocos.instrucao(arvore, "FRASES_ONDA")
    partes = blocos.entradas(no) if no is not None else None
    if not partes:
        raise ValueError("não percebi como estão escritas as FRASES_ONDA no ficheiro.")
    frases = [blocos.texto_constante(elemento) for elemento, _, _ in partes]
    frase = _nome_livre("Uma frase nova, escrita por ti.", frases, " ")
    ultima = partes[-1][2]
    primeira = linhas[partes[0][1] - 1]
    margem = primeira[:len(primeira) - len(primeira.lstrip())]
    _por_virgula(linhas, ultima)
    linhas[ultima:ultima] = [margem + json.dumps(frase, ensure_ascii=False) + ","]
    aviso = ("Juntei uma frase nova ao fim das frases das ondas: é a última. Muda-a para o que quiseres. "
             "No jogo sai uma ao calhas no início de cada onda.")
    return "\n".join(linhas), "frases", aviso


def novo(fonte, grupo):
    if grupo == "Inimigos":
        return _novo_inimigo(fonte)
    if grupo == "Cartas":
        return _nova_carta(fonte)
    if grupo == "Ondas":
        return _nova_onda(fonte)
    if grupo == "Textos":
        return _nova_frase(fonte)
    raise ValueError("aqui não dá para criar isso.")


# =====================================================================
#                          APAGAR UMA COISA
# =====================================================================
# Um inimigo, uma carta ou uma onda especial saem do jogo. O inimigo sai
# tambem dos sitios onde o chamavam pelo nome (a lista de quem o Saudosista
# chama, as ondas especiais); onde ficaria uma lista vazia fica o corredor,
# para o jogo nao parar. Devolve o ficheiro inteiro ja sem a coisa, e uma
# frase a contar o que se fez. (As ferramentas para tirar bocados do
# ficheiro sao as do bicharada.py.)

def _tirar_nome(linhas, lista, nome, cortes, trocas):
    # Tira um nome de uma lista [...] escrita no codigo, todas as vezes que
    # la estiver. Diz se la estava.
    dele = [no for no in lista.elts if blocos.texto_constante(no) == nome]
    ficam = len(lista.elts) - len(dele)
    for no in dele:
        if (ficam == 0 and no is dele[0]) or not base._tirar_da_lista(linhas, no, cortes, trocas):
            base._trocar_no(linhas, no, '"corredor"', trocas)
    return len(dele) > 0


def apagar(fonte, escolha):
    tipo, _, numero = escolha.partition(":")
    arvore = ast.parse(fonte)
    linhas = fonte.split("\n")
    cortes = []
    trocas = []
    if not numero.isdigit():
        raise ValueError("isso não se pode apagar.")
    qual = int(numero)

    if tipo == "onda":
        ondas = _ondas_especiais(arvore)
        if qual >= len(ondas):
            raise ValueError("isso não se pode apagar.")
        onda, _, inicio, fim = ondas[qual]
        cortes.append((inicio, fim))
        return base._aplicar(linhas, cortes, trocas), ("Apaguei a onda " + str(onda) + " especial: essa onda volta "
                                                       "a ter os inimigos do orçamento.")

    no = blocos.instrucao(arvore, {"inimigo": "PERFIS", "carta": "MELHORIAS"}.get(tipo, ""))
    partes = blocos.entradas(no) if no is not None else None
    if not partes or qual >= len(partes):
        raise ValueError("isso não se pode apagar.")
    parte, inicio, fim = partes[qual]
    cortes.append((inicio, fim))

    if tipo == "carta":
        if len(partes) < 2:
            raise ValueError("tem de haver pelo menos uma carta.")
        nome = _nome_da_carta(parte) or "a carta"
        aviso = ('Apaguei a carta "' + nome + '". O elif dela em "O que cada carta faz" ficou lá: '
                 "não faz mal nenhum, e podes apagá-lo à mão.")
        return base._aplicar(linhas, cortes, trocas), aviso

    nome = blocos.texto_constante(parte)
    if nome in INIMIGOS_PRECISOS:
        raise ValueError('o jogo precisa do "' + nome + '": ' + INIMIGOS_PRECISOS[nome] + ".")
    # Sai tambem de onde o chamavam pelo nome.
    onde = []
    invocados = blocos.instrucao(arvore, "INVOCADOS_PELO_CHEFE")
    if invocados is not None and isinstance(invocados.value, ast.List):
        if _tirar_nome(linhas, invocados.value, nome, cortes, trocas):
            onde.append("de quem o Saudosista chama")
    for onda, ficha, _, _ in _ondas_especiais(arvore):
        lista = base._lista_da_chave(ficha, "inimigos")
        if lista is not None and _tirar_nome(linhas, lista, nome, cortes, trocas):
            onde.append("da onda " + str(onda) + " especial")
    aviso = 'Apaguei o "' + str(nome) + '".'
    if len(onde) == 1:
        aviso = aviso + " Saiu também " + onde[0] + "."
    elif onde:
        aviso = aviso + " Saiu também " + ", ".join(onde[:-1]) + " e " + onde[-1] + "."
    return base._aplicar(linhas, cortes, trocas), aviso


# =====================================================================
#                    ESCOLHER NOMES DE UMA LISTA
# =====================================================================
# Onde o ficheiro tem uma lista de nomes (os ataques do Saudosista, quem ele
# chama, os inimigos de uma onda especial), a Oficina mostra os nomes que
# existem e a crianca carrega neles, pela ordem em que os quer. Trabalha-se
# sobre o codigo que esta no editor, e devolve-se esse codigo com a lista
# nova: o resto do caminho e o de sempre, como se a crianca o tivesse escrito.
#   sem "escolhidos": devolve a lista e os que la estao agora
#   com "escolhidos": devolve {"codigo": ...}

# tipo -> (o que vem antes do [ no codigo, o titulo, a nota)
ONDE_ESTA_A_LISTA = {
    "ataques": (r"=\s*", "Que ataques faz o Saudosista?",
                "Carrega neles pela ordem em que os faz. Quando chega ao fim, volta ao primeiro."),
    "invocados": (r"=\s*", "Quem é que o Saudosista chama?",
                  "Ele tira um destes ao calhas para cada inimigo que chama. "
                  "(Para um sair mais vezes, escreve o nome dele duas vezes, no código.)"),
    "onda": (r'"inimigos"\s*:\s*', "Que inimigos vêm nesta onda?",
             'Vêm tantos de cada um como disser o "de_cada", pela ordem em que carregares neles.'),
}


def lista(fonte, escolha, codigo, escolhidos=None):
    tipo = escolha.partition(":")[0]
    if tipo not in ONDE_ESTA_A_LISTA:
        raise ValueError("aqui não há nada para escolher de uma lista.")
    antes, titulo, nota = ONDE_ESTA_A_LISTA[tipo]
    opcoes = ATAQUES_DO_CHEFE if tipo == "ataques" else _nomes_dos_inimigos(ast.parse(fonte))
    onde = re.search("(" + antes + r")\[(.*?)\]", codigo, re.DOTALL)
    atuais = None
    if onde is not None:
        try:
            atuais = ast.literal_eval("[" + onde.group(2) + "]")
        except (ValueError, SyntaxError):
            atuais = None
    if not isinstance(atuais, list):
        raise ValueError("o código tem um erro: corrige-o primeiro, ou carrega em Repor o original.")
    if escolhidos is None:
        vistos = []
        for nome in atuais:
            if nome in opcoes and nome not in vistos:
                vistos.append(nome)
        return {"titulo": titulo, "opcoes": list(opcoes), "escolhidos": vistos, "nota": nota}

    novos = []
    for nome in escolhidos if isinstance(escolhidos, list) else []:
        if nome in opcoes and nome not in novos:
            novos.append(nome)
    if len(novos) == 0:
        raise ValueError("tens de escolher pelo menos um.")
    escrito = "[" + ", ".join(json.dumps(nome, ensure_ascii=False) for nome in novos) + "]"
    return {"codigo": codigo[:onde.start(2) - 1] + escrito + codigo[onde.end(2) + 1:]}


# =====================================================================
#                        CAIXAS PARA MARCAR
# =====================================================================
# Ha coisas que no codigo sao um True ou um False, e que na Oficina se
# marcam numa caixa: como o jogo arranca, se um inimigo dispara e se aparece
# nas ondas, se uma carta so se apanha uma vez. Como nas listas, trabalha-se
# sobre o codigo que esta no editor.
#   sem "chave": devolve as caixas e como estao
#   com "chave": devolve {"codigo": ...} ja com esse valor

CAIXAS_DO_INIMIGO = {
    "dispara": "Dispara contra ti, como o atirador",
    "desde_onda": "Aparece nas ondas (desmarcado, só aparece se alguma coisa o chamar)",
}
CAIXA_DA_CARTA = {"unica": "Só se pode apanhar uma vez"}
ERRO_NO_CODIGO = "o código tem um erro: corrige-o primeiro, ou carrega em Repor o original."


def _trocar_no_texto(linhas, no, texto, desvio=0):
    # O que esta escrito num no (de uma linha so) passa a ser "texto".
    # desvio: quantas linhas a mais tinha o codigo que se deu a ler ao Python.
    linha = linhas[no.lineno - 1 - desvio]
    linhas[no.lineno - 1 - desvio] = (linha[:base._coluna(linha, no.col_offset)] + texto
                                      + linha[base._coluna(linha, no.end_col_offset):])


def caixas(fonte, escolha, codigo, chave=None, valor=None):
    tipo = escolha.partition(":")[0]
    texto = codigo.rstrip()
    fim = codigo[len(texto):]
    linhas = texto.split("\n")

    if tipo == "arranque":
        estado = {}
        for nome in ARRANQUE:
            for numero, linha in enumerate(linhas):
                acerto = re.match(r"(" + nome + r"\s*=\s*)(True|False)\b", linha)
                if acerto:
                    estado[nome] = (numero, acerto)
        if chave is None:
            return {"caixas": [{"chave": nome, "texto": ARRANQUE[nome],
                                "ligada": nome in estado and estado[nome][1].group(2) == "True"}
                               for nome in ARRANQUE if nome in estado]}
        if chave not in estado:
            raise ValueError('não encontrei a linha "' + str(chave) + ' = True" (ou False) no código.')
        numero, acerto = estado[chave]
        linhas[numero] = acerto.group(1) + ("True" if valor else "False") + linhas[numero][acerto.end():]
        return {"codigo": "\n".join(linhas) + fim}

    if tipo == "carta":
        try:
            carta = ast.parse(texto.rstrip(","), mode="eval").body
        except SyntaxError:
            raise ValueError(ERRO_NO_CODIGO)
        if not isinstance(carta, ast.Tuple) or len(carta.elts) != 5 or carta.elts[4].lineno != carta.elts[4].end_lineno:
            raise ValueError("a carta tem de ter 5 coisas entre ( ): id, nome, descrição, raridade e única.")
        unica = carta.elts[4]
        if chave is None:
            return {"caixas": [{"chave": "unica", "texto": CAIXA_DA_CARTA["unica"],
                                "ligada": isinstance(unica, ast.Constant) and unica.value is True}]}
        if chave != "unica":
            raise ValueError("essa caixa não existe.")
        _trocar_no_texto(linhas, unica, "True" if valor else "False")
        return {"codigo": "\n".join(linhas) + fim}

    if tipo != "inimigo":
        raise ValueError("aqui não há caixas para marcar.")
    # A ficha de um inimigo e   "nome": {...},   que sozinha nao e Python:
    # le-se dentro de { }, numa linha a mais por cima (o "desvio").
    try:
        fora = ast.parse("{\n" + texto + "\n}", mode="eval").body
    except SyntaxError:
        raise ValueError(ERRO_NO_CODIGO)
    if not isinstance(fora, ast.Dict) or len(fora.values) != 1 or not isinstance(fora.values[0], ast.Dict):
        raise ValueError("não percebi a ficha deste inimigo.")
    ficha = fora.values[0]
    valores = {}
    for k, v in zip(ficha.keys, ficha.values):
        if blocos.texto_constante(k) in CAIXAS_DO_INIMIGO:
            valores[blocos.texto_constante(k)] = v
    if chave is None:
        dispara = valores.get("dispara")
        desde = valores.get("desde_onda")
        return {"caixas": [
            {"chave": "dispara", "texto": CAIXAS_DO_INIMIGO["dispara"],
             "ligada": isinstance(dispara, ast.Constant) and dispara.value is True},
            {"chave": "desde_onda", "texto": CAIXAS_DO_INIMIGO["desde_onda"],
             "ligada": desde is not None and not (isinstance(desde, ast.Constant) and desde.value is None)},
        ]}
    if chave not in CAIXAS_DO_INIMIGO:
        raise ValueError("essa caixa não existe.")
    no = valores.get(chave)
    if no is not None and no.lineno != no.end_lineno:
        raise ValueError('não percebi o que está escrito em "' + chave + '".')
    if chave == "desde_onda":
        if no is None:
            raise ValueError('falta o "desde_onda" na ficha: escreve "desde_onda": 1,')
        marcada = not (isinstance(no, ast.Constant) and no.value is None)
        if bool(valor) != marcada:
            # Desmarcar: None (nunca aparece sozinho). Marcar: desde a onda 1.
            _trocar_no_texto(linhas, no, "1" if valor else "None", 1)
    elif no is not None:
        _trocar_no_texto(linhas, no, "True" if valor else "False", 1)
    elif valor:
        # Ainda nao esta na ficha: vai para o fim dela, antes do } que a fecha.
        linha = linhas[ficha.end_lineno - 2]
        fecho = base._coluna(linha, ficha.end_col_offset) - 1
        antes = linha[:fecho].rstrip()
        junta = " " if antes.endswith(",") or antes.endswith("{") else ", "
        linhas[ficha.end_lineno - 2] = antes + junta + '"dispara": True' + linha[fecho:]
    return {"codigo": "\n".join(linhas) + fim}


# =====================================================================
#                 VER SE O QUE FOI ESCRITO FAZ SENTIDO
# =====================================================================
# Antes de uma mudanca entrar no jogo, passa por aqui. Devolve duas listas
# de frases: problemas (a mudanca nao entra) e avisos (entra, mas atencao).

def _numero(valor):
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


def _inteiro(valor):
    return isinstance(valor, int) and not isinstance(valor, bool)


def _cor(valor):
    if not isinstance(valor, (tuple, list)) or len(valor) != 3:
        return False
    for parte in valor:
        if not _inteiro(parte) or parte < 0 or parte > 255:
            return False
    return True


def _ver_valor(valor, quem, limites, problemas):
    # quem e como se fala do numero: VIDAS_JOGADOR, ou corredor: "vida".
    minimo, maximo, inteiro = limites
    if not _numero(valor) or valor != valor:
        problemas.append(quem + " tem de ser um número, sem aspas.")
    elif inteiro and not _inteiro(valor):
        problemas.append(quem + " tem de ser um número inteiro, como 3 (e não 3.5).")
    elif valor < minimo:
        problemas.append(quem + " não pode ser menos que " + str(minimo) + ".")
    elif valor > maximo and maximo == 1:
        problemas.append(quem + " vai de 0 a 1: é uma percentagem (0.5 = 50%, 1 = 100%).")
    elif valor > maximo:
        problemas.append(quem + " é grande demais para o jogo. O máximo é " + str(maximo) + ".")


def _ver_numeros(ns, problemas, avisos):
    for nome, limites in NUMEROS.items():
        if nome not in ns:
            problemas.append("Falta " + nome + ".")
        else:
            _ver_valor(ns[nome], nome, limites, problemas)


# O que cada ficha de PERFIS tem de ter: (minimo, maximo, inteiro?).
FICHA_DE_INIMIGO = {
    "raio": (1, 200, False),
    "vida": (1, 1000000, False),
    "velocidade": (0, 3000, False),
    "lados": (3, 40, True),
    "pontos": (0, 1000000, False),
    "custo": (0, 1000, True),
}


def _ver_perfis(ns, problemas, avisos):
    perfis = ns.get("PERFIS")
    if not isinstance(perfis, dict) or len(perfis) == 0:
        problemas.append("Tem de haver pelo menos um inimigo em PERFIS.")
        return
    na_onda_1 = False
    for nome, ficha in perfis.items():
        quem = str(nome)
        if not isinstance(nome, str):
            problemas.append("O nome de um inimigo tem de estar entre aspas.")
            continue
        if not isinstance(ficha, dict):
            problemas.append(quem + ": a ficha tem de estar entre { }.")
            continue
        for chave, limites in FICHA_DE_INIMIGO.items():
            if chave not in ficha:
                problemas.append(quem + ': falta "' + chave + '".')
            else:
                _ver_valor(ficha[chave], quem + ': "' + chave + '"', limites, problemas)
        if "cor" not in ficha:
            problemas.append(quem + ': falta a "cor".')
        elif not _cor(ficha["cor"]):
            problemas.append(quem + ': a "cor" é uma das cores lá de cima (ROSA, VERDE...) '
                             "ou três números de 0 a 255, como (200, 60, 60).")
        if "desde_onda" not in ficha:
            problemas.append(quem + ': falta "desde_onda".')
        elif ficha["desde_onda"] is not None:
            _ver_valor(ficha["desde_onda"], quem + ': "desde_onda"', (1, 999, True), problemas)
            if ficha["desde_onda"] == 1 and _numero(ficha.get("custo")) and ficha["custo"] > 0:
                na_onda_1 = True
        if "dispara" in ficha and not isinstance(ficha["dispara"], bool):
            problemas.append(quem + ': o "dispara" é True ou False, sem aspas.')
        if "imagem" in ficha and not isinstance(ficha["imagem"], str):
            problemas.append(quem + ': a "imagem" é o nome de um ficheiro, entre aspas, como "corredor.png".')
        if "som" in ficha and not isinstance(ficha["som"], str):
            problemas.append(quem + ': o "som" é o nome de um ficheiro, entre aspas, como "corredor.wav".')
    for nome, razao in INIMIGOS_PRECISOS.items():
        if nome not in perfis:
            problemas.append('Tem de haver um inimigo chamado "' + nome + '": ' + razao + ".")
    if not problemas and not na_onda_1:
        avisos.append('Nenhum inimigo tem "desde_onda": 1 e custo acima de 0: a onda 1 fica vazia.')


def _ver_arranque(ns, problemas, avisos):
    for nome in ARRANQUE:
        if nome not in ns:
            problemas.append("Falta " + nome + ".")
        elif not isinstance(ns[nome], bool):
            problemas.append(nome + " é True (ligado) ou False (desligado), com maiúscula e sem aspas.")


def _ver_listas(ns, problemas, avisos):
    # As listas de nomes: os ataques do Saudosista, quem ele chama e as ondas
    # especiais. Um nome que nao exista fazia o jogo parar a meio.
    perfis = ns.get("PERFIS") if isinstance(ns.get("PERFIS"), dict) else {}

    def nomes_certos(lista, quem, conhecidos, de_que):
        if not isinstance(lista, list) or len(lista) == 0:
            problemas.append(quem + " tem de ser uma lista entre [ ], com pelo menos um nome.")
            return
        for nome in lista:
            if not isinstance(nome, str):
                problemas.append(quem + ": cada nome vai entre aspas.")
                return
            if nome not in conhecidos:
                problemas.append(quem + ': "' + nome + '" não é ' + de_que + ". Os que há: "
                                 + ", ".join(conhecidos) + "." + base._parecido(nome, list(conhecidos)))

    nomes_certos(ns.get("PADROES_DO_CHEFE"), "PADROES_DO_CHEFE", ATAQUES_DO_CHEFE,
                 "um ataque que o Saudosista saiba fazer")
    nomes_certos(ns.get("INVOCADOS_PELO_CHEFE"), "INVOCADOS_PELO_CHEFE", list(perfis), "um inimigo de PERFIS")

    ondas = ns.get("ONDAS_ESPECIAIS")
    if not isinstance(ondas, dict):
        problemas.append("ONDAS_ESPECIAIS tem de estar entre { }. Sem ondas especiais fica vazio: { }")
        return
    do_chefe = ns.get("ONDA_DO_CHEFE")
    for numero, ficha in ondas.items():
        quem = "A onda " + str(numero) + " especial"
        if not _inteiro(numero) or numero < 1 or numero > 999:
            problemas.append("Em ONDAS_ESPECIAIS, à esquerda dos : vai o número da onda, sem aspas: 3: {...}")
            continue
        if not isinstance(ficha, dict):
            problemas.append(quem + ': a ficha é assim: {"inimigos": ["corredor"], "de_cada": 4}')
            continue
        nomes_certos(ficha.get("inimigos"), quem + ': os "inimigos"', list(perfis), "um inimigo de PERFIS")
        if "de_cada" not in ficha:
            problemas.append(quem + ': falta o "de_cada" (quantos vêm de cada inimigo).')
        else:
            _ver_valor(ficha["de_cada"], quem + ': "de_cada"', (1, 60, True), problemas)
        if _inteiro(do_chefe) and do_chefe > 0 and numero % do_chefe == 0:
            avisos.append(quem + " não se vai ver: a onda " + str(numero) + " é do Saudosista (ONDA_DO_CHEFE é "
                          + str(do_chefe) + ").")


def _experimentar(ns, regra, problemas):
    # Uma regra que devolve uma resposta tem de devolver uma que o jogo
    # perceba. Experimenta-se com coisas a fingir.
    funcao = ns[regra]
    if regra == "inimigos_da_onda":
        for numero in (1, 3, 8):
            nomes = funcao(numero)
            if not isinstance(nomes, list) or not all(isinstance(nome, str) for nome in nomes):
                problemas.append("inimigos_da_onda tem de devolver uma lista de nomes, como "
                                 '["corredor", "atirador"]. Na onda ' + str(numero) + " devolveu "
                                 + repr(nomes)[:50] + ".")
                return
            for nome in nomes:
                if nome not in ns["PERFIS"]:
                    problemas.append('inimigos_da_onda devolveu "' + nome + '", que não é um inimigo de PERFIS.'
                                     + base._parecido(nome, list(ns["PERFIS"])))
                    return
            if len(nomes) > 400:
                problemas.append("inimigos_da_onda devolveu " + str(len(nomes)) + " inimigos para a onda "
                                 + str(numero) + ": são demasiados para o jogo. O máximo é 400.")
                return
    elif regra == "escolher_cartas":
        cartas = funcao(ns["Jogador"]())
        if not isinstance(cartas, list) or len(cartas) == 0:
            problemas.append("escolher_cartas tem de devolver uma lista com uma a três cartas de MELHORIAS. "
                             "Devolveu " + repr(cartas)[:50] + ".")
            return
        for carta in cartas:
            if carta not in ns["MELHORIAS"]:
                problemas.append("escolher_cartas tem de devolver cartas tiradas de MELHORIAS (linhas inteiras). "
                                 "Devolveu " + repr(carta)[:50] + ".")
                return
    elif regra == "pontos_por_morte" and ns.get("jogo") is not None:
        modelo = ns["Inimigo"](list(ns["PERFIS"])[0], (0, 0), 1)
        pontos = funcao(modelo)
        if not _numero(pontos) or pontos != pontos:
            problemas.append("pontos_por_morte tem de devolver um número: falta um return no fim, ou devolve "
                             "outra coisa? Devolveu " + repr(pontos)[:40] + ".")


def _ids_com_efeito(ns):
    # Os ids de carta que a funcao aplicar_carta() conhece: sao os textos
    # que la estao escritos (carta == "guitarra"...). Assim uma carta nova
    # passa a contar logo que a crianca lhe escreve o "elif".
    funcao = ns.get("aplicar_carta")
    if not inspect.isfunction(funcao):
        return CARTAS_COM_EFEITO
    ids = []
    for coisa in funcao.__code__.co_consts:
        for parte in coisa if isinstance(coisa, (tuple, frozenset)) else [coisa]:
            if isinstance(parte, str):
                ids.append(parte)
    return ids


def _ver_cartas(ns, problemas, avisos):
    com_efeito = _ids_com_efeito(ns)
    cartas = ns.get("MELHORIAS")
    if not isinstance(cartas, list) or len(cartas) == 0:
        problemas.append("Tem de haver pelo menos uma carta em MELHORIAS.")
        return
    vistos = []
    numero = 0
    for carta in cartas:
        numero = numero + 1
        quem = "A carta " + str(numero)
        if not isinstance(carta, tuple) or len(carta) != 5:
            problemas.append(quem + " tem de ter 5 coisas entre ( ), separadas por vírgulas: "
                             "id, nome, descrição, raridade e única.")
            continue
        ident, nome, descricao, raridade, unica = carta
        if isinstance(nome, str) and nome != "":
            quem = nome
        if not isinstance(ident, str) or not isinstance(nome, str) or not isinstance(descricao, str):
            problemas.append(quem + ": o id, o nome e a descrição são textos, entre aspas.")
            continue
        if not _inteiro(raridade) or raridade not in (1, 2, 3):
            problemas.append(quem + ": a raridade é 1 (comum), 2 (rara) ou 3 (lendária).")
        if not isinstance(unica, bool):
            problemas.append(quem + ": a última coisa é True (só se apanha uma vez) ou False.")
        if ident in vistos:
            avisos.append(quem + ': já há outra carta com o id "' + ident + '". Contam como a mesma.')
        elif ident not in com_efeito:
            avisos.append(quem + ': o jogo não conhece o id "' + ident + '", por isso a carta não faz nada. '
                          'O que cada carta faz está nas Regras do jogo, em "O que cada carta faz".')
        vistos.append(ident)


def _ver_textos(ns, problemas, avisos):
    for nome in ("FRASES_ONDA", "CRITICAS", "CREDITOS"):
        lista = ns.get(nome)
        if not isinstance(lista, list) or len(lista) == 0:
            problemas.append(nome + " tem de ser uma lista entre [ ], com pelo menos um texto.")
            continue
        for texto in lista:
            if not isinstance(texto, str):
                problemas.append(nome + ": cada linha é um texto entre aspas, com uma vírgula no fim.")
                break

    conquistas = ns.get("CONQUISTAS")
    if not isinstance(conquistas, dict):
        problemas.append("CONQUISTAS tem de estar entre { }.")
        return
    for nome in CONQUISTAS_PRECISAS:
        if nome not in conquistas:
            problemas.append('Falta a conquista "' + nome + '": o jogo chama por ela com esse nome.')
    for nome, par in conquistas.items():
        certo = isinstance(par, (tuple, list)) and len(par) == 2
        if not certo or not isinstance(par[0], str) or not isinstance(par[1], str):
            problemas.append('A conquista "' + str(nome) + '" tem de ser ("título", "texto"): '
                             "dois textos entre aspas, dentro de ( ).")


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
        problemas.append("A memoria tem de ser um dicionário: memoria = {}")


def _primeira_diferenca(antes, agora):
    # Em que posicao e que duas listas deixam de ser iguais (0 se sao iguais).
    for i in range(len(agora)):
        if i >= len(antes) or antes[i] != agora[i]:
            return i
    return 0


# =====================================================================
#                              O PALCO
# =====================================================================

class Palco:

    def __init__(self, escolha):
        tipo, _, numero = escolha.partition(":")
        self.tipo = tipo
        self.numero = int(numero) if numero.isdigit() else 0
        self.jogo = None         # o objeto Jogo, quando acabar de carregar
        self.espera = 0          # frames ate a proxima coisa acontecer
        self.vez = 0             # qual o proximo (inimigo, frase, conquista...)
        self.antes = []          # os textos como estavam, para ver qual mudou
        self.funcao = numero if tipo in FUNCOES else None
        # Nos acontecimentos o jogo joga-se sozinho, onda atras de onda; nas
        # regras e nos desenhos ha sempre inimigos de todos na arena. A regra
        # das cartas mostra as cartas, como o palco de uma carta.
        # (Tambem as duas regras que so se veem com o jogo inteiro a andar.)
        self.sozinho = tipo == "evento" or self.funcao in ("inimigos_da_onda", "escolher_cartas")
        self.com_cartas = tipo == "carta" or self.funcao == "aplicar_carta"
        self.volta = 0           # quantas vezes ja se deram cartas
        self.vez_da_lupa = 0
        if tipo in FUNCOES:
            # Uma regra nova so mostra o que vale quando chega a vez de ser
            # usada (um tiro acertar, um inimigo rebentar): prova-se mais tempo.
            self.quadros_de_prova = 150

    def verificar(self, ns):
        problemas = []
        avisos = []
        _ver_numeros(ns, problemas, avisos)
        _ver_perfis(ns, problemas, avisos)
        _ver_cartas(ns, problemas, avisos)
        _ver_textos(ns, problemas, avisos)
        _ver_arranque(ns, problemas, avisos)
        _ver_listas(ns, problemas, avisos)
        _ver_funcoes(ns, problemas, avisos)
        if self.tipo == "regra" and self.jogo is not None and not problemas:
            _experimentar(ns, self.funcao, problemas)
        return problemas, avisos

    # --- Encontrar o jogo e prepara-lo ---

    def procurar_jogo(self, ns):
        # O jogo nao tem um nome a que se possa chegar: e feito dentro do
        # main(). Mas quem nos chamou foi o pygame.display.flip() que esta
        # no ciclo dele (Jogo.correr), por isso andamos para tras, de funcao
        # em funcao, ate dar com ele. Enquanto o jogo esta no ecra de
        # carregamento ainda nao ha ciclo, e nao se encontra nada.
        quadro = sys._getframe()
        while quadro is not None:
            if quadro.f_code.co_name == "correr" and isinstance(quadro.f_locals.get("self"), ns["Jogo"]):
                return quadro.f_locals["self"]
            quadro = quadro.f_back
        return None

    def preparar(self, ns, pygame):
        jogo = self.jogo
        # Sem janela nao ha ecra inteiro: a tecla F rebentava o jogo.
        pygame.display.toggle_fullscreen = lambda: None
        # A musica comeca calada (numa sala cheia de computadores agradece-se).
        # A tecla M liga-a.
        jogo.musica_ligada = False
        jogo.ajustar_musica()
        jogo.auto = self.tipo in COM_TIRO_AUTOMATICO
        if self.tipo in FUNCOES:
            # (Para se ver o que acontece ao perder um coracao, e preciso
            # que os inimigos cheguem ao jogador.)
            jogo.auto = self.funcao != "ao_perder_coracao"
        if self.tipo == "arranque":
            self.arrancar(ns, False)
        self.guardar_textos(ns)
        self.comecar(ns)

    def guardar_textos(self, ns):
        if self.tipo in TEXTOS:
            textos = ns[TEXTOS[self.tipo]]
            self.antes = list(textos.values()) if isinstance(textos, dict) else list(textos)

    def comecar(self, ns):
        # Poe o jogo a mostrar a coisa escolhida, desde o inicio.
        jogo = self.jogo
        self.espera = 0
        if self.tipo in JOGO_INTEIRO or self.sozinho:
            jogo.novo_jogo()
            if self.tipo == "onda":
                self.nesta_onda(ns)
            return
        jogo.limpar_mundo()
        jogo.estado = "jogo"
        jogo.onda = 1
        jogo.fase = "combate"
        if self.tipo in COM_CHEFE:
            self.novo_chefe(ns)
        elif self.tipo == "laser":
            jogo.farol = 1.0
        elif self.com_cartas:
            self.dar_cartas(ns, False)
        elif self.tipo == "criticas":
            jogo.estado = "titulo"
            self.mostrar_critica(ns, 0)
        elif self.tipo == "creditos":
            jogo.estado = "vitoria"
            self.mostrar_credito(0)

    def ao_mudar(self, ns):
        # O codigo mudou. O que andava no ecra foi feito com os numeros
        # antigos, por isso faz-se de novo com os que la estao agora.
        jogo = self.jogo
        if jogo is None:
            return
        if self.tipo in JOGO_INTEIRO:
            if self.tipo == "arranque":
                self.arrancar(ns, True)
            self.comecar(ns)
            return
        if self.tipo in FUNCOES:
            self.ao_mudar_funcao(ns)
            return
        if self.tipo in LISTAS:
            # As listas do Saudosista: ele vai busca-las pelo nome da proxima
            # vez que precisar, e o combate continua como ia.
            return

        novos = []
        for inimigo in jogo.inimigos:
            if inimigo.chefe:
                novo = ns["Chefe"](inimigo.onda)
                novo.pos = inimigo.pos
                jogo.chefe = novo
                novos.append(novo)
            elif inimigo.tipo in ns["PERFIS"]:
                novos.append(ns["Inimigo"](inimigo.tipo, inimigo.pos, inimigo.onda))
        jogo.inimigos = novos
        jogo.avisos = [aviso for aviso in jogo.avisos if aviso.tipo in ns["PERFIS"]]
        jogo.fila = []

        velho = jogo.jogador
        jogo.jogador = ns["Jogador"]()
        jogo.jogador.pos = velho.pos
        jogo.jogador.ang = velho.ang
        jogo.laser_t = 0.0

        if self.tipo == "laser":
            jogo.farol = 1.0
        elif self.tipo == "carta":
            self.dar_cartas(ns, True)
        elif self.tipo in TEXTOS:
            textos = ns[TEXTOS[self.tipo]]
            agora = list(textos.values()) if isinstance(textos, dict) else list(textos)
            mudou = _primeira_diferenca(self.antes, agora)
            self.antes = agora
            self.vez = mudou
            self.espera = 0
            if self.tipo == "frases":
                jogo.fase = "combate"      # tira a frase que la estava
            elif self.tipo == "criticas":
                self.mostrar_critica(ns, mudou)
            elif self.tipo == "creditos":
                self.mostrar_credito(mudou)
            elif self.tipo == "conquistas":
                jogo.notificacoes = []

    def ao_mudar_funcao(self, ns):
        # Uma funcao nova nao precisa que se refaca nada: o jogo vai busca-la
        # pelo nome da proxima vez que a chamar, e a accao continua como ia.
        # So se mexe no que e preciso para a mudanca se ver ja.
        jogo = self.jogo
        if self.funcao in ("ao_comecar_onda", "inimigos_da_onda") and jogo.estado == "jogo":
            # A onda comeca outra vez, para o acontecimento acontecer agora.
            if jogo.chefe in jogo.inimigos:
                jogo.inimigos.remove(jogo.chefe)
            jogo.chefe = None
            jogo.inimigos = []
            jogo.avisos = []
            jogo.balas_inimigas = []
            jogo.fila = []
            jogo.onda = max(0, jogo.onda - 1)
            jogo.proxima_onda()
        elif self.funcao == "ao_perder_coracao" and jogo.estado == "jogo" and jogo.fase != "morte":
            # Um golpe ja, vindo de cima, para o acontecimento acontecer agora.
            jogador = jogo.jogador
            jogador.vida = max(jogador.vida, 2)
            jogador.invulneravel = 0.0
            jogador.dash_t = 0.0
            jogo.ferir_jogador(jogador.pos + ns["Vector2"](0, -30))
        elif self.funcao == "aplicar_carta":
            # Experimenta-se ja cada carta num jogador a fingir: se a regra
            # rebentar numa delas, sabe-se agora (e o jogo volta a regra
            # anterior), e nao so no dia em que essa carta for escolhida.
            for carta in ns["MELHORIAS"]:
                ns["aplicar_carta"](carta[0], ns["Jogador"]())
            # As cartas voltam, e o jogador volta aos numeros do inicio.
            velho = jogo.jogador
            jogo.jogador = ns["Jogador"]()
            jogo.jogador.pos = velho.pos
            jogo.jogador.ang = velho.ang
            self.dar_cartas(ns, True)
        elif self.funcao in ("escolher_cartas", "ao_escolher_carta") and jogo.estado == "jogo":
            # As cartas aparecem ja (e, passado um bocadinho, uma e escolhida).
            if jogo.fase != "morte":
                jogo.sortear_cartas()
        elif self.funcao == "ao_acabar_onda" and jogo.estado == "jogo" and jogo.fase != "morte":
            # A onda acaba ja: sem ninguem na arena nem a espera, o jogo
            # da-a por acabada no proximo frame.
            jogo.chefe = None
            jogo.inimigos = []
            jogo.avisos = []
            jogo.fila = []
            jogo.fase = "combate"
        elif self.funcao == "ao_disparar_laser":
            jogo.laser_t = 0.0
            jogo.farol = 1.0
        elif self.funcao == "ao_investir":
            self.espera = 0

    def arrancar(self, ns, com_musica):
        # No palco de "como o jogo arranca", liga e desliga o que la esta
        # escrito. A musica so obedece depois de uma mudanca: ao abrir, o
        # palco comeca sempre calado.
        jogo = self.jogo
        jogo.auto = ns["TIRO_AUTOMATICO"]
        jogo.bloom = ns["BRILHO_NEON"]
        jogo.crt = ns["ECRA_ANTIGO"]
        if com_musica:
            jogo.musica_ligada = ns["MUSICA_LIGADA"]
            jogo.ajustar_musica()

    def a_onda(self, ns):
        # O numero da onda especial que esta aberta (ou 1, se ja nao houver).
        numeros = [numero for numero in ns["ONDAS_ESPECIAIS"] if _inteiro(numero)]
        if len(numeros) == 0:
            return 1
        return max(1, numeros[min(self.numero, len(numeros) - 1)])

    def nesta_onda(self, ns):
        # O jogo acabou de comecar na onda 1: passa para a onda aberta.
        jogo = self.jogo
        jogo.chefe = None
        jogo.inimigos = []
        jogo.avisos = []
        jogo.fila = []
        jogo.onda = self.a_onda(ns) - 1
        jogo.proxima_onda()

    # --- As pecas com que se montam os palcos ---

    def sem_dano(self):
        # Coracoes sempre cheios, e sempre um bocadinho de "invulneravel":
        # tao pouco que o jogador nao chega a piscar.
        jogador = self.jogo.jogador
        jogador.vida = jogador.vida_max
        jogador.invulneravel = 0.12

    def a_meio_do_combate(self, ns):
        # Sem menu, sem fim e sem ondas: o jogo fica sempre a meio de um combate.
        jogo = self.jogo
        if jogo.estado == "fim" or jogo.estado == "titulo":
            self.comecar(ns)           # ficou sem coracoes: nasce outra vez
        jogo.estado = "jogo"
        jogo.onda = 1
        jogo.infinito = False
        if jogo.fase in ("limpo", "chefe_intro"):
            jogo.fase = "combate"

    def segurar_fila(self, ns):
        # O jogo da a onda por acabada quando nao ha inimigos nem ninguem na
        # fila para entrar. Deixamos sempre um na fila, e seguramo-lo la:
        # enquanto spawn_cd nao chegar a zero, ele nao entra.
        jogo = self.jogo
        if not jogo.fila:
            jogo.fila.append(list(ns["PERFIS"])[0])
        jogo.spawn_cd = 0.5

    def mandar_vir(self, ns, elenco, quantos):
        # Mantem "quantos" inimigos do elenco na arena. Quem os faz entrar e
        # o jogo, com o aviso de sempre: nos so pomos o proximo na fila.
        jogo = self.jogo
        elenco = [nome for nome in elenco if nome in ns["PERFIS"]]
        if len(elenco) == 0:
            elenco = [list(ns["PERFIS"])[0]]
        if not jogo.fila:
            jogo.fila.append(elenco[self.vez % len(elenco)])
            self.vez = self.vez + 1
        ca_estao = len([inimigo for inimigo in jogo.inimigos if inimigo.tipo in elenco])
        ca_estao = ca_estao + len([aviso for aviso in jogo.avisos if aviso.tipo in elenco])
        if ca_estao >= quantos or len(jogo.inimigos) >= 30:
            jogo.spawn_cd = 0.5
        else:
            # Faltam inimigos: o proximo entra ja, sem a espera entre dois
            # que o jogo faz nas ondas (senao morriam mais depressa do que
            # chegavam, e a arena ficava vazia).
            jogo.spawn_cd = min(jogo.spawn_cd, 0.15)

    def o_inimigo(self, ns):
        nomes = list(ns["PERFIS"])
        return nomes[min(self.numero, len(nomes) - 1)]

    def a_carta(self, ns):
        if self.funcao is not None:
            # Na regra das cartas vem tres de cada vez, sempre outras.
            return (self.volta * 3 + 1) % len(ns["MELHORIAS"])
        return min(self.numero, len(ns["MELHORIAS"]) - 1)

    def novo_chefe(self, ns):
        jogo = self.jogo
        jogo.chefe = ns["Chefe"](1)
        jogo.inimigos.append(jogo.chefe)
        self.espera = 150

    def dar_cartas(self, ns, ja):
        # Poe o ecra das cartas, com a carta escolhida no meio e as duas
        # vizinhas dela ao lado. "ja" e para aparecerem logo no sitio, sem
        # a animacao de entrada (quando o codigo acabou de mudar).
        jogo = self.jogo
        cartas = ns["MELHORIAS"]
        minha = self.a_carta(ns)
        mostrar = [minha]
        if len(cartas) > 1:
            mostrar.insert(0, (minha - 1) % len(cartas))
        if len(cartas) > 2:
            mostrar.append((minha + 1) % len(cartas))
        jogo.cartas = [[cartas[i], 1.0 if ja else 0.0] for i in mostrar]
        jogo.carta_rato = mostrar.index(minha)
        jogo.estado = "melhoria"
        jogo.estado_t = 1.0 if ja else 0.0
        jogo.inimigos = []
        jogo.avisos = []
        jogo.balas_inimigas = []
        jogo.chefe = None
        jogo.fila = []
        jogo.onda = 1
        jogo.fase = "combate"
        self.espera = 0
        if not ja:
            self.volta = self.volta + 1

    def mostrar_critica(self, ns, qual):
        jogo = self.jogo
        jogo.critica_i = min(qual, len(ns["CRITICAS"]) - 1)
        jogo.critica_x = 380          # ja a meio do ecra, para se ler logo

    def mostrar_credito(self, qual):
        # Os creditos sobem 32 pixeis por segundo, com 26 entre linhas. Isto
        # poe o relogio do ecra na altura em que a linha "qual" vai a meio.
        self.jogo.estado_t = (qual * 26 + 90) / 32

    # --- Todos os frames ---

    def quadro(self, ns, pygame):
        if self.jogo is None:
            self.jogo = self.procurar_jogo(ns)
            if self.jogo is None:
                return                  # ainda esta a carregar
            self.preparar(ns, pygame)
        jogo = self.jogo
        jogo.sair = False               # no palco, o Esc do menu nao fecha o jogo
        if jogo.estado != "pausa":      # na pausa fica tudo parado, e o palco tambem
            self.encenar(ns)
            self.desenhar(ns, pygame)

    def encenar(self, ns):
        jogo = self.jogo
        tipo = self.tipo

        if tipo in JOGO_INTEIRO or self.sozinho:
            # O jogo verdadeiro, a jogar-se sozinho: escolhe uma carta se
            # ninguem escolher, e quando ganha comeca outra vez.
            if tipo == "onda" and jogo.estado in ("melhoria", "vitoria"):
                self.comecar(ns)        # a onda acabou: vem outra vez a mesma
                return
            if self.funcao == "ao_investir" and jogo.estado == "jogo" and jogo.fase == "combate":
                # A nave investe sozinha de vez em quando, para o acontecimento acontecer.
                self.espera = self.espera - 1
                if self.espera <= 0:
                    self.espera = 120
                    jogo.jogador.dash_cd = 0.0
                    jogo.investir()
            elif self.funcao == "ao_disparar_laser" and jogo.estado == "jogo" and jogo.laser_t <= 0:
                jogo.farol = min(1.0, jogo.farol + 0.004)       # enche em poucos segundos
            if not self.sozinho:
                self.sem_dano()
            elif jogo.jogador.vida <= 1 and jogo.fase != "morte":
                # Nos acontecimentos perdem-se coracoes a serio (ha um
                # acontecimento para isso), mas aqui nao se morre. No
                # "quando perdes um coracao", antes do ultimo voltam todos,
                # para continuar a haver coracoes para perder. Nos outros, o
                # ultimo coracao fica como esta e deixa de se levar dano:
                # encher os coracoes desfazia o que a crianca escreveu
                # ("na onda 2 ficas so com um coracao" nunca se chegava a ver).
                if self.funcao == "ao_perder_coracao":
                    jogo.jogador.vida = jogo.jogador.vida_max
                else:
                    jogo.jogador.invulneravel = max(jogo.jogador.invulneravel, 0.12)
            if jogo.estado in ("titulo", "fim"):
                jogo.novo_jogo()
            elif jogo.estado == "vitoria" and jogo.estado_t > 4:
                jogo.novo_jogo()
            elif jogo.estado == "melhoria" and jogo.estado_t > 2.5:
                if jogo.cartas:
                    jogo.escolher(max(0, jogo.carta_rato))
                else:
                    jogo.estado = "jogo"
                    jogo.proxima_onda()
            return

        if tipo == "criticas":
            jogo.estado = "titulo"
            jogo.critica_i = min(jogo.critica_i, len(ns["CRITICAS"]) - 1)
            return

        if tipo == "creditos":
            jogo.estado = "vitoria"
            jogo.infinito = False
            return

        if self.com_cartas:
            if jogo.estado == "melhoria":
                self.sem_dano()
                return
            if jogo.estado != "jogo":
                self.dar_cartas(ns, False)
                return
            # Escolheram uma carta: uns segundos de arena para a experimentar.
            if self.espera <= 0:
                self.espera = 540
                if jogo.chefe in jogo.inimigos:
                    jogo.inimigos.remove(jogo.chefe)
                jogo.chefe = None
                jogo.fila = []
                jogo.fase = "combate"
            self.espera = self.espera - 1
            if self.espera <= 0:
                self.dar_cartas(ns, False)
                return

        self.a_meio_do_combate(ns)
        if tipo not in PODE_LEVAR_DANO:
            self.sem_dano()

        if tipo == "inimigo":
            self.mandar_vir(ns, [self.o_inimigo(ns)], 4)
        elif self.com_cartas:
            self.mandar_vir(ns, ELENCO["carta"], 4)
        elif self.funcao in ("disparo_do_inimigo", "desenhar_bala_inimiga"):
            # So os que disparam (se ja nao houver nenhum, vem todos).
            atiradores = [nome for nome, ficha in ns["PERFIS"].items() if ficha.get("dispara") is True]
            self.mandar_vir(ns, atiradores or list(ns["PERFIS"]), 5)
        elif tipo in FUNCOES:
            self.mandar_vir(ns, list(ns["PERFIS"]), 5)     # um de cada, a vez
        elif tipo in ELENCO:
            self.mandar_vir(ns, ELENCO[tipo], 6 if tipo == "laser" else 4)
        else:
            self.segurar_fila(ns)

        if tipo in COM_CHEFE and jogo.chefe is None:
            # Caiu. Passado um bocadinho vem outro.
            self.espera = self.espera - 1
            if self.espera <= 0:
                self.novo_chefe(ns)
        elif tipo == "invocados" and jogo.chefe.padrao == "espera" and "invocar" in ns["PADROES_DO_CHEFE"]:
            # Aqui o Saudosista so chama inimigos, que e o que se quer ver.
            jogo.chefe.ordem = ns["PADROES_DO_CHEFE"].index("invocar")
        elif tipo == "frases":
            if jogo.fase == "banner":
                self.espera = 40
            else:
                self.espera = self.espera - 1
                if self.espera <= 0:
                    frases = ns["FRASES_ONDA"]
                    jogo.frase = frases[self.vez % len(frases)]
                    self.vez = self.vez + 1
                    jogo.fase = "banner"
                    jogo.fase_t = 1.8
        elif tipo == "conquistas":
            self.espera = self.espera - 1
            if self.espera <= 0 and len(jogo.notificacoes) < 3:
                pares = list(ns["CONQUISTAS"].values())
                titulo, texto = pares[self.vez % len(pares)]
                jogo.notificacoes.append([titulo, texto, 0.0])
                self.vez = self.vez + 1
                self.espera = 80

    # --- O que o palco desenha por cima do jogo ---

    def desenhar(self, ns, pygame):
        jogo = self.jogo
        tipo = self.tipo
        texto = ""
        if tipo == "inimigo":
            nome = self.o_inimigo(ns)
            ficha = ns["PERFIS"][nome]
            texto = nome + ":   vida " + str(ficha["vida"]) + "   velocidade " + str(ficha["velocidade"])
            texto = texto + "   raio " + str(ficha["raio"]) + "   pontos " + str(ficha["pontos"])
            texto = texto + "   custo " + str(ficha["custo"])
            if ficha["desde_onda"] is None:
                texto = texto + "   não aparece nas ondas"
            else:
                texto = texto + "   desde a onda " + str(ficha["desde_onda"])
            self.lupa(ns, pygame, nome)
        elif tipo == "chefe":
            texto = "O Saudosista:   VIDA_CHEFE " + str(ns["VIDA_CHEFE"])
            if jogo.chefe is not None:
                texto = texto + "   (ainda tem " + str(max(0, int(jogo.chefe.vida))) + ")"
            else:
                texto = texto + "   (caiu: já vem outro)"
        elif tipo == "ataques" or tipo == "invocados":
            nomes = ns["PADROES_DO_CHEFE"] if tipo == "ataques" else ns["INVOCADOS_PELO_CHEFE"]
            texto = ("Os ataques:   " if tipo == "ataques" else "Quem ele chama:   ") + ",  ".join(nomes)
            if jogo.chefe is None:
                texto = texto + "   (caiu: já vem outro)"
            elif jogo.chefe.padrao != "espera":
                texto = texto + "   ·   agora: " + jogo.chefe.padrao
            if tipo == "invocados" and "invocar" not in ns["PADROES_DO_CHEFE"]:
                texto = 'O Saudosista não chama ninguém: o ataque "invocar" não está na lista dos ataques dele.'
        elif tipo == "arranque":
            ligado = {True: "ligado", False: "desligado"}
            texto = "Tiro automático " + ligado[bool(jogo.auto)] + "   ·   música " + ligado[bool(jogo.musica_ligada)]
            texto = texto + "   ·   brilho " + ligado[bool(jogo.bloom)] + "   ·   riscas " + ligado[bool(jogo.crt)]
        elif tipo == "onda":
            numero = self.a_onda(ns)
            ficha = ns["ONDAS_ESPECIAIS"].get(numero)
            do_chefe = ns["ONDA_DO_CHEFE"]
            if not isinstance(ficha, dict):
                texto = "Já não há esta onda especial."
            elif do_chefe > 0 and numero % do_chefe == 0:
                texto = "A onda " + str(numero) + " é do Saudosista: a onda especial não se vê. Muda-lhe o número."
            else:
                texto = "Onda " + str(numero) + ":   " + str(ficha["de_cada"]) + " de cada:  " + ",  ".join(ficha["inimigos"])
                texto = texto + "   ·   faltam entrar " + str(len(jogo.fila) + len(jogo.avisos))
        elif tipo == "jogo":
            texto = "Onda " + str(jogo.onda) + " de " + str(ns["ONDAS_TOTAIS"])
            if ns["ONDA_DO_CHEFE"] == 1:
                texto = texto + "   ·   o Saudosista aparece em todas as ondas"
            else:
                texto = texto + "   ·   o Saudosista aparece de " + str(ns["ONDA_DO_CHEFE"]) + " em "
                texto = texto + str(ns["ONDA_DO_CHEFE"]) + " ondas"
        elif tipo == "ondas":
            onda = max(1, jogo.onda)
            pontos = ns["ORCAMENTO_BASE"] + onda * ns["ORCAMENTO_POR_ONDA"]
            vida = 1 + ns["VIDA_EXTRA_POR_ONDA"] * (onda - 1)
            pressa = min(ns["VELOCIDADE_EXTRA_MAXIMA"], 1 + ns["VELOCIDADE_EXTRA_POR_ONDA"] * (onda - 1))
            texto = "Onda " + str(onda) + ":   " + str(round(pontos, 2)) + " pontos para gastar em inimigos"
            texto = texto + "   ·   vida x" + str(round(vida, 2)) + "   ·   velocidade x" + str(round(pressa, 2))
            texto = texto + "   ·   faltam entrar " + str(len(jogo.fila) + len(jogo.avisos))
        elif tipo in BLOCOS:
            texto = "      ".join(nome + " " + str(ns[nome]) for nome in BLOCOS[tipo])
        elif tipo == "carta":
            carta = ns["MELHORIAS"][self.a_carta(ns)]
            texto = "Carta: " + carta[1] + '   (id "' + carta[0] + '")'
            if jogo.estado == "melhoria":
                texto = texto + "   ·   escolhe-a para a experimentares"
            else:
                texto = texto + "   ·   as cartas voltam daqui a " + str(self.espera // 60 + 1) + " s"
        elif tipo == "frases":
            total = len(ns["FRASES_ONDA"])
            texto = "Frase " + str((self.vez - 1) % total + 1) + " de " + str(total)
        elif tipo == "criticas":
            texto = "Crítica " + str(jogo.critica_i + 1) + " de " + str(len(ns["CRITICAS"]))
        elif tipo == "creditos":
            texto = "Créditos: " + str(len(ns["CREDITOS"])) + " linhas, a subir sem parar"
        elif tipo == "conquistas":
            texto = "Conquistas: " + str(len(ns["CONQUISTAS"])) + ", uma de cada vez"
        elif tipo in FUNCOES:
            texto = self.desenhar_funcao(ns, pygame)
        self.faixa(ns, pygame, texto)

    def desenhar_funcao(self, ns, pygame):
        # O que a faixa diz no palco de uma regra, de um acontecimento ou de
        # um desenho (e, nos desenhos, a lupa no canto). Devolve o texto.
        jogo = self.jogo
        funcoes = FUNCOES[self.tipo][0]
        if self.tipo == "evento":
            # A memoria a vista: e a maneira de ver o codigo a contar coisas.
            memoria = str(ns["memoria"])
            if len(memoria) > 70:
                memoria = memoria[:67] + "..."
            # (E a onda e os coracoes: e o que quase todos os acontecimentos mudam.)
            agora = "onda " + str(self.jogo.onda) + "   ·   corações " + str(self.jogo.jogador.vida)
            return funcoes[self.funcao][0] + "   ·   " + agora + "   ·   memoria = " + memoria
        if self.funcao == "aplicar_carta":
            j = jogo.jogador
            texto = "Tu:   balas " + str(j.multi) + "   espera " + str(round(j.intervalo, 3))
            texto = texto + "   dano " + str(round(j.dano, 1)) + "   crítico " + str(round(j.critico, 2))
            texto = texto + "   corações " + str(j.vida_max) + "   velocidade " + str(round(j.velocidade))
            return texto + "   perfura " + str(j.perfura) + "   ricochete " + str(j.ricochete)
        if self.funcao == "inimigos_da_onda":
            # Quem vem nesta onda: os que ja ca estao e os que faltam entrar.
            quantos = {}
            for nome in [i.tipo for i in jogo.inimigos if not i.chefe] + [a.tipo for a in jogo.avisos] + list(jogo.fila):
                quantos[nome] = quantos.get(nome, 0) + 1
            partes = [str(quantos[nome]) + " " + nome for nome in quantos]
            return "Onda " + str(jogo.onda) + ":   " + (",  ".join(partes) if partes else "ninguém (ou é a do Saudosista)")
        if self.funcao == "escolher_cartas":
            if jogo.estado == "melhoria":
                return "Cartas oferecidas:   " + ",  ".join(carta[0][1] for carta in jogo.cartas)
            return "Regra:   Que cartas aparecem   ·   as cartas vêm no fim da onda (ou quando mudares o código)"
        if self.funcao == "pontos_por_morte":
            return "Regra:   Quantos pontos vale um inimigo   ·   pontos " + str(int(jogo.pontos)) + "   combo " + str(jogo.combo)
        if self.tipo == "regra":
            return "Regra:   " + funcoes[self.funcao][0] + "   (a função " + self.funcao + ")"
        # Um desenho. No canto, aumentado: um de cada, a vez.
        self.vez_da_lupa = self.vez_da_lupa + 1
        vetor = ns["Vector2"]
        if self.funcao == "desenhar_inimigo":
            nomes = list(ns["PERFIS"])
            self.lupa(ns, pygame, nomes[(self.vez_da_lupa // 120) % len(nomes)])
        elif self.funcao == "desenhar_jogador":
            self.aumentar(ns, pygame, 48, lambda folha: ns["desenhar_jogador"](folha, jogo.jogador, vetor(24, 24)))
        elif self.funcao == "desenhar_bala":
            # Uma bala normal e, de vez em quando, uma critica.
            bala = ns["Bala"]((0, 0), vetor(ns["VELOCIDADE_BALA"], 0), 10, 4.0, ns["CIANO"])
            if (self.vez_da_lupa // 90) % 2 == 1:
                bala.critica = True
                bala.cor = ns["AMARELO"]
                bala.raio = bala.raio * 1.4
            self.aumentar(ns, pygame, 40, lambda folha: ns["desenhar_bala"](folha, bala, vetor(29, 20)))
        elif self.funcao == "desenhar_bala_inimiga":
            bala = ns["Bala"]((0, 0), vetor(210, 0), 1, 5, ns["LARANJA"])
            self.aumentar(ns, pygame, 28, lambda folha: ns["desenhar_bala_inimiga"](folha, bala, vetor(14, 14)))
        elif self.funcao == "desenhar_recompensa":
            # Uma nota e, de vez em quando, um coracao.
            coisa = ns["Recompensa"]((0, 0), "coracao" if (self.vez_da_lupa // 90) % 2 == 1 else "nota")
            coisa.ang = self.vez_da_lupa / 15
            self.aumentar(ns, pygame, 32, lambda folha: ns["desenhar_recompensa"](folha, coisa, vetor(16, 16)))
        elif self.funcao == "desenhar_aviso":
            # O aviso de cada inimigo, a vez, com o tempo a acabar.
            nomes = list(ns["PERFIS"])
            aviso = ns["Aviso"]((0, 0), nomes[(self.vez_da_lupa // 54) % len(nomes)])
            aviso.t = 0.9 - (self.vez_da_lupa % 54) / 60
            self.aumentar(ns, pygame, 80, lambda folha: ns["desenhar_aviso"](folha, aviso, vetor(40, 40)))
        return "Desenho:   " + funcoes[self.funcao][0] + "   (a função " + self.funcao + ")"

    def faixa(self, ns, pygame, texto):
        # Uma faixa escura, meio transparente, no unico sitio onde o jogo
        # nunca escreve nada: por baixo das cartas e por cima das ultimas
        # linhas do ecra (a onda, as teclas do menu, as criticas).
        ecra = self.jogo.ecra
        topo = ns["ALTURA"] - 88
        fundo = pygame.Surface((ns["LARGURA"], 26), pygame.SRCALPHA)
        fundo.fill((10, 8, 24, 215))
        ecra.blit(fundo, (0, topo))
        pygame.draw.rect(ecra, ns["AMARELO"], (0, topo, 5, 26))
        ns["escrever"](ecra, texto, 20, (16, topo + 13), ns["BRANCO"], "midleft")

    def lupa(self, ns, pygame, nome):
        # Desenha o inimigo numa folha pequena, com o desenhar() do proprio
        # jogo, e mostra essa folha aumentada no canto.
        modelo = ns["Inimigo"](nome, (0, 0), 1)
        lado = int(max(24, min(modelo.raio * 3.6 + 8, 420)))
        modelo.pos = ns["Vector2"](lado / 2, lado / 2)
        modelo.ang = -math.pi / 2       # de bico para cima
        modelo.cd_tiro = 9              # sem o anel de "vou disparar"
        self.aumentar(ns, pygame, lado, lambda folha: modelo.desenhar(folha, ns["Vector2"](0, 0)))

    def aumentar(self, ns, pygame, lado, desenhar):
        # Uma folha pequena, com "lado" pixeis de lado, onde o desenhar(folha)
        # desenha a coisa. Mostra-se aumentada no canto.
        folha = pygame.Surface((lado, lado))
        folha.fill(ns["FUNDO"])
        desenhar(folha)
        grande = pygame.transform.smoothscale(folha, (104, 104))
        ecra = self.jogo.ecra
        caixa = pygame.Rect(ns["LARGURA"] - 122, ns["ALTURA"] - 208, 108, 108)
        ecra.blit(grande, (caixa.x + 2, caixa.y + 2))
        pygame.draw.rect(ecra, ns["AMARELO"], caixa, 2, border_radius=6)


def criar_palco(escolha):
    return Palco(escolha)
