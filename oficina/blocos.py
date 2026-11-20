# Ferramentas para encontrar "um bocado" dentro do ficheiro de um jogo:
# a ficha de um inimigo, uma torre, o mapa. Usa o modulo ast, que le o
# Python como o proprio Python o le, por isso nao se engana com comentarios
# nem com aspas.
#
# As linhas contam-se a partir de 1, e as regioes incluem a primeira e a
# ultima linha.

import ast


def instrucao(arvore, nome):
    # A instrucao "NOME = ..." escrita encostada a margem, ou None.
    for no in arvore.body:
        if isinstance(no, ast.Assign) and len(no.targets) == 1:
            alvo = no.targets[0]
            if isinstance(alvo, ast.Name) and alvo.id == nome:
                return no
    return None


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


def nos_da_regiao(arvore, inicio, fim):
    # As instrucoes inteiras que tocam na regiao. Se a regiao e so a ficha
    # do Soldado, a instrucao inteira e "INIMIGOS = {...}".
    return [no for no in arvore.body if no.lineno <= fim and no.end_lineno >= inicio]
