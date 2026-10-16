# Sessao 3 — 🥉 BRONZE
# Uma funcao que devolve nome e classe ao acaso, chamada tres vezes.

import random

PRIMEIROS = ["Zara", "Kai", "Nuno", "Bel", "Tork", "Ana", "Vex", "Mira"]
APELIDOS = ["Sombra-Longa", "do Norte", "Punho-de-Ferro", "Sem-Medo"]
CLASSES = ["Guerreiro", "Feiticeira", "Ladrao", "Curandeira", "Arqueiro"]


def gerar_personagem():
    primeiro = random.choice(PRIMEIROS)
    apelido = random.choice(APELIDOS)
    classe = random.choice(CLASSES)
    return primeiro + " " + apelido + " - " + classe


print("=== A TUA PARTY ===")
print()

# Tres chamadas. Cada uma volta a sortear tudo de novo, por isso saem
# tres personagens diferentes da mesma funcao.
print("1:", gerar_personagem())
print("2:", gerar_personagem())
print("3:", gerar_personagem())
