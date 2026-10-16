# Sessao 3 — Gerador de personagens
# Corre-me com:  python3 esqueleto.py

import random

PRIMEIROS = ["Zara", "Kai", "Nuno", "Bel", "Tork", "Ana"]
APELIDOS = ["Sombra-Longa", "do Norte", "Punho-de-Ferro", "Sem-Medo"]


# def cria uma funcao: um bocado de codigo com um nome, que so corre quando
# alguem o chama. O return e o que a funcao entrega a quem a chamou.
def gerar_nome():
    primeiro = random.choice(PRIMEIROS)
    apelido = random.choice(APELIDOS)
    return primeiro + " " + apelido


print("=== GERADOR DE PERSONAGENS ===")
print()

# Chamar a funcao. Os parenteses sao o "corre isso agora".
nome = gerar_nome()
print("Nome:", nome)

# TODO: chama a funcao gerar_nome() mais duas vezes, para saires com tres
#       personagens em vez de uma. Precisas de escrever a funcao outra vez?

# TODO: uma personagem so com nome e fraca. Que outra coisa e que ela
#       devia ter? Como e que farias uma funcao que a sorteasse?

# TODO: as duas funcoes que escreveste sorteiam sempre de listas fixas.
#       O que terias de mudar para gerar_nome() aceitar a lista de fora?
