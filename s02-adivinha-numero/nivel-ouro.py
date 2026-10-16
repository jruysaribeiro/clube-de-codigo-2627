# Sessao 2 — 🥇 OURO
# Jogo invertido: tu pensas num numero e o computador adivinha.
#
# NOTA PARA O FACILITADOR: a estratégia aqui e a PESQUISA BINARIA. O
# computador arrisca sempre o meio do intervalo que lhe resta, porque assim,
# seja qual for a resposta, deita fora metade das hipoteses de uma vez. Por
# isso adivinha qualquer numero de 1 a 100 em 7 tentativas ou menos.

MINIMO = 1
MAXIMO = 100

minimo = MINIMO
maximo = MAXIMO
tentativas = 0
acabou = False

print("=== AGORA E AO CONTRARIO ===")
print("Pensa num numero entre", MINIMO, "e", MAXIMO, "e NAO me digas qual e.")
print("Responde-me so: maior, menor ou acertaste")
print()
input("Carrega em Enter quando tiveres o numero na cabeca. ")
print()

while acabou == False:
    # O meio do intervalo. As duas barras dividem e deitam fora as casas
    # decimais, porque nao ha palpites com virgula.
    palpite = (minimo + maximo) // 2
    tentativas = tentativas + 1

    print("Tentativa", tentativas, "- o teu numero e", palpite, "?")
    resposta = input("maior / menor / acertaste: ")

    if resposta == "acertaste":
        print()
        print("Apanhei-te em", tentativas, "tentativas.")
        acabou = True
    elif resposta == "maior":
        # Se e maior, todos os numeros ate ao palpite deixam de interessar.
        minimo = palpite + 1
    elif resposta == "menor":
        maximo = palpite - 1
    else:
        print("Nao percebi. Escreve maior, menor ou acertaste.")
        tentativas = tentativas - 1

    # Quando o minimo passa o maximo ja nao sobra numero nenhum possivel.
    if minimo > maximo:
        print()
        print("Nao sobra nenhum numero possivel. Fizeste batota!")
        acabou = True
