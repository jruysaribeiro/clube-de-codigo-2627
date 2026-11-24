# A Bicharada a Solta na Oficina. O jogo e a Bicharada (s12) com um mundo por
# onde se anda, por isso quase tudo vem do bicharada.py aqui ao lado: os
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
    "Edifícios": "Os sítios onde se entra por uma porta. Cada um é uma zona por dentro.",
    "Bichos": "Tipo, vida, ataque, forma, cor. Podes pôr uma imagem tua.",
    "Ataques": "O poder, a precisão e o efeito de cada ataque.",
    "Treinadores": "Quem encontras no mapa, o que dizem e que bichos levam.",
    "Tipos": "As cores dos tipos, e quem é forte contra quem.",
    "Regras do jogo": "Aqui mudas a maneira como o jogo se comporta, na batalha e no mapa: é programar a sério.",
    "Acontecimentos": "Estão vazios: o que lá escreveres passa a acontecer nesse momento. É aqui que se inventa.",
    "Desenhos": "Como se desenha um bicho, um quadrado do mapa, tu e os treinadores.",
}

# Apagar um bicho e escolher de uma lista os bichos de um treinador fazem-se
# como na Bicharada.
apagar = base.apagar
lista = base.lista

CRIAVEIS = dict(base.CRIAVEIS)
CRIAVEIS["Mapa"] = "Nova zona"
CRIAVEIS["Edifícios"] = "Novo edifício"

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
    "desenhar_quadrado": ["Põe flores amarelas na relva", "Faz as paredes de tijolo vermelho",
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
}
ACONTECIMENTOS = {
    "ao_dar_passo": ("Quando dás um passo", ["letra"]),
    "ao_descansar": ("Quando descansas em casa da avó", []),
    "a_cada_frame": ("A cada frame, no mapa", []),
}
DESENHOS = {
    "desenhar_quadrado": ("Um quadrado do mapa", ["letra", "x", "y"]),
    "desenhar_jogador": ("Tu, no mapa", ["x", "y", "olha_para"]),
    "desenhar_treinador": ("Um treinador, no mapa", ["treinador", "x", "y", "vencido"]),
}
# tipo da escolha -> as funcoes do mapa desse tipo. (O grupo onde aparecem e
# as explicacoes gerais sao os mesmos das funcoes da batalha.)
FUNCOES = {"regra": REGRAS, "evento": ACONTECIMENTOS, "desenho": DESENHOS}
DO_MAPA = list(REGRAS) + list(ACONTECIMENTOS) + list(DESENHOS)

# Com estas, o boneco anda de erva em erva, que e onde elas se veem.
NA_ERVA = ["ha_batalha_na_erva", "escolher_bicho_selvagem"]

SOZINHO = (" O boneco anda sozinho, e foge dos bichos que saltam da erva. Se clicares no jogo e"
           " carregares numa seta, ele espera uns segundos e deixa-te andar a ti.")

DICAS = {
    "zona": "Cada letra é um quadrado: muda uma letra e vê a zona mudar. A faixa de baixo diz o que é"
            " cada letra. Para experimentares, clica no jogo e anda com as setas: se saíres por um lado,"
            " entras na zona do lado.",
    "mundo": "Estás a ver o mundo todo, em ponto pequeno: cada retângulo é uma zona. Troca dois nomes de"
             " sítio e vê as zonas mudarem. O ponto amarelo és tu: clica no jogo e anda com as setas.",
    "portas": "Estás a ver o mundo todo, em ponto pequeno, e os edifícios por baixo. Cada porta é uma"
              " letra, escrita cá fora e lá dentro. O ponto amarelo és tu: clica no jogo e anda com as setas.",
    "regra": "Isto é uma regra do mapa: muda-a e o jogo passa a comportar-se de outra maneira."
             " O quadro do canto mostra o que a tua regra responde agora." + SOZINHO,
    "evento": "Tira o pass e escreve o que queres que aconteça nesse momento."
              " O quadro do canto mostra o que tens na memoria." + SOZINHO,
    "desenho": "Isto é o desenho: muda-o e vês logo, na zona toda." + SOZINHO,
}

LEGENDA = "A árvore  ~ água  e erva alta  . relva  # parede  _ soalho  H casa da avó  P partida  1-9 treinadores"
CONHECIDAS = ".eA~HP#_ 123456789"
ZONA = (20, 14)          # quantas letras tem uma zona: por linha, e linhas
PASSOS = ((0, 1), (0, -1), (1, 0), (-1, 0))      # a ordem e a do passar_a_porta do jogo

# Uma zona nova: relva, com uma saida ao meio de cada lado.
ZONA_NOVA = (["AAAAAAAAA..AAAAAAAAA"] + ["A..................A"] * 5 + ["...................."] * 2
             + ["A..................A"] * 5 + ["AAAAAAAAA..AAAAAAAAA"])
# O interior de um edificio novo: uma sala, com a porta (o ?) na parede de baixo.
SALA_NOVA = ([" " * 20] * 3 + ["     ##########     "] + ["     #________#     "] * 6
             + ["     ####?#####     "] + [" " * 20] * 3)
LETRAS_DE_PORTA = "BCDFGIJKLMNOQRSTUVWXYZ"


# =====================================================================
#                     O MUNDO, COMO O JOGO O VE
# =====================================================================

class Mundo:
    # As contas que o jogo faz com as ZONAS, o MUNDO e as PORTAS (a letra de
    # um quadrado, para onde vai um passo, onde da uma porta), feitas aqui so
    # com os dados, para se poder perguntar "chega-se a pe ate ali?" sem
    # mexer no jogo. Um sitio e (zona, coluna, linha).

    def __init__(self, zonas, mundo, portas, treinadores, pode=None):
        self.zonas = zonas
        self.mundo = mundo
        self.portas = portas
        self.treinadores = treinadores      # quantos ha
        # A regra de andar: a original, ou a que o jogo tiver agora.
        self.pode = pode or (lambda letra: letra not in "A~# ")

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

    def livre(self, letra):
        if letra in self.portas or letra == "H" or self.e_treinador(letra):
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
        #   contra   {o sitio de uma casa da avo ou de um treinador:
        #             (o sitio de onde se vai contra ele, o passo)}
        passos = {partida: 0}
        veio = {partida: None}
        contra = {}
        fila = collections.deque([partida])
        while fila:
            sitio = fila.popleft()
            for passo in PASSOS:
                vizinho = self.passo(sitio, passo[0], passo[1])
                letra = self.letra(*vizinho)
                if letra == "H" or self.e_treinador(letra):
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
    # Sem ZONAS nao e este jogo (e a Bicharada do s12, por exemplo).
    if blocos.instrucao(arvore, "ZONAS") is None or blocos.instrucao(arvore, "MUNDO") is None:
        return []
    interiores = _interiores(arvore)
    lista = [{"id": "mundo", "grupo": "Mapa", "titulo": "O mundo: como as zonas se juntam"}]
    if blocos.instrucao(arvore, "PORTAS") is not None:
        lista.append({"id": "portas", "grupo": "Edifícios", "titulo": "As portas"})
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


def regiao(fonte, escolha):
    # Igual a do bicharada.py, mais o mundo, as portas, as zonas e as funcoes
    # do mapa.
    arvore = ast.parse(fonte)
    linhas = fonte.split("\n")
    tipo, _, numero = escolha.partition(":")

    if escolha == "mundo" or escolha == "portas":
        no = blocos.instrucao(arvore, escolha.upper())
        if no is None:
            return None
        titulo = "O mundo" if escolha == "mundo" else "As portas"
        return {"inicio": no.lineno, "fim": no.end_lineno, "titulo": titulo, "imagem": None, "som": None,
                "ajuda": blocos.ajuda_acima(linhas, no.lineno), "dica": DICAS[escolha],
                "sugestoes": SUGESTOES[escolha]}

    if tipo == "zona":
        no = blocos.instrucao(arvore, "ZONAS")
        partes = _zonas_escritas(arvore)
        if not numero.isdigit() or int(numero) >= len(partes):
            return None
        nome, inicio, fim = partes[int(numero)]
        dentro = nome in _interiores(arvore)
        return {"inicio": inicio, "fim": fim, "titulo": nome or escolha, "imagem": None, "som": None,
                "ajuda": blocos.ajuda_acima(linhas, no.lineno), "dica": DICAS["zona"],
                "sugestoes": SUGESTOES["interior" if dentro else "zona"]}

    if tipo in FUNCOES and numero in FUNCOES[tipo]:
        no = blocos.funcao(arvore, numero)
        if no is None:
            return None
        ajuda = blocos.ajuda_acima(linhas, no.lineno)
        for inicio in base.FUNCOES[tipo][2]:
            geral = blocos.comentarios_a_partir_de(linhas, inicio)
            if geral and geral != ajuda:
                ajuda = ajuda + "\n\n" + geral
        return {"inicio": no.lineno, "fim": no.end_lineno, "ajuda": ajuda, "dica": DICAS[tipo],
                "titulo": FUNCOES[tipo][numero][0], "imagem": None, "som": None, "sugestoes": SUGESTOES[numero]}

    resposta = base.regiao(fonte, escolha)
    if resposta is not None and tipo == "treinador" and numero.isdigit():
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
    return arvore, Mundo(zonas, mundo, portas, treinadores)


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
        if nomes and any(mundo.letra(nomes[-1], ZONA[0] - 1, linha) in ".e" for linha in (6, 7)):
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
    _juntar_ao_dicionario(arvore, linhas, "ZONAS", _texto_da_zona(nome, ZONA_NOVA))

    aviso = 'Criei a zona "' + nome + '": relva, com uma saída ao meio de cada lado.'
    if vizinha is None:
        aviso = aviso + " Pu-la no MUNDO, na última fila."
    else:
        aviso = aviso + ' No MUNDO, pu-la à direita de "' + vizinha + '".'
    if not ligada:
        aviso = aviso + " Ainda não se chega lá a pé: abre uma saída na zona do lado, ou muda-a de sítio em O mundo."
    return "\n".join(linhas), "zona:" + str(len(mundo.zonas)), aviso


def _novo_edificio(fonte):
    arvore, mundo = _ler_mundo(fonte)
    if mundo is None:
        raise ValueError("não percebi como estão escritas as ZONAS, o MUNDO ou as PORTAS no ficheiro.")
    usadas = "".join("".join(filas) for filas in mundo.zonas.values()) + "".join(mundo.portas)
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
    novas = {"ZONAS": _texto_da_zona(nome, [fila.replace("?", letra) for fila in SALA_NOVA]),
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


def novo(fonte, grupo):
    if grupo == "Mapa":
        return _nova_zona(fonte)
    if grupo == "Edifícios":
        return _novo_edificio(fonte)
    nova, escolha, aviso = base.novo(fonte, grupo)
    if grupo == "Bichos":
        aviso = aviso + " E pode saltar da erva, à solta."
    if grupo == "Treinadores":
        numero = int(escolha.partition(":")[2]) + 1
        aviso = aviso.split(" No jogo inteiro")[0]
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


def _ver_mundo(ns, treinadores, aberto, problemas, avisos):
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
        if letra in CONHECIDAS:
            problemas.append('Em PORTAS, a letra "' + letra + '" já quer dizer outra coisa no mapa. Escolhe outra.')
            return
    if not aberto:
        return

    quantos = len(treinadores) if isinstance(treinadores, list) else 0
    este = Mundo(zonas, mundo, portas, quantos)
    no_mundo = este.no_mundo()
    interiores = [nome for nome in portas.values() if nome in zonas]
    tudo = "".join("".join(zonas[nome]) for nome in zonas)

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
    if "H" not in tudo:
        avisos.append("Não há casa da avó (H): não tens onde curar a equipa.")
    if "e" not in tudo:
        avisos.append("Não há erva alta (e): não salta nenhum bicho à solta.")

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
    if "H" in tudo and "H" not in chega_se:
        avisos.append("Não se chega a pé a nenhuma casa da avó (H).")
    novas = sorted(set(tudo) - set(CONHECIDAS) - set(portas))
    if novas:
        avisos.append("Letras novas: " + " ".join(novas) + ". O jogo trata-as como relva, até lhes dares "
                      "um desenho (em Desenhos) ou uma regra.")


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
        for letra in ".eA~#_ ":
            _sem_deixar_marcas(ns, lambda: ns["pode_andar"](letra))
    elif regra == "ha_batalha_na_erva":
        _sem_deixar_marcas(ns, ns["ha_batalha_na_erva"])
    elif regra == "escolher_bicho_selvagem":
        valor = _sem_deixar_marcas(ns, ns["escolher_bicho_selvagem"])
        if not _e_um_bicho(ns, valor):
            problemas.append("escolher_bicho_selvagem tem de devolver um bicho feito com criar_bicho(nome, nivel). "
                             "Devolveu " + repr(valor)[:60] + ".")


# =====================================================================
#                              O PALCO
# =====================================================================

class Palco(base.Palco):

    def __init__(self, escolha):
        super().__init__(escolha)
        # no_mapa: o palco e o mapa, e nao uma batalha.
        self.dados = self.tipo in ("zona", "mundo", "portas")     # anda so a crianca
        self.de_cima = self.tipo in ("mundo", "portas")           # ve-se o mundo todo, pequeno
        self.no_mapa = self.dados or self.regra in DO_MAPA
        self.caminho = []            # os passos que o boneco vai dar: [(de onde, o passo), ...]
        self.voltas = 0
        self.relogio = 0
        self.miniatura = None        # o desenho do mundo todo, feito uma vez

    def verificar(self, ns):
        problemas, avisos = super().verificar(ns)
        _ver_funcoes(ns, problemas)
        _ver_mundo(ns, self.ler(ns, "TREINADORES"), self.dados, problemas, avisos)
        if self.regra in REGRAS and self.preparado and not problemas:
            _experimentar(ns, self.regra, problemas)
        return problemas, avisos

    # --- Preparar e voltar a preparar ---

    def preparar(self, ns, pygame):
        if not self.no_mapa:
            super().preparar(ns, pygame)
            return
        self.letra = pygame.font.SysFont(None, 22)
        self.letra_pequena = pygame.font.SysFont(None, 18)
        self.preparado = True
        self.arrumar(ns)
        self.passeio(ns, None)

    def ao_mudar(self, ns):
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
            self.redesenhar = True

    def arrumar(self, ns):
        super().arrumar(ns)
        if not self.no_mapa:
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
                     lambda letra: ns["pode_andar"](letra))

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
        if self.tipo == "zona":
            nomes = list(ns["ZONAS"])
            nome = nomes[min(self.numero, len(nomes) - 1)]
            if ns["jogador"]["zona"] != nome:
                este = self.mundo(ns)
                sitio = None
                for letra in "._e":
                    sitio = sitio or este.encontrar(letra, [nome])
                sitio = sitio or (nome, 1, 1)
                ns["ir_para"](*sitio)
                for chave in ("zona", "coluna", "linha"):
                    ns["descanso"][chave] = ns["jogador"][chave]
        self.caminho = []
        self.redesenhar = True

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
        casas = [sitio for sitio in contra if este.letra(*sitio) == "H"]
        if self.regra == "ao_descansar" and casas and self.voltas % 2 == 1:
            # Ate a casa da avo mais perto: o ultimo passo e contra ela.
            casa = min(casas, key=lambda sitio: passos[contra[sitio][0]])
            return _caminho(veio, contra[casa][0]) + [contra[casa]]
        alvos = [sitio for sitio in passos if sitio != aqui]
        if self.regra in NA_ERVA:
            alvos = [sitio for sitio in alvos if este.letra(*sitio) == "e"] or alvos
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
                self.andar_sozinho(ns)
        elif ns["estado"] == "batalha":
            if ns["batalha_selvagem"] and ns["fase"] == "menu" and "Fugir" in ns["OPCOES_MENU"]:
                # De um bicho a solta foge-se, para voltar depressa ao mapa.
                self.espera = self.espera - 1
                if self.espera <= 0:
                    ns["cursor"] = ns["OPCOES_MENU"].index("Fugir")
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
            for letra in ".eA~#_" + "".join("".join(filas) for filas in ns["ZONAS"].values()):
                if letra not in letras and letra not in " HP123456789" and letra not in ns["PORTAS"]:
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
        elif self.tipo == "evento":
            linhas.append(("Passos: " + str(ns["jogador"]["passos"]) + "    Sopas: " + str(ns["sopas"]),
                           ns["BRANCO"]))
            linhas.append(("O que está na memoria:", ns["AMARELO"]))
            for chave in list(ns["memoria"])[:6]:
                linhas.append((str(chave) + ": " + str(ns["memoria"][chave])[:30], ns["BRANCO"]))
            if len(ns["memoria"]) == 0:
                linhas.append(("(nada, por enquanto)", ns["CINZA"]))
        self.quadro_de_contas = linhas

    # --- Todos os frames ---

    def quadro(self, ns, pygame):
        if not self.no_mapa:
            super().quadro(ns, pygame)
            return
        if not self.preparado:
            self.preparar(ns, pygame)

        if ns["estado"] == "derrota":
            ns["acordar_em_casa"]()
            self.redesenhar = True
        elif ns["estado"] != "mundo" and ns["estado"] != "batalha":
            self.passeio(ns, "Ganhaste a todos os treinadores! Vamos outra vez.")
        if self.de_cima and ns["estado"] == "batalha":
            ns["voltar_ao_mundo"]()      # visto de cima nao ha batalhas: nao se viam

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
        self.redesenhar = False
        self.desenhar_no_mapa(ns, pygame)

    def cor_da_letra(self, ns, letra):
        cores = {"A": ns["COPA"], "~": ns["AGUA"], "e": ns["ERVA_ALTA"], "H": ns["TELHADO"], "P": ns["AMARELO"],
                 "#": ns["PAREDE"], "_": ns["SOALHO"], " ": ns["PRETO"]}
        if letra in ns["PORTAS"]:
            return ns["TRONCO"]
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
            texto = LEGENDA
            if len(ns["PORTAS"]) > 0:
                texto = texto + "  " + " ".join(ns["PORTAS"]) + " porta"
        elif self.tipo == "mundo":
            texto = "O mundo visto de cima. O ponto amarelo és tu: clica aqui e anda com as setas."
        elif self.tipo == "portas":
            texto = "O mundo e os edifícios, vistos de cima. As portas são os quadrados castanhos."
        else:
            genero = {"regra": "Regra", "evento": "Acontecimento", "desenho": "Desenho"}[self.tipo]
            texto = genero + ":   " + FUNCOES[self.tipo][self.regra][0] + "   (a função " + self.regra + ")"
        # No mapa a faixa fica em baixo, para nao tapar a primeira linha de
        # quadrados. Numa batalha fica em cima, como no palco das batalhas.
        y = 0
        if ns["estado"] == "mundo":
            y = ns["ALTURA"] - 40
        altura = 40 if y > 0 else 32
        pygame.draw.rect(ecra, ns["PAINEL"], (0, y, ns["LARGURA"], altura))
        pygame.draw.rect(ecra, ns["AMARELO"], (0, y, 6, altura))
        desenho = self.letra.render(texto, True, ns["BRANCO"])
        if desenho.get_width() > ns["LARGURA"] - 30:
            desenho = self.letra_pequena.render(texto, True, ns["BRANCO"])
        ecra.blit(desenho, (18, y + (altura - desenho.get_height()) // 2))

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


def criar_palco(escolha):
    return Palco(escolha)
