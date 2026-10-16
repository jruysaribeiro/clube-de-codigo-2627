# Sessao 3 — ERRO PROPOSITAL
# Este ficheiro tem UM erro. Corre-o no projetor e le o traceback.

import random

PRIMEIROS = ["Zara", "Kai", "Nuno", "Bel", "Tork", "Ana"]
APELIDOS = ["Sombra-Longa", "do Norte", "Punho-de-Ferro", "Sem-Medo"]
CLASSES = ["Guerreiro", "Feiticeira", "Ladrao", "Curandeira", "Arqueiro"]


def gerar_nome():
    primeiro = random.choice(PRIMEIROS)
    apelido = random.choice(APELIDOS)
    print(primeiro + " " + apelido)


def gerar_classe():
    return random.choice(CLASSES)


print("=== GERADOR DE PERSONAGENS ===")
print()

# Ate aqui parece que resulta: o nome aparece mesmo no ecra.
gerar_nome()

# E agora queremos usar o nome para outra coisa qualquer.
nome = gerar_nome()
ficha = "Nome: " + nome + " | Classe: " + gerar_classe()
print(ficha)
