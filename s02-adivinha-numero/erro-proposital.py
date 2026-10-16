# Sessao 2 — ERRO PROPOSITAL
# Este ficheiro tem UM erro. Corre-o no projetor e deixa acontecer.
# Para o parares: Ctrl + C no terminal.

import random

MINIMO = 1
MAXIMO = 20

segredo = random.randint(MINIMO, MAXIMO)
acertou = False

print("Pensei num numero entre", MINIMO, "e", MAXIMO)
print()

while acertou == False:
    resposta = input("Qual e o teu palpite? ")
    palpite = int(resposta)

    if palpite == segredo:
        print("Acertaste! Era mesmo", segredo)
    elif palpite < segredo:
        print("O meu numero e MAIOR do que esse.")
    else:
        print("O meu numero e MENOR do que esse.")

print("Ate a proxima!")
