# Trocar cêntimos em moedas
centimos = int(input("Quantos cêntimos tens? "))

moedas50 = centimos // 50
centimos = centimos % 50

moedas20 = centimos // 20
centimos = centimos % 20

moedas10 = centimos // 10
centimos = centimos % 10

moedas5 = centimos // 5
centimos = centimos % 5

print(f"Moedas de 50 cêntimos: {moedas50}")
print(f"Moedas de 20 cêntimos: {moedas20}")
print(f"Moedas de 10 cêntimos: {moedas10}")
print(f"Moedas de 5 cêntimos: {moedas5}")
print(f"Sobram {centimos} cêntimos")
