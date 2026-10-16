# Sessao 1 — Gerador de historias malucas
# Corre-me com:  python3 esqueleto.py

print("=== O GERADOR DE HISTORIAS MALUCAS ===")
print()

# input() escreve a pergunta, espera que a pessoa escreva, e guarda o que
# ela escreveu dentro da variavel.
nome = input("Escreve um nome: ")
animal = input("Escreve um animal: ")
lugar = input("Escreve um lugar: ")

print()
print("--- A tua historia ---")

# O f antes das aspas deixa-nos meter variaveis dentro do texto, com chavetas.
print(f"Era uma vez {nome}, que vivia em {lugar}.")
print(f"Um dia apareceu-lhe um {animal} a porta de casa.")
print(f"E foi assim que {nome} deixou de ter medo de {animal}s.")

# TODO: pede mais duas coisas a pessoa. Que perguntas farias tu?

# TODO: as tuas duas coisas novas nao aparecem em lado nenhum da historia.
#       Onde e que elas deviam entrar para a historia ficar mais maluca?

# TODO: esta historia comeca sempre da mesma maneira, "Era uma vez".
#       Que outra frase de abertura terias tu escolhido?
