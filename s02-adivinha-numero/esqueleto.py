# Sessao 2 — Adivinha o numero
# Corre-me com:  python3 esqueleto.py

import random

MINIMO = 1
MAXIMO = 20

# random.randint() sorteia um numero inteiro entre os dois limites.
segredo = random.randint(MINIMO, MAXIMO)
acertou = False

print("Pensei num numero entre", MINIMO, "e", MAXIMO)
print("Consegues adivinhar?")
print()

# O ciclo repete-se enquanto a condicao for verdadeira.
while acertou == False:
    resposta = input("Qual e o teu palpite? ")

    # input() devolve sempre TEXTO. O int() transforma esse texto num numero,
    # para o podermos comparar com o segredo.
    palpite = int(resposta)

    if palpite == segredo:
        print("Acertaste! Era mesmo", segredo)
        acertou = True
    else:
        print("Nao e esse.")

        # TODO: dizer so "nao e esse" nao ajuda nada. O que e que o jogador
        #       precisava de saber para o proximo palpite ser melhor?

        # TODO: ja sabemos que o palpite esta errado. Como e que descobres,
        #       aqui dentro, se ele e grande demais ou pequeno demais?
