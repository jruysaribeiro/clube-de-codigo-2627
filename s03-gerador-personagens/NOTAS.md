# Sessão 3 — Gerador de personagens de jogo

Conceitos: `def`, parâmetros, `return`, listas, `random.choice()`.

Esta pasta tem um ficheiro a mais: **`ferramentas.py`**. Ver a secção
própria, mais abaixo.

## O que o facilitador precisa de perceber

**Uma função é código com nome, que só corre quando alguém o chama.**
> «Escrever a função não faz nada. É só guardar a receita com um nome. Ela só
> acontece quando alguém escreve o nome com parênteses à frente. Os parênteses
> são o "faz isso agora".»

Isto vai ser preciso dizer mais do que uma vez: metade da turma vai escrever
uma função perfeita, correr o programa, e não sair nada. A função nunca foi
chamada.

**`return` entrega. `print` mostra.** É a ideia inteira da sessão, e é a
única que tem mesmo de ficar. Prepara esta imagem, que funciona sempre:
> «Mandas alguém ao café. Se ele voltar com o café na mão, isso é `return` —
> podes bebê-lo, dá-lo a outra pessoa, guardá-lo. Se ele te gritar da rua
> "TENHO AQUI UM CAFÉ!" e for embora, isso é `print`. Ouviste. Mas ficaste
> sem café.»

**Uma função que não tem `return` devolve `None`.** Não devolve nada — devolve
`None`, que é uma coisa de pleno direito e a palavra que vai aparecer nos
erros deles a tarde toda. `None` significa: *não há nada aqui*.

**Parâmetros são as coisas que a função pede para poder trabalhar.**
> «`gerar_personagem(raca, nivel)` é uma máquina com duas ranhuras. Quem a
> chama é que decide o que lá mete. A mesma função dá coisas diferentes
> conforme o que lhe metes — e é para isso que ela serve.»

**Uma função pode chamar outras funções.** No `solucao.py`, a
`gerar_personagem()` não sorteia nada sozinha: junta o resultado das outras
duas. Vale a pena apontar para isso — é a primeira vez que veem código
montado por camadas, e é como todo o software é feito.

**As listas.** Já apareceram de raspão no 🥇 da sessão 1. Hoje são
ferramenta de trabalho, mas continua a chegar a versão simples: «uma caixa com
coisas lá dentro, por ordem, e o `random.choice()` tira uma à sorte». Índices,
`len()`, fatias — nada disso é preciso hoje.

## O `ferramentas.py` — a primeira caixa preta

Este ficheiro tem duas funções feitas e documentadas: `barra(valor, maximo)` e
`moldura(titulo, linhas)`. Os alunos importam-nas e usam-nas **sem olhar para
dentro**.

É a primeira vez no ano que correm código escrito por outra pessoa, e é um
momento pequeno mas importante. Diz isto à turma, com estas palavras:
> «Não precisam de perceber o que está lá dentro. Precisam de saber o que ela
> **pede** e o que ela **devolve**. Isso está escrito no topo de cada função.
> É assim que se usa praticamente todo o código do mundo — incluindo o
> Pygame, daqui a três sessões.»

Mecânica, que é onde vão tropeçar:
- `import ferramentas` no topo do ficheiro deles;
- chamar com **`ferramentas.barra(7, 10)`**, com o nome do módulo à frente;
- e o `ferramentas.py` tem de estar **na mesma pasta**. É a causa de nove em
  dez `ModuleNotFoundError` de hoje.

Se alguém quiser espreitar lá dentro, deixa — mas não o expliques à turma. O
`ljust` e o `"#" * cheios` são conversas para o 🥇 de quem lá chegar sozinho.

## Demonstração ao vivo (máx. 10 min)

**1. A função mais pequena que existe (2 min).**
```python
def dizer_ola():
    print("ola!")
```
Corre. **Não sai nada.** Deixa o silêncio assentar e pergunta porquê.
> «Eu escrevi a receita. Nunca disse a ninguém para a fazer.»

Acrescenta `dizer_ola()` no fim. Corre. Sai. Chama três vezes. Saem três.
> «Escrevi uma vez, usei três. É para isto que servem as funções.»

**2. Um parâmetro (2 min).**
```python
def dizer_ola(nome):
    print("ola, " + nome + "!")

dizer_ola("Rita")
dizer_ola("Tomas")
```
> «A mesma função, resultados diferentes. Quem chama é que decide.»

**3. `return` contra `print` (3 min).** ← *o coração da sessão*
```python
def somar(a, b):
    print(a + b)

resultado = somar(2, 3)
print("o dobro e", resultado * 2)
```
Corre. Sai `5` — e depois rebenta:
```
TypeError: unsupported operand type(s) for *: 'NoneType' and 'int'
```
> «O 5 apareceu no ecrã. Mas quando eu quis usá-lo, não havia nada. A função
> gritou-me o número da rua e foi-se embora.»

Troca o `print` por `return`. Corre. Funciona. **Não apagues o exemplo do
quadro** — vais apontar para ele umas seis vezes durante a sessão.

**4. Corre o `erro-proposital.py` (3 min).** ← *é aqui, no fim*

Não digas nada. Corre. E repara na ordem, que é o que faz este ficheiro valer
a pena: **primeiro aparece um nome no ecrã**, tudo parece bem, e só depois
rebenta.

```
Zara Sem-Medo
Zara do Norte
Traceback (most recent call last):
  File "erro-proposital.py", line 29, in <module>
    ficha = "Nome: " + nome + " | Classe: " + gerar_classe()
            ~~~~~~~~~^~~~~~
TypeError: can only concatenate str (not "NoneType") to str
```

Lê o traceback pela ordem do costume. E depois faz **a** pergunta:
> «Ele diz que a variável `nome` é `NoneType` — não tem nada lá dentro. Mas
> nós vimos um nome aparecer no ecrã, duas vezes. Onde é que ele foi parar?»

O erro é que `gerar_nome()` faz `print` em vez de `return`. Deixa-os
encontrá-lo. Troca a palavra, corre, funciona.

> **Este é o mal-entendido número um da sessão** e a razão de ser deste
> ficheiro: o `print` dá a ilusão perfeita de que está tudo bem. O programa
> parece funcionar até ao momento em que se tenta *usar* o resultado.

## Os três níveis

**🥉 Bronze — uma função que devolve nome e classe, chamada três vezes.**
O mínimo da sessão: escrever um `def`, pôr lá um `return`, e chamá-lo mais do
que uma vez. Se alguém sair daqui hoje, a sessão cumpriu.
A dificuldade não é escrever a função — é resistir a copiá-la e colá-la três
vezes. Se vires isso, a pergunta é: «e se quisesses dez personagens?»

**🥈 Prata — parâmetros, atributos, ficha formatada, e o `ferramentas.py`.**
Aqui é que a sessão fica interessante, e há quatro coisas novas a sério:

1. **Parâmetros** — a função passa a receber `raca` e `nivel` de fora.
2. **Os parâmetros influenciam o resultado** — o `nivel` entra na conta da
   força e da vida. Sem isto, os parâmetros são decorativos e ninguém percebe
   para que servem.
3. **Construir uma lista com `append()`** — as linhas da ficha juntam-se uma
   a uma. É a primeira vez que constroem uma lista em vez de a escreverem
   toda de uma vez, e é exatamente o que vão fazer na sessão 8 com os
   inimigos.
4. **Importar código de outra pessoa.**

Faz uma coisa por vez, e testa entre elas. Diz isto antes de eles começarem.

**🥇 Ouro — tabela alinhada, 20 pontos a distribuir, gravar num ficheiro.**
O ficheiro `nivel-ouro.py` faz **as três coisas** que o desafio oferece em
alternativa, para teres as três à mão. Na sala, propõe **uma** a cada par;
fazer as três é trabalho para duas sessões.

- *A tabela alinhada* é a mais acessível: só precisa de `ljust`/`rjust`, que
  se dão como receita.
- *Distribuir 20 pontos* é a mais rica. É a primeira decisão de **design de
  jogo** do ano — as personagens deixam de ser desequilibradas ao acaso e
  passam a ser todas comparáveis entre si. Vale a pena conversar sobre isto
  com quem lá chegar.
- *Gravar num `.txt`* é a que dá mais prazer imediato, porque produz um
  ficheiro que se abre fora do editor. Cuidado com uma coisa: o `open("...")`
  grava na pasta onde o terminal está aberto, **não** na pasta do ficheiro.
  Se o ficheiro não aparecer onde esperam, é isso.

O `distribuir_pontos()` devolve **três valores de uma vez**, separados por
vírgulas, e quem chama recebe-os pela mesma ordem:
`forca, magia, destreza = distribuir_pontos(20)`. Dá-o como receita e não lhe
chames tuplo. Se alguém perguntar: «o `return` pode entregar mais do que uma
coisa; recebem-se pela ordem por que foram entregues».

## Erros que os alunos vão cometer

| Sintoma | Causa | A pergunta a fazer |
|---|---|---|
| A função existe mas não sai nada no ecrã | Nunca chamou a função | «Percorre o ficheiro de cima a baixo comigo. Em que linha é que mandas o computador *fazer* a função, e não só guardá-la?» |
| `TypeError: can only concatenate str (not "NoneType") to str` | A função faz `print` em vez de `return` | «O Python diz que essa variável não tem nada lá dentro. Vai à função — qual é a última coisa que ela faz antes de acabar?» |
| A personagem aparece no ecrã mas não dá para a guardar numa variável | O mesmo: `print` em vez de `return` | «Lembras-te do café? A tua função trouxe o café, ou gritou-te da rua?» |
| `TypeError: gerar_personagem() missing 1 required positional argument` | Definiu parâmetros e depois chamou sem eles | «Vai à linha do `def`. Quantas coisas é que essa função pede? E quantas é que lhe deste?» |
| As três personagens saem todas iguais | Sorteou uma vez fora da função e usou a mesma variável nas três chamadas | «O sorteio está dentro ou fora da função? Quantas vezes é que essa linha corre?» |
| `ModuleNotFoundError: No module named 'ferramentas'` | O `ferramentas.py` não está na mesma pasta, ou o terminal está noutra pasta | «Abre a barra do lado. O `ferramentas.py` está mesmo na mesma pasta que o teu ficheiro?» |
| `NameError: name 'barra' is not defined` | Escreveu `barra(...)` em vez de `ferramentas.barra(...)` | «Como é que o Python sabe em que ficheiro deve ir procurar essa função?» |
| `AttributeError: module 'ferramentas' has no attribute ...` | Escreveu mal o nome da função | «Vai ao `ferramentas.py` e lê-me o nome da função exatamente como lá está. Agora lê-me o que escreveste.» |
| `IndentationError`, ou o programa faz coisas que deviam estar dentro da função | O corpo da função não está indentado, ou o código de baixo ficou indentado por engano | «Quais destas linhas fazem parte da receita e quais é que são o programa? Como é que o Python distingue as duas coisas?» |
| A função devolve o valor certo mas nada aparece | Trocou na direção contrária: pôs `return` mas esqueceu o `print` na chamada | «A função entregou-te a personagem. E agora, o que é que fizeste com ela?» |
| O `party.txt` não aparece na pasta (🥇) | O terminal está aberto noutra pasta | «Onde é que o teu terminal está aberto? É a mesma pasta do ficheiro?» |

## Critério de sucesso

Aos 90 minutos:

- [ ] Toda a gente tem **uma função com `return`, chamada mais do que uma
      vez**. É o mínimo não negociável.
- [ ] Toda a gente já viu um `NoneType` no seu próprio ecrã e sabe dizer, por
      palavras suas, porque é que ele apareceu.
- [ ] Ninguém tem código copiado e colado três vezes onde bastava uma chamada.
      Se tiver, ainda não percebeu a sessão, mesmo que o programa funcione.
- [ ] Pelo menos um terço da turma usou o `ferramentas.py` e ficou com a ficha
      dentro da moldura.

**O sinal mais forte da sessão:** um aluno que muda a função **uma vez** e vê
as três personagens mudarem ao mesmo tempo, e reage. Esse aluno percebeu para
que servem as funções — que é a única coisa que aqui interessa.

**Sinal de alarme:** um par com um ficheiro comprido, sem nenhum `def`, que
funciona muito bem. Estão a resolver o exercício com as ferramentas da sessão
1 e a fugir à sessão de hoje. Pergunta-lhes: «e agora, para fazer dez
personagens?» — e deixa a resposta ser deles.

**Nota de encerramento, e vale a pena dizê-la a sério:** esta é a última
sessão de consola do ano. Da sessão 7 em diante há uma janela, e a primeira
coisa que vão ver do Pygame é `pygame.display.set_mode()` — uma função escrita
por outra pessoa, que se chama pelo nome do módulo e devolve uma coisa que
depois se usa. Exatamente como o `ferramentas.py` de hoje.
