# A Bicharada a Solta na Oficina. O jogo e a Bicharada (s12) com um mapa por
# onde se anda, por isso quase tudo vem do bicharada.py aqui ao lado: os
# bichos, os ataques, os treinadores, os tipos e as funcoes da batalha
# abrem-se da mesma maneira, no mesmo palco (ja dentro de uma batalha).
#
# O que este ficheiro junta e o que e do mapa: o MAPA, tres regras, tres
# acontecimentos e tres desenhos. Para essas coisas o palco e outro: o jogo
# ja no mapa, com o boneco a andar sozinho para se ver logo o que a funcao
# nova faz. No MAPA anda so a crianca, para o mapa nao fugir debaixo dela.

import ast
import inspect
import random

import blocos
from jogos import bicharada as base

NOME = "Bicharada à Solta"
FICHEIRO = "s15-bicharada-a-solta/bicharada-a-solta.py"
DESCRICAO = "A Bicharada com um mapa: andas por lá, e os bichos saltam da erva."

# Uma frase por grupo, para a pagina do jogo dizer o que la ha. A ordem
# daqui e a ordem dos grupos na pagina.
SOBRE_OS_GRUPOS = {
    "Mapa": "O sítio por onde andas, desenhado com letras: relva, erva alta, árvores, água.",
    "Bichos": "Tipo, vida, ataque, forma, cor. Podes pôr uma imagem tua.",
    "Ataques": "O poder, a precisão e o efeito de cada ataque.",
    "Treinadores": "Quem encontras no mapa, o que dizem e que bichos levam.",
    "Tipos": "As cores dos tipos, e quem é forte contra quem.",
    "Regras do jogo": "Aqui mudas a maneira como o jogo se comporta, na batalha e no mapa: é programar a sério.",
    "Acontecimentos": "Estão vazios: o que lá escreveres passa a acontecer nesse momento. É aqui que se inventa.",
    "Desenhos": "Como se desenha um bicho, um quadrado do mapa, tu e os treinadores.",
}

CRIAVEIS = base.CRIAVEIS

QUE_FAZER = "O que posso fazer aqui?"
LINHA_A_LINHA = "Explica-me esta função linha a linha"

# Pedidos ja escritos para o ajudante. (Os das coisas da batalha estao no
# bicharada.py.)
SUGESTOES = {
    "mapa": ["Faz um lago grande no meio do mapa", "Põe mais erva alta perto da casa da avó",
             "O que quer dizer cada letra?"],
    "pode_andar": ["Deixa-me andar na água se tiver um bicho de água na equipa",
                   "Faz a letra M ser um muro por onde não se passa", LINHA_A_LINHA],
    "ha_batalha_na_erva": ["Faz saltar um bicho 1 vez em cada 3 passos",
                           "Nunca saltam dois bichos em passos seguidos", LINHA_A_LINHA],
    "escolher_bicho_selvagem": ["Faz saltar só bichos de planta",
                                "Do lado direito do mapa os bichos são dois níveis mais fortes", LINHA_A_LINHA],
    "ao_dar_passo": ["A letra s no mapa é uma sopa: quando a piso, ganho uma sopa",
                     "A cada 20 passos, os meus bichos perdem 1 de vida", QUE_FAZER],
    "ao_descansar": ["A avó dá-me uma sopa a mais", "A avó diz uma frase diferente de cada vez", QUE_FAZER],
    "a_cada_frame": ["Faz um relógio que diz há quantos segundos ando no mapa",
                     "Os meus bichos recuperam 1 de vida a cada 2 segundos", QUE_FAZER],
    "desenhar_quadrado": ["Põe flores amarelas na relva", "Faz um mapa de neve: relva branca e água gelada",
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
    "mapa": "Cada letra é um quadrado: muda uma letra e vê o mapa mudar. A faixa de baixo diz o que é"
            " cada letra. Para experimentares, clica no jogo e anda com as setas.",
    "regra": "Isto é uma regra do mapa: muda-a e o jogo passa a comportar-se de outra maneira."
             " O quadro do canto mostra o que a tua regra responde agora." + SOZINHO,
    "evento": "Tira o pass e escreve o que queres que aconteça nesse momento."
              " O quadro do canto mostra o que tens na memoria." + SOZINHO,
    "desenho": "Isto é o desenho: muda-o e vês logo, no mapa todo." + SOZINHO,
}

LEGENDA = "A árvore   ~ água   e erva alta   . relva   H casa da avó   P partida   1 a 9 treinadores"
CONHECIDAS = ".eA~HP123456789"
TAMANHO = (20, 14)       # quantas letras cabem no ecra: por linha, e linhas


# =====================================================================
#                    ONDE ESTA O CODIGO DE CADA COISA
# =====================================================================

def escolhas(fonte):
    arvore = ast.parse(fonte)
    # Sem MAPA nao e este jogo (e a Bicharada do s12, por exemplo).
    if blocos.instrucao(arvore, "MAPA") is None:
        return []
    lista = [{"id": "mapa", "grupo": "Mapa", "titulo": "O mapa"}] + base.escolhas(fonte)
    for tipo in FUNCOES:
        grupo = base.FUNCOES[tipo][1]
        for nome in FUNCOES[tipo]:
            if blocos.funcao(arvore, nome) is not None:
                lista.append({"id": tipo + ":" + nome, "grupo": grupo, "titulo": FUNCOES[tipo][nome][0]})
    ordem = list(SOBRE_OS_GRUPOS)
    lista.sort(key=lambda escolha: ordem.index(escolha["grupo"]) if escolha["grupo"] in ordem else len(ordem))
    return lista


def regiao(fonte, escolha):
    # Igual a do bicharada.py, mais o mapa e as funcoes do mapa.
    arvore = ast.parse(fonte)
    linhas = fonte.split("\n")
    tipo, _, numero = escolha.partition(":")

    if escolha == "mapa":
        no = blocos.instrucao(arvore, "MAPA")
        if no is None:
            return None
        return {"inicio": no.lineno, "fim": no.end_lineno, "titulo": "O mapa", "imagem": None, "som": None,
                "ajuda": blocos.ajuda_acima(linhas, no.lineno), "dica": DICAS["mapa"],
                "sugestoes": SUGESTOES["mapa"]}

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
        letra = int(numero) + 1
        if letra <= 9:
            resposta["dica"] = ("No mapa, este treinador é o " + str(letra) + ": para o mudares de sítio, "
                                "muda o " + str(letra) + " em Mapa. " + resposta["dica"])
        else:
            resposta["dica"] = "No mapa só cabem 9 treinadores: este não aparece lá. " + resposta["dica"]
    return resposta


# =====================================================================
#                        CRIAR UMA COISA NOVA
# =====================================================================

def _andar_pelo_mapa(mapa, treinadores):
    # Ate onde se chega a pe, a partir da partida, com a regra de andar
    # original: {(coluna, linha): passos}. A partida e o P ou, sem P, o
    # primeiro bocado de relva (como no jogo).
    def letra(coluna, linha):
        if 0 <= linha < len(mapa) and 0 <= coluna < len(mapa[linha]):
            return mapa[linha][coluna]
        return "A"

    partida = None
    for procurada in "P.":
        for linha in range(len(mapa)):
            for coluna in range(len(mapa[linha])):
                if partida is None and mapa[linha][coluna] == procurada:
                    partida = (coluna, linha)
    if partida is None:
        return {}, letra
    passos = {partida: 0}
    fila = [partida]
    while fila:
        coluna, linha = fila.pop(0)
        for vizinho in ((coluna + 1, linha), (coluna - 1, linha), (coluna, linha + 1), (coluna, linha - 1)):
            if vizinho not in passos and not _obstaculo(letra(*vizinho), treinadores):
                passos[vizinho] = passos[(coluna, linha)] + 1
                fila.append(vizinho)
    return passos, letra


def _obstaculo(letra, treinadores):
    # Arvores, agua, a casa da avo e os treinadores que existem.
    if letra in "A~H":
        return True
    return letra in "123456789" and int(letra) <= treinadores


def _por_no_mapa(fonte, numero):
    # Escreve o numero de um treinador novo num bocado de relva do MAPA, onde
    # se chegue a pe e nao tape a passagem (com relva ou erva a toda a volta).
    # Devolve o ficheiro, e True se o pos.
    arvore = ast.parse(fonte)
    no = blocos.instrucao(arvore, "MAPA")
    partes = blocos.entradas(no) if no is not None else None
    if not partes or numero > 9:
        return fonte, False
    mapa = [blocos.texto_constante(elemento) for elemento, _, _ in partes]
    if None in mapa or str(numero) in "".join(mapa):
        return fonte, False
    passos, letra = _andar_pelo_mapa(mapa, numero - 1)
    livres = []
    for (coluna, linha), quantos in passos.items():
        a_volta = [letra(coluna + dc, linha + dl) for dc in (-1, 0, 1) for dl in (-1, 0, 1)]
        if letra(coluna, linha) == "." and all(vizinha in ".e" for vizinha in a_volta):
            # (Perto da partida, para se dar logo com ele, mas nao em cima dela.)
            livres.append((quantos < 3, quantos, coluna, linha))
    if not livres:
        return fonte, False
    _, _, coluna, linha = min(livres)
    elemento, primeira, ultima = partes[linha]
    linhas = fonte.split("\n")
    texto = linhas[primeira - 1]
    onde = base._coluna(texto, elemento.col_offset) + 1 + coluna
    if primeira != ultima or texto[onde:onde + 1] != ".":
        return fonte, False
    linhas[primeira - 1] = texto[:onde] + str(numero) + texto[onde + 1:]
    return "\n".join(linhas), True


def novo(fonte, grupo):
    nova, escolha, aviso = base.novo(fonte, grupo)
    if grupo == "Bichos":
        aviso = aviso + " E pode saltar da erva, à solta."
    if grupo == "Treinadores":
        numero = int(escolha.partition(":")[2]) + 1
        aviso = aviso.split(" No jogo inteiro")[0]
        nova, posto = _por_no_mapa(nova, numero)
        if posto:
            aviso = aviso + " Pu-lo no mapa: é o " + str(numero) + ". Em Mapa podes mudá-lo de sítio."
        elif numero > 9:
            aviso = aviso + " No mapa só cabem 9 treinadores, por isso este não aparece no jogo."
        else:
            aviso = aviso + " Ainda não está no mapa: em Mapa, escreve um " + str(numero) + " onde o quiseres."
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


def _ver_mapa(ns, treinadores, aberto, problemas, avisos):
    # aberto: e o mapa que esta aberto no editor? So nesse caso se dao os
    # avisos, para nao aparecerem cada vez que se muda outra coisa.
    mapa = ns.get("MAPA")
    if not isinstance(mapa, list) or len(mapa) == 0:
        problemas.append("O MAPA tem de ser uma lista de linhas, entre [ ].")
        return
    for linha in mapa:
        if not isinstance(linha, str):
            problemas.append("Cada linha do MAPA tem de estar entre aspas e acabar com uma vírgula.")
            return
    tudo = "".join(mapa)
    if tudo == "":
        problemas.append("O MAPA está vazio: escreve pelo menos uma linha com letras.")
        return
    if not aberto:
        return

    if "P" not in tudo:
        avisos.append("Falta o P, a partida: assim começas no primeiro bocado de relva.")
    elif tudo.count("P") > 1:
        avisos.append("Há mais do que um P: começas no primeiro.")
    if len(mapa) > TAMANHO[1] or max(len(linha) for linha in mapa) > TAMANHO[0]:
        avisos.append("O mapa é grande demais: só cabem " + str(TAMANHO[0]) + " letras por linha e "
                      + str(TAMANHO[1]) + " linhas. O resto fica fora do ecrã.")
    if "H" not in tudo:
        avisos.append("Não há casa da avó (H): não tens onde curar a equipa.")
    if "e" not in tudo:
        avisos.append("Não há erva alta (e): não salta nenhum bicho à solta.")

    quantos = len(treinadores) if isinstance(treinadores, list) else 0
    passos, letra = _andar_pelo_mapa(mapa, quantos)

    def chega_se(procurada):
        # Ha algum quadrado com esta letra encostado a um sitio onde se chega?
        for linha in range(len(mapa)):
            for coluna in range(len(mapa[linha])):
                if mapa[linha][coluna] == procurada:
                    for vizinho in ((coluna + 1, linha), (coluna - 1, linha), (coluna, linha + 1), (coluna, linha - 1)):
                        if vizinho in passos:
                            return True
        return False

    no_mapa = 0
    for numero in range(1, min(quantos, 9) + 1):
        ficha = treinadores[numero - 1]
        nome = ficha.get("nome") if isinstance(ficha, dict) else None
        nome = nome if isinstance(nome, str) else "O treinador " + str(numero)
        if str(numero) not in tudo:
            avisos.append(nome + " não está no mapa: escreve um " + str(numero) + " onde o quiseres.")
            continue
        no_mapa = no_mapa + 1
        if not chega_se(str(numero)):
            avisos.append("Não se chega a pé a " + nome + " (o " + str(numero) + "): há árvores ou água no caminho.")
    if no_mapa == 0:
        avisos.append("Sem treinadores no mapa, o jogo nunca acaba.")
    for numero in range(quantos + 1, 10):
        if str(numero) in tudo:
            avisos.append("O " + str(numero) + " não é nenhum treinador (só há " + str(quantos)
                          + "): fica relva.")
    if "H" in tudo and not chega_se("H"):
        avisos.append("Não se chega a pé à casa da avó (H): há árvores ou água no caminho.")
    novas = sorted(set(tudo) - set(CONHECIDAS))
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
        for letra in ".eA~":
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
        self.no_mapa = self.tipo == "mapa" or self.regra in DO_MAPA
        self.caminho = []            # os quadrados por onde o boneco vai a seguir
        self.voltas = 0
        self.relogio = 0

    def verificar(self, ns):
        problemas, avisos = super().verificar(ns)
        _ver_funcoes(ns, problemas)
        _ver_mapa(ns, self.ler(ns, "TREINADORES"), self.tipo == "mapa", problemas, avisos)
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
        if self.tipo == "mapa":
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

    def passeio(self, ns, noticia):
        # Poe o jogo no mapa, na partida, com as funcoes do proprio jogo.
        equipa = []
        for nome in self.equipa:
            equipa.append(ns["criar_bicho"](nome, self.nivel))
        ns["minha_equipa"] = equipa
        ns["comecar_mundo"]()
        # (Sem a caixa que explica as teclas: tapava o fundo do mapa.)
        ns["aviso"] = noticia or ""
        self.caminho = []
        self.redesenhar = True

    # --- O boneco que anda sozinho ---

    def por_onde(self, ns):
        # Aonde vai o boneco a seguir: os quadrados do caminho, por ordem.
        # Usa a regra de andar do jogo, tal como esta agora.
        jogador = ns["jogador"]
        aqui = (jogador["coluna"], jogador["linha"])
        letra = ns["letra_do_mapa"]
        veio_de = {aqui: None}
        fila = [aqui]
        casa = None                  # um sitio encostado a casa da avo, e a casa
        while fila:
            sitio = fila.pop(0)
            for vizinho in ((sitio[0] + 1, sitio[1]), (sitio[0] - 1, sitio[1]),
                            (sitio[0], sitio[1] + 1), (sitio[0], sitio[1] - 1)):
                esta = letra(*vizinho)
                if esta == "H" and casa is None:
                    casa = (sitio, vizinho)
                if vizinho in veio_de or esta == "H" or ns["treinador_do_quadrado"](esta) != -1:
                    continue
                if ns["pode_andar"](esta):
                    veio_de[vizinho] = sitio
                    fila.append(vizinho)

        self.voltas = self.voltas + 1
        fim = []
        if self.regra == "ao_descansar" and casa is not None and self.voltas % 2 == 1:
            alvo, fim = casa[0], [casa[1]]       # o ultimo passo e contra a casa
        else:
            alvos = [sitio for sitio in veio_de if sitio != aqui]
            na_erva = [sitio for sitio in alvos if letra(*sitio) == "e"]
            if self.regra in NA_ERVA and na_erva:
                alvos = na_erva
            if not alvos:
                return []
            alvo = random.choice(alvos)
        caminho = []
        while alvo != aqui:
            caminho.insert(0, alvo)
            alvo = veio_de[alvo]
        return caminho + fim

    def andar_sozinho(self, ns):
        self.espera = self.espera - 1
        if self.espera > 0:
            return
        self.espera = 9
        jogador = ns["jogador"]
        aqui = (jogador["coluna"], jogador["linha"])
        if not self.caminho or abs(self.caminho[0][0] - aqui[0]) + abs(self.caminho[0][1] - aqui[1]) != 1:
            self.caminho = self.por_onde(ns)
        if self.caminho:
            proximo = self.caminho.pop(0)
            ns["andar"](proximo[0] - aqui[0], proximo[1] - aqui[1])

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
            if self.tipo != "mapa":          # no mapa anda so a crianca
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
            for letra in ".eA~" + "".join(ns["MAPA"]):
                if letra not in letras and letra not in "HP123456789":
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
            linhas.append(("Em 40 vezes, saltava da erva:", ns["AMARELO"]))
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

        antes = ns["estado"]
        self.jogar_no_mapa(ns, pygame)
        if ns["estado"] != antes:
            self.redesenhar = True
        # As contas fazem-se de novo duas vezes por segundo (os
        # acontecimentos mexem na memoria a qualquer altura).
        if self.regra is not None and self.relogio % 30 == 0:
            self.fazer_contas(ns)
        self.relogio = self.relogio + 1

        if self.redesenhar:
            # O jogo ja tinha desenhado este frame com o que havia antes.
            if ns["estado"] == "mundo":
                ns["desenhar_mundo"]()
            elif ns["estado"] == "batalha":
                ns["desenhar_batalha"]()
            self.redesenhar = False
        self.desenhar_no_mapa(ns, pygame)

    def desenhar_no_mapa(self, ns, pygame):
        ecra = ns["ecra"]
        if self.tipo == "mapa":
            texto = LEGENDA
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
