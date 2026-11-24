# A Bicharada a Solta na Oficina. O jogo sao batalhas por turnos com um mundo
# por onde se anda. Quase tudo o que e da batalha vem do bicharada.py aqui ao
# lado (que era o de um jogo so de batalhas, e ficou como base deste): os
# bichos, os ataques, os treinadores, os tipos e as funcoes da batalha
# abrem-se da mesma maneira, no mesmo palco (ja dentro de uma batalha).
#
# O que este ficheiro junta e o que e do mundo: as zonas (cada uma e um ecra),
# a maneira como se juntam (o MUNDO), os edificios e as portas deles, e tres
# regras, tres acontecimentos e tres desenhos. Para essas coisas o palco e
# outro: o jogo ja no mapa. Nas funcoes o boneco anda sozinho, para se ver
# logo o que a funcao nova faz; numa zona anda so a crianca, para o mapa nao
# lhe fugir; no MUNDO e nas PORTAS ve-se o mundo todo em ponto pequeno.

import ast
import collections
import inspect
import random
import re

import blocos
from jogos import bicharada as base

NOME = "Bicharada à Solta"
FICHEIRO = "s15-bicharada-a-solta/bicharada-a-solta.py"
DESCRICAO = "A Bicharada com um mundo: andas de zona em zona, e os bichos saltam da erva."

# Uma frase por grupo, para a pagina do jogo dizer o que la ha. A ordem
# daqui e a ordem dos grupos na pagina.
SOBRE_OS_GRUPOS = {
    "Mapa": "O mundo é feito de zonas, cada uma do tamanho do ecrã e desenhada com letras. "
            "Sais por um lado de uma, entras na do lado.",
    "Blocos": "Os quadrados com que se fazem as zonas: a relva, as árvores, a água, a mobília... e os que inventares (areia, neve, lava). Cada um é uma letra, um nome e um desenho.",
    "Edifícios": "Os sítios onde se entra por uma porta (cada um é uma zona por dentro), e o que se vende na loja.",
    "Bichos": "Tipo, vida, ataque, forma, cor. Podes pôr uma imagem tua.",
    "Ataques": "O poder, a precisão e o efeito de cada ataque.",
    "Treinadores": "Quem encontras no mapa: as falas e as perguntas deles, e que bichos levam.",
    "Tipos": "Cada tipo e a cor dele, quem é forte contra quem, e o tipo que todos podem aprender.",
    "Regras do jogo": "Aqui mudas a maneira como o jogo se comporta, na batalha e no mapa: é programar a sério.",
    "Acontecimentos": "Estão vazios: o que lá escreveres passa a acontecer nesse momento. É aqui que se inventa.",
    "Desenhos": "Como se desenha um bicho, um quadrado do mapa, tu e os treinadores.",
}

# Escolher de uma lista os bichos de um treinador faz-se como na Bicharada.
# (Apagar tambem, mas aqui ha o mapa para acertar: ve o apagar, mais abaixo.)
lista = base.lista

CRIAVEIS = dict(base.CRIAVEIS)
CRIAVEIS["Mapa"] = "Nova zona"
CRIAVEIS["Edifícios"] = "Novo edifício"
CRIAVEIS["Blocos"] = "Novo bloco"

QUE_FAZER = "O que posso fazer aqui?"
LINHA_A_LINHA = "Explica-me esta função linha a linha"

# Pedidos ja escritos para o ajudante. (Os das coisas da batalha estao no
# bicharada.py.)
SUGESTOES = {
    "zona": ["Faz um lago grande no meio desta zona", "Põe mais erva alta do lado esquerdo",
             "O que quer dizer cada letra?"],
    "interior": ["Faz esta sala maior", "Põe um balcão de parede a meio da sala", "O que quer dizer cada letra?"],
    "mundo": ["Troca a serra com a praia", "Como é que junto uma zona nova ao mundo?",
              "Como é que isto funciona?"],
    "portas": ["Como é que faço um edifício novo?", "Para que serve a letra de cada porta?",
               "Como é que ponho duas portas no mesmo edifício?"],
    "bloco": ["Faz com que não se possa andar por cima deste bloco", "Faz saltar só bichos de fogo deste bloco",
              "O que quer dizer cada coisa?"],
    "desenho_feito": ["Põe maçãs vermelhas nas árvores", "Faz as paredes de tijolo vermelho",
                      "Explica-me este desenho linha a linha"],
    "desenhar_bloco": ["Põe uma sombra por baixo dos blocos que tapam o caminho", "Faz os blocos sem imagem redondos",
                       "Explica-me este desenho linha a linha"],
    "loja": ["Põe à venda uma Pomada que cura a equipa toda, por 40 moedas", "Faz as redes mais baratas",
             "Como é que ponho uma coisa nova à venda?"],
    "consegue_apanhar": ["Faz com que se apanhe sempre", "Só se apanha um bicho com menos de metade da vida",
                         LINHA_A_LINHA],
    "premio_da_batalha": ["Os treinadores pagam o dobro", "Os bichos à solta não dão moedas nenhumas", LINHA_A_LINHA],
    "receber_compra": ["Faz uma Pomada que cura a equipa toda", "Faz um Bolo que dá 20 de experiência ao meu primeiro bicho",
                       LINHA_A_LINHA],
    "ao_apanhar": ["O bicho que apanho fica logo com a vida toda", "Ganho 10 moedas por cada bicho que apanho", QUE_FAZER],
    "ao_responder": ["Se disser à Tia da Mercearia que não quero lutar, ela dá-me uma sopa",
                     "Guarda na memoria o que respondi, para outro treinador falar disso", QUE_FAZER],
    "pode_andar": ["Deixa-me andar na água se tiver um bicho de água na equipa",
                   "Faz a letra c ser uma cerca por onde não se passa", LINHA_A_LINHA],
    "ha_batalha_na_erva": ["Faz saltar um bicho 1 vez em cada 3 passos",
                           "Nunca saltam dois bichos em passos seguidos", LINHA_A_LINHA],
    "escolher_bicho_selvagem": ["Na praia só saltam bichos de água",
                                "Na serra os bichos são dois níveis mais fortes", LINHA_A_LINHA],
    "ao_dar_passo": ["A letra s no mapa é uma sopa: quando a piso, ganho uma sopa",
                     "A cada 20 passos, os meus bichos perdem 1 de vida", QUE_FAZER],
    "ao_descansar": ["A avó dá-me uma sopa a mais", "A avó diz uma frase diferente de cada vez", QUE_FAZER],
    "a_cada_frame": ["Faz um relógio que diz há quantos segundos ando no mapa",
                     "Os meus bichos recuperam 1 de vida a cada 2 segundos", QUE_FAZER],
    "jogador": ["Muda a cor da minha camisola para azul", "Para que servem as três imagens?",
                "Como é que desenho o meu boneco?"],
    "desenhar_bicho_de_costas": ["Põe uma cauda nas costas do bicho", "Faz as costas mais escuras do que a frente",
                                 "Explica-me este desenho linha a linha"],
    "desenhar_quadrado": ["Faz as portas vermelhas, com uma janelinha", "Põe um tapete à frente de cada porta",
                          "Explica-me este desenho linha a linha"],
    "desenhar_jogador": ["Põe-me um chapéu vermelho", "Faz o meu primeiro bicho andar atrás de mim, pequenino",
                         "Explica-me este desenho linha a linha"],
    "desenhar_treinador": ["Põe uma coroa na Campeã da Feira", "Faz os treinadores vencidos ficarem deitados",
                           "Explica-me este desenho linha a linha"],
}

# As funcoes do mapa. Para cada uma, o titulo que aparece na Oficina e o que
# ela recebe (o jogo chama-a assim, por isso nao pode mudar).
REGRAS = {
    "pode_andar": ("Onde se pode andar", ["letra"]),
    "ha_batalha_na_erva": ("Quando salta um bicho da erva", []),
    "escolher_bicho_selvagem": ("Que bicho salta da erva", []),
    "consegue_apanhar": ("Quando se consegue apanhar um bicho", ["bicho"]),
    "premio_da_batalha": ("Quantas moedas dá uma batalha", ["equipa", "selvagem"]),
    "receber_compra": ("O que se recebe ao comprar", ["nome"]),
}
ACONTECIMENTOS = {
    "ao_dar_passo": ("Quando dás um passo", ["letra"]),
    "ao_descansar": ("Quando descansas em casa da avó", []),
    "a_cada_frame": ("A cada frame, no mapa", []),
    "ao_apanhar": ("Quando apanhas um bicho", ["bicho"]),
    "ao_responder": ("Quando respondes a uma pergunta", ["nome", "pergunta", "resposta"]),
}
DESENHOS = {
    "desenhar_quadrado": ("Um quadrado do mapa", ["letra", "x", "y"]),
    "desenhar_jogador": ("Tu, no mapa", ["x", "y", "olha_para"]),
    "desenhar_treinador": ("Um treinador, no mapa", ["treinador", "x", "y", "vencido"]),
    "desenhar_bicho_de_costas": ("O teu bicho, visto de costas", ["bicho", "cx", "cy", "tamanho"]),
    "desenhar_bloco": ("Um bloco", ["letra", "x", "y"]),
    "desenho_feito": ("Os desenhos que já vinham com o jogo", ["qual", "cor", "x", "y"]),
}
# tipo da escolha -> as funcoes do mapa desse tipo. (O grupo onde aparecem e
# as explicacoes gerais sao os mesmos das funcoes da batalha.)
FUNCOES = {"regra": REGRAS, "evento": ACONTECIMENTOS, "desenho": DESENHOS}
# (Esta e da batalha: abre no palco das batalhas, como as do bicharada.py.)
NA_BATALHA = ["desenhar_bicho_de_costas"]
DO_MAPA = [nome for nome in list(REGRAS) + list(ACONTECIMENTOS) + list(DESENHOS) if nome not in NA_BATALHA]

# Com estas, o boneco anda de erva em erva, que e onde elas se veem.
NA_ERVA = ["ha_batalha_na_erva", "escolher_bicho_selvagem", "consegue_apanhar", "ao_apanhar"]
# Com estas, o boneco atira a rede aos bichos que saltam, em vez de fugir.
COM_REDE = ["consegue_apanhar", "ao_apanhar"]

SOZINHO = (" O boneco anda sozinho, e foge dos bichos que saltam da erva. Se clicares no jogo e"
           " carregares numa seta, ele espera uns segundos e deixa-te andar a ti.")

DICAS = {
    "zona": "Cada letra é um quadrado: muda uma letra e vê a zona mudar. A faixa de baixo diz o que é"
            " cada letra. Para experimentares, clica no jogo e anda com as setas: se saíres por um lado,"
            " entras na zona do lado.",
    "interior": "É o interior de um edifício. Cada letra é um quadrado: muda uma letra e vê a sala mudar."
                " A faixa de baixo diz as letras que há cá dentro (lá fora são outras). Sai-se pela porta."
                " Para experimentares, clica no jogo e anda com as setas.",
    "mundo": "Estás a ver o mundo todo, em ponto pequeno: cada retângulo é uma zona. Troca dois nomes de"
             " sítio e vê as zonas mudarem. O ponto amarelo és tu: clica no jogo e anda com as setas.",
    "portas": "Estás a ver o mundo todo, em ponto pequeno, e os edifícios por baixo. Cada porta é uma"
              " letra, escrita cá fora e lá dentro. O ponto amarelo és tu: clica no jogo e anda com as setas.",
    "jogador": "És tu, no mapa: clica no jogo e anda com as setas para te veres de frente, de costas e de lado."
               " Por cima do código escolhes qual das três imagens queres desenhar ou trocar.",
    "bicho": "O teu bicho é o de baixo, visto de costas; lá em cima vês-o de frente, na ficha."
             " «Escolher os ataques» mostra os ataques que existem; os de «aprende» só aparecem a partir desse nível."
             " Por cima do código escolhes se desenhas a imagem de frente ou a de costas."
             " Muda um número e vê a ficha lá em cima. Setas e Enter para jogar, Esc para voltar atrás.",
    "desenho_da_batalha": "Isto é o desenho: muda-o e vês logo, na batalha e em todos os bichos lá em cima."
                          " Um bicho que tenha imagem de costas mostra a imagem, e não este desenho."
                          " A batalha joga-se sozinha.",
    "bloco": "Um bloco é um quadrado inventado por ti. Desenha-o com «Desenhar» (ou usa um modelo), diz nas caixas"
             " se se anda por cima dele, e depois escreve a letra dele nas zonas. Estás numa zona onde ele"
             " aparece (ou na da partida, se ainda não está em nenhuma): clica no jogo e anda com as setas.",
    "loja": "Estás ao balcão, com moedas para experimentar: setas e Enter para comprar. Muda um preço, ou"
            " acrescenta uma coisa, e vê a loja mudar. O que cada coisa faz está na regra «O que se recebe ao comprar».",
    "treinador": "O treinador fala contigo e depois luta: é o que está nas falas dele. Enter passa as falas"
                 " (sozinhas também passam), e as setas escolhem a resposta a uma pergunta."
                 " «Escolher os bichos» mostra os bichos que existem. Depois da luta ele diz as falas_depois."
                 " «Desenhar» faz o boneco dele no mapa (ou começa por um modelo).",
    "regra": "Isto é uma regra do mapa: muda-a e o jogo passa a comportar-se de outra maneira."
             " O quadro do canto mostra o que a tua regra responde agora." + SOZINHO,
    "evento": "Tira o pass e escreve o que queres que aconteça nesse momento."
              " O quadro do canto mostra o que tens na memoria." + SOZINHO,
    "desenho": "Isto é o desenho: muda-o e vês logo, na zona toda." + SOZINHO,
}

# As letras de ca de fora e as de dentro de um edificio nao sao as mesmas:
# la dentro nao ha arvores nem erva, e ca fora nao ha mesas nem estantes.
# As letras que nao sao de nenhum bloco: a partida e os treinadores.
CONHECIDAS = "P123456789"
# Os blocos que nao se apagam: a relva e o soalho sao o que fica no lugar dos
# outros, e sem a parede e o "nada" os edificios deixavam de ter forma.
CHAO_DE_FORA, CHAO_DE_DENTRO = ".", "_"
NAO_SE_APAGAM = {".": "A relva", "_": "O soalho", "#": "A parede", " ": 'O "nada"'}
INICIO_DOS_INTERIORES = "# --- Os interiores ---"
INICIO_DAS_ZONAS = "# --- As zonas ---"
ZONA = (20, 14)          # quantas letras tem uma zona: por linha, e linhas
PASSOS = ((0, 1), (0, -1), (1, 0), (-1, 0))      # a ordem e a do passar_a_porta do jogo

# Uma zona nova: relva, com uma saida ao meio de cada lado.
ZONA_NOVA = (["AAAAAAAAA..AAAAAAAAA"] + ["A..................A"] * 5 + ["...................."] * 2
             + ["A..................A"] * 5 + ["AAAAAAAAA..AAAAAAAAA"])
# O interior de um edificio novo: uma sala, com a porta (o ?) na parede de baixo.
SALA_NOVA = ([" " * 20] * 3 + ["     ##j####j##     ", "     #l______v#     ", "     #________#     ",
                               "     #___mb___#     ", "     #________#     ", "     #________#     ",
                               "     #___tt___#     ", "     ####?#####     "] + [" " * 20] * 3)
LETRAS_DE_PORTA = "BCDFGIJKLMNOQRSTUVWXYZ"
LETRAS_DE_BLOCO = "adfghikqwxyznorsup"        # minusculas que o jogo ainda nao usa para outra coisa
CORES_PARA_BLOCOS = [(200, 170, 120), (120, 200, 210), (220, 120, 90), (160, 130, 200), (110, 170, 120), (235, 200, 90)]


# =====================================================================
#                     O MUNDO, COMO O JOGO O VE
# =====================================================================

class Mundo:
    # As contas que o jogo faz com as ZONAS, o MUNDO e as PORTAS (a letra de
    # um quadrado, para onde vai um passo, onde da uma porta), feitas aqui so
    # com os dados, para se poder perguntar "chega-se a pe ate ali?" sem
    # mexer no jogo. Um sitio e (zona, coluna, linha).

    def __init__(self, zonas, mundo, portas, treinadores, pode=None, os_blocos=None):
        self.zonas = zonas
        self.mundo = mundo
        self.portas = portas
        self.treinadores = treinadores      # quantos ha
        self.blocos = os_blocos if isinstance(os_blocos, dict) else {}
        # A regra de andar: a original, ou a que o jogo tiver agora.
        self.pode = pode or self.pode_original

    def pode_original(self, letra):
        ficha = self.blocos.get(letra)
        return not (isinstance(ficha, dict) and ficha.get("passa") is False)

    def faz(self, letra):
        # O que um bloco faz a quem vai contra ele: "cura", "loja", ou "".
        ficha = self.blocos.get(letra)
        faz = ficha.get("faz", "") if isinstance(ficha, dict) else ""
        return faz if isinstance(faz, str) else ""

    def erva(self, letra):
        ficha = self.blocos.get(letra)
        return isinstance(ficha, dict) and ficha.get("erva") is True

    def letra(self, nome, coluna, linha):
        zona = self.zonas.get(nome)
        if zona is None or linha < 0 or linha >= min(ZONA[1], len(zona)):
            return "A"
        if coluna < 0 or coluna >= min(ZONA[0], len(zona[linha])):
            return "A"
        return zona[linha][coluna]

    def ao_lado(self, nome, passo_coluna, passo_linha):
        for fila, nomes in enumerate(self.mundo):
            for lugar, este in enumerate(nomes):
                if este == nome:
                    fila, lugar = fila + passo_linha, lugar + passo_coluna
                    if 0 <= fila < len(self.mundo) and 0 <= lugar < len(self.mundo[fila]):
                        if self.mundo[fila][lugar] in self.zonas:
                            return self.mundo[fila][lugar]
                    return ""
        return ""

    def passo(self, sitio, passo_coluna, passo_linha):
        nome, coluna, linha = sitio
        coluna, linha = coluna + passo_coluna, linha + passo_linha
        if 0 <= coluna < ZONA[0] and 0 <= linha < ZONA[1]:
            return nome, coluna, linha
        return self.ao_lado(nome, passo_coluna, passo_linha), coluna % ZONA[0], linha % ZONA[1]

    def encontrar(self, letra, nomes):
        for nome in nomes:
            for linha in range(ZONA[1]):
                for coluna in range(ZONA[0]):
                    if self.letra(nome, coluna, linha) == letra:
                        return nome, coluna, linha
        return None

    def no_mundo(self):
        # As zonas que estao no MUNDO, por ordem, sem repetir.
        nomes = []
        for fila in self.mundo:
            for nome in fila:
                if nome in self.zonas and nome not in nomes:
                    nomes.append(nome)
        return nomes

    def e_treinador(self, letra):
        return letra in "123456789" and int(letra) <= self.treinadores

    def contra(self, letra):
        # As coisas contra as quais se vai, em vez de se passar por cima: uma
        # casa da avo, o balcao de uma loja, um treinador.
        return self.faz(letra) != "" or self.e_treinador(letra)

    def livre(self, letra):
        if letra in self.portas or self.contra(letra):
            return False
        return bool(self.pode(letra))

    def porta(self, sitio, letra):
        # Onde vai parar quem pisa essa porta nesse sitio.
        dentro = self.portas[letra]
        if sitio[0] != dentro:
            outro = self.encontrar(letra, [dentro])
        else:
            outro = self.encontrar(letra, [nome for nome in self.zonas if nome != dentro])
        if outro is None:
            return sitio
        for passo_coluna, passo_linha in PASSOS:
            if self.livre(self.letra(outro[0], outro[1] + passo_coluna, outro[2] + passo_linha)):
                return outro[0], outro[1] + passo_coluna, outro[2] + passo_linha
        return outro

    def partida(self):
        for letra in "P.":
            sitio = self.encontrar(letra, list(self.zonas))
            if sitio is not None:
                return sitio
        return None

    def andar(self, partida):
        # Ate onde se chega a pe a partir de um sitio. Devolve tres coisas:
        #   passos   {sitio: quantos passos ate la}
        #   veio     {sitio: (o sitio anterior, o passo dado)}
        #   contra   {o sitio de uma casa da avo, de um balcao ou de um
        #             treinador: (de onde se vai contra ele, o passo)}
        passos = {partida: 0}
        veio = {partida: None}
        contra = {}
        fila = collections.deque([partida])
        while fila:
            sitio = fila.popleft()
            for passo in PASSOS:
                vizinho = self.passo(sitio, passo[0], passo[1])
                letra = self.letra(*vizinho)
                if self.contra(letra):
                    contra.setdefault(vizinho, (sitio, passo))
                    continue
                if not self.pode(letra):
                    continue
                if letra in self.portas and self.portas[letra] in self.zonas:
                    vizinho = self.porta(vizinho, letra)
                if vizinho not in passos:
                    passos[vizinho] = passos[sitio] + 1
                    veio[vizinho] = (sitio, passo)
                    fila.append(vizinho)
        return passos, veio, contra


def _caminho(veio, sitio):
    # Os passos a dar para chegar a um sitio: [(de onde, o passo), ...].
    caminho = []
    while veio[sitio] is not None:
        caminho.insert(0, veio[sitio])
        sitio = veio[sitio][0]
    return caminho


# =====================================================================
#                    ONDE ESTA O CODIGO DE CADA COISA
# =====================================================================

def _valor(arvore, nome):
    # O valor de "NOME = ..." escrito no ficheiro, ou None se nao se percebe.
    no = blocos.instrucao(arvore, nome)
    try:
        return ast.literal_eval(no.value)
    except (ValueError, SyntaxError, AttributeError, TypeError):
        return None


def _zonas_escritas(arvore):
    # As zonas, pela ordem do ficheiro: [(nome, primeira linha, ultima), ...].
    no = blocos.instrucao(arvore, "ZONAS")
    partes = blocos.entradas(no) if no is not None else None
    return [(blocos.texto_constante(chave), primeira, ultima) for chave, primeira, ultima in partes or []]


def _interiores(arvore):
    # Os nomes das zonas a que se chega por uma porta.
    portas = _valor(arvore, "PORTAS")
    if not isinstance(portas, dict):
        return []
    return [nome for nome in portas.values() if isinstance(nome, str)]


def escolhas(fonte):
    arvore = ast.parse(fonte)
    # Sem ZONAS nao e este jogo.
    if blocos.instrucao(arvore, "ZONAS") is None or blocos.instrucao(arvore, "MUNDO") is None:
        return []
    interiores = _interiores(arvore)
    lista = [{"id": "mundo", "grupo": "Mapa", "titulo": "O mundo: como as zonas se juntam"}]
    if blocos.instrucao(arvore, "JOGADOR") is not None:
        lista.append({"id": "jogador", "grupo": "Mapa", "titulo": "Tu: o teu boneco"})
    if blocos.instrucao(arvore, "PORTAS") is not None:
        lista.append({"id": "portas", "grupo": "Edifícios", "titulo": "As portas"})
    if blocos.instrucao(arvore, "LOJA") is not None:
        lista.append({"id": "loja", "grupo": "Edifícios", "titulo": "A loja: o que se vende"})
    numero = 0
    for letra, ficha, _, _ in base._fichas(blocos.instrucao(arvore, "BLOCOS")):
        nome = blocos.valor_da_chave(ficha, "nome") or "bloco"
        lista.append({"id": "bloco:" + str(numero), "grupo": "Blocos", "titulo": nome + " (a letra " + str(letra) + ")"})
        numero = numero + 1
    numero = 0
    for nome, _, _ in _zonas_escritas(arvore):
        titulo = nome or "Zona " + str(numero + 1)
        if nome in interiores:
            lista.append({"id": "zona:" + str(numero), "grupo": "Edifícios", "titulo": titulo + " (por dentro)"})
        else:
            lista.append({"id": "zona:" + str(numero), "grupo": "Mapa", "titulo": titulo})
        numero = numero + 1
    lista = lista + base.escolhas(fonte)
    for tipo in FUNCOES:
        grupo = base.FUNCOES[tipo][1]
        for nome in FUNCOES[tipo]:
            if blocos.funcao(arvore, nome) is not None:
                lista.append({"id": tipo + ":" + nome, "grupo": grupo, "titulo": FUNCOES[tipo][nome][0]})
    ordem = list(SOBRE_OS_GRUPOS)
    lista.sort(key=lambda escolha: ordem.index(escolha["grupo"]) if escolha["grupo"] in ordem else len(ordem))
    return lista


def _juntar_imagens(resposta, ficha, chaves):
    # Quando uma coisa tem varias imagens, a regiao leva "imagens": o nome
    # que a Oficina mostra para cada uma, e o ficheiro escrito no codigo.
    # ("imagem" fica com a primeira, que e a que se abre.)
    imagens = []
    for chave, nome in chaves:
        ficheiro = blocos.valor_da_chave(ficha, chave)
        if ficheiro is not None:
            imagens.append({"nome": nome, "ficheiro": ficheiro})
    if imagens:
        resposta["imagem"] = imagens[0]["ficheiro"]
        resposta["imagens"] = imagens


def _serve(ficha, dentro):
    # Este bloco e para este genero de zona (dentro de um edificio, ou ca fora)?
    return ficha.get("sempre") is True or bool(ficha.get("dentro")) == bool(dentro)


def _blocos_escritos(arvore, dentro):
    # Os blocos que ha, para dentro dos edificios ou para ca fora:
    # [(letra, nome, o que se faz com ele), ...]
    lista = []
    os_blocos = _valor(arvore, "BLOCOS")
    for letra, ficha in os_blocos.items() if isinstance(os_blocos, dict) else []:
        if not isinstance(ficha, dict) or not _serve(ficha, dentro):
            continue
        faz = "anda-se por cima" if ficha.get("passa") is not False else "nao se passa"
        if ficha.get("erva") is True:
            faz = faz + ", e saltam de la bichos"
        if ficha.get("faz") == "cura":
            faz = "vai-se contra ele para curar a equipa"
        if ficha.get("faz") == "loja":
            faz = "vai-se contra ele para abrir a loja"
        lista.append((str(letra), str(ficha.get("nome", "bloco")), faz))
    return lista


def _quem_e_quem(arvore, aqui, dentro=False):
    # A lista dos blocos e dos treinadores que ha agora (com o numero de cada
    # um e a zona onde esta), e a das portas. "aqui" e a zona que esta aberta.
    zonas = _valor(arvore, "ZONAS")
    zonas = zonas if _sao_zonas(zonas) else {}
    os_blocos = _blocos_escritos(arvore, dentro)
    texto_dos_blocos = []
    if os_blocos:
        texto_dos_blocos = ["OS BLOCOS QUE HA AGORA para " + ("dentro dos edificios" if dentro else "as zonas ca de fora")
                            + " (fazem-se e mudam-se em Blocos). A letra, o nome, e o que faz:"]
        texto_dos_blocos += ["  " + letra + "   " + nome + " (" + faz + ")" for letra, nome, faz in os_blocos]
        texto_dos_blocos.append("")
    treinadores = [blocos.valor_da_chave(ficha, "nome") or "sem nome"
                   for _, ficha, _, _ in base._fichas(blocos.instrucao(arvore, "TREINADORES"))]
    texto = texto_dos_blocos + ["OS TREINADORES QUE HA AGORA, e o numero de cada um no mapa:"]
    for numero, nome in enumerate(treinadores, 1):
        if numero > 9:
            texto.append("  -   " + nome + ": nao cabe no mapa (so ha numeros ate ao 9)")
            continue
        onde = [zona for zona in zonas if str(numero) in "".join(zonas[zona])]
        if aqui in onde:
            sitio = "esta nesta zona"
        elif onde:
            sitio = 'esta na zona "' + onde[0] + '"'
        else:
            sitio = "ainda nao esta em nenhuma zona: escreve um " + str(numero) + " onde o quiseres"
        texto.append("  " + str(numero) + "   " + nome + " (" + sitio + ")")
    texto.append("Para mudares um treinador de sitio, apaga o numero dele (poe relva, ou soalho) e escreve-o")
    texto.append("noutro quadrado, desta zona ou de outra. Cada numero so se escreve uma vez.")
    portas = _valor(arvore, "PORTAS")
    if _sao_portas(portas) and portas:
        texto.append("")
        texto.append("AS PORTAS QUE HA AGORA:")
        for letra, destino in portas.items():
            fora = [zona for zona in zonas if zona != destino and letra in "".join(zonas[zona])]
            texto.append("  " + letra + '   a porta de "' + destino + '"'
                         + (' (ca fora, esta na zona "' + fora[0] + '")' if fora else " (ainda nao esta em nenhuma zona ca fora)"))
    return "\n".join(texto)


def regiao(fonte, escolha):
    # Igual a do bicharada.py, mais o mundo, as portas, as zonas e as funcoes
    # do mapa.
    arvore = ast.parse(fonte)
    linhas = fonte.split("\n")
    tipo, _, numero = escolha.partition(":")

    if escolha in ("mundo", "portas", "loja", "jogador"):
        no = blocos.instrucao(arvore, escolha.upper())
        if no is None:
            return None
        titulo = {"mundo": "O mundo", "portas": "As portas", "loja": "A loja", "jogador": "Tu"}[escolha]
        resposta = {"inicio": no.lineno, "fim": no.end_lineno, "titulo": titulo, "imagem": None, "som": None,
                    "ajuda": blocos.ajuda_acima(linhas, no.lineno), "dica": DICAS[escolha],
                    "sugestoes": SUGESTOES[escolha]}
        if escolha == "jogador":
            _juntar_imagens(resposta, no.value, [("imagem", "De frente"), ("imagem_costas", "De costas"),
                                                 ("imagem_lado", "De lado")])
        return resposta

    if tipo == "bloco":
        no = blocos.instrucao(arvore, "BLOCOS")
        partes = base._fichas(no)
        if not numero.isdigit() or int(numero) >= len(partes):
            return None
        letra, ficha, inicio, fim = partes[int(numero)]
        zonas = _valor(arvore, "ZONAS")
        onde = [zona for zona in zonas if str(letra) in "".join(zonas[zona])] if _sao_zonas(zonas) else []
        ajuda = blocos.ajuda_acima(linhas, no.lineno) + "\n\nA LETRA DESTE BLOCO E: " + str(letra) + "\n"
        ajuda = ajuda + ("Esta nas zonas: " + ", ".join(onde) if onde else
                         "Ainda nao esta em nenhuma zona: abre uma zona e escreve a letra " + str(letra) + ".")
        return {"inicio": inicio, "fim": fim, "titulo": blocos.valor_da_chave(ficha, "nome") or escolha,
                "imagem": blocos.valor_da_chave(ficha, "imagem"), "som": None, "ajuda": ajuda, "dica": DICAS["bloco"],
                "sugestoes": SUGESTOES["bloco"], "caixas": True, "apagar": "Apagar este bloco"}

    if tipo == "zona":
        no = blocos.instrucao(arvore, "ZONAS")
        partes = _zonas_escritas(arvore)
        if not numero.isdigit() or int(numero) >= len(partes):
            return None
        nome, inicio, fim = partes[int(numero)]
        dentro = nome in _interiores(arvore)
        # A explicacao das letras e a de dentro ou a de fora, conforme a zona.
        # E, por baixo, quem e cada numero e cada porta neste momento: isso
        # muda quando se cria, apaga ou muda o nome a um treinador.
        ajuda = blocos.comentarios_a_partir_de(linhas, INICIO_DOS_INTERIORES if dentro else INICIO_DAS_ZONAS)
        ajuda = (ajuda or blocos.ajuda_acima(linhas, no.lineno)) + "\n\n" + _quem_e_quem(arvore, nome, dentro)
        return {"inicio": inicio, "fim": fim, "titulo": nome or escolha, "imagem": None, "som": None,
                "ajuda": ajuda, "dica": DICAS["interior" if dentro else "zona"],
                "sugestoes": SUGESTOES["interior" if dentro else "zona"],
                "apagar": "Apagar este edifício" if dentro else "Apagar esta zona", "renomear": "Mudar o nome"}

    if tipo in FUNCOES and numero in FUNCOES[tipo]:
        no = blocos.funcao(arvore, numero)
        if no is None:
            return None
        ajuda = blocos.ajuda_acima(linhas, no.lineno)
        for inicio in base.FUNCOES[tipo][2]:
            geral = blocos.comentarios_a_partir_de(linhas, inicio)
            if geral and geral != ajuda:
                ajuda = ajuda + "\n\n" + geral
        dica = DICAS["desenho_da_batalha"] if numero in NA_BATALHA else DICAS[tipo]
        return {"inicio": no.lineno, "fim": no.end_lineno, "ajuda": ajuda, "dica": dica,
                "titulo": FUNCOES[tipo][numero][0], "imagem": None, "som": None, "sugestoes": SUGESTOES[numero]}

    resposta = base.regiao(fonte, escolha)
    if resposta is not None and tipo == "bicho" and numero.isdigit():
        resposta["sugestoes"] = ["Faz este bicho maior na batalha",
                                 "Põe-no mais rápido mas com menos vida", "O que quer dizer o «aprende»?"]
        # Cada bicho tem duas imagens: de frente e de costas.
        ficha = base._fichas(blocos.instrucao(arvore, "BICHOS"))[int(numero)][1]
        _juntar_imagens(resposta, ficha, [("imagem", "De frente"), ("imagem_costas", "De costas")])
        resposta["dica"] = DICAS["bicho"]
    if resposta is not None and tipo == "treinador" and numero.isdigit():
        # (Ha caixas para marcar: ve a funcao caixas, mais abaixo.)
        resposta["caixas"] = True
        resposta["dica"] = DICAS["treinador"]
        # O boneco dele, no mapa.
        ficha = base._fichas(blocos.instrucao(arvore, "TREINADORES"))[int(numero)][1]
        resposta["imagem"] = blocos.valor_da_chave(ficha, "imagem") if isinstance(ficha, ast.Dict) else None
        letra = str(int(numero) + 1)
        zonas = _valor(arvore, "ZONAS")
        onde = [nome for nome in zonas if letra in "".join(zonas[nome])] if _sao_zonas(zonas) else []
        if int(letra) > 9:
            resposta["dica"] = "No mapa só cabem 9 treinadores: este não aparece lá. " + resposta["dica"]
        elif onde:
            resposta["dica"] = ("No mapa, este treinador é o " + letra + ', e está na zona "' + onde[0]
                                + '": para o mudares de sítio, muda o ' + letra + " de lugar. " + resposta["dica"])
        else:
            resposta["dica"] = ("No mapa, este treinador é o " + letra + ", mas ainda não está em nenhuma zona: "
                                "escreve um " + letra + " onde o quiseres. " + resposta["dica"])
    return resposta


# =====================================================================
#                        CRIAR UMA COISA NOVA
# =====================================================================

def _sao_zonas(zonas):
    if not isinstance(zonas, dict) or len(zonas) == 0:
        return False
    for nome, filas in zonas.items():
        if not isinstance(nome, str) or not isinstance(filas, list):
            return False
        if not all(isinstance(fila, str) for fila in filas):
            return False
    return True


def _e_mundo(mundo):
    if not isinstance(mundo, list) or len(mundo) == 0:
        return False
    for fila in mundo:
        if not isinstance(fila, list) or not all(isinstance(nome, str) for nome in fila):
            return False
    return True


def _sao_portas(portas):
    return isinstance(portas, dict) and all(isinstance(letra, str) and len(letra) == 1 and isinstance(nome, str)
                                            for letra, nome in portas.items())


def _ler_mundo(fonte, treinadores=None):
    # (a arvore, o Mundo) do que esta escrito no ficheiro. O Mundo vem None
    # se as ZONAS, o MUNDO ou as PORTAS nao se perceberem.
    arvore = ast.parse(fonte)
    zonas = _valor(arvore, "ZONAS")
    mundo = _valor(arvore, "MUNDO")
    portas = _valor(arvore, "PORTAS")
    if treinadores is None:
        no = blocos.instrucao(arvore, "TREINADORES")
        treinadores = len(no.value.elts) if no is not None and isinstance(no.value, ast.List) else 0
    if not _sao_zonas(zonas) or not _e_mundo(mundo) or not _sao_portas(portas):
        return arvore, None
    return arvore, Mundo(zonas, mundo, portas, treinadores, os_blocos=_valor(arvore, "BLOCOS"))


def _escrever_na_zona(arvore, linhas, nome, coluna, linha, texto):
    # Troca letras de uma zona, no ficheiro: "texto" fica a partir dessa
    # coluna dessa linha da zona. So troca relva, e diz se trocou.
    no = blocos.instrucao(arvore, "ZONAS")
    if no is None or not isinstance(no.value, ast.Dict):
        return False
    for chave, valor in zip(no.value.keys, no.value.values):
        if blocos.texto_constante(chave) != nome or not isinstance(valor, ast.List) or linha >= len(valor.elts):
            continue
        fila = valor.elts[linha]
        if blocos.texto_constante(fila) is None or fila.lineno != fila.end_lineno:
            return False
        escrito = linhas[fila.lineno - 1]
        onde = base._coluna(escrito, fila.col_offset) + 1 + coluna
        if escrito[onde:onde + len(texto)] != "." * len(texto):
            return False
        linhas[fila.lineno - 1] = escrito[:onde] + texto + escrito[onde + len(texto):]
        return True
    return False


def _juntar_ao_dicionario(arvore, linhas, nome, novas):
    # Poe linhas novas no fim de um dicionario "NOME = {...}" do ficheiro.
    # (Muda o numero das linhas dai para baixo: quem juntar a dois
    # dicionarios comeca pelo que esta mais abaixo.)
    no = blocos.instrucao(arvore, nome)
    partes = blocos.entradas(no) if no is not None else None
    if partes:
        ultima = partes[-1][2]
        if not linhas[ultima - 1].rstrip().endswith(","):
            linhas[ultima - 1] = linhas[ultima - 1].rstrip() + ","
        linhas[ultima:ultima] = novas
    elif no is not None and isinstance(no.value, ast.Dict) and len(no.value.keys) == 0:
        linhas[no.lineno - 1:no.end_lineno] = [nome + " = {"] + novas + ["}"]
    else:
        raise ValueError("não percebi como está escrito " + nome + " no ficheiro.")


def _texto_da_zona(nome, filas):
    return ['    "' + nome + '": ['] + ['        "' + fila + '",' for fila in filas] + ["    ],"]


def _por_treinador(fonte, numero):
    # Escreve o numero de um treinador novo num bocado de relva onde se
    # chegue a pe e nao tape a passagem (com relva ou erva a toda a volta),
    # de preferencia na zona da partida. Devolve o ficheiro e o nome da zona
    # (None se nao o pos).
    arvore, mundo = _ler_mundo(fonte, numero - 1)
    if mundo is None or numero > 9 or mundo.partida() is None:
        return fonte, None
    if any(str(numero) in "".join(filas) for filas in mundo.zonas.values()):
        return fonte, None
    partida = mundo.partida()
    passos, _, _ = mundo.andar(partida)
    livres = []
    for (nome, coluna, linha), quantos in passos.items():
        a_volta = [mundo.letra(nome, coluna + dc, linha + dl) for dc in (-1, 0, 1) for dl in (-1, 0, 1)]
        if all(vizinha in ".e" for vizinha in a_volta) and mundo.letra(nome, coluna, linha) == ".":
            # (Perto da partida, para se dar logo com ele, mas nao em cima dela.)
            livres.append((nome != partida[0], quantos < 3, quantos, nome, coluna, linha))
    linhas = fonte.split("\n")
    for _, _, _, nome, coluna, linha in sorted(livres):
        if _escrever_na_zona(arvore, linhas, nome, coluna, linha, str(numero)):
            return "\n".join(linhas), nome
    return fonte, None


def _nova_zona(fonte):
    arvore, mundo = _ler_mundo(fonte)
    no = blocos.instrucao(arvore, "MUNDO")
    if mundo is None or not all(isinstance(fila, ast.List) and fila.lineno == fila.end_lineno
                                for fila in no.value.elts):
        raise ValueError("não percebi como estão escritas as ZONAS ou o MUNDO no ficheiro.")
    nome = base._nome_livre("zona nova", list(mundo.zonas))
    # Fica no fim de uma fila do MUNDO: da primeira cuja ultima zona tenha
    # uma saida para a direita, que e onde a zona nova tem a entrada.
    fila = None
    for numero, nomes in enumerate(mundo.mundo):
        if nomes and any(mundo.livre(mundo.letra(nomes[-1], ZONA[0] - 1, linha)) for linha in (6, 7)):
            fila = fila if fila is not None else numero
    ligada = fila is not None
    if fila is None:
        fila = len(mundo.mundo) - 1
    vizinha = mundo.mundo[fila][-1] if mundo.mundo[fila] else None

    linhas = fonte.split("\n")
    lista = no.value.elts[fila]
    escrito = linhas[lista.lineno - 1]
    corte = base._coluna(escrito, lista.end_col_offset - 1)
    antes = escrito[:corte].rstrip().rstrip(",")
    junta = ', "' if len(lista.elts) > 0 else '"'
    linhas[lista.lineno - 1] = antes + junta + nome + '"' + escrito[corte:]
    _juntar_ao_dicionario(arvore, linhas, "ZONAS", _texto_da_zona(nome, _so_com_blocos(arvore, ZONA_NOVA, CHAO_DE_FORA)))

    aviso = 'Criei a zona "' + nome + '": relva, com uma saída ao meio de cada lado.'
    if vizinha is None:
        aviso = aviso + " Pu-la no MUNDO, na última fila."
    else:
        aviso = aviso + ' No MUNDO, pu-la à direita de "' + vizinha + '".'
    if not ligada:
        aviso = aviso + " Ainda não se chega lá a pé: abre uma saída na zona do lado, ou muda-a de sítio em O mundo."
    return "\n".join(linhas), "zona:" + str(len(mundo.zonas)), aviso


def _so_com_blocos(arvore, filas, chao):
    # Uma zona nova so leva blocos que existam: se alguem apagou as arvores
    # ou as mesas, no lugar delas vai chao. (O "?" e o lugar da porta.)
    os_blocos = _valor(arvore, "BLOCOS")
    if not isinstance(os_blocos, dict):
        return filas
    # (Sem janelas, a parede fica inteira.)
    filas = [fila if "j" in os_blocos else fila.replace("j", "#") for fila in filas]
    return ["".join(letra if letra in os_blocos or letra == "?" else chao for letra in fila) for fila in filas]


def _novo_edificio(fonte):
    arvore, mundo = _ler_mundo(fonte)
    if mundo is None:
        raise ValueError("não percebi como estão escritas as ZONAS, o MUNDO ou as PORTAS no ficheiro.")
    usadas = "".join("".join(filas) for filas in mundo.zonas.values()) + "".join(mundo.portas)
    usadas = usadas + "".join(str(letra) for letra in mundo.blocos)
    letras = [letra for letra in LETRAS_DE_PORTA if letra not in usadas]
    if not letras:
        raise ValueError("já não há letras livres para mais uma porta.")
    letra = letras[0]
    nome = base._nome_livre("casa nova", list(mundo.zonas))
    linhas = fonte.split("\n")

    # Ca fora: tres quadrados de parede e, por baixo, parede, porta, parede.
    # Num sitio com relva a toda a volta, onde se chegue a pe a frente da
    # porta, de preferencia na zona da partida.
    posta = None
    partida = mundo.partida()
    if partida is not None:
        passos, _, _ = mundo.andar(partida)
        sitios = []
        for zona in mundo.no_mundo():
            for linha in range(1, ZONA[1] - 3):
                for coluna in range(1, ZONA[0] - 3):
                    a_volta = [mundo.letra(zona, coluna + dc, linha + dl) for dc in range(-1, 4) for dl in range(-1, 3)]
                    casa = [mundo.letra(zona, coluna + dc, linha + dl) for dc in range(3) for dl in range(2)]
                    frente = (zona, coluna + 1, linha + 2)
                    if all(vizinha in ".e" for vizinha in a_volta) and all(esta == "." for esta in casa):
                        if frente in passos:
                            sitios.append((zona != partida[0], passos[frente] < 2, passos[frente], zona, coluna, linha))
        for _, _, _, zona, coluna, linha in sorted(sitios):
            if _escrever_na_zona(arvore, linhas, zona, coluna, linha, "###"):
                _escrever_na_zona(arvore, linhas, zona, coluna, linha + 1, "#" + letra + "#")
                posta = zona
                break

    # (Primeiro o dicionario que esta mais abaixo no ficheiro.)
    sala = _so_com_blocos(arvore, SALA_NOVA, CHAO_DE_DENTRO)
    novas = {"ZONAS": _texto_da_zona(nome, [fila.replace("?", letra) for fila in sala]),
             "PORTAS": ['    "' + letra + '": "' + nome + '",']}
    for dicionario in sorted(novas, key=lambda qual: blocos.instrucao(arvore, qual).lineno, reverse=True):
        _juntar_ao_dicionario(arvore, linhas, dicionario, novas[dicionario])

    aviso = 'Criei o edifício "' + nome + '": uma sala, e a porta é a letra ' + letra + "."
    if posta is not None:
        aviso = aviso + ' Cá fora, pu-lo na zona "' + posta + '". Muda-lhe o nome e a sala; em As portas vês como funciona.'
    else:
        aviso = (aviso + " Cá fora ainda não está em lado nenhum: numa zona, escreve ### e por baixo #"
                 + letra + "#, com relva à frente da porta.")
    return "\n".join(linhas), "zona:" + str(len(mundo.zonas)), aviso


def _ficheiro_sem_acentos(nome):
    # "Campeã da Feira" -> "campea-da-feira": os nomes dos ficheiros de
    # imagem so levam letras sem acentos, algarismos, "-" e "_".
    import unicodedata
    simples = unicodedata.normalize("NFKD", base._ficheiro(nome)).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9_-]", "", simples) or "treinador"


def _novo_treinador(fonte):
    # Aqui um treinador novo nao e copia do primeiro (que e quem da a rede):
    # e uma ficha simples, com uma fala e o primeiro bicho que houver.
    arvore = ast.parse(fonte)
    no = blocos.instrucao(arvore, "TREINADORES")
    partes = base._fichas(no)
    bichos = base._fichas(blocos.instrucao(arvore, "BICHOS"))
    if not partes or not bichos:
        raise ValueError("não percebi como estão escritos os TREINADORES no ficheiro.")
    nome = base._nome_livre("Treinador novo", [blocos.valor_da_chave(parte[1], "nome") for parte in partes])
    linhas = fonte.split("\n")
    ultima = partes[-1][3]
    if not linhas[ultima - 1].rstrip().endswith(","):
        linhas[ultima - 1] = linhas[ultima - 1].rstrip() + ","
    linhas[ultima:ultima] = [
        "    {",
        '        "nome": "' + nome + '",',
        '        "falas": ["Olá! Ainda não sei o que dizer."],',
        '        "frase": "Vamos a isto!",',
        '        "falas_depois": ["Boa luta!"],',
        '        "cor_fundo": (200, 190, 150),',
        '        "imagem": "' + _ficheiro_sem_acentos(nome) + '.png",',
        '        "equipa": [',
        '            {"bicho": "' + str(bichos[0][0]) + '", "nivel": 5},',
        "        ],",
        "    },",
    ]
    aviso = 'Criei o "' + nome + '". Escolhe os bichos dele, e muda-lhe o nome e as falas.'
    return "\n".join(linhas), "treinador:" + str(len(partes)), aviso


def _novo_bloco(fonte):
    arvore = ast.parse(fonte)
    partes = base._fichas(blocos.instrucao(arvore, "BLOCOS"))
    zonas = _valor(arvore, "ZONAS")
    portas = _valor(arvore, "PORTAS")
    usadas = "".join("".join(filas) for filas in zonas.values()) if _sao_zonas(zonas) else ""
    usadas = usadas + "".join(str(parte[0]) for parte in partes) + "".join(portas if isinstance(portas, dict) else [])
    livres = [letra for letra in LETRAS_DE_BLOCO if letra not in usadas and letra not in CONHECIDAS]
    if not livres:
        raise ValueError("já não há letras livres para mais um bloco.")
    letra = livres[0]
    nome = base._nome_livre("bloco novo", [blocos.valor_da_chave(parte[1], "nome") for parte in partes])
    cor = CORES_PARA_BLOCOS[len(partes) % len(CORES_PARA_BLOCOS)]
    linhas = fonte.split("\n")
    _juntar_ao_dicionario(arvore, linhas, "BLOCOS", [
        '    "' + letra + '": {',
        '        "nome": "' + nome + '",',
        '        "passa": True,',
        '        "erva": False,',
        '        "dentro": False,',
        '        "por_baixo": ".",',
        '        "cor": ' + str(cor) + ",",
        '        "imagem": "' + base._ficheiro(nome) + '.png",',
        "    },",
    ])
    aviso = ('Criei o bloco "' + nome + '": é a letra ' + letra + ". Dá-lhe um nome, desenha-o (ou começa por um modelo) "
             "e diz nas caixas se se anda por cima dele. Depois abre uma zona e escreve a letra " + letra + " onde o quiseres.")
    return "\n".join(linhas), "bloco:" + str(len(partes)), aviso


def _apagar_bloco(fonte, escolha):
    # O bloco sai dos BLOCOS, e nas zonas fica relva (ou soalho, dentro dos
    # edificios) no lugar dele.
    arvore = ast.parse(fonte)
    partes = base._fichas(blocos.instrucao(arvore, "BLOCOS"))
    numero = escolha.partition(":")[2]
    if not numero.isdigit() or int(numero) >= len(partes):
        raise ValueError("isso não se pode apagar.")
    letra, ficha, inicio, fim = partes[int(numero)]
    if letra in NAO_SE_APAGAM:
        raise ValueError(NAO_SE_APAGAM[letra].lower() + " não se apaga: a relva e o soalho são o que fica no lugar "
                         "dos blocos que se apagam, e as paredes e o «nada» dão a forma aos edifícios. "
                         "Mas podes mudar-lhe o nome, a cor e o desenho.")
    interiores = _interiores(arvore)
    linhas = fonte.split("\n")
    quantos = []

    def mudar(zona, texto):
        quantos.extend(letra for esta in texto if esta == letra)
        return texto.replace(letra, "_" if zona in interiores else ".")
    trocas = _trocas_nas_zonas(arvore, linhas, mudar)
    # (Um bloco que o tinha por baixo passa a ter relva.)
    for _, outra, _, _ in partes:
        no = base._no_da_chave(outra, "por_baixo") if isinstance(outra, ast.Dict) and outra is not ficha else None
        if no is not None and blocos.texto_constante(no) == letra and no.lineno == no.end_lineno:
            base._trocar_no(linhas, no, '"."', trocas)
    aviso = 'Apaguei o bloco "' + (blocos.valor_da_chave(ficha, "nome") or str(letra)) + '" (a letra ' + str(letra) + ")."
    if quantos:
        aviso = aviso + " Havia " + str(len(quantos)) + " nas zonas: ficou relva (ou soalho) no lugar deles."
    return base._aplicar(linhas, [(inicio, fim)], trocas), aviso


def novo(fonte, grupo):
    if grupo == "Blocos":
        return _novo_bloco(fonte)
    if grupo == "Mapa":
        return _nova_zona(fonte)
    if grupo == "Edifícios":
        return _novo_edificio(fonte)
    if grupo == "Treinadores":
        nova, escolha, aviso = _novo_treinador(fonte)
    else:
        nova, escolha, aviso = base.novo(fonte, grupo)
    if grupo == "Bichos":
        # (A copia vinha com a imagem de costas do bicho copiado.)
        linhas = nova.split("\n")
        nome, _, inicio, fim = base._fichas(blocos.instrucao(ast.parse(nova), "BICHOS"))[-1]
        for linha in range(inicio - 1, fim):
            linhas[linha] = re.sub(r'"imagem_costas": "[^"]*"',
                                   '"imagem_costas": "' + base._ficheiro(nome) + '-costas.png"', linhas[linha])
        nova = "\n".join(linhas)
        aviso = aviso.replace(" No jogo inteiro já aparece no ecrã de escolha.", "") + " Pode saltar da erva, à solta."
    if grupo == "Treinadores":
        numero = int(escolha.partition(":")[2]) + 1
        nova, zona = _por_treinador(nova, numero)
        if zona is not None:
            aviso = (aviso + " Pu-lo no mapa: é o " + str(numero) + ', na zona "' + zona
                     + '". Podes mudá-lo de sítio.')
        elif numero > 9:
            aviso = aviso + " No mapa só cabem 9 treinadores, por isso este não aparece no jogo."
        else:
            aviso = aviso + " Ainda não está no mapa: numa zona, escreve um " + str(numero) + " onde o quiseres."
    return nova, escolha, aviso


# =====================================================================
#                        CAIXAS PARA MARCAR
# =====================================================================
# Ha coisas que no codigo sao um True ou um False, e que na Oficina se
# marcam numa caixa: aqui, se um treinador da a rede no inicio. Como na
# lista dos bichos, trabalha-se sobre o codigo que esta no editor.
#   sem "chave": devolve as caixas e como estao
#   com "chave": devolve {"codigo": ...} ja com esse valor

CAIXAS_DE = {
    "treinador": {"da_rede": "Dá a rede no início (sem bichos, em vez de lutar dá uma rede; depois faz uma luta de treino)"},
    "bloco": {"passa": "Anda-se por cima dele (desmarcado, tapa o caminho)",
              "erva": "Saltam de lá bichos à solta, como da erva alta",
              "dentro": "É para dentro dos edifícios (desmarcado, é para as zonas cá de fora)"},
}


def caixas(fonte, escolha, codigo, chave=None, valor=None):
    CAIXAS = CAIXAS_DE.get(escolha.partition(":")[0])
    if CAIXAS is None:
        raise ValueError("aqui não há caixas para marcar.")
    texto = codigo.rstrip()
    virgula = texto.endswith(",")
    if virgula:
        texto = texto[:-1]
    # A ficha de um treinador e um {...}. A de um bloco e "letra": {...}:
    # para o Python a ler mete-se entre chavetas, numa linha a parte (assim
    # as linhas e as colunas do que la esta nao mudam de sitio... a nao ser a
    # linha, que passa a ser a seguinte).
    desvio = 0
    try:
        ficha = ast.parse(texto, mode="eval").body
    except SyntaxError:
        try:
            ficha = ast.parse("{\n" + texto + "\n}", mode="eval").body
            ficha = ficha.values[0] if isinstance(ficha, ast.Dict) and len(ficha.values) == 1 else None
            desvio = 1
        except SyntaxError:
            raise ValueError("o código tem um erro: corrige-o primeiro, ou carrega em Repor o original.")
    if not isinstance(ficha, ast.Dict) or len(ficha.keys) == 0:
        raise ValueError("não percebi esta ficha.")
    if desvio:
        for no in ast.walk(ficha):
            if hasattr(no, "lineno"):
                no.lineno, no.end_lineno = no.lineno - 1, no.end_lineno - 1
    valores = {}
    for k, v in zip(ficha.keys, ficha.values):
        if blocos.texto_constante(k) in CAIXAS:
            valores[blocos.texto_constante(k)] = v
    if chave is None:
        return {"caixas": [{"chave": qual, "texto": CAIXAS[qual],
                            "ligada": isinstance(valores.get(qual), ast.Constant) and valores[qual].value is True}
                           for qual in CAIXAS]}
    if chave not in CAIXAS:
        raise ValueError("essa caixa não existe.")
    linhas = texto.split("\n")
    escrito = "True" if valor else "False"
    if chave in valores:
        no = valores[chave]
        if no.lineno != no.end_lineno:
            raise ValueError('não percebi o que está escrito em "' + chave + '".')
        linha = linhas[no.lineno - 1]
        linhas[no.lineno - 1] = (linha[:base._coluna(linha, no.col_offset)] + escrito
                                 + linha[base._coluna(linha, no.end_col_offset):])
    elif valor:
        # Ainda nao esta na ficha: vai para uma linha nova, a seguir a primeira coisa dela.
        primeira = ficha.values[0]
        modelo = linhas[ficha.keys[0].lineno - 1]
        margem = modelo[:len(modelo) - len(modelo.lstrip())]
        if ficha.keys[0].lineno == ficha.lineno:
            margem = margem + "    "
        if not linhas[primeira.end_lineno - 1].rstrip().endswith((",", "{")):
            raise ValueError("não consegui acrescentar à ficha: escreve tu \"" + chave + '": True, numa linha nova.')
        linhas[primeira.end_lineno:primeira.end_lineno] = [margem + '"' + chave + '": True,']
    return {"codigo": "\n".join(linhas) + ("," if virgula else "") + codigo[len(codigo.rstrip()):]}


# =====================================================================
#                          APAGAR UMA COISA
# =====================================================================
# Os bichos e os ataques apagam-se como na Bicharada. Um treinador tambem,
# mas aqui tem um numero no mapa: esse numero sai, e os dos treinadores que
# vinham a seguir descem um. Uma zona (ou o interior de um edificio) sai das
# ZONAS, do MUNDO e das PORTAS.

def _trocas_nas_zonas(arvore, linhas, mudar, menos=None):
    # As letras das zonas, no ficheiro, passam por mudar(zona, o texto da
    # linha), que devolve o texto novo, do mesmo tamanho. Devolve as trocas a
    # fazer (ve o _aplicar do bicharada.py). "menos" e uma zona onde nao se mexe.
    trocas = []
    no = blocos.instrucao(arvore, "ZONAS")
    for chave, valor in zip(no.value.keys, no.value.values):
        nome = blocos.texto_constante(chave)
        if nome == menos or not isinstance(valor, ast.List):
            continue
        for fila in valor.elts:
            antes = blocos.texto_constante(fila)
            if antes is None or fila.lineno != fila.end_lineno:
                continue
            depois = mudar(nome, antes)
            escrito = linhas[fila.lineno - 1]
            onde = base._coluna(escrito, fila.col_offset) + 1
            if depois != antes and len(depois) == len(antes) and escrito[onde:onde + len(antes)] == antes:
                trocas.append((fila.lineno, onde, onde + len(antes), depois))
    return trocas


def _apagar_treinador(fonte, escolha):
    numero = int(escolha.partition(":")[2]) + 1
    arvore, mundo = _ler_mundo(fonte)
    if mundo is None:
        return base.apagar(fonte, escolha)
    quantos = mundo.treinadores
    desceram = []

    def mudar(nome, texto):
        nova = ""
        for lugar, letra in enumerate(texto):
            if letra in "123456789" and int(letra) == numero:
                # No lugar dele fica o chao que houver ao lado.
                letra = "_" if "_" in texto[max(0, lugar - 1):lugar + 2] else "."
            elif letra in "123456789" and numero < int(letra) <= quantos:
                desceram.append(letra)
                letra = str(int(letra) - 1)
            nova = nova + letra
        return nova

    linhas = fonte.split("\n")
    nova = base._aplicar(linhas, [], _trocas_nas_zonas(arvore, linhas, mudar))
    nova, aviso = base.apagar(nova, escolha)
    if desceram:
        aviso = aviso + " No mapa, os treinadores que vinham a seguir passaram a ter o número abaixo."
    return nova, aviso


def _apagar_zona(fonte, escolha):
    arvore, mundo = _ler_mundo(fonte)
    partes = _zonas_escritas(arvore)
    numero = escolha.partition(":")[2]
    if mundo is None or not numero.isdigit() or int(numero) >= len(partes):
        raise ValueError("isso não se pode apagar.")
    nome, inicio, fim = partes[int(numero)]
    if len(partes) < 2:
        raise ValueError("tem de haver pelo menos uma zona.")
    letras = "".join(mundo.zonas[nome])
    if "P" in letras:
        raise ValueError("é nesta zona que se começa (tem o P). Muda primeiro o P para outra zona.")
    linhas = fonte.split("\n")
    cortes = [(inicio, fim)]
    trocas = []

    # No MUNDO fica um buraco no lugar dela, para as outras nao mudarem de sitio.
    no = blocos.instrucao(arvore, "MUNDO")
    for fila in no.value.elts:
        for este in fila.elts if isinstance(fila, ast.List) else []:
            if blocos.texto_constante(este) == nome and este.lineno == este.end_lineno:
                base._trocar_no(linhas, este, '""', trocas)
    # As portas que davam para ela saem das PORTAS, e ca fora passam a parede.
    portas = [letra for letra in mundo.portas if mundo.portas[letra] == nome]
    no = blocos.instrucao(arvore, "PORTAS")
    for (chave, primeira, ultima), valor in zip(blocos.entradas(no) or [], no.value.values):
        if blocos.texto_constante(valor) == nome:
            cortes.append((primeira, ultima))
    trocas += _trocas_nas_zonas(arvore, linhas, lambda _, texto: "".join("#" if letra in portas else letra
                                                                          for letra in texto), menos=nome)

    interior = len(portas) > 0
    aviso = ('Apaguei o edifício "' if interior else 'Apaguei a zona "') + str(nome) + '".'
    if interior:
        aviso = aviso + " Cá fora, onde era a porta ficou parede: as paredes dele continuam lá, podes tirá-las."
    perdidos = [letra for letra in "123456789" if letra in letras and mundo.e_treinador(letra)]
    if perdidos:
        aviso = (aviso + " Os treinadores que lá estavam ficaram sem sítio: escreve o " + " e o ".join(perdidos)
                 + " noutra zona.")
    return base._aplicar(linhas, cortes, trocas), aviso


class _Bocado:
    # Um bocado de uma linha do codigo, do inicio de uma coisa ao fim de outra.
    def __init__(self, inicio, fim):
        self.lineno, self.col_offset = inicio.lineno, inicio.col_offset
        self.end_lineno, self.end_col_offset = fim.end_lineno, fim.end_col_offset


def _apagar_ataque(fonte, escolha):
    # Como na Bicharada, e o ataque sai tambem do "aprende" dos bichos.
    arvore = ast.parse(fonte)
    partes = base._fichas(blocos.instrucao(arvore, "ATAQUES"))
    numero = escolha.partition(":")[2]
    if not numero.isdigit() or int(numero) >= len(partes):
        return base.apagar(fonte, escolha)
    nome = partes[int(numero)][0]
    linhas = fonte.split("\n")
    cortes, trocas, donos = [], [], []
    for bicho, ficha, _, _ in base._fichas(blocos.instrucao(arvore, "BICHOS")):
        aprende = base._no_da_chave(ficha, "aprende") if isinstance(ficha, ast.Dict) else None
        if not isinstance(aprende, ast.Dict):
            continue
        for chave, valor in zip(aprende.keys, aprende.values):
            if blocos.texto_constante(chave) == nome and base._tirar_da_lista(linhas, _Bocado(chave, valor), cortes, trocas):
                donos.append(str(bicho))
    nova, aviso = base.apagar(base._aplicar(linhas, cortes, trocas), escolha)
    if donos:
        nomes = donos[0] if len(donos) == 1 else ", ".join(donos[:-1]) + " e " + donos[-1]
        aviso = aviso + " Também deixou de estar no «aprende» de: " + nomes + "."
    return nova, aviso


def _tipo_escrito(fonte, numero):
    # O nome do tipo que esta aberto, ou None.
    cores = base._fichas(blocos.instrucao(ast.parse(fonte), "CORES_TIPO"))
    return cores[int(numero)][0] if numero.isdigit() and int(numero) < len(cores) else None


def _tipo_nos_blocos(fonte, antigo, novo):
    # Os blocos dizem os tipos dos bichos que deles saltam ("bichos"): quando
    # um tipo muda de nome, ou e apagado (e passa a ser o "novo"), muda la
    # tambem. Devolve o ficheiro e os nomes dos blocos em que mexeu.
    arvore = ast.parse(fonte)
    linhas = fonte.split("\n")
    trocas, mexidos = [], []
    for letra, ficha, _, _ in base._fichas(blocos.instrucao(arvore, "BLOCOS")):
        no = base._no_da_chave(ficha, "bichos") if isinstance(ficha, ast.Dict) else None
        if not isinstance(no, ast.List) or no.lineno != no.end_lineno:
            continue
        tipos = [blocos.texto_constante(este) for este in no.elts]
        if antigo not in tipos or None in tipos:
            continue
        novos = []
        for este in tipos:
            este = novo if este == antigo else este
            if este not in novos:
                novos.append(este)
        base._trocar_no(linhas, no, "[" + ", ".join('"' + este + '"' for este in novos) + "]", trocas)
        mexidos.append(blocos.valor_da_chave(ficha, "nome") or str(letra))
    return base._aplicar(linhas, [], trocas), mexidos


def renomear(fonte, escolha, nome):
    # Como na Bicharada, mais as zonas: o nome muda nas ZONAS, no MUNDO e nas
    # PORTAS que davam para ela. E um tipo muda tambem nos blocos.
    tipo, _, numero = escolha.partition(":")
    if tipo == "tipo":
        antigo = _tipo_escrito(fonte, numero)
        fonte, escolha, aviso = base.renomear(fonte, escolha, nome)
        novo = _tipo_escrito(fonte, numero)
        if antigo is not None and novo is not None and novo != antigo:
            fonte, mexidos = _tipo_nos_blocos(fonte, antigo, novo)
            if mexidos:
                aviso = aviso + " Mudei-o também nos blocos de onde saltam bichos desse tipo (" + ", ".join(mexidos) + ")."
        return fonte, escolha, aviso
    if tipo != "zona":
        return base.renomear(fonte, escolha, nome)
    arvore = ast.parse(fonte)
    partes = _zonas_escritas(arvore)
    if not numero.isdigit() or int(numero) >= len(partes):
        raise ValueError("a isso não se pode mudar o nome.")
    antigo = partes[int(numero)][0]
    nome = base._nome_escrito(nome)
    if nome == antigo:
        raise ValueError("esse já é o nome dela.")
    if nome in [parte[0] for parte in partes]:
        raise ValueError('já há outra zona com o nome "' + nome + '".')
    linhas = fonte.split("\n")
    trocas = []
    base._trocar_no(linhas, blocos.instrucao(arvore, "ZONAS").value.keys[int(numero)], '"' + nome + '"', trocas)
    onde = []
    for fila in blocos.instrucao(arvore, "MUNDO").value.elts:
        for este in fila.elts if isinstance(fila, ast.List) else []:
            if blocos.texto_constante(este) == antigo and este.lineno == este.end_lineno:
                base._trocar_no(linhas, este, '"' + nome + '"', trocas)
                onde = ["no MUNDO"]
    portas = blocos.instrucao(arvore, "PORTAS")
    for valor in portas.value.values if portas is not None and isinstance(portas.value, ast.Dict) else []:
        if blocos.texto_constante(valor) == antigo and valor.lineno == valor.end_lineno:
            base._trocar_no(linhas, valor, '"' + nome + '"', trocas)
            onde.append("nas PORTAS")
    aviso = '"' + str(antigo) + '" passou a chamar-se "' + nome + '".'
    if onde:
        aviso = aviso + " Mudei o nome também " + " e ".join(onde) + "."
    return base._aplicar(linhas, [], trocas), escolha, aviso


def apagar(fonte, escolha):
    tipo = escolha.partition(":")[0]
    if tipo == "zona":
        return _apagar_zona(fonte, escolha)
    if tipo == "bloco":
        return _apagar_bloco(fonte, escolha)
    if tipo == "tipo":
        antigo = _tipo_escrito(fonte, escolha.partition(":")[2])
        de_todos = base._tipo_de_todos(ast.parse(fonte))
        fonte, aviso = base.apagar(fonte, escolha)
        if antigo is not None:
            fonte, mexidos = _tipo_nos_blocos(fonte, antigo, de_todos)
            if mexidos:
                aviso = aviso + " Nos blocos de onde saltavam bichos desse tipo (" + ", ".join(mexidos) + ') ficou "' + de_todos + '".'
        return fonte, aviso
    if tipo == "ataque":
        return _apagar_ataque(fonte, escolha)
    if tipo == "treinador":
        return _apagar_treinador(fonte, escolha)
    return base.apagar(fonte, escolha)


# =====================================================================
#                 VER SE O QUE FOI ESCRITO FAZ SENTIDO
# =====================================================================

def _ver_funcoes(ns, problemas):
    # Como no bicharada.py: o jogo chama cada funcao pelo nome e da-lhe
    # sempre as mesmas coisas.
    for tipo in FUNCOES:
        for nome in FUNCOES[tipo]:
            esperado = FUNCOES[tipo][nome][1]
            funcao = ns.get(nome)
            como = "def " + nome + "(" + ", ".join(esperado) + "):"
            if not inspect.isfunction(funcao):
                problemas.append('"' + nome + '" tem de ser uma função. A primeira linha é: ' + como)
            elif len(inspect.signature(funcao).parameters) != len(esperado):
                problemas.append("A função " + nome + " tem de receber "
                                 + (", ".join(esperado) if esperado else "nada, só ( )") + ", nem mais nem menos. "
                                 "A primeira linha tem de ser: " + como)


def _ver_mundo(ns, treinadores, aberto, problemas, avisos, zona_aberta=False):
    # zona_aberta: e uma zona (e nao o MUNDO ou as PORTAS) que esta aberta.
    # aberto: e uma zona, o MUNDO ou as PORTAS que estao abertos no editor?
    # So nesse caso se dao os avisos, para nao aparecerem cada vez que se
    # muda outra coisa.
    zonas, mundo, portas = ns.get("ZONAS"), ns.get("MUNDO"), ns.get("PORTAS")
    if not isinstance(zonas, dict) or len(zonas) == 0:
        problemas.append("ZONAS tem de ter pelo menos uma zona, entre { }.")
        return
    for nome, filas in zonas.items():
        if not isinstance(nome, str):
            problemas.append("O nome de uma zona tem de estar entre aspas.")
            return
        if not isinstance(filas, list) or len(filas) == 0:
            problemas.append('A zona "' + nome + '" tem de ser uma lista de linhas, entre [ ].')
            return
        if not all(isinstance(fila, str) for fila in filas):
            problemas.append('Na zona "' + nome + '", cada linha tem de estar entre aspas e acabar com uma vírgula.')
            return
    if not isinstance(mundo, list) or len(mundo) == 0 or not all(isinstance(fila, list) for fila in mundo):
        problemas.append('O MUNDO é uma lista de filas, e cada fila é uma lista de nomes: [["aldeia", "ribeira"]].')
        return
    if not all(isinstance(nome, str) for fila in mundo for nome in fila):
        problemas.append("No MUNDO, o nome de cada zona tem de estar entre aspas.")
        return
    if not isinstance(portas, dict):
        problemas.append('PORTAS tem de estar entre { }, com uma letra para cada edifício: {"M": "mercearia"}.')
        return
    for letra, nome in portas.items():
        if not isinstance(letra, str) or len(letra) != 1 or not isinstance(nome, str):
            problemas.append('Em PORTAS, cada porta é uma letra só e o nome de uma zona: "M": "mercearia".')
            return
        if letra in CONHECIDAS or (isinstance(ns.get("BLOCOS"), dict) and letra in ns["BLOCOS"]):
            problemas.append('Em PORTAS, a letra "' + letra + '" já quer dizer outra coisa no mapa. Escolhe outra.')
            return
    if not aberto:
        return

    quantos = len(treinadores) if isinstance(treinadores, list) else 0
    os_blocos = ns.get("BLOCOS") if isinstance(ns.get("BLOCOS"), dict) else {}
    este = Mundo(zonas, mundo, portas, quantos, os_blocos=os_blocos)
    no_mundo = este.no_mundo()
    interiores = [nome for nome in portas.values() if nome in zonas]
    tudo = "".join("".join(zonas[nome]) for nome in zonas)

    # Com uma zona aberta, um nome que o MUNDO ou as PORTAS usam e que
    # deixou de existir quer dizer que lhe mudaram o nome a mao: nao entra, e
    # diz-se como se faz.
    orfas = [nome for fila in mundo for nome in fila if nome != "" and nome not in zonas]
    orfas += [nome for nome in portas.values() if nome not in zonas and nome not in orfas]
    if zona_aberta and orfas:
        problemas.append('O MUNDO ou as PORTAS ainda falam de "' + orfas[0] + '", que deixou de existir. Se lhe '
                         "querias mudar o nome, deixa o nome antigo no código e usa o botão «Mudar o nome», que o "
                         "muda em todo o lado.")
        return
    for fila in mundo:
        for nome in fila:
            if nome != "" and nome not in zonas:
                avisos.append('O MUNDO chama por "' + nome + '", que não existe em ZONAS: fica um buraco.'
                              + base._parecido(nome, list(zonas)))
    for nome in zonas:
        if nome not in no_mundo and nome not in interiores:
            avisos.append('A zona "' + nome + '" não está no MUNDO nem tem porta: não se chega lá.')
        if len(zonas[nome]) > ZONA[1] or max(len(fila) for fila in zonas[nome]) > ZONA[0]:
            avisos.append('A zona "' + nome + '" é grande demais: só cabem ' + str(ZONA[0]) + " letras por linha e "
                          + str(ZONA[1]) + " linhas. O resto não aparece. (Falta uma vírgula no fim de uma linha?)")
    for letra, nome in portas.items():
        if nome not in zonas:
            avisos.append('A porta "' + letra + '" leva a "' + nome + '", que não existe em ZONAS.'
                          + base._parecido(nome, list(zonas)))
            continue
        if letra not in "".join(zonas[nome]):
            avisos.append('Falta a porta "' + letra + '" dentro de "' + nome + '": é por ela que se sai.')
        if este.encontrar(letra, [outra for outra in zonas if outra != nome]) is None:
            avisos.append('A porta "' + letra + '" não está em nenhuma zona cá fora: não se entra em "' + nome + '".')

    if "P" not in tudo:
        avisos.append("Falta o P, a partida: assim começas no primeiro bocado de relva.")
    elif tudo.count("P") > 1:
        avisos.append("Há mais do que um P: começas no primeiro.")
    if not any(este.faz(letra) == "cura" for letra in set(tudo)):
        avisos.append("Não há casa da avó (H) em nenhuma zona: não tens onde curar a equipa.")
    if not any(este.erva(letra) for letra in set(tudo)):
        avisos.append("Não há erva alta (e) em nenhuma zona: não salta nenhum bicho à solta.")

    partida = este.partida()
    passos, _, contra = este.andar(partida) if partida is not None else ({}, {}, {})
    chega_se = [este.letra(*sitio) for sitio in contra]
    onde_se_chega = [sitio[0] for sitio in passos]
    longe = ['"' + nome + '"' for nome in no_mundo + interiores if nome not in onde_se_chega]
    if len(longe) == 1:
        avisos.append("Não se chega a pé à zona " + longe[0] + ": as saídas dela não batem certo com as das "
                      "zonas do lado, ou há árvores ou água no caminho.")
    elif longe:
        avisos.append("Não se chega a pé a " + str(len(longe)) + " zonas (" + ", ".join(longe) + "): as saídas "
                      "não batem certo com as das zonas do lado, ou há árvores ou água no caminho.")
    no_mapa = 0
    for numero in range(1, min(quantos, 9) + 1):
        ficha = treinadores[numero - 1]
        nome = ficha.get("nome") if isinstance(ficha, dict) else None
        nome = nome if isinstance(nome, str) else "O treinador " + str(numero)
        if str(numero) not in tudo:
            avisos.append(nome + " não está em nenhuma zona: escreve um " + str(numero) + " onde o quiseres.")
            continue
        no_mapa = no_mapa + 1
        if str(numero) not in chega_se:
            avisos.append("Não se chega a pé a " + nome + " (o " + str(numero) + "): há árvores, água ou paredes "
                          "no caminho.")
    if no_mapa == 0:
        avisos.append("Sem treinadores no mapa, o jogo nunca acaba.")
    for numero in range(quantos + 1, 10):
        if str(numero) in tudo:
            avisos.append("O " + str(numero) + " não é nenhum treinador (só há " + str(quantos) + "): fica relva.")
    for faz, texto in (("cura", "Não se chega a pé a nenhuma casa da avó."),
                       ("loja", "Não se chega a pé ao balcão da loja: há uma parede ou um móvel à frente dele.")):
        letras = [letra for letra in set(tudo) if este.faz(letra) == faz]
        if letras and not any(letra in chega_se for letra in letras):
            avisos.append(texto)
    # As letras de fora la dentro, e as de dentro ca fora.
    for nome in zonas:
        letras = set("".join(zonas[nome]))
        de_fora = [letra for letra in os_blocos if isinstance(os_blocos[letra], dict) and not _serve(os_blocos[letra], True)]
        de_dentro = [letra for letra in os_blocos if isinstance(os_blocos[letra], dict) and not _serve(os_blocos[letra], False)]
        if nome in interiores:
            blocos_errados = sorted(str(os_blocos[letra].get("nome", letra)) for letra in letras & set(de_fora))
            if blocos_errados:
                avisos.append('Dentro de "' + nome + '" há blocos que são para cá de fora (' + ", ".join(blocos_errados)
                              + "). Se os queres lá dentro, marca neles a caixa «É para dentro dos edifícios».")
        else:
            blocos_errados = sorted(str(os_blocos[letra].get("nome", letra)) for letra in letras & set(de_dentro))
            if blocos_errados:
                avisos.append('Na zona "' + nome + '" há blocos que são para dentro dos edifícios ('
                              + ", ".join(blocos_errados) + ").")
    novas = sorted(set(tudo) - set(CONHECIDAS) - set(portas) - set(os_blocos))
    if novas:
        avisos.append("Letras que o jogo não conhece: " + " ".join(novas) + ". Ficam chão. Para serem outra coisa, "
                      "faz um bloco com essa letra, em Blocos.")


def _ver_falas(falas, quem, chave, problemas):
    # As falas de um treinador: uma lista de textos e de perguntas.
    exemplo = ' Uma pergunta é assim: {"pergunta": "Queres lutar?", "respostas": {"Sim": "Vamos!", "Não": "Adeus."}}.'
    if not isinstance(falas, list):
        problemas.append(quem + ': as "' + chave + '" são uma lista de textos, entre [ ].')
        return
    for fala in falas:
        if isinstance(fala, str):
            continue
        if not isinstance(fala, dict):
            problemas.append(quem + ': nas "' + chave + '", cada fala é um texto entre aspas, ou uma pergunta.' + exemplo)
            return
        respostas = fala.get("respostas")
        if not isinstance(fala.get("pergunta"), str) or not isinstance(respostas, dict) or len(respostas) == 0:
            problemas.append(quem + ': uma pergunta precisa de "pergunta" e de "respostas".' + exemplo)
            return
        for resposta, texto in respostas.items():
            if not isinstance(resposta, str) or not isinstance(texto, str):
                problemas.append(quem + ": cada resposta é um texto, e à frente dela vai o que ele diz, também um texto.")
                return
        if "sem_luta" in fala and fala["sem_luta"] not in respostas:
            problemas.append(quem + ': o "sem_luta" tem de ser uma das respostas: ' + ", ".join(respostas) + ".")


def _ver_conversas(ns, treinadores, aberto, problemas, avisos):
    # aberto: e um treinador que esta aberto no editor?
    da_rede = False
    for ficha in treinadores if isinstance(treinadores, list) else []:
        if not isinstance(ficha, dict):
            continue
        quem = ficha.get("nome") if isinstance(ficha.get("nome"), str) else "Um treinador"
        if "imagem" in ficha:
            _ver_imagem(ficha, quem, "imagem", ns, problemas)
        for chave in ("falas", "falas_depois", "falas_rede"):
            if chave in ficha:
                _ver_falas(ficha[chave], quem, chave, problemas)
        if "da_rede" in ficha and not isinstance(ficha["da_rede"], bool):
            problemas.append(quem + ': o "da_rede" é True ou False, sem aspas.')
        da_rede = da_rede or ficha.get("da_rede") is True
    comeca_com = ns.get("REDES_INICIAIS")
    if aberto and not da_rede and not (base._numero(comeca_com) and comeca_com > 0):
        avisos.append("Nenhum treinador dá a rede no início: sem rede não se apanha o primeiro bicho, "
                      "e o jogo não anda. Marca a caixa num deles.")


def _ver_aprende(ns, bichos, aberto, problemas, avisos):
    # aberto: e a ficha de um bicho que esta aberta no editor? "bichos" e o
    # que esta escrito no ficheiro.
    ataques = ns.get("ATAQUES") if isinstance(ns.get("ATAQUES"), dict) else {}
    for nome, ficha in bichos.items() if isinstance(bichos, dict) else []:
        if isinstance(ficha, dict) and "tamanho" in ficha:
            tamanho = ficha["tamanho"]
            if isinstance(tamanho, bool) or not isinstance(tamanho, (int, float)) or tamanho < 0.3 or tamanho > 2.5:
                problemas.append(str(nome) + ': o "tamanho" é um número entre 0.3 e 2.5, sem aspas: 1.0 é o normal, '
                                 "1.5 é uma vez e meia maior.")
        if not isinstance(ficha, dict) or "aprende" not in ficha:
            continue
        aprende = ficha["aprende"]
        if not isinstance(aprende, dict):
            problemas.append(str(nome) + ': o "aprende" é assim: {"Estalido": 9} (o ataque, e o nível em que o aprende).')
            continue
        for ataque, nivel in aprende.items():
            if not isinstance(nivel, int) or isinstance(nivel, bool) or nivel < 1 or nivel > 99:
                problemas.append(str(nome) + ': em "aprende", o nível de "' + str(ataque) + '" é um número inteiro, de 1 a 99.')
            elif ataque not in ataques:
                if aberto:
                    problemas.append(str(nome) + ': o ataque "' + str(ataque) + '", em "aprende", não existe em ATAQUES.'
                                     + base._parecido(str(ataque), list(ataques)))
                else:
                    avisos.append(str(nome) + ' ainda aprende o ataque "' + str(ataque) + '", que já não existe. '
                                  "Muda o nome também na ficha desse bicho, senão o jogo pára.")
        # (Tambem os que se aprendem tem de ser do tipo do bicho, ou normais.)
        base._ver_tipo_dos_ataques(str(nome), ficha, list(aprende), ' em "aprende"', ns, aberto, problemas, avisos)


def _ver_blocos(ns, problemas, avisos):
    os_blocos = ns.get("BLOCOS")
    if not isinstance(os_blocos, dict):
        problemas.append("BLOCOS tem de estar entre { }.")
        return
    portas = ns.get("PORTAS") if isinstance(ns.get("PORTAS"), dict) else {}
    tipos = ns.get("CORES_TIPO") if isinstance(ns.get("CORES_TIPO"), dict) else {}
    for letra, ficha in os_blocos.items():
        if not isinstance(letra, str) or len(letra) != 1:
            problemas.append("Em BLOCOS, cada bloco é uma letra só, entre aspas.")
            continue
        if not isinstance(ficha, dict):
            problemas.append('O bloco "' + letra + '" tem de ter a ficha entre { }.')
            continue
        quem = "O bloco " + str(ficha.get("nome", letra)) if isinstance(ficha.get("nome"), str) else 'O bloco "' + letra + '"'
        if letra in CONHECIDAS or letra in portas:
            problemas.append(quem + ': a letra "' + letra + '" já quer dizer outra coisa no mapa. Escolhe outra.')
        base._ver_texto(ficha, quem, "nome", problemas)
        base._ver_cor(ficha, quem, "cor", problemas)
        if not isinstance(ficha.get("passa"), bool):
            problemas.append(quem + ': o "passa" é True (anda-se por cima) ou False (tapa o caminho), sem aspas.')
        for chave in ("erva", "dentro"):
            if chave in ficha and not isinstance(ficha[chave], bool):
                problemas.append(quem + ': o "' + chave + '" é True ou False, sem aspas.')
        if "faz" in ficha and ficha["faz"] not in ("cura", "loja"):
            problemas.append(quem + ': o "faz" é "cura" (cura a equipa) ou "loja" (abre a loja). Se não faz nada, '
                             "apaga essa linha.")
        if "sempre" in ficha and not isinstance(ficha["sempre"], bool):
            problemas.append(quem + ': o "sempre" é True ou False, sem aspas.')
        if "desenho" in ficha and not isinstance(ficha["desenho"], str):
            problemas.append(quem + ': o "desenho" é um nome entre aspas: "arvore", "mesa"...')
        if ficha.get("erva") is True and ficha.get("passa") is False:
            avisos.append(quem + " tem erva mas não se passa por ele: nunca vai saltar de lá nenhum bicho.")
        por_baixo = ficha.get("por_baixo", ".")
        if not isinstance(por_baixo, str) or len(por_baixo) != 1:
            problemas.append(quem + ': o "por_baixo" é uma letra só: "." para relva, "_" para soalho, a de outro '
                             'bloco, ou "?" para o chão que ele tiver ao lado.')
        if "imagem" in ficha:
            _ver_imagem(ficha, quem, "imagem", ns, problemas)
        if "bichos" in ficha:
            if not isinstance(ficha["bichos"], list) or not all(isinstance(tipo, str) for tipo in ficha["bichos"]):
                problemas.append(quem + ': os "bichos" são uma lista de tipos, entre [ ]: ["agua", "normal"].')
            else:
                for tipo in ficha["bichos"]:
                    if tipos and tipo not in tipos:
                        problemas.append(quem + ': em "bichos" está o tipo "' + tipo + '", que não existe. Os tipos '
                                         "que há: " + ", ".join(str(este) for este in tipos) + "."
                                         + base._parecido(tipo, list(tipos)))


def _ver_loja_e_jogador(ns, problemas, avisos):
    loja = ns.get("LOJA")
    if not isinstance(loja, dict):
        problemas.append('A LOJA tem de estar entre { }: {"Sopa": {"preco": 15}}.')
    else:
        for nome, ficha in loja.items():
            if not isinstance(nome, str) or not isinstance(ficha, dict):
                problemas.append('Na LOJA, cada coisa é um nome entre aspas e a ficha dela: "Sopa": {"preco": 15}.')
                break
            base._ver_numero(ficha, "LOJA, " + nome, "preco", 0, 9999, problemas)
        if len(loja) > 6:
            avisos.append("Na loja só cabem 6 coisas no ecrã: as outras ficam de fora.")
    jogador = ns.get("JOGADOR")
    if not isinstance(jogador, dict):
        problemas.append("O JOGADOR tem de estar entre { }.")
        return
    base._ver_cor(jogador, "JOGADOR", "cor", problemas)
    for chave in ("imagem", "imagem_costas", "imagem_lado"):
        if chave in jogador:
            _ver_imagem(jogador, "JOGADOR", chave, ns, problemas)
    for nome, ficha in ns["BICHOS"].items() if isinstance(ns.get("BICHOS"), dict) else []:
        if isinstance(ficha, dict) and "imagem_costas" in ficha:
            _ver_imagem(ficha, str(nome), "imagem_costas", ns, problemas)


def _ver_imagem(ficha, quem, chave, ns, problemas):
    # Como no bicharada.py, para uma chave qualquer: se o ficheiro existe mas
    # nao e uma imagem, o jogo para ao desenhar.
    nome = ficha[chave]
    if not isinstance(nome, str) or nome.strip() == "":
        problemas.append(quem + ': a "' + chave + '" é o nome de um ficheiro, entre aspas, como "bicho.png".')
        return
    try:
        caminho = ns["PASTA_ASSETS"] / "imagens" / nome
        if caminho.exists():
            ns["pygame"].image.load(caminho)
    except Exception:
        problemas.append(quem + ': não consegui abrir a imagem "' + nome + '". É mesmo uma imagem (PNG)?')


def _sem_deixar_marcas(ns, funcao):
    # Corre uma funcao do jogo so para ver o que ela responde: o que ela
    # disser, e o que guardar na memoria, nao fica la.
    mensagens = list(ns["mensagens"])
    memoria = dict(ns["memoria"])
    fase = ns["fase"]
    aviso = ns["aviso"]
    try:
        return funcao()
    finally:
        ns["mensagens"][:] = mensagens
        ns["memoria"].clear()
        ns["memoria"].update(memoria)
        ns["fase"] = fase
        ns["aviso"] = aviso


def _e_um_bicho(ns, valor):
    return (isinstance(valor, dict) and valor.get("nome") in ns["BICHOS"]
            and base._numero(valor.get("vida")) and base._numero(valor.get("vida_max"))
            and base._numero(valor.get("nivel")))


def _experimentar(ns, regra, problemas):
    # Uma regra tem de devolver uma resposta que o jogo perceba.
    if regra == "pode_andar":
        for letra in list(ns["BLOCOS"]) + ["?"]:
            _sem_deixar_marcas(ns, lambda: ns["pode_andar"](letra))
    elif regra == "ha_batalha_na_erva":
        _sem_deixar_marcas(ns, ns["ha_batalha_na_erva"])
    elif regra == "escolher_bicho_selvagem":
        valor = _sem_deixar_marcas(ns, ns["escolher_bicho_selvagem"])
        if not _e_um_bicho(ns, valor):
            problemas.append("escolher_bicho_selvagem tem de devolver um bicho feito com criar_bicho(nome, nivel). "
                             "Devolveu " + repr(valor)[:60] + ".")
    elif regra == "consegue_apanhar":
        modelo = ns["criar_bicho"](list(ns["BICHOS"])[0], 3)
        _sem_deixar_marcas(ns, lambda: ns["consegue_apanhar"](modelo))
    elif regra == "premio_da_batalha":
        equipa = [ns["criar_bicho"](list(ns["BICHOS"])[0], 3)]
        for selvagem in (True, False):
            valor = _sem_deixar_marcas(ns, lambda: ns["premio_da_batalha"](equipa, selvagem))
            if not base._numero(valor) or valor < 0:
                problemas.append("premio_da_batalha tem de devolver um número de moedas (zero ou mais). Devolveu "
                                 + repr(valor)[:40] + ".")
                break


# =====================================================================
#                              O PALCO
# =====================================================================

class Palco(base.Palco):

    def __init__(self, escolha):
        super().__init__(escolha)
        # no_mapa: o palco e o mapa, e nao uma batalha.
        self.dados = self.tipo in ("zona", "mundo", "portas", "loja", "jogador", "bloco")     # anda so a crianca
        self.de_cima = self.tipo in ("mundo", "portas")           # ve-se o mundo todo, pequeno
        self.no_mapa = self.dados or self.regra in DO_MAPA
        # Um treinador abre num palco so dele: fala e depois luta (ve as cenas).
        self.falador = self.tipo == "treinador"
        self.cena = None
        self.pausa = 0
        self.ultima_compra = ""
        self.caminho = []            # os passos que o boneco vai dar: [(de onde, o passo), ...]
        self.voltas = 0
        self.relogio = 0
        self.miniatura = None        # o desenho do mundo todo, feito uma vez

    def verificar(self, ns):
        problemas, avisos = super().verificar(ns)
        _ver_funcoes(ns, problemas)
        _ver_mundo(ns, self.ler(ns, "TREINADORES"), self.tipo in ("zona", "mundo", "portas"), problemas, avisos,
                   self.tipo == "zona")
        _ver_conversas(ns, self.ler(ns, "TREINADORES"), self.falador, problemas, avisos)
        _ver_aprende(ns, self.ler(ns, "BICHOS"), self.tipo == "bicho", problemas, avisos)
        _ver_loja_e_jogador(ns, problemas, avisos)
        _ver_blocos(ns, problemas, avisos)
        if self.regra in REGRAS and self.preparado and not problemas:
            _experimentar(ns, self.regra, problemas)
        base._resumir_avisos_de_tipo(avisos)
        return problemas, avisos

    # --- Preparar e voltar a preparar ---

    def preparar(self, ns, pygame):
        if not self.no_mapa and not self.falador:
            super().preparar(ns, pygame)
            return
        self.letra = pygame.font.SysFont(None, 22)
        self.letra_pequena = pygame.font.SysFont(None, 18)
        self.preparado = True
        self.arrumar(ns)
        if self.falador:
            self.comecar_cena(ns, self.cenas(ns)[0], None)
        else:
            self.passeio(ns, None)

    def ao_mudar(self, ns):
        if self.falador:
            if self.preparado:
                self.arrumar(ns)
                self.comecar_cena(ns, self.cenas(ns)[0], None)
            return
        if not self.no_mapa:
            super().ao_mudar(ns)
            return
        if not self.preparado:
            return
        self.caminho = []
        self.relogio = 0
        self.miniatura = None
        if self.dados:
            # O mapa mudou: o boneco podia ter ficado dentro de uma arvore.
            self.arrumar(ns)
            self.passeio(ns, None)
        else:
            ns["memoria"].clear()      # como se o jogo recomecasse
            # Uma funcao do mapa so corre no mapa: se o boneco estava a meio
            # de uma batalha ou de uma conversa, volta ja para la. Senao, o
            # codigo novo era dado por bom sem nunca ter corrido.
            if ns["estado"] != "mundo" and self.regra not in COM_REDE and self.regra != "ao_responder":
                ns["voltar_ao_mundo"]()
            self.redesenhar = True

    def arrumar(self, ns):
        super().arrumar(ns)
        # (Na versao dos BICHOS que o palco poe no jogo, o "aprende" fica so
        # com os ataques que existem: um nome antigo fazia o jogo parar.)
        for ficha in ns["BICHOS"].values():
            if isinstance(ficha.get("aprende"), dict):
                ficha["aprende"] = {ataque: nivel for ataque, nivel in ficha["aprende"].items()
                                    if ataque in ns["ATAQUES"] and isinstance(nivel, int)}
        if not self.no_mapa and not self.falador:
            return
        # O palco das batalhas fica so com um treinador. No mapa estao todos,
        # cada um sem os bichos que ja nao existem.
        bichos = ns["BICHOS"]
        todos = []
        for ficha in self.ler(ns, "TREINADORES"):
            membros = [membro for membro in ficha["equipa"] if membro["bicho"] in bichos]
            if len(membros) == 0:
                membros = [{"bicho": list(bichos)[0], "nivel": self.nivel}]
            ficha = dict(ficha)
            ficha["equipa"] = membros
            todos.append(ficha)
        self.por(ns, "TREINADORES", todos)

    def batalha(self, ns, noticia):
        # No palco das batalhas e sempre contra um treinador, e a mochila
        # vem cheia (no jogo, as sopas so se enchem em casa da avo).
        ns["batalha_selvagem"] = False
        ns["sopas"] = ns["SOPAS_NA_MOCHILA"]
        super().batalha(ns, noticia)

    def mundo(self, ns):
        # O mundo como esta agora no jogo, com a regra de andar que la estiver.
        return Mundo(ns["ZONAS"], ns["MUNDO"], ns["PORTAS"], len(ns["TREINADORES"]),
                     lambda letra: ns["pode_andar"](letra), ns.get("BLOCOS"))

    def passeio(self, ns, noticia):
        # Poe o jogo no mapa, com as funcoes do proprio jogo: na partida ou,
        # se e uma zona que esta aberta, dentro dessa zona.
        equipa = []
        for nome in self.equipa:
            equipa.append(ns["criar_bicho"](nome, self.nivel))
        ns["minha_equipa"] = equipa
        ns["comecar_mundo"]()
        # (Sem a caixa que explica as teclas: tapava o fundo do mapa.)
        ns["aviso"] = noticia or ""
        # No palco anda-se como a meio do jogo: com bichos, redes e moedas.
        ns["redes"] = 5
        ns["moedas"] = 100
        if self.tipo == "loja":
            ns["abrir_loja"]()
        nome = None
        if self.tipo == "zona":
            nomes = list(ns["ZONAS"])
            nome = nomes[min(self.numero, len(nomes) - 1)]
        elif self.tipo == "bloco" and len(ns["BLOCOS"]) > 0:
            # Um bloco abre numa zona onde ele esteja (se estiver nalguma).
            letra = list(ns["BLOCOS"])[min(self.numero, len(ns["BLOCOS"]) - 1)]
            com_ele = [zona for zona in ns["ZONAS"] if letra in "".join(ns["ZONAS"][zona])]
            nome = com_ele[0] if com_ele else None
        if nome is not None:
            if ns["jogador"]["zona"] != nome:
                este = self.mundo(ns)
                sitio = None
                for letra in "._e":
                    sitio = sitio or este.encontrar(letra, [nome])
                for letra, ficha in ns["BLOCOS"].items():        # ou um bloco por onde se anda (a areia)
                    if sitio is None and isinstance(ficha, dict) and ficha.get("passa") is True:
                        sitio = este.encontrar(letra, [nome])
                sitio = sitio or (nome, 1, 1)
                ns["ir_para"](*sitio)
                for chave in ("zona", "coluna", "linha"):
                    ns["descanso"][chave] = ns["jogador"][chave]
        self.caminho = []
        self.redesenhar = True

    # --- O treinador que fala, e depois luta ---
    # Um treinador aberto mostra-se em cenas, umas a seguir as outras, com as
    # funcoes do jogo: (se e ele que da a rede) a conversa em que a da, a
    # quem ainda nao tem bichos; depois as falas e a luta; e, ganha a luta,
    # as falas de depois. E volta ao principio.

    def cenas(self, ns):
        ficha = ns["TREINADORES"][self.quem(ns)]
        if ficha.get("da_rede") is True:
            return ["rede", "luta", "depois"]
        return ["luta", "depois"]

    def quem(self, ns):
        return min(self.numero, len(ns["TREINADORES"]) - 1)

    def comecar_cena(self, ns, cena, noticia):
        numero = self.quem(ns)
        self.cena = cena
        self.pausa = 0
        self.espera = 110
        self.voltas = self.voltas + 1
        equipa = []
        for nome in self.equipa:
            equipa.append(ns["criar_bicho"](nome, self.nivel))
        ns["minha_equipa"] = equipa
        ns["comecar_mundo"]()
        ns["aviso"] = noticia or ""
        ns["sopas"] = ns["SOPAS_NA_MOCHILA"]
        # O boneco fica ao lado do treinador, se ele estiver no mapa.
        este = self.mundo(ns)
        sitio = este.encontrar(str(numero + 1), list(ns["ZONAS"])) if numero < 9 else None
        if sitio is not None:
            for passo, olha in zip(PASSOS, ("cima", "baixo", "esquerda", "direita")):
                vizinho = este.passo(sitio, passo[0], passo[1])
                if vizinho[0] != "" and este.livre(este.letra(*vizinho)):
                    ns["ir_para"](*vizinho)
                    ns["jogador"]["olha"] = olha
                    break
        if cena == "rede":
            ns["minha_equipa"] = []
            ns["redes"] = 0
        elif cena == "depois":
            ns["treinadores_vencidos"].append(numero)
        ns["desafiar"](numero)
        self.redesenhar = True

    def quadro_do_falador(self, ns, pygame):
        if not self.preparado:
            self.preparar(ns, pygame)
        teclas = pygame.key.get_pressed()
        for tecla in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_RETURN,
                      pygame.K_SPACE, pygame.K_ESCAPE, pygame.K_BACKSPACE):
            if teclas[tecla]:
                self.maos = 300
        if self.maos > 0:
            self.maos = self.maos - 1

        cenas = self.cenas(ns)
        estado = ns["estado"]
        if estado == "conversa":
            # As falas passam sozinhas, devagar, se a crianca nao as passar.
            self.pausa = 0
            self.espera = self.espera - 1
            if self.espera <= 0 and self.maos == 0:
                fala = ns["conversa"][0]
                if not isinstance(fala, str):
                    ns["cursor"] = self.voltas % len(fala["respostas"])     # ora uma resposta, ora outra
                ns["tecla_na_conversa"](pygame.K_RETURN)
                self.espera = 110
                self.redesenhar = True
        elif estado == "derrota":
            self.comecar_cena(ns, "luta", "A tua equipa desmaiou... Vamos outra vez!")
        elif estado != "batalha":
            # A cena acabou (ou a luta, ou a conversa sem luta): passa-se a seguinte.
            self.pausa = self.pausa + 1
            if self.pausa > 90 and self.maos == 0:
                seguinte = cenas[(cenas.index(self.cena) + 1) % len(cenas)] if self.cena in cenas else cenas[0]
                if seguinte == "depois" and self.quem(ns) not in ns["treinadores_vencidos"]:
                    seguinte = cenas[0]          # nao houve luta: nao ha "depois"
                self.comecar_cena(ns, seguinte, None)

        estado = ns["estado"]
        if self.redesenhar:
            if estado == "conversa":
                ns["desenhar_conversa"]()
            elif estado == "batalha":
                ns["desenhar_batalha"]()
            elif estado == "mundo":
                ns["desenhar_mundo"]()
            self.redesenhar = False
        ficha = ns["TREINADORES"][self.quem(ns)]
        partes = [membro["bicho"] + " nv " + str(membro["nivel"]) for membro in ficha["equipa"]]
        nomes = {"rede": "a dar a rede", "luta": "antes da luta, e a luta", "depois": "depois de lhe ganhares"}
        self.faixa(ns, pygame, ficha["nome"] + " (" + nomes.get(self.cena, "") + "):   " + ",  ".join(partes))

    # --- O boneco que anda sozinho ---

    def por_onde(self, ns):
        # Os passos que o boneco vai dar a seguir, com a regra de andar do
        # jogo tal como esta agora: ate um sitio ao calhas (quase sempre na
        # zona onde esta, para o ecra nao andar sempre a mudar).
        jogador = ns["jogador"]
        aqui = (jogador["zona"], jogador["coluna"], jogador["linha"])
        este = self.mundo(ns)
        passos, veio, contra = este.andar(aqui)

        self.voltas = self.voltas + 1
        casas = [sitio for sitio in contra if este.faz(este.letra(*sitio)) == "cura"]
        if self.regra == "ao_descansar" and casas and self.voltas % 2 == 1:
            # Ate a casa da avo mais perto: o ultimo passo e contra ela.
            casa = min(casas, key=lambda sitio: passos[contra[sitio][0]])
            return _caminho(veio, contra[casa][0]) + [contra[casa]]
        if self.regra == "ao_responder":
            # De treinador em treinador, para lhes responder as perguntas.
            treinadores = sorted([sitio for sitio in contra if este.e_treinador(este.letra(*sitio))],
                                 key=lambda sitio: passos[contra[sitio][0]])

            def pergunta(sitio):
                falas = ns["TREINADORES"][int(este.letra(*sitio)) - 1].get("falas")
                return isinstance(falas, list) and any(isinstance(fala, dict) for fala in falas)
            # (De preferencia os que fazem perguntas, que e o que aqui se quer ver.)
            treinadores = [sitio for sitio in treinadores if pergunta(sitio)] or treinadores
            if treinadores:
                treinador = treinadores[self.voltas % min(2, len(treinadores))]
                return _caminho(veio, contra[treinador][0]) + [contra[treinador]]
        alvos = [sitio for sitio in passos if sitio != aqui]
        if self.regra in NA_ERVA:
            alvos = [sitio for sitio in alvos if este.erva(este.letra(*sitio))] or alvos
        perto = [sitio for sitio in alvos if sitio[0] == aqui[0]]
        if perto and self.voltas % 6 != 0:
            alvos = perto
        if not alvos:
            return []
        return _caminho(veio, random.choice(alvos))

    def andar_sozinho(self, ns):
        self.espera = self.espera - 1
        if self.espera > 0:
            return
        self.espera = 9
        jogador = ns["jogador"]
        aqui = (jogador["zona"], jogador["coluna"], jogador["linha"])
        if not self.caminho or self.caminho[0][0] != aqui:
            self.caminho = self.por_onde(ns)
        if self.caminho:
            _, passo = self.caminho.pop(0)
            ns["andar"](passo[0], passo[1])

    def jogar_no_mapa(self, ns, pygame):
        # Se a crianca carregar numa tecla, espera uns segundos por ela.
        teclas = pygame.key.get_pressed()
        for tecla in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_RETURN,
                      pygame.K_SPACE, pygame.K_ESCAPE, pygame.K_BACKSPACE):
            if teclas[tecla]:
                self.maos = 480
                self.caminho = []
        if self.maos > 0:
            self.maos = self.maos - 1
            return
        if ns["estado"] == "mundo":
            if not self.dados:               # numa zona anda so a crianca
                # (Para haver sempre lugar na equipa e redes para atirar.)
                if len(ns["minha_equipa"]) >= ns["EQUIPA_MAXIMA"]:
                    del ns["minha_equipa"][3:]
                ns["redes"] = max(ns["redes"], 3)
                if self.regra == "receber_compra" and self.relogio % 150 == 149 and len(ns["LOJA"]) > 0:
                    # De vez em quando compra-se uma coisa, para se ver o que se recebe.
                    nomes = list(ns["LOJA"])
                    nome = nomes[(self.relogio // 150) % len(nomes)]
                    ns["moedas"] = max(ns["moedas"], 100)
                    self.ultima_compra = str(ns["comprar"](nome))
                self.andar_sozinho(ns)
        elif ns["estado"] == "conversa":
            # As falas passam sozinhas, e as perguntas respondem-se ora com
            # uma resposta, ora com outra.
            self.espera = self.espera - 1
            if self.espera <= 0:
                fala = ns["conversa"][0]
                if not isinstance(fala, str):
                    ns["cursor"] = self.voltas % len(fala["respostas"])
                ns["tecla_na_conversa"](pygame.K_RETURN)
                self.espera = 80
        elif ns["estado"] == "loja":
            if self.tipo != "loja":
                ns["fechar_loja"]()
        elif ns["estado"] == "encontro":
            ns["voltar_ao_mundo"]()
        elif ns["estado"] == "batalha":
            if self.regra == "ao_responder" and not ns["batalha_selvagem"]:
                ns["voltar_ao_mundo"]()      # aqui interessa a conversa, e nao a luta
            elif ns["batalha_selvagem"] and ns["fase"] == "menu" and "Fugir" in ns["opcoes_do_menu"]():
                # De um bicho a solta foge-se, para voltar depressa ao mapa
                # (ou atira-se-lhe a rede, se e isso que se quer ver).
                self.espera = self.espera - 1
                if self.espera <= 0:
                    opcao = "Apanhar" if self.regra in COM_REDE and "Apanhar" in ns["opcoes_do_menu"]() else "Fugir"
                    if opcao == "Apanhar":
                        # (Ja magoado, como se tivesse havido luta: com a vida
                        # toda, a regra original nao deixa apanhar.)
                        bicho = ns["equipa_inimiga"][ns["ativo_inimigo"]]
                        if bicho["vida"] == bicho["vida_max"]:
                            bicho["vida"] = max(1, bicho["vida_max"] // 3)
                    ns["cursor"] = ns["opcoes_do_menu"]().index(opcao)
                    ns["tecla_na_batalha"](pygame.K_RETURN)
                    self.espera = 40
            else:
                self.jogar_sozinho(ns, pygame)

    def fazer_contas(self, ns):
        if not self.no_mapa:
            super().fazer_contas(ns)
            return
        # As linhas do quadro do canto: o que a funcao aberta responde agora.
        linhas = []
        if self.regra == "pode_andar":
            letras = []
            este = self.mundo(ns)
            for letra in "".join(ns["BLOCOS"]) + "".join("".join(filas) for filas in ns["ZONAS"].values()):
                if letra not in letras and letra not in " P123456789" and letra not in ns["PORTAS"] and este.faz(letra) == "":
                    letras.append(letra)
            sim = [letra for letra in letras if _sem_deixar_marcas(ns, lambda: ns["pode_andar"](letra))]
            nao = [letra for letra in letras if letra not in sim]
            linhas.append(("Onde se pode andar, agora:", ns["AMARELO"]))
            linhas.append(("Passa-se em:   " + "   ".join(sim), ns["VERDE"]))
            linhas.append(("Não se passa em:   " + "   ".join(nao), ns["VERMELHO"]))
        elif self.regra == "ha_batalha_na_erva":
            def cem_passos():
                return len([1 for _ in range(100) if ns["ha_batalha_na_erva"]()])
            linhas.append(("Em 100 passos na erva alta,", ns["AMARELO"]))
            linhas.append(("saltava um bicho em " + str(_sem_deixar_marcas(ns, cem_passos)) + ".", ns["BRANCO"]))
        elif self.regra == "escolher_bicho_selvagem":
            def quarenta():
                return [ns["escolher_bicho_selvagem"]() for _ in range(40)]
            niveis = {}
            for bicho in _sem_deixar_marcas(ns, quarenta):
                if _e_um_bicho(ns, bicho):
                    niveis.setdefault(bicho["nome"], []).append(bicho["nivel"])
            linhas.append(('Em 40 vezes, na zona "' + ns["jogador"]["zona"] + '", saltava:', ns["AMARELO"]))
            for nome in sorted(niveis, key=lambda nome: len(niveis[nome]), reverse=True)[:7]:
                nivel = "nv " + str(min(niveis[nome]))
                if min(niveis[nome]) != max(niveis[nome]):
                    nivel = nivel + " a " + str(max(niveis[nome]))
                linhas.append((nome + " (" + nivel + "): " + str(len(niveis[nome])) + " vezes", ns["BRANCO"]))
        elif self.regra == "consegue_apanhar":
            linhas.append(("Em 100 redes atiradas, apanhava-se:", ns["AMARELO"]))
            for nome, fracao in (("com a vida toda", 1.0), ("com metade da vida", 0.5), ("quase sem vida", 0.1)):
                modelo = ns["criar_bicho"](list(ns["BICHOS"])[0], self.nivel)
                modelo["vida"] = max(1, int(modelo["vida_max"] * fracao))

                def cem_redes():
                    return len([1 for _ in range(100) if ns["consegue_apanhar"](modelo)])
                linhas.append((nome + ": " + str(_sem_deixar_marcas(ns, cem_redes)), ns["BRANCO"]))
        elif self.regra == "premio_da_batalha":
            linhas.append(("Quantas moedas dá ganhar a:", ns["AMARELO"]))
            modelo = [ns["criar_bicho"](list(ns["BICHOS"])[0], 4)]
            linhas.append(("um bicho à solta de nível 4: "
                           + str(_sem_deixar_marcas(ns, lambda: ns["premio_da_batalha"](modelo, True))), ns["BRANCO"]))
            for ficha in ns["TREINADORES"][:6]:
                equipa = [ns["criar_bicho"](membro["bicho"], membro["nivel"]) for membro in ficha["equipa"]]
                linhas.append((ficha["nome"] + ": "
                               + str(_sem_deixar_marcas(ns, lambda: ns["premio_da_batalha"](equipa, False))), ns["BRANCO"]))
        elif self.regra == "receber_compra":
            linhas.append(("Na mochila:", ns["AMARELO"]))
            linhas.append(("Sopas " + str(ns["sopas"]) + "   Redes " + str(ns["redes"]) + "   Moedas "
                           + str(ns["moedas"]), ns["BRANCO"]))
            for nome in list(ns["LOJA"])[:5]:
                linhas.append((nome + ": " + str(ns["LOJA"][nome].get("preco")) + " moedas", ns["CINZA"]))
            if self.ultima_compra:
                linhas.append((self.ultima_compra, ns["VERDE"]))
        elif self.tipo == "evento":
            linhas.append(("Passos: " + str(ns["jogador"]["passos"]) + "    Sopas: " + str(ns["sopas"])
                           + "    Redes: " + str(ns["redes"]) + "    Moedas: " + str(ns["moedas"]), ns["BRANCO"]))
            linhas.append(("Bichos na equipa: " + str(len(ns["minha_equipa"])), ns["BRANCO"]))
            linhas.append(("O que está na memoria:", ns["AMARELO"]))
            for chave in list(ns["memoria"])[:6]:
                linhas.append((str(chave) + ": " + str(ns["memoria"][chave])[:30], ns["BRANCO"]))
            if len(ns["memoria"]) == 0:
                linhas.append(("(nada, por enquanto)", ns["CINZA"]))
        self.quadro_de_contas = linhas

    # --- Todos os frames ---

    def quadro(self, ns, pygame):
        if self.falador:
            self.quadro_do_falador(ns, pygame)
            return
        if not self.no_mapa:
            super().quadro(ns, pygame)
            return
        if not self.preparado:
            self.preparar(ns, pygame)

        if ns["estado"] == "derrota":
            ns["acordar_em_casa"]()
            self.redesenhar = True
        elif ns["estado"] not in ("mundo", "batalha", "conversa", "loja", "encontro"):
            self.passeio(ns, "Ganhaste a todos os treinadores! Vamos outra vez.")
        if self.de_cima and ns["estado"] != "mundo":
            ns["voltar_ao_mundo"]()      # visto de cima nao ha batalhas nem conversas: nao se viam
        if self.tipo == "loja" and ns["estado"] == "mundo":
            ns["abrir_loja"]()           # aqui esta-se sempre ao balcao

        antes = ns["estado"]
        self.jogar_no_mapa(ns, pygame)
        if ns["estado"] != antes:
            self.redesenhar = True
        # As contas fazem-se de novo duas vezes por segundo (os
        # acontecimentos mexem na memoria a qualquer altura).
        if self.regra is not None and self.relogio % 30 == 0:
            self.fazer_contas(ns)
        self.relogio = self.relogio + 1

        if self.de_cima:
            self.desenhar_de_cima(ns, pygame)
        elif self.redesenhar:
            # O jogo ja tinha desenhado este frame com o que havia antes.
            if ns["estado"] == "mundo":
                ns["desenhar_mundo"]()
            elif ns["estado"] == "batalha":
                ns["desenhar_batalha"]()
            elif ns["estado"] == "loja":
                ns["desenhar_loja"]()
            elif ns["estado"] == "conversa":
                ns["desenhar_conversa"]()
        self.redesenhar = False
        self.desenhar_no_mapa(ns, pygame)

    def cor_da_letra(self, ns, letra):
        cores = {"A": ns["COPA"], "~": ns["AGUA"], "e": ns["ERVA_ALTA"], "H": ns["TELHADO"], "P": ns["AMARELO"],
                 "$": ns["AMARELO"], "t": ns["TELHADO"], "j": ns["AGUA"], "m": ns["TRONCO"], "b": ns["TRONCO"],
                 "l": ns["TRONCO"], "c": ns["AGUA"], "v": ns["COPA"],
                 "#": ns["PAREDE"], "_": ns["SOALHO"], " ": ns["PRETO"]}
        if letra in ns["PORTAS"]:
            return ns["TRONCO"]
        if letra in ns["BLOCOS"] and isinstance(ns["BLOCOS"][letra], dict):
            return ns["BLOCOS"][letra].get("cor", ns["RELVA"])
        if letra in "123456789" and int(letra) <= len(ns["TREINADORES"]):
            return ns["VERMELHO"]
        return cores.get(letra, ns["RELVA"])

    def fazer_miniatura(self, ns, pygame):
        # O mundo todo num desenho so: as zonas do MUNDO no sitio delas e,
        # por baixo, os edificios (as zonas a que se chega por uma porta).
        # Guarda tambem onde ficou cada zona, para la por o ponto do boneco.
        zonas, mundo, portas = ns["ZONAS"], ns["MUNDO"], ns["PORTAS"]
        este = self.mundo(ns)
        interiores = []
        for letra, nome in portas.items():
            if nome in zonas and nome not in interiores:
                interiores.append(nome)
        lugares = max([len(fila) for fila in mundo] + [1])
        filas = len(mundo) + (1 if interiores else 0)
        lugares = max(lugares, len(interiores))
        largura, altura = ns["LARGURA"] - 20, ns["ALTURA"] - 60
        lado = max(1, min(largura // (lugares * ZONA[0]), altura // (filas * (ZONA[1] + 2))))
        passo_x, passo_y = lado * ZONA[0], lado * (ZONA[1] + 2)
        desenho = pygame.Surface((ns["LARGURA"], ns["ALTURA"] - 40))
        desenho.fill(ns["PRETO"])
        x0 = (ns["LARGURA"] - lugares * passo_x) // 2
        y0 = (ns["ALTURA"] - 40 - filas * passo_y) // 2
        onde = {}

        def uma(nome, x, y, titulo):
            for linha in range(ZONA[1]):
                for coluna in range(ZONA[0]):
                    cor = self.cor_da_letra(ns, este.letra(nome, coluna, linha))
                    pygame.draw.rect(desenho, cor, (x + coluna * lado, y + lado * 2 + linha * lado, lado, lado))
            pygame.draw.rect(desenho, ns["BRANCO"], (x, y + lado * 2, passo_x, lado * ZONA[1]), 1)
            texto = self.letra_pequena.render(titulo, True, ns["AMARELO"])
            desenho.blit(texto, (x + 3, y + max(0, lado * 2 - texto.get_height())), (0, 0, passo_x - 4, 20))
            onde.setdefault(nome, (x, y + lado * 2))

        for fila in range(len(mundo)):
            for lugar in range(len(mundo[fila])):
                nome = mundo[fila][lugar]
                if nome in zonas:
                    uma(nome, x0 + lugar * passo_x, y0 + fila * passo_y, nome)
                elif nome != "":
                    texto = self.letra_pequena.render(nome + "?", True, ns["VERMELHO"])
                    desenho.blit(texto, (x0 + lugar * passo_x + 3, y0 + fila * passo_y + lado * 2 + 3))
        lugar = 0
        for nome in interiores:
            letras = [letra for letra in portas if portas[letra] == nome]
            uma(nome, x0 + lugar * passo_x, y0 + len(mundo) * passo_y, nome + " (porta " + " ".join(letras) + ")")
            lugar = lugar + 1
        self.miniatura = (desenho, onde, lado)

    def desenhar_de_cima(self, ns, pygame):
        if self.miniatura is None:
            self.fazer_miniatura(ns, pygame)
        desenho, onde, lado = self.miniatura
        ecra = ns["ecra"]
        ecra.blit(desenho, (0, 0))
        jogador = ns["jogador"]
        if jogador["zona"] in onde:
            x, y = onde[jogador["zona"]]
            centro = (x + jogador["coluna"] * lado + lado // 2, y + jogador["linha"] * lado + lado // 2)
            pygame.draw.circle(ecra, ns["PRETO"], centro, max(4, lado // 2 + 2))
            pygame.draw.circle(ecra, ns["AMARELO"], centro, max(3, lado // 2))

    def desenhar_no_mapa(self, ns, pygame):
        ecra = ns["ecra"]
        if self.tipo == "zona":
            nomes = list(ns["ZONAS"])
            dentro = nomes[min(self.numero, len(nomes) - 1)] in ns["PORTAS"].values()
            # As letras que estao escritas nesta zona, e o que cada uma e.
            # (A lista de todos os blocos esta na ajuda, por baixo do codigo.)
            nesta = "".join(ns["ZONAS"][nomes[min(self.numero, len(nomes) - 1)]])
            texto = ""
            for letra, ficha in ns["BLOCOS"].items():
                if isinstance(ficha, dict) and letra in nesta and letra != " ":
                    texto = texto + letra + " " + str(ficha.get("nome", "bloco")) + "  "
            if any(letra in nesta for letra in ns["PORTAS"]):
                texto = texto + " ".join(letra for letra in ns["PORTAS"] if letra in nesta) + " porta  "
            texto = texto + ("P partida  " if "P" in nesta else "") + "1-9 treinadores"
        elif self.tipo == "bloco":
            letras = list(ns["BLOCOS"])
            letra = letras[min(self.numero, len(letras) - 1)] if letras else "?"
            ficha = ns["BLOCOS"].get(letra, {})
            texto = ("O bloco «" + str(ficha.get("nome", "?")) + "» é a letra " + letra + ". "
                     + ("Anda-se por cima dele." if ficha.get("passa") is not False else "Tapa o caminho."))
            if letra not in "".join("".join(filas) for filas in ns["ZONAS"].values()):
                texto = texto + " Ainda não está em nenhuma zona: abre uma zona e escreve a letra " + letra + "."
        elif self.tipo == "mundo":
            texto = "O mundo visto de cima. O ponto amarelo és tu: clica aqui e anda com as setas."
        elif self.tipo == "portas":
            texto = "O mundo e os edifícios, vistos de cima. As portas são os quadrados castanhos."
        elif self.tipo == "loja":
            texto = "A loja: setas e Enter para comprar. Aqui tens sempre moedas para experimentar."
        elif self.tipo == "jogador":
            texto = "Tu, no mapa: anda com as setas para te veres de frente, de costas e de lado."
        else:
            genero = {"regra": "Regra", "evento": "Acontecimento", "desenho": "Desenho"}[self.tipo]
            texto = genero + ":   " + FUNCOES[self.tipo][self.regra][0] + "   (a função " + self.regra + ")"
        self.faixa(ns, pygame, texto)

        linhas = self.quadro_de_contas
        if ns["estado"] != "mundo" or len(linhas) == 0:
            return
        desenhos = [self.letra_pequena.render(linha, True, cor) for linha, cor in linhas]
        largura = max(220, min(420, 20 + max(desenho.get_width() for desenho in desenhos)))
        caixa = pygame.Rect(ns["LARGURA"] - largura - 10, 10, largura, 10 + 17 * len(linhas))
        pygame.draw.rect(ecra, ns["PAINEL"], caixa, border_radius=6)
        pygame.draw.rect(ecra, ns["AMARELO"], caixa, 2, border_radius=6)
        y = caixa.y + 6
        for desenho in desenhos:
            ecra.blit(desenho, (caixa.x + 10, y), (0, 0, caixa.width - 20, 17))
            y = y + 17


    def faixa(self, ns, pygame, texto):
        # A faixa do palco, com o que esta aberto. No mapa fica em baixo, para
        # nao tapar a primeira linha de quadrados. Numa batalha fica em cima,
        # como no palco das batalhas.
        ecra = ns["ecra"]
        y = ns["ALTURA"] - 40
        if ns["estado"] in ("batalha", "encontro"):
            y = 0
        altura = 40 if y > 0 else 32
        pygame.draw.rect(ecra, ns["PAINEL"], (0, y, ns["LARGURA"], altura))
        pygame.draw.rect(ecra, ns["AMARELO"], (0, y, 6, altura))
        desenho = self.letra.render(texto, True, ns["BRANCO"])
        if desenho.get_width() > ns["LARGURA"] - 30:
            desenho = self.letra_pequena.render(texto, True, ns["BRANCO"])
        ecra.blit(desenho, (18, y + (altura - desenho.get_height()) // 2), (0, 0, ns["LARGURA"] - 30, altura))

    # --- O desenho que e da batalha ---

    def desenhar(self, ns, pygame):
        # (O palco das batalhas so conhece as funcoes do bicharada.py.)
        if self.regra not in NA_BATALHA:
            super().desenhar(ns, pygame)
            return
        ecra = ns["ecra"]
        pygame.draw.rect(ecra, ns["PAINEL"], (0, 0, ns["LARGURA"], 32))
        pygame.draw.rect(ecra, ns["AMARELO"], (0, 0, 6, 32))
        texto = "Desenho:   " + FUNCOES[self.tipo][self.regra][0] + "   (a função " + self.regra + ")"
        ecra.blit(self.letra.render(texto, True, ns["BRANCO"]), (18, 9))
        if ns["fase"] != "equipa" and ns["estado"] == "batalha":
            self.mostrar_montra(ns, pygame)

    def mostrar_montra(self, ns, pygame):
        if self.regra not in NA_BATALHA:
            super().mostrar_montra(ns, pygame)
            return
        # Todos os bichos, pequenos e de costas, para se ver o desenho em todos.
        ecra = ns["ecra"]
        caixa = pygame.Rect(352, 40, 436, 66)
        pygame.draw.rect(ecra, ns["PAINEL"], caixa, border_radius=6)
        pygame.draw.rect(ecra, ns["AMARELO"], caixa, 2, border_radius=6)
        passo = min(60, (caixa.width - 16) // max(1, len(self.montra)))
        x = caixa.x + 8 + passo // 2
        for modelo in self.montra:
            if modelo["nome"] in ns["BICHOS"]:
                ns["desenhar_bicho_de_costas"](modelo, x, caixa.centery, 40)
            x = x + passo


def criar_palco(escolha):
    return Palco(escolha)
