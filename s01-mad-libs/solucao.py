# Sessao 1 — Gerador de historias malucas
# Solucao de referencia: o esqueleto com os TODO resolvidos.

print("=== O GERADOR DE HISTORIAS MALUCAS ===")
print()

nome = input("Escreve um nome: ")
animal = input("Escreve um animal: ")
lugar = input("Escreve um lugar: ")
comida = input("Escreve uma comida: ")
adjetivo = input("Escreve um adjetivo (ex: verde, gigante): ")

print()
print("--- A tua historia ---")

print(f"Numa manha muito {adjetivo}, {nome} acordou em {lugar}.")
print(f"A porta estava um {animal} {adjetivo} a comer {comida}.")
print(f"— Bom dia — disse o {animal}. — Trouxe {comida} para os dois.")
print(f"{nome} nunca tinha comido {comida} ao pequeno-almoco,")
print(f"e muito menos com um {animal} em {lugar}.")
print()
print(f"Desde esse dia, {nome} come sempre {comida} a segunda-feira.")
print("FIM.")
