# Sessao 3 — 🥈 PRATA
# gerar_personagem(raca, nivel) com parametros, atributos sorteados,
# ficha formatada, e uma funcao vinda do ferramentas.py.

import random

import ferramentas

PRIMEIROS = ["Zara", "Kai", "Nuno", "Bel", "Tork", "Ana", "Vex", "Mira"]
APELIDOS = ["Sombra-Longa", "do Norte", "Punho-de-Ferro", "Sem-Medo"]
CLASSES = ["Guerreiro", "Feiticeira", "Ladrao", "Curandeira", "Arqueiro"]


def gerar_nome():
    return random.choice(PRIMEIROS) + " " + random.choice(APELIDOS)


# Os parametros sao as coisas que a funcao PEDE para poder trabalhar.
# Quem a chama e que decide o que la mete.
def gerar_personagem(raca, nivel):
    nome = gerar_nome()
    classe = random.choice(CLASSES)

    # Personagens de nivel alto sao mais fortes: o nivel entra na conta.
    forca = random.randint(1, 6) + nivel
    magia = random.randint(1, 6) + nivel
    vida = random.randint(10, 20) + nivel * 5

    linhas = []
    linhas.append("Nome:   " + nome)
    linhas.append("Raca:   " + raca)
    linhas.append("Classe: " + classe)
    linhas.append("Nivel:  " + str(nivel))
    linhas.append("Forca:  " + ferramentas.barra(forca, 12))
    linhas.append("Magia:  " + ferramentas.barra(magia, 12))
    linhas.append("Vida:   " + str(vida))

    return ferramentas.moldura("FICHA DE PERSONAGEM", linhas)


print(gerar_personagem("Elfo", 1))
print()
print(gerar_personagem("Anao", 5))
print()
print(gerar_personagem("Humano", 3))
