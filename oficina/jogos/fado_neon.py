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

import ast
import math
import sys

import blocos

NOME = "FADO//NEON"
FICHEIRO = "s10-jogo-do-ano/fado-neon.py"
DESCRICAO = "Um roguelite de saudade e neon. Jogo do Ano 2026."

# Uma frase por grupo, para a pagina do jogo dizer o que la ha.
SOBRE_OS_GRUPOS = {
    "Inimigos": "Tamanho, vida, velocidade, cor. Podes pôr uma imagem tua.",
    "Tu": "As tuas vidas, os tiros, a investida e o laser.",
    "Ondas": "Quantas ondas há e como vão ficando mais difíceis.",
    "Cartas": "As melhorias que aparecem entre as ondas.",
    "Textos": "As frases que o jogo diz.",
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
    ("vidas", "Tu", "Vidas e velocidade"),
    ("tiros", "Tu", "Os teus tiros"),
    ("dash", "Tu", "Investida e dano"),
    ("laser", "Tu", "Laser e corações"),
    ("jogo", "Ondas", "Quantas ondas"),
    ("ondas", "Ondas", "Quantos inimigos"),
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
    "investida": "o chefe chama por ele",
    "pequeno": "é o que sai de um divisor quando rebenta",
}
COM_COMPORTAMENTO = ["corredor", "atirador", "divisor", "pequeno", "investida"]

# As cartas a que a funcao escolher() do jogo sabe dar um efeito.
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
COM_TIRO_AUTOMATICO = ["inimigo", "chefe", "tiros", "laser", "jogo", "ondas", "carta"]
# Onde o jogador pode perder coracoes (quando ficam a zero, volta a nascer).
PODE_LEVAR_DANO = ["vidas", "dash", "tiros", "laser"]

JOGAR = "Clica no jogo para jogares: WASD anda, as setas disparam, Espaço investe, E é o laser."

DICAS = {
    "inimigo": "Estão sempre a chegar mais destes, e tu disparas sozinho (a tecla T desliga isso). "
               "No palco não perdes vidas. " + JOGAR,
    "chefe": "O Saudosista está sempre na arena: quando cai, vem outro. Disparas sozinho e "
             "não perdes vidas. A barra lá em cima é a vida dele.",
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
        if tipo in BLOCOS:
            existe = any(blocos.instrucao(arvore, nome) is not None for nome in BLOCOS[tipo])
        else:
            existe = blocos.instrucao(arvore, TEXTOS[tipo]) is not None
        if existe:
            lista.append({"id": tipo, "grupo": grupo, "titulo": titulo})

    no = blocos.instrucao(arvore, "MELHORIAS")
    partes = blocos.entradas(no) if no is not None else None
    if partes:
        for i, (elemento, _, _) in enumerate(partes):
            nome = _nome_da_carta(elemento) or "Carta " + str(i + 1)
            lista.append({"id": "carta:" + str(i), "grupo": "Cartas", "titulo": nome})

    # Os grupos ficam juntos, pela ordem em que apareceram pela primeira vez.
    ordem = []
    for escolha in lista:
        if escolha["grupo"] not in ordem:
            ordem.append(escolha["grupo"])
    lista.sort(key=lambda escolha: ordem.index(escolha["grupo"]))
    return lista


def regiao(fonte, escolha):
    # Devolve {"inicio", "fim", "ajuda", "titulo", "dica", "imagem"} ou None.
    # "imagem" e o nome do PNG que essa coisa usa (None se nao usa nenhum):
    # neste jogo so os inimigos de PERFIS e que tem imagem.
    arvore = ast.parse(fonte)
    linhas = fonte.split("\n")
    tipo, _, numero = escolha.partition(":")
    if tipo not in DICAS:
        return None
    resposta = {"dica": DICAS[tipo], "imagem": None}

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
    else:
        titulo = _nome_da_carta(parte)
    resposta.update(inicio=inicio, fim=fim, titulo=titulo or escolha,
                    ajuda=blocos.ajuda_acima(linhas, no.lineno))
    return resposta


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
        if "imagem" in ficha and not isinstance(ficha["imagem"], str):
            problemas.append(quem + ': a "imagem" é o nome de um ficheiro, entre aspas, como "corredor.png".')
        if nome not in COM_COMPORTAMENTO:
            avisos.append(quem + ": o jogo não sabe o que este faz, por isso fica parado. O que "
                          "cada inimigo faz depende do nome (corredor, atirador, divisor, investida).")
    for nome, razao in INIMIGOS_PRECISOS.items():
        if nome not in perfis:
            problemas.append('Tem de haver um inimigo chamado "' + nome + '": ' + razao + ".")
    if not problemas and not na_onda_1:
        avisos.append('Nenhum inimigo tem "desde_onda": 1 e custo acima de 0: a onda 1 fica vazia.')


def _ver_cartas(ns, problemas, avisos):
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
        elif ident not in CARTAS_COM_EFEITO:
            avisos.append(quem + ': o jogo não conhece o id "' + ident + '", por isso a carta não faz '
                          "nada. O que cada carta faz está na função escolher() do jogo.")
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

    def verificar(self, ns):
        problemas = []
        avisos = []
        _ver_numeros(ns, problemas, avisos)
        _ver_perfis(ns, problemas, avisos)
        _ver_cartas(ns, problemas, avisos)
        _ver_textos(ns, problemas, avisos)
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
        if self.tipo in ("jogo", "ondas"):
            jogo.novo_jogo()
            return
        jogo.limpar_mundo()
        jogo.estado = "jogo"
        jogo.onda = 1
        jogo.fase = "combate"
        if self.tipo == "chefe":
            self.novo_chefe(ns)
        elif self.tipo == "laser":
            jogo.farol = 1.0
        elif self.tipo == "carta":
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
        if self.tipo in ("jogo", "ondas"):
            self.comecar(ns)
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

        if tipo in ("jogo", "ondas"):
            # O jogo verdadeiro, a jogar-se sozinho: escolhe uma carta se
            # ninguem escolher, e quando ganha comeca outra vez.
            self.sem_dano()
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

        if tipo == "carta":
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
        elif tipo in ELENCO:
            self.mandar_vir(ns, ELENCO[tipo], 6 if tipo == "laser" else 4)
        else:
            self.segurar_fila(ns)

        if tipo == "chefe" and jogo.chefe is None:
            # Caiu. Passado um bocadinho vem outro.
            self.espera = self.espera - 1
            if self.espera <= 0:
                self.novo_chefe(ns)
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
        self.faixa(ns, pygame, texto)

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
        folha = pygame.Surface((lado, lado))
        folha.fill(ns["FUNDO"])
        modelo.desenhar(folha, ns["Vector2"](0, 0))
        grande = pygame.transform.smoothscale(folha, (104, 104))
        ecra = self.jogo.ecra
        caixa = pygame.Rect(ns["LARGURA"] - 122, ns["ALTURA"] - 208, 108, 108)
        ecra.blit(grande, (caixa.x + 2, caixa.y + 2))
        pygame.draw.rect(ecra, ns["AMARELO"], caixa, 2, border_radius=6)


def criar_palco(escolha):
    return Palco(escolha)
