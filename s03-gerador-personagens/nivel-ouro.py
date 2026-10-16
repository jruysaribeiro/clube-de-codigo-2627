# Sessao 3 — 🥇 OURO
# Cinco personagens numa tabela alinhada, 20 pontos distribuidos pelos
# atributos, e tudo gravado num party.txt.

import random

PRIMEIROS = ["Zara", "Kai", "Nuno", "Bel", "Tork", "Ana", "Vex", "Mira"]
APELIDOS = ["Sombra-Longa", "do Norte", "Punho-de-Ferro", "Sem-Medo"]
CLASSES = ["Guerreiro", "Feiticeira", "Ladrao", "Curandeira", "Arqueiro"]

TOTAL_PONTOS = 20
QUANTOS = 5

# Distribui um total fixo por tres atributos, um ponto de cada vez, para a
# soma dar SEMPRE 20. Uma funcao pode devolver varias coisas de uma vez:
# separam-se por virgulas, e quem chama recebe-as pela mesma ordem.
def distribuir_pontos(total):
    forca = 0
    magia = 0
    destreza = 0
    sobram = total
    while sobram > 0:
        sorte = random.randint(1, 3)
        if sorte == 1:
            forca = forca + 1
        elif sorte == 2:
            magia = magia + 1
        else:
            destreza = destreza + 1
        sobram = sobram - 1
    return forca, magia, destreza


def gerar_linha():
    nome = random.choice(PRIMEIROS) + " " + random.choice(APELIDOS)
    classe = random.choice(CLASSES)
    forca, magia, destreza = distribuir_pontos(TOTAL_PONTOS)
    # ljust e rjust enchem com espacos ate ao tamanho pedido. E so isso que
    # faz as colunas ficarem alinhadas.
    return (nome.ljust(24) + classe.ljust(13) + str(forca).rjust(3)
            + str(magia).rjust(7) + str(destreza).rjust(10))


cabecalho = "NOME".ljust(24) + "CLASSE".ljust(13) + "FOR" + "  MAGIA" + "  DESTREZA"
linhas = [cabecalho, "-" * len(cabecalho)]
contador = 0
while contador < QUANTOS:
    linhas.append(gerar_linha())
    contador = contador + 1

for linha in linhas:
    print(linha)

# "w" quer dizer escrever. Se o ficheiro nao existir, e criado.
ficheiro = open("party.txt", "w", encoding="utf-8")
for linha in linhas:
    ficheiro.write(linha + "\n")
ficheiro.close()
print()
print("Gravado em party.txt, na pasta deste ficheiro.")
