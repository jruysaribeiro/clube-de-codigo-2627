# Sessao 2 — 🥈 PRATA
# Conta tentativas, limita a sete, e nao rebenta se escreverem texto.

import random

MINIMO = 1
MAXIMO = 100
MAXIMO_TENTATIVAS = 7

segredo = random.randint(MINIMO, MAXIMO)
tentativas = 0
acertou = False

print("=== ADIVINHA O NUMERO ===")
print("Pensei num numero entre", MINIMO, "e", MAXIMO)
print("Tens", MAXIMO_TENTATIVAS, "tentativas. Boa sorte.")
print()

while acertou == False and tentativas < MAXIMO_TENTATIVAS:
    resposta = input("Palpite: ")

    # RECEITA: o try tenta fazer a linha. Se ela rebentar com um ValueError
    # (que e o que o int() faz quando lhe damos texto), o Python salta para o
    # except em vez de parar o programa todo.
    try:
        palpite = int(resposta)
    except ValueError:
        print("Isso nao e um numero. Escreve so algarismos.")
        # continue = volta ja ao inicio do ciclo. Assim nao gasta tentativa.
        continue

    tentativas = tentativas + 1
    restantes = MAXIMO_TENTATIVAS - tentativas

    if palpite == segredo:
        print("BOA! Era mesmo o", segredo)
        print("Conseguiste em", tentativas, "tentativas.")
        acertou = True
    elif palpite < segredo:
        print("Muito baixo. Restam", restantes)
    else:
        print("Muito alto. Restam", restantes)

if acertou == False:
    print()
    print("Acabaram-se as tentativas. O numero era", segredo)
    print("Para a proxima comeca pelo meio.")
