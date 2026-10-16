# Sessao 2 — 🥉 BRONZE
# Responde "maior" ou "menor" ate se acertar. Sem limite de tentativas.

import random

MINIMO = 1
MAXIMO = 100

segredo = random.randint(MINIMO, MAXIMO)
acertou = False

print("=== ADIVINHA O NUMERO ===")
print("Pensei num numero entre", MINIMO, "e", MAXIMO)
print()

while acertou == False:
    resposta = input("Palpite: ")
    palpite = int(resposta)

    if palpite == segredo:
        print("BOA! Era mesmo o", segredo)
        acertou = True
    elif palpite < segredo:
        print("Muito baixo. Vai mais para cima.")
    else:
        print("Muito alto. Vai mais para baixo.")
