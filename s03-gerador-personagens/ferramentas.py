# =====================================================================
# FERRAMENTAS — codigo escrito por outra pessoa, para tu usares.
#
# Nao precisas de perceber o que esta aqui dentro. Precisas de saber o
# que cada funcao PEDE e o que cada funcao DEVOLVE. E isso esta escrito
# aqui em baixo.
#
# Para usar, poe no topo do teu ficheiro:
#     import ferramentas
#
# E depois chama assim:
#     ferramentas.barra(7, 10)
#     ferramentas.moldura("TITULO", ["linha 1", "linha 2"])
# =====================================================================


def barra(valor, maximo):
    """Desenha uma barra de progresso em texto.

    PEDE:     valor  - quanto esta preenchido (numero)
              maximo - o total possivel (numero)
    DEVOLVE:  um texto, por exemplo  "[#######---] 7/10"

    Exemplo:  ferramentas.barra(7, 10)
    """
    cheios = round(valor * 10 / maximo)
    if cheios > 10:
        cheios = 10
    if cheios < 0:
        cheios = 0
    vazios = 10 - cheios
    return "[" + "#" * cheios + "-" * vazios + "] " + str(valor) + "/" + str(maximo)


def moldura(titulo, linhas):
    """Poe um titulo e varias linhas de texto dentro de uma moldura.

    PEDE:     titulo - um texto
              linhas - uma LISTA de textos
    DEVOLVE:  um texto com varias linhas, ja com a moldura desenhada

    Exemplo:  ferramentas.moldura("FICHA", ["Nome: Rita", "Nivel: 3"])
    """
    largura = len(titulo)
    for linha in linhas:
        if len(linha) > largura:
            largura = len(linha)

    topo = "+" + "-" * (largura + 2) + "+"
    resultado = topo + "\n"
    resultado = resultado + "| " + titulo.ljust(largura) + " |\n"
    resultado = resultado + "+" + "-" * (largura + 2) + "+\n"
    for linha in linhas:
        resultado = resultado + "| " + linha.ljust(largura) + " |\n"
    resultado = resultado + topo
    return resultado
