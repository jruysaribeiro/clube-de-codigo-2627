# Cheat sheet v1 — Python de consola

Para as sessões 1, 2 e 3. Imprime em papel, uma folha frente e verso.
Só biblioteca padrão: não é preciso instalar nada.

---

## Escrever no ecrã

```python
print("Ola!")                      # texto
print(pontuacao)                   # o que esta dentro da variavel
print("Pontos:", pontuacao)        # varias coisas, separadas por virgulas
print()                            # uma linha em branco
```

## Variáveis

```python
nome = "Rita"          # texto (string)
idade = 12             # numero inteiro (int)
altura = 1.55          # numero com virgula (float)
acabou = False         # verdadeiro ou falso (bool): True ou False
```

Uma variável é uma **etiqueta colada a uma coisa**. `=` não quer dizer
"é igual a": quer dizer **"passa a ser"**.

## Perguntar à pessoa

```python
nome = input("Como te chamas? ")
```

> ⚠️ **`input()` devolve SEMPRE texto.** Mesmo que escrevam `7`, é a
> palavra `"7"` e não o número 7.

```python
idade = int(input("Que idade tens? "))     # texto -> numero inteiro
preco = float(input("Quanto custa? "))     # texto -> numero com virgula
```

## Juntar texto e variáveis (f-string)

```python
print(f"Ola, {nome}! Tens {idade} anos.")
```

O **`f`** antes das aspas é obrigatório. Sem ele aparece `{nome}` no ecrã,
com chavetas e tudo.

## Comentários

```python
# O computador nao le esta linha. E para ti, e para o teu eu de daqui a
# duas semanas, que ja se esqueceu de tudo.
```

## Contas

```python
a + b      # somar          a - b      # subtrair
a * b      # multiplicar    a / b      # dividir  (5 / 2 = 2.5)
a // b     # dividir e deitar fora as decimais  (5 // 2 = 2)
a % b      # o resto da divisao  (7 % 2 = 1)
```

## Comparar

```python
a == b     # sao iguais?   ATENCAO: dois sinais de igual
a != b     # sao diferentes?
a < b      a > b      a <= b     a >= b
```

> ⚠️ `=` guarda um valor. `==` compara dois valores. É o erro mais comum.

## Decidir: `if` / `elif` / `else`

```python
if pontuacao > 100:
    print("Muito bem!")
elif pontuacao > 50:
    print("Nada mau.")
else:
    print("Tenta outra vez.")
```

Os **dois pontos** no fim da linha e os **quatro espaços** à frente das linhas
de dentro não são decoração: é assim que o Python sabe o que pertence a quê.

## Repetir: `while`

```python
contador = 0
while contador < 3:
    print("ola")
    contador = contador + 1
```

> ⚠️ **Alguma coisa dentro do ciclo tem de mudar a resposta à pergunta do
> `while`.** Senão ele nunca sai.
>
> **Para parar um programa em fuga: `Ctrl + C` no terminal.**

## Percorrer uma lista: `for`

```python
for animal in animais:
    print(animal)
```

## Listas

```python
animais = ["gato", "cao", "pato"]

animais.append("peixe")     # acrescentar ao fim
len(animais)                # quantos sao
animais[0]                  # o primeiro (a contagem comeca no ZERO)
```

> ⚠️ **Nunca tires nada de uma lista enquanto a estás a percorrer.** Faz uma
> lista nova com os que ficam.

## Sorte: `random`

```python
import random                       # no topo do ficheiro, uma vez

random.randint(1, 6)                # inteiro entre 1 e 6, inclusive
random.choice(["cara", "coroa"])    # uma coisa da lista, a sorte
```

## Funções

```python
def gerar_nome():
    return random.choice(PRIMEIROS)      # devolve

def saudar(nome, idade):                 # com parametros
    return f"Ola {nome}, tens {idade}."

resultado = saudar("Rita", 12)           # chamar: parenteses = "faz agora"
```

> ⚠️ **`return` entrega. `print` mostra.**
> Uma função com `print` em vez de `return` devolve `None`, e não dá para
> reutilizar o resultado.
>
> Escrever a função não faz nada. Ela só corre quando é **chamada**.

## Usar código de outro ficheiro

```python
import ferramentas                    # o ficheiro tem de estar na MESMA pasta

ferramentas.barra(7, 10)              # com o nome do modulo a frente
```

## Não rebentar com texto onde devia estar um número

```python
try:
    palpite = int(resposta)
except ValueError:
    print("Isso nao e um numero.")
    continue                          # volta ja ao inicio do ciclo
```

## Guardar num ficheiro

```python
ficheiro = open("dados.txt", "w", encoding="utf-8")
ficheiro.write("uma linha\n")
ficheiro.close()
```

`"w"` escreve (apaga o que lá estava), `"a"` acrescenta ao fim.
O ficheiro aparece na pasta **onde o terminal está aberto**.

---

## Mensagens de erro: o que querem dizer

**Lê sempre de baixo para cima.** A última linha diz *o quê*, e a linha do
`File` diz *onde*.

| Erro | Quer dizer |
|---|---|
| `SyntaxError: unterminated string literal` | Falta uma aspa a fechar |
| `SyntaxError: invalid syntax` | Falta um `:`, um parêntesis, ou está `=` onde devia estar `==` |
| `IndentationError` | Os espaços à esquerda não batem certo |
| `NameError: name 'x' is not defined` | Escreveste um nome que não existe — ou está mal escrito, ou usaste-o antes de o criar |
| `TypeError: can only concatenate str (not "int") to str` | Estás a somar texto com número. Falta `str()` ou `int()` |
| `TypeError: ... 'NoneType' ...` | Uma função fez `print` onde devia ter feito `return` |
| `ValueError: invalid literal for int()` | Deste texto ao `int()` |
| `IndexError: list index out of range` | Pediste um item que a lista não tem |
| `KeyError: 'x'` | Pediste um nome que o dicionário não tem |
| `ModuleNotFoundError` | O ficheiro que queres importar não está na mesma pasta |
| `KeyboardInterrupt` | **Não é um erro teu.** Foste tu que carregaste em `Ctrl + C` |

---

## As regras de ouro

1. **Corre o programa a cada três ou quatro linhas.** Não escrevas trinta
   linhas e só depois corras.
2. **A mensagem vermelha é ajuda, não é castigo.** Diz-te o ficheiro, a linha
   e o problema.
3. **Se não perceberes o erro, lê a última linha em voz alta.** Resulta mais
   vezes do que parece.
4. **`Ctrl + C` pára qualquer programa.**
