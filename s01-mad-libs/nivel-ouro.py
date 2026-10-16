# Sessao 1 — 🥇 OURO
# A historia varia sozinha: o final e escolhido ao acaso pelo computador,
# e a mesma historia e impressa duas vezes com palavras diferentes.

import random

print("=== A HISTORIA QUE NUNCA E IGUAL ===")
print()

nome = input("Escreve um nome: ")
animal = input("Escreve um animal: ")
lugar = input("Escreve um lugar: ")
comida = input("Escreve uma comida: ")

# Uma lista e uma caixa com varias coisas la dentro, separadas por virgulas.
finais = [
    "e nunca mais ninguem os viu.",
    "e ainda hoje la estao os dois.",
    "e a policia continua a procurar respostas.",
    "e no dia seguinte tudo recomecou, igualzinho.",
]

# random.choice() vai a lista e traz UMA coisa a sorte.
final_sorteado = random.choice(finais)

print()
print("--- Versao 1 ---")
print(f"{nome} foi a {lugar} com um {animal} debaixo do braco.")
print(f"Levava {comida} para o caminho.")
print(final_sorteado)

# Agora a mesma historia, mas com palavras que o computador escolhe sozinho.
nomes_extra = ["a Rita", "o Tomas", "a professora de fisica", "o meu vizinho"]
animais_extra = ["ganso", "polvo", "hamster", "crocodilo"]
lugares_extra = ["para Marte", "para o balcao do cafe", "para dentro do frigorifico"]
comidas_extra = ["sopa fria", "gelado de alho", "torradas com areia"]

# Primeiro sorteamos, e so depois escrevemos. Fica mais facil de ler do que
# sortear tudo la dentro do print.
outro_nome = random.choice(nomes_extra)
outro_animal = random.choice(animais_extra)
outro_lugar = random.choice(lugares_extra)
outra_comida = random.choice(comidas_extra)
outro_final = random.choice(finais)

print()
print("--- Versao 2, escolhida pelo computador ---")
print(f"{outro_nome} foi {outro_lugar} com um {outro_animal} ao colo.")
print(f"Levava {outra_comida} para o caminho.")
print(outro_final)
