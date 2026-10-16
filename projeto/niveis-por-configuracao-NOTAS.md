# `niveis-por-configuracao.py` — sessão 13

## A ideia, em trinta segundos

**Dados contra lógica.** Os níveis não são código: são uma **lista de
configurações**, e há **um só** bloco de código que sabe ler qualquer uma
delas.

> «Repara: para acrescentar um nível novo escreves mais uma linha na lista.
> Mais nada, no ficheiro inteiro. A alternativa era um `if` para o nível 1,
> outro para o 2, outro para o 3 — e quando descobrisses um erro, tinhas de o
> corrigir cinco vezes.»

É a primeira vez no ano que se separa *o que o jogo é* de *como o jogo
funciona*. É uma ideia grande e vale a pena nomeá-la.

## O dicionário

É a única coisa nova. Dá-a como receita:
> «Uma lista guarda coisas por ordem e vais buscá-las pelo número. Um
> dicionário guarda coisas com **nome**: `nivel["velocidade"]` lê-se
> "a velocidade deste nível". Escreve-se com chavetas e dois pontos.»

Não fales de chaves, valores, `.get()` nem de nada disso. Chavetas, dois
pontos, e vai-se buscar pelo nome.

## Demonstração (3 min)

Corre o ficheiro. Passa os quatro níveis (é rápido: 3, 6, 9 e 12 moedas).
Repara em voz alta que **a cor do fundo e a velocidade também vêm do nível**,
não só o número de moedas.

Depois, ao vivo, acrescenta uma linha à lista `NIVEIS`:
```python
    {"nome": "Impossivel", "moedas": 20, "velocidade": 3, "cor": (20, 20, 20)},
```
Corre. Há cinco níveis. **Não se mexeu em mais nada.** É esse o momento.

## Quando é que uma equipa deve usar isto

Quando o jogo tiver **três ou mais níveis mesmo diferentes** uns dos outros.

Se o jogo só precisa de ficar mais rápido com o tempo, isto é trabalho a mais:
manda-os ao `dificuldade-crescente.py`, que resolve o mesmo em duas linhas.
Escolher entre os dois é a conversa de design a ter com cada equipa na sessão
13.

## Erros previsíveis

| Sintoma | A pergunta a fazer |
|---|---|
| `KeyError: 'velocidad'` | «O Python diz que não encontrou esse nome. Lê-me o nome exato como está escrito na lista.» |
| `IndexError: list index out of range` | «Quantos níveis tens na lista? E que número estás a pedir depois do último?» |
| O último nível repete-se para sempre | «O que devia acontecer quando já não há mais níveis? Onde é que isso está escrito?» |
| Acrescentou um nível e nada mudou | «Puseste a linha dentro dos parênteses retos da lista? E a vírgula no fim?» |
