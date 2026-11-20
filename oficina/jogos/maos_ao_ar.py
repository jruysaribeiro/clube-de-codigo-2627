# O Maos ao Ar! na Oficina: que coisas se podem escolher, onde esta o
# codigo de cada uma, e o "palco" que mostra so essa coisa a funcionar.
#
# O palco nao e um jogo a parte: e o Maos ao Ar! verdadeiro a correr, ja
# dentro de um nivel, sem titulo, sem treino e sem se poder perder. Por
# isso tudo o que se ve e desenhado pelo codigo do proprio jogo.
#
# Na Oficina nao ha camara: joga-se com o teclado, no modo que o jogo ja
# tem para isso (o da tecla T). Para o jogo nem tentar ligar a camara, nem
# instalar o mediapipe, pomos a variavel MAOS_AO_AR_SO_TECLADO a "1" antes
# de ele arrancar (ver criar_palco, no fim, e SO_TECLADO no jogo).

import ast
import os

import blocos

NOME = "Mãos ao Ar!"
FICHEIRO = "s14-maos-ao-ar/maos-ao-ar.py"
DESCRICAO = "Um jogo de plataformas. Aqui joga-se com o teclado."

# Uma frase por grupo, para a pagina do jogo dizer o que la ha.
SOBRE_OS_GRUPOS = {
    "Inimigos": "Vida, velocidade, tamanho, cor. Podes pôr uma imagem tua.",
    "O herói": "As cores do Faísca, ou uma imagem tua.",
    "Mundos": "As cores de cada mundo.",
    "Afinar o jogo": "Os saltos, as velocidades, as vidas, as cores e os textos.",
    "Níveis": "Cada nível é desenhado com letras: muda uma letra e muda o nível.",
}

# As letras que o mapa de um nivel conhece, fora as dos inimigos.
LETRAS_DO_MAPA = ".#=%BM^~ohPFc"
JEITOS = ["andar", "saltar", "voar", "carregar", "canhao", "chefe"]
# Em que lista do jogo esta cada tipo de coisa.
LISTAS = {"inimigo": "INIMIGOS", "mundo": "MUNDOS", "nivel": "NIVEIS"}

# Os grupos de constantes que se abrem de uma vez: da primeira a ultima.
NUMEROS = ["VIDAS", "VEL_ANDAR", "VEL_CORRER", "GRAVIDADE", "FORCA_SALTO", "FORCA_MOLA",
           "TEMPO_ENTRE_TIROS", "VEL_TIRO", "ALCANCE_TIRO", "TEMPO_COIOTE", "TOLERANCIA_SALTO"]
CORES = ["BRANCO", "PRETO", "CINZA", "AMARELO", "VERMELHO", "VERDE", "AZUL", "LARANJA",
         "COR_HEROI", "COR_HEROI_ESCURA", "COR_TIRO", "COR_MOEDA", "COR_MADEIRA",
         "COR_PONTE_PODRE", "COR_LAVA", "COR_ESPINHO"]
TEXTOS = ["TITULO", "SUBTITULO", "NOME_DO_HEROI", "TEXTO_VITORIA"]
GRUPOS = {
    "heroi": ["IMAGEM_DO_HEROI", "COR_HEROI", "COR_HEROI_ESCURA"],
    "numeros": NUMEROS,
    "cores": CORES,
    "textos": TEXTOS,
}
TITULOS = {"numeros": "Os números do jogo", "cores": "As cores", "textos": "Os textos"}

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
    "inimigo": TECLAS + "Ele está atrás de um caixote: salta-o, ou parte-o com um tiro.",
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
}
AJUDAS = {
    "numeros": "Os números que mandam no Faísca. As velocidades são em pixeis por frame "
               "(60 frames = um segundo) e cada quadrado do mapa tem 48 pixeis.",
    "textos": "O que o jogo escreve no ecrã. Os textos ficam entre aspas.",
}


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


def _ajuda(linhas, primeira_linha):
    # A explicacao que o ficheiro traz por cima, sem as linhas so de tracos.
    ajuda = []
    for linha in blocos.ajuda_acima(linhas, primeira_linha).split("\n"):
        if linha.startswith("---"):
            linha = linha.strip("- ")
        if linha != "" or (len(ajuda) > 0 and ajuda[-1] != ""):
            ajuda.append(linha)
    return "\n".join(ajuda).strip("\n")


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

    for i, (_, ficha, _, _) in enumerate(_fichas(arvore, "MUNDOS")):
        nome = _valor(ficha, "nome") or "Mundo " + str(i + 1)
        lista.append({"id": "mundo:" + str(i), "grupo": "Mundos", "titulo": str(nome)})

    for tipo in ("numeros", "cores", "textos"):
        if len(_constantes(arvore, GRUPOS[tipo])) > 0:
            lista.append({"id": tipo, "grupo": "Afinar o jogo", "titulo": TITULOS[tipo]})

    fichas = _fichas(arvore, "NIVEIS")
    for i in range(len(fichas)):
        lista.append({"id": "nivel:" + str(i), "grupo": "Níveis", "titulo": _nome_do_nivel(fichas, i)})
    return lista


def regiao(fonte, escolha):
    # Devolve {"inicio", "fim", "ajuda", "titulo", "dica", "imagem"} ou None.
    # "imagem" e o nome do PNG que essa coisa usa (None se nao usa nenhum):
    # e com ele que a Oficina sabe onde guardar a imagem que a crianca escolher.
    arvore = ast.parse(fonte)
    linhas = fonte.split("\n")
    tipo, _, numero = escolha.partition(":")
    if tipo not in DICAS:
        return None
    resposta = {"dica": DICAS[tipo], "imagem": None}

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
        resposta.update(inicio=inicio, fim=fim, titulo=titulo,
                        ajuda=AJUDAS.get(tipo) or _ajuda(linhas, inicio))
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
    no = blocos.instrucao(arvore, LISTAS[tipo])
    resposta.update(inicio=inicio, fim=fim, titulo=str(titulo), ajuda=_ajuda(linhas, no.lineno))
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

    def verificar(self, ns):
        problemas = []
        avisos = []
        _ver_constantes(ns, problemas, avisos)
        _ver_inimigos(ns, problemas, avisos)
        _ver_mundos(ns, problemas, avisos)
        if self.tipo == "nivel":
            _ver_nivel(ns, self.numero, problemas, avisos)
        if self.tipo == "inimigo":
            _ver_letras_sem_dono(ns, avisos)
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
            # O primeiro nivel que se passa nesse mundo (cada mundo tem 5).
            indice = 0
            for i in range(len(ns["NIVEIS"])):
                if (ns["numero_do_nivel"](i) - 1) // 5 == self.numero:
                    indice = i
                    break
            ns["comecar_nivel"](indice)
            nivel["mundo"] = self.o_mundo(ns)
        elif self.tipo == "inimigo":
            letra = self.a_letra(ns)
            self.montar_arena(ns, arena_do_inimigo(letra, ns["INIMIGOS"][letra]))
        elif self.tipo == "numeros":
            self.montar_arena(ns, pista(ns))
        else:
            self.montar_arena(ns, montra(ns))
        nivel["da_oficina"] = True       # o jogo apaga isto se carregar outro nivel
        self.mapa_pequeno = None
        self.contar(ns)

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

        # Nunca se perde: antes do ultimo coracao, voltam todos.
        if jogo["fase"] == "perdeu":
            jogo["fase"] = "jogar"
            ns["repor_heroi"](nivel["ponto"][0], nivel["ponto"][1])
            heroi["invencivel"] = 110
            heroi["vidas"] = ns["VIDAS"]
            outro_ecra = True
        if heroi["vidas"] < 2:
            heroi["vidas"] = ns["VIDAS"]

        if outro_ecra:
            # O jogo ja tinha desenhado este frame (o titulo, o "Quase!"...):
            # desenha-se por cima o nivel, para esse ecra nem se chegar a ver.
            parado = {"direcao": 0, "andar": False, "correr": False, "saltar": False, "disparar": False}
            ns["desenhar_jogo"](ns["ler_mao"](), parado)
        if self.tipo == "textos":
            jogo["fase"] = "pausa"       # parado por baixo; por cima, o titulo
            ns["desenhar_titulo"](ns["ler_mao"]())

        if self.tipo in ("nivel", "mundo", "numeros"):
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

        if texto != "":
            ecra = ns["janela"]["ecra"]
            fundo = ns["ALTURA"] - 30
            pygame.draw.rect(ecra, (30, 30, 48), (0, fundo, ns["LARGURA"], 30))
            pygame.draw.rect(ecra, ns["AMARELO"], (0, fundo, 6, 30))
            ecra.blit(self.letra.render(texto, True, (245, 245, 245)), (18, fundo + 8))

    def quadrados(self, quantos):
        return str(round(quantos, 1))

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
