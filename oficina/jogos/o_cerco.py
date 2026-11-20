# O Cerco na Oficina: que coisas se podem escolher, onde esta o codigo de
# cada uma, e o "palco" que mostra so essa coisa a funcionar.
#
# O palco nao e um jogo a parte: e O Cerco verdadeiro a correr, com ouro
# sem fim e sem ondas, e nos a mandarmos vir os inimigos que interessam.
# Por isso tudo o que se ve e desenhado pelo codigo do proprio jogo.

import ast
import inspect

import blocos

NOME = "O Cerco"
FICHEIRO = "s13-o-cerco/o-cerco.py"
DESCRICAO = "Um tower defense. Guimarães, 1128."

# Uma frase por grupo, para a pagina do jogo dizer o que la ha.
SOBRE_OS_GRUPOS = {
    "Inimigos": "Vida, velocidade, cor, tamanho. Podes pôr uma imagem tua.",
    "Torres": "Custo, alcance, dano, efeito. Podes pôr uma imagem tua.",
    "Mapa": "O caminho, desenhado com letras.",
    "Regras do jogo": "Aqui mudas a maneira como o jogo se comporta: é programar a sério.",
}

# Pedidos ja escritos para o ajudante, para se perceber o que se pode pedir.
SUGESTOES = {
    "inimigo": ["Põe-no mais rápido mas com menos vida", "Muda-lhe a cor para verde", "O que quer dizer cada número?"],
    "torre": ["Faz esta torre disparar mais depressa", "Dá-lhe mais alcance, mas mais cara", "O que faz o efeito?"],
    "mapa": ["Como é que desenho um caminho novo?", "O que quer dizer cada letra?"],
    "escolher_alvo": ["Faz as torres atacarem o inimigo com menos vida", "Faz as torres atacarem o que está mais perto",
                      "Explica-me esta função linha a linha"],
    "disparar": ["Faz o Besteiro disparar duas setas de cada vez", "Faz a pedra do Trabuco voar mais depressa",
                 "Explica-me esta função linha a linha"],
    "magoar": ["Quero golpes críticos: às vezes o dano conta a dobrar", "Dá 1 de ouro por cada golpe que acerta",
               "Explica-me esta função linha a linha"],
    "mover_inimigo": ["Faz os inimigos acelerarem quando têm pouca vida", "Faz os inimigos pararem um bocadinho de vez em quando",
                      "Explica-me esta função linha a linha"],
}

EFEITOS = ["tiro", "explosao", "area", "golpe"]

# As regras: funcoes do jogo que se podem mudar. Para cada uma, o titulo que
# aparece na Oficina, e o que ela recebe (o jogo chama-a assim, por isso nao
# pode mudar).
REGRAS = {
    "escolher_alvo": ("Quem a torre ataca", ["torre"]),
    "disparar": ("O que a torre faz ao disparar", ["torre", "alvo"]),
    "magoar": ("O que acontece a um inimigo atingido", ["inimigo", "dano"]),
    "mover_inimigo": ("Como anda um inimigo", ["inimigo"]),
}
INICIO_DAS_REGRAS = "# --- As regras do jogo ---"

DICAS = {
    "inimigo": "O inimigo anda sozinho pelo caminho. "
               "Clica na relva para pôr mais torres e ver quanto ele aguenta.",
    "torre": "A tua torre já está posta, com o alcance à vista. "
             "Clica na relva para pôr mais; as teclas 1 2 3 4 escolhem outra torre.",
    "mapa": "Cada letra é um quadrado. Muda uma letra e vê o mapa mudar. "
            "Os inimigos andam pelo caminho para veres por onde ele vai.",
    "regra": "Isto é uma regra do jogo: muda-a e o jogo passa a comportar-se de outra maneira. "
             "Há uma torre de cada e inimigos de todos, para veres logo a diferença. "
             "O círculo amarelo marca quem cada torre escolheu.",
}


# =====================================================================
#                    ONDE ESTA O CODIGO DE CADA COISA
# =====================================================================

def escolhas(fonte):
    arvore = ast.parse(fonte)
    lista = []

    no = blocos.instrucao(arvore, "INIMIGOS")
    partes = blocos.entradas(no) if no is not None else None
    if partes:
        for i, (chave, _, _) in enumerate(partes):
            nome = blocos.texto_constante(chave) or "Inimigo " + str(i + 1)
            lista.append({"id": "inimigo:" + str(i), "grupo": "Inimigos", "titulo": nome})

    no = blocos.instrucao(arvore, "TORRES")
    partes = blocos.entradas(no) if no is not None else None
    if partes:
        for i, (elemento, _, _) in enumerate(partes):
            nome = blocos.valor_da_chave(elemento, "nome") or "Torre " + str(i + 1)
            lista.append({"id": "torre:" + str(i), "grupo": "Torres", "titulo": nome})

    if blocos.instrucao(arvore, "MAPA") is not None:
        lista.append({"id": "mapa", "grupo": "Mapa", "titulo": "O mapa"})

    for nome in REGRAS:
        if blocos.funcao(arvore, nome) is not None:
            lista.append({"id": "regra:" + nome, "grupo": "Regras do jogo", "titulo": REGRAS[nome][0]})
    return lista


def regiao(fonte, escolha):
    # Devolve {"inicio", "fim", "ajuda", "titulo", "dica", "imagem"} ou None.
    # "imagem" e o nome do PNG que essa coisa usa (None se nao usa nenhum):
    # e com ele que a Oficina sabe onde guardar a imagem que a crianca escolher.
    arvore = ast.parse(fonte)
    linhas = fonte.split("\n")
    tipo, _, numero = escolha.partition(":")
    if tipo == "regra":
        # Uma regra e uma funcao inteira. A ajuda junta o que se pode usar
        # dentro de qualquer regra ao que o ficheiro diz sobre esta.
        no = blocos.funcao(arvore, numero) if numero in REGRAS else None
        if no is None:
            return None
        geral = blocos.comentarios_a_partir_de(linhas, INICIO_DAS_REGRAS)
        ajuda = blocos.ajuda_acima(linhas, no.lineno)
        if geral and geral != ajuda:
            ajuda = ajuda + "\n\n" + geral
        return {"inicio": no.lineno, "fim": no.end_lineno, "ajuda": ajuda, "dica": DICAS["regra"],
                "titulo": REGRAS[numero][0], "imagem": None, "sugestoes": SUGESTOES[numero]}
    nomes = {"inimigo": "INIMIGOS", "torre": "TORRES", "mapa": "MAPA"}
    if tipo not in nomes:
        return None
    no = blocos.instrucao(arvore, nomes[tipo])
    if no is None:
        return None
    resposta = {"ajuda": blocos.ajuda_acima(linhas, no.lineno), "dica": DICAS[tipo], "imagem": None,
                "sugestoes": SUGESTOES[tipo]}

    if tipo == "mapa":
        resposta.update(inicio=no.lineno, fim=no.end_lineno, titulo="O mapa")
        return resposta

    partes = blocos.entradas(no)
    if not partes or not numero.isdigit() or int(numero) >= len(partes):
        return None
    parte, inicio, fim = partes[int(numero)]
    if tipo == "inimigo":
        titulo = blocos.texto_constante(parte)
    else:
        titulo = blocos.valor_da_chave(parte, "nome")
    ficha = blocos.valor_da_entrada(no, int(numero))
    resposta.update(inicio=inicio, fim=fim, titulo=titulo or escolha,
                    imagem=blocos.valor_da_chave(ficha, "imagem"))
    return resposta


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


def _ver_numeros(ficha, quem, chaves, problemas):
    for chave in chaves:
        if chave not in ficha:
            problemas.append(quem + ': falta "' + chave + '".')
        elif not _numero(ficha[chave]):
            problemas.append(quem + ': "' + chave + '" tem de ser um número, sem aspas.')
        elif ficha[chave] < 0:
            problemas.append(quem + ': "' + chave + '" não pode ser menos que zero.')


def _ver_maximo(ficha, quem, chave, maximo, problemas):
    # Numeros gigantes nao rebentam o jogo: deixam-no preso a desenhar.
    if _numero(ficha.get(chave)) and ficha[chave] > maximo:
        problemas.append(quem + ': "' + chave + '" é grande demais para o ecrã. O máximo é ' + str(maximo) + ".")


def _ver_cor(ficha, quem, problemas):
    if "cor" not in ficha:
        problemas.append(quem + ': falta a "cor".')
    elif not _cor(ficha["cor"]):
        problemas.append(quem + ': a "cor" são três números de 0 a 255, como (200, 60, 60).')


def _ver_imagem(ficha, quem, problemas):
    if "imagem" in ficha and not isinstance(ficha["imagem"], str):
        problemas.append(quem + ': a "imagem" é o nome de um ficheiro, entre aspas, como "soldado.png".')


def _ver_inimigos(ns, problemas, avisos):
    inimigos = ns.get("INIMIGOS")
    if not isinstance(inimigos, dict) or len(inimigos) == 0:
        problemas.append("Tem de haver pelo menos um inimigo.")
        return
    for nome, ficha in inimigos.items():
        quem = str(nome)
        if not isinstance(nome, str):
            problemas.append("O nome de um inimigo tem de estar entre aspas.")
            continue
        if not isinstance(ficha, dict):
            problemas.append(quem + ": a ficha tem de estar entre { }.")
            continue
        _ver_numeros(ficha, quem, ["vida", "velocidade", "recompensa", "estrago", "tamanho"], problemas)
        _ver_maximo(ficha, quem, "tamanho", 300, problemas)
        _ver_maximo(ficha, quem, "velocidade", 100, problemas)
        if _numero(ficha.get("vida")) and 0 <= ficha["vida"] < 1:
            problemas.append(quem + ': a "vida" tem de ser pelo menos 1.')
        _ver_cor(ficha, quem, problemas)
        _ver_imagem(ficha, quem, problemas)
        forma = ficha.get("forma")
        if forma not in ("circulo", "quadrado"):
            avisos.append(quem + ': a "forma" só pode ser "circulo" ou "quadrado". Fica círculo.')

    ondas = ns.get("ONDAS")
    em_falta = []
    if isinstance(ondas, list):
        for onda in ondas:
            for grupo in onda if isinstance(onda, list) else []:
                nome = grupo.get("inimigo") if isinstance(grupo, dict) else None
                if nome not in inimigos and nome not in em_falta:
                    em_falta.append(nome)
    for nome in em_falta:
        avisos.append('As ONDAS ainda chamam por "' + str(nome) + '", que já não existe. '
                      "O jogo inteiro vai parar quando essa onda chegar.")


def _ver_torres(ns, problemas, avisos):
    torres = ns.get("TORRES")
    if not isinstance(torres, list) or len(torres) == 0:
        problemas.append("Tem de haver pelo menos uma torre.")
        return
    numero = 0
    for ficha in torres:
        numero = numero + 1
        if not isinstance(ficha, dict):
            problemas.append("A torre " + str(numero) + " tem de estar entre { }.")
            continue
        quem = ficha.get("nome")
        if not isinstance(quem, str):
            problemas.append("A torre " + str(numero) + ': o "nome" tem de ser um texto entre aspas.')
            quem = "Torre " + str(numero)
        if not isinstance(ficha.get("tecla"), int):
            problemas.append(quem + ': falta a "tecla", como pygame.K_1.')
        _ver_numeros(ficha, quem, ["custo", "alcance", "dano", "cadencia"], problemas)
        _ver_maximo(ficha, quem, "alcance", 2000, problemas)
        _ver_maximo(ficha, quem, "raio_explosao", 2000, problemas)
        _ver_cor(ficha, quem, problemas)
        _ver_imagem(ficha, quem, problemas)
        efeito = ficha.get("efeito")
        if efeito not in EFEITOS:
            problemas.append(quem + ': o "efeito" tem de ser "tiro", "explosao", "area" ou "golpe".')
        if efeito == "explosao":
            _ver_numeros(ficha, quem, ["raio_explosao"], problemas)
        if efeito == "area":
            _ver_numeros(ficha, quem, ["lentidao"], problemas)
    if len(torres) > 4:
        avisos.append("Só cabem 4 botões na barra de baixo: as outras torres escolhem-se só pela tecla.")


def _andar_pelo_mapa(mapa):
    # O mesmo passeio que o jogo faz em encontrar_caminho(): do E ate ao C.
    # Devolve quantos quadrados andou e se chegou.
    def letra(coluna, linha):
        if 0 <= linha < len(mapa) and 0 <= coluna < len(mapa[linha]):
            return mapa[linha][coluna]
        return " "

    atual = None
    for linha in range(len(mapa)):
        for coluna in range(len(mapa[linha])):
            if mapa[linha][coluna] == "E":
                atual = (coluna, linha)
    visitados = [atual]
    while letra(atual[0], atual[1]) != "C":
        andou = False
        for passo in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            vizinho = (atual[0] + passo[0], atual[1] + passo[1])
            if not andou and letra(vizinho[0], vizinho[1]) in ("#", "E", "C") and vizinho not in visitados:
                atual = vizinho
                visitados.append(atual)
                andou = True
        if not andou:
            return (len(visitados), False)
    return (len(visitados), True)


def _ver_mapa(ns, problemas, avisos):
    mapa = ns.get("MAPA")
    if not isinstance(mapa, list) or len(mapa) == 0:
        problemas.append("O MAPA tem de ser uma lista de linhas, entre [ ].")
        return
    for linha in mapa:
        if not isinstance(linha, str):
            problemas.append("Cada linha do MAPA tem de estar entre aspas e acabar com uma vírgula.")
            return
    tudo = "".join(mapa)
    if tudo.count("E") == 0:
        problemas.append("Falta o E: a entrada por onde os inimigos chegam.")
    if tudo.count("E") > 1:
        problemas.append("Só pode haver um E (uma entrada).")
    if tudo.count("C") == 0:
        problemas.append("Falta o C: o castelo, no fim do caminho.")
    if problemas:
        return
    passos, chegou = _andar_pelo_mapa(mapa)
    if not chegou:
        problemas.append("O caminho não chega ao C. Parou ao fim de " + str(passos) + " quadrados: "
                         "vê se há um buraco, ou se o caminho toca nele próprio.")
    estranhas = sorted(set(tudo) - set(".#ECT"))
    if estranhas:
        avisos.append("Letras que o mapa não conhece (ficam relva onde não se constrói): " + " ".join(estranhas))
    if len(mapa) > 13 or max(len(linha) for linha in mapa) > 20:
        avisos.append("O ecrã só mostra 20 letras de largura e 13 linhas. O resto fica de fora.")


def _ver_regras(ns, problemas, avisos):
    # O jogo chama cada regra pelo nome e da-lhe sempre as mesmas coisas.
    for nome in REGRAS:
        esperado = REGRAS[nome][1]
        funcao = ns.get(nome)
        como = "def " + nome + "(" + ", ".join(esperado) + "):"
        if not inspect.isfunction(funcao):
            problemas.append('"' + nome + '" tem de ser uma função. A primeira linha é: ' + como)
            continue
        recebe = list(inspect.signature(funcao).parameters)
        if len(recebe) != len(esperado):
            problemas.append("Esta função tem de receber " + ", ".join(esperado) + ", nem mais nem menos. "
                             "A primeira linha tem de ser: " + como)


# =====================================================================
#                              O PALCO
# =====================================================================

class Palco:

    def __init__(self, escolha):
        tipo, _, numero = escolha.partition(":")
        self.tipo = tipo
        self.numero = int(numero) if numero.isdigit() else 0
        self.preparado = False
        self.espera = 0          # frames ate ao proximo inimigo
        self.vez = 0             # qual o proximo inimigo, quando vem todos
        self.letra = None
        self.regra = numero if tipo == "regra" else None
        if tipo == "regra":
            # Uma regra nova so mostra o que vale quando chega a vez de ser
            # usada (a torre disparar, o golpe acertar): prova-se mais tempo.
            self.quadros_de_prova = 150

    def verificar(self, ns):
        problemas = []
        avisos = []
        _ver_inimigos(ns, problemas, avisos)
        _ver_torres(ns, problemas, avisos)
        _ver_mapa(ns, problemas, avisos)
        _ver_regras(ns, problemas, avisos)
        return problemas, avisos

    # --- Preparar e voltar a preparar ---

    def preparar(self, ns, pygame):
        ns["comecar_jogo"]()
        self.letra = pygame.font.SysFont(None, 22)
        self.preparado = True
        self.arrumar(ns)
        if self.tipo == "regra":
            self.espalhar_inimigos(ns)

    def ao_mudar(self, ns):
        # O codigo mudou. Os inimigos que andavam no ecra foram feitos com
        # os numeros antigos, por isso saem e vem outros novos.
        if not self.preparado:
            return
        if self.tipo == "mapa":
            ns["CAMINHO_PONTOS"] = ns["encontrar_caminho"]()
        ns["inimigos"] = []
        ns["projeteis"] = []
        ns["efeitos"] = []
        self.espera = 0
        self.arrumar(ns)
        if self.tipo == "regra":
            self.espalhar_inimigos(ns)

    def espalhar_inimigos(self, ns):
        # Para a regra nova ter logo trabalho: inimigos ja a meio do caminho,
        # ao pe das torres, em vez de esperar que eles la cheguem.
        pontos = ns["CAMINHO_PONTOS"]
        nomes = list(ns["INIMIGOS"])
        for i in range(6):
            indice = min(len(pontos) - 2, int(len(pontos) * (0.08 + 0.13 * i)))
            inimigo = ns["criar_inimigo"](nomes[i % len(nomes)])
            inimigo["x"] = pontos[indice][0]
            inimigo["y"] = pontos[indice][1]
            inimigo["ponto"] = indice + 1
            inimigo["andado"] = indice * ns["TILE"]
            ns["inimigos"].append(inimigo)

    def arrumar(self, ns):
        # Tira as torres que ja nao fazem sentido e garante que ha uma.
        boas = []
        for torre in ns["torres"]:
            if torre["tipo"] < len(ns["TORRES"]) and ns["letra_do_mapa"](torre["coluna"], torre["linha"]) == ".":
                boas.append(torre)
        ns["torres"] = boas
        ns["torre_escolhida"] = None
        if ns["torre_para_construir"] >= len(ns["TORRES"]):
            ns["torre_para_construir"] = 0

        if self.tipo == "mapa":
            return
        if self.tipo == "regra":
            # Uma torre de cada, espalhadas pelo caminho, prontas a disparar.
            for tipo in range(min(4, len(ns["TORRES"]))):
                if len([torre for torre in ns["torres"] if torre["tipo"] == tipo]) == 0:
                    self.construir(ns, tipo, 0.12 + 0.2 * tipo)
            for torre in ns["torres"]:
                torre["recarga"] = min(torre["recarga"], 20)
            return
        minha = 0
        if self.tipo == "torre":
            minha = min(self.numero, len(ns["TORRES"]) - 1)
            ns["torre_para_construir"] = minha
        da_minha = [torre for torre in ns["torres"] if torre["tipo"] == minha]
        if len(da_minha) == 0:
            self.construir(ns, minha)
            da_minha = [torre for torre in ns["torres"] if torre["tipo"] == minha]
        if self.tipo == "torre" and len(da_minha) > 0:
            ns["torre_escolhida"] = da_minha[0]   # fica com o alcance a vista

    def construir(self, ns, tipo, onde=0.25):
        # Procura um quadrado de relva colado ao caminho, mais ou menos a
        # um quarto do percurso (ou "onde", de 0 a 1), e constroi la com a
        # funcao do jogo.
        pontos = ns["CAMINHO_PONTOS"]
        ocupados = [(torre["coluna"], torre["linha"]) for torre in ns["torres"]]
        primeiro = int(len(pontos) * onde)
        for i in range(len(pontos)):
            ponto = pontos[(primeiro + i) % len(pontos)]
            coluna = ponto[0] // ns["TILE"]
            linha = (ponto[1] - ns["TOPO"]) // ns["TILE"]
            for passo in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                c = coluna + passo[0]
                l = linha + passo[1]
                if 0 <= c < 20 and 0 <= l < 13 and ns["letra_do_mapa"](c, l) == "." and (c, l) not in ocupados:
                    antes = ns["torre_para_construir"]
                    ns["torre_para_construir"] = tipo
                    ns["ouro"] = 99999
                    ns["construir"](c, l)
                    ns["torre_para_construir"] = antes
                    return

    # --- Todos os frames ---

    def quadro(self, ns, pygame):
        if not self.preparado:
            self.preparar(ns, pygame)

        # O jogo fica sempre "a meio": sem menu, sem ondas, sem perder.
        ns["estado"] = "jogo"
        ns["ouro"] = 99999
        ns["vidas"] = 99
        ns["numero_onda"] = 1
        ns["onda_a_decorrer"] = False
        ns["a_por_sair"] = []

        nomes = list(ns["INIMIGOS"])
        if not ns["pausa"]:
            self.espera = self.espera - ns["velocidade_jogo"]
        if self.espera <= 0:
            if self.tipo == "inimigo":
                nome = nomes[min(self.numero, len(nomes) - 1)]
                iguais = [inimigo for inimigo in ns["inimigos"] if inimigo["nome"] == nome]
                if len(iguais) < 4:
                    ns["inimigos"].append(ns["criar_inimigo"](nome))
                self.espera = 150
            else:
                if len(ns["inimigos"]) < 25:
                    ns["inimigos"].append(ns["criar_inimigo"](nomes[self.vez % len(nomes)]))
                    self.vez = self.vez + 1
                self.espera = 55

        self.desenhar(ns, pygame, nomes)

    def desenhar(self, ns, pygame, nomes):
        ecra = ns["ecra"]
        pygame.draw.rect(ecra, ns["PAINEL"], (0, 0, ns["LARGURA"], ns["TOPO"]))
        pygame.draw.rect(ecra, ns["AMARELO"], (0, 0, 6, ns["TOPO"]))

        texto = ""
        if self.tipo == "inimigo":
            nome = nomes[min(self.numero, len(nomes) - 1)]
            ficha = ns["INIMIGOS"][nome]
            texto = nome + ":   vida " + str(ficha["vida"]) + "   velocidade " + str(ficha["velocidade"])
            texto = texto + "   recompensa " + str(ficha["recompensa"]) + "   estrago " + str(ficha["estrago"])
            modelo = ns["criar_inimigo"](nome)
            self.lupa(ns, pygame, ns["desenhar_inimigo"], modelo, ficha["tamanho"] + 16)
        elif self.tipo == "torre":
            tipo = min(self.numero, len(ns["TORRES"]) - 1)
            ficha = ns["TORRES"][tipo]
            texto = ficha["nome"] + ":   custo " + str(ficha["custo"]) + "   alcance " + str(ficha["alcance"])
            texto = texto + "   dano " + str(ficha["dano"]) + "   cadência " + str(ficha["cadencia"])
            texto = texto + "   efeito " + str(ficha["efeito"])
            modelo = {"tipo": tipo, "nivel": 1, "x": 0, "y": 0, "mira": (1, 0)}
            self.lupa(ns, pygame, ns["desenhar_torre"], modelo, ns["TILE"] + 8)
        elif self.tipo == "regra":
            texto = "Regra:   " + REGRAS[self.regra][0] + "   (a função " + self.regra + ")"
            # Um circulo a volta de quem cada torre escolheu agora.
            for torre in ns["torres"]:
                alvo = ns["escolher_alvo"](torre)
                if isinstance(alvo, dict) and "x" in alvo and "y" in alvo:
                    pygame.draw.circle(ecra, ns["AMARELO"], (int(alvo["x"]), int(alvo["y"])), 16, 2)
        elif self.tipo == "mapa":
            mapa = ns["MAPA"]
            texto = "Mapa:   " + str(max(len(linha) for linha in mapa)) + " letras de largura   "
            texto = texto + str(len(mapa)) + " linhas   caminho com " + str(len(ns["CAMINHO_PONTOS"])) + " quadrados"

        desenho = self.letra.render(texto, True, ns["BRANCO"])
        ecra.blit(desenho, (18, 12))

    def lupa(self, ns, pygame, desenhar, modelo, lado):
        # Desenha a coisa numa folha pequena, com a funcao do proprio jogo,
        # e mostra essa folha aumentada no canto.
        lado = int(max(24, min(lado, 110)))
        folha = pygame.Surface((lado, lado))
        folha.fill(ns["RELVA"])
        modelo["x"] = lado // 2
        modelo["y"] = lado // 2
        if "mira" in modelo:
            modelo["mira"] = (lado, lado // 2)
        ecra = ns["ecra"]
        ns["ecra"] = folha
        try:
            desenhar(modelo)
        finally:
            ns["ecra"] = ecra
        grande = pygame.transform.scale(folha, (110, 110))
        caixa = pygame.Rect(ns["LARGURA"] - 122, ns["TOPO"] + 8, 114, 114)
        pygame.draw.rect(ecra, ns["PAINEL"], caixa.inflate(6, 6), border_radius=6)
        ecra.blit(grande, (caixa.x + 2, caixa.y + 2))
        pygame.draw.rect(ecra, ns["AMARELO"], caixa.inflate(6, 6), 2, border_radius=6)


def criar_palco(escolha):
    return Palco(escolha)
