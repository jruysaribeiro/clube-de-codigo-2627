# Sessao 2 — Adivinha o numero
# Solucao de referencia: o esqueleto com os TODO resolvidos.

import random

MINIMO = 1
MAXIMO = 20

segredo = random.randint(MINIMO, MAXIMO)
acertou = False

print("Pensei num numero entre", MINIMO, "e", MAXIMO)
print("Consegues adivinhar?")
print()

while acertou == False:
    resposta = input("Qual e o teu palpite? ")
    palpite = int(resposta)

    if palpite == segredo:
        print("Acertaste! Era mesmo", segredo)
        acertou = True
    elif palpite < segredo:
        print("O meu numero e MAIOR do que esse.")
    else:
        print("O meu numero e MENOR do que esse.")

print()
print("Ate a proxima!")
