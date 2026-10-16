# Sessao 3 — Gerador de personagens
# Solucao de referencia: o esqueleto com os TODO resolvidos.

import random

PRIMEIROS = ["Zara", "Kai", "Nuno", "Bel", "Tork", "Ana"]
APELIDOS = ["Sombra-Longa", "do Norte", "Punho-de-Ferro", "Sem-Medo"]
CLASSES = ["Guerreiro", "Feiticeira", "Ladrao", "Curandeira", "Arqueiro"]


def gerar_nome():
    primeiro = random.choice(PRIMEIROS)
    apelido = random.choice(APELIDOS)
    return primeiro + " " + apelido


def gerar_classe():
    return random.choice(CLASSES)


# Uma funcao pode chamar outras funcoes. Esta nao sorteia nada sozinha:
# junta o trabalho das duas de cima e entrega o resultado.
def gerar_personagem():
    nome = gerar_nome()
    classe = gerar_classe()
    return nome + ", " + classe


print("=== GERADOR DE PERSONAGENS ===")
print()

# Escrevemos a funcao UMA vez e chamamo-la tres. E para isto que servem.
print("1:", gerar_personagem())
print("2:", gerar_personagem())
print("3:", gerar_personagem())
