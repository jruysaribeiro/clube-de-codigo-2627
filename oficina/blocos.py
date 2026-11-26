# Ferramentas para encontrar "um bocado" dentro do ficheiro de um jogo:
# a ficha de um inimigo, uma torre, o mapa. Usa o modulo ast, que le o
# Python como o proprio Python o le, por isso nao se engana com comentarios
# nem com aspas.
#
# As linhas contam-se a partir de 1, e as regioes incluem a primeira e a
# ultima linha.

import ast
import os


def instrucao(arvore, nome):
    # A instrucao "NOME = ..." escrita encostada a margem, ou None.
    for no in arvore.body:
        if isinstance(no, ast.Assign) and len(no.targets) == 1:
            alvo = no.targets[0]
            if isinstance(alvo, ast.Name) and alvo.id == nome:
                return no
    return None


def funcao(arvore, nome):
    # A funcao "def nome(...)" escrita encostada a margem, ou None.
    for no in arvore.body:
        if isinstance(no, ast.FunctionDef) and no.name == nome:
            return no
    return None


def comentarios_a_partir_de(linhas, inicio):
    # O bloco de comentarios que comeca na linha que diz "inicio", sem os #.
    for i, linha in enumerate(linhas):
        if linha.strip() == inicio:
            fim = i
            while fim < len(linhas) and linhas[fim].lstrip().startswith("#"):
                fim = fim + 1
            return ajuda_acima(linhas, fim + 1)
    return ""


def entradas(no):
    # As entradas de uma lista [...] ou de um dicionario {...}:
    # devolve [(valor_ou_chave, primeira_linha, ultima_linha), ...].
    # Devolve None se nao der para as separar linha a linha (duas entradas
    # na mesma linha, por exemplo).
    valor = no.value
    if isinstance(valor, ast.Dict):
        partes = []
        for chave, conteudo in zip(valor.keys, valor.values):
            if chave is None:
                return None
            partes.append((chave, chave.lineno, conteudo.end_lineno))
    elif isinstance(valor, ast.List):
        partes = [(elemento, elemento.lineno, elemento.end_lineno) for elemento in valor.elts]
    else:
        return None

    anterior = no.lineno
    for _, primeira, ultima in partes:
        if primeira <= anterior:
            return None
        anterior = ultima
    if partes and partes[-1][2] >= no.end_lineno:
        return None
    return partes


def valor_da_entrada(no, indice):
    # O que esta escrito na entrada numero "indice" (a contar do 0) de uma
    # lista [...] ou de um dicionario {...}: num dicionario e o valor, nao a
    # chave. Devolve None se nao houver.
    valor = no.value
    if isinstance(valor, ast.Dict):
        valores = valor.values
    elif isinstance(valor, ast.List):
        valores = valor.elts
    else:
        return None
    if 0 <= indice < len(valores):
        return valores[indice]
    return None


def texto_constante(no):
    if isinstance(no, ast.Constant) and isinstance(no.value, str):
        return no.value
    return None


def valor_da_chave(dicionario, chave):
    # Dentro de um {...} escrito no codigo, o texto guardado em "chave".
    if not isinstance(dicionario, ast.Dict):
        return None
    for k, v in zip(dicionario.keys, dicionario.values):
        if texto_constante(k) == chave:
            return texto_constante(v)
    return None


def ajuda_acima(linhas, primeira_linha):
    # Os comentarios colados por cima de uma instrucao: e a explicacao que
    # o ficheiro ja traz, e que mostramos ao lado do codigo.
    fim = primeira_linha - 2
    i = fim
    while i >= 0 and linhas[i].lstrip().startswith("#"):
        i = i - 1
    ajuda = []
    for linha in linhas[i + 1:fim + 1]:
        linha = linha.lstrip()[1:]
        if linha.startswith(" "):
            linha = linha[1:]
        ajuda.append(linha.rstrip())
    return "\n".join(ajuda)


def margem_comum(linhas):
    # Os espacos que todas as linhas tem no inicio (as vazias nao contam).
    margem = None
    for linha in linhas:
        if linha.strip() == "":
            continue
        espacos = linha[:len(linha) - len(linha.lstrip())]
        if margem is None or len(espacos) < len(margem):
            margem = espacos
    return margem or ""


def tirar_margem(linhas, margem):
    return [linha[len(margem):] if linha.startswith(margem) else linha.lstrip() for linha in linhas]


def por_margem(linhas, margem):
    return [margem + linha if linha.strip() != "" else "" for linha in linhas]


def nomes_dados(arvore):
    # Os nomes a que o ficheiro da um valor encostado a margem: "MAPA = ...",
    # "VIDAS = 3". Serve para dar por uma linha dessas que foi apagada.
    nomes = []
    for no in arvore.body:
        if isinstance(no, ast.Assign):
            for alvo in no.targets:
                if isinstance(alvo, ast.Name) and alvo.id not in nomes:
                    nomes.append(alvo.id)
    return nomes


def nomes_das_funcoes(arvore):
    # Os nomes das funcoes escritas encostadas a margem.
    return [no.name for no in arvore.body if isinstance(no, ast.FunctionDef)]


def repetidos(antes, agora):
    # As frases a mostrar por cada nome que passou a estar escrito mais vezes
    # encostado a margem ("VIDAS = 3" duas vezes, duas funcoes com o mesmo
    # nome). O Python fica com a ultima, e a Oficina so mostra a primeira: a
    # outra ficava no ficheiro, escondida, a mandar no jogo.
    def contar(arvore):
        contas = {}
        for no in arvore.body:
            if isinstance(no, ast.Assign):
                nomes = [("linha", alvo.id) for alvo in no.targets if isinstance(alvo, ast.Name)]
            elif isinstance(no, ast.FunctionDef):
                nomes = [("funcao", no.name)]
            else:
                nomes = []
            for nome in nomes:
                contas[nome] = contas.get(nome, 0) + 1
        return contas
    havia = contar(antes)
    frases = []
    for (tipo, nome), vezes in contar(agora).items():
        if vezes > 1 and vezes > havia.get((tipo, nome), 0):
            if tipo == "linha":
                frases.append('Há mais do que uma linha "' + nome + ' = ...". Só pode haver uma: apaga a que está a mais.')
            else:
                frases.append('Há mais do que uma função chamada "' + nome + '". Só pode haver uma: '
                              "apaga a que está a mais, ou dá-lhe outro nome.")
    return frases


# O que o codigo escrito na Oficina nao pode fazer: ir buscar outros modulos,
# mexer em ficheiros, correr outros programas. Um jogo nao precisa de nada
# disto, e um engano (da crianca ou do ajudante) podia estragar o computador.
# Nao e uma muralha a prova de tudo: e uma vedacao contra o que e obvio.
NOMES_PROIBIDOS = {
    "open", "exec", "eval", "compile", "__import__", "input", "breakpoint", "exit", "quit",
    "globals", "locals", "vars", "getattr", "setattr", "delattr",
    "os", "sys", "subprocess", "shutil", "socket", "pathlib", "Path", "importlib",
}


def proibidos(nos):
    # As frases a mostrar, uma por cada coisa proibida que o codigo usa.
    frases = []

    def juntar(frase):
        if frase not in frases:
            frases.append(frase)

    for raiz in nos:
        for no in ast.walk(raiz):
            if isinstance(no, (ast.Import, ast.ImportFrom)):
                juntar('Aqui não se pode usar "import". O jogo já tem tudo o que precisa.')
            elif isinstance(no, ast.Name) and no.id in NOMES_PROIBIDOS:
                juntar('Aqui não se pode usar "' + no.id + '": serve para mexer no computador, não no jogo.')
            elif isinstance(no, ast.Attribute) and no.attr.startswith("__"):
                juntar('Aqui não se pode usar "' + no.attr + '".')
    return frases


def nos_da_regiao(arvore, inicio, fim):
    # As instrucoes inteiras que tocam na regiao. Se a regiao e so a ficha
    # do Soldado, a instrucao inteira e "INIMIGOS = {...}".
    return [no for no in arvore.body if no.lineno <= fim and no.end_lineno >= inicio]


def corpo_livre(escrito, corpo, fins=(".png", ".wav")):
    # Uma coisa nova fica com ficheiros so dela. Recebe o codigo todo do jogo
    # e o nome que os ficheiros teriam ("bicho-novo") e devolve esse nome ou,
    # se ja houver "bicho-novo.png" (escrito no codigo, ou nas pastas das
    # imagens e dos sons), o primeiro que estiver livre: "bicho-novo-2".
    # Senao, a quem mudasse o nome ao primeiro bicho novo e criasse outro, os
    # dois ficavam a partilhar a imagem: desenhar um mudava o outro.
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pastas = [os.path.join(raiz, "comum", "assets", "imagens"), os.path.join(raiz, "comum", "assets", "sons")]

    def ocupado(nome):
        return '"' + nome + '"' in escrito or any(os.path.exists(os.path.join(pasta, nome)) for pasta in pastas)
    tentativa = corpo
    numero = 2
    while any(ocupado(tentativa + fim) for fim in fins):
        tentativa = corpo + "-" + str(numero)
        numero = numero + 1
    return tentativa
