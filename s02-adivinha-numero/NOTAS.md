# Sessão 2 — Jogo "Adivinha o número"

Conceitos: `while`, `if/elif/else`, `random.randint()`, `int()`, contadores.

## O que o facilitador precisa de perceber

**O `while` é um `if` que se repete.**
> «O `if` pergunta uma vez e segue em frente. O `while` pergunta, faz, e
> volta a perguntar. E outra vez. E outra. Enquanto a resposta for sim, ele
> não sai dali.»

Esta é a comparação certa, porque eles já viram o `if` na sessão anterior sem
lhe chamar isso. A frase a repetir é: **«o `while` volta sempre ao princípio
e volta sempre a perguntar»**.

**Um ciclo só acaba se alguma coisa lá dentro mudar.**
Esta é a ideia central da sessão inteira e vale a pena ser explícito:
> «Se a pergunta do `while` for sempre a mesma e nada lá dentro a mudar, ele
> nunca sai. O ciclo não é burro: está a fazer exatamente o que lhe
> mandaste.»

O `erro-proposital.py` é feito à medida disto. Não o corras já — está marcado
o momento certo no guião.

**`input()` devolve texto. Sempre.**
Ficou anunciado na sessão 1 e hoje é a fatura. `"7"` e `7` não são a mesma
coisa para o computador: um é uma palavra de um algarismo, o outro é um
número com que se pode contar.
> «Isto é a diferença entre a palavra "sete" escrita num papel e sete berlindes
> na mão. Podes comparar berlindes. A palavra, não.»

O `int()` é o tradutor: pega no texto e devolve o número. Sem ele,
`palpite == segredo` compara texto com número e dá sempre falso — o jogo fica
impossível de ganhar.

**`elif` existe para não fazer perguntas já respondidas.**
> «Se já sei que não é igual, não vale a pena perguntar outra vez se é igual.
> O `elif` é "senão, se". Ele só é testado quando o de cima falhou.»

**Um contador é uma variável que cresce sozinha.**
`tentativas = tentativas + 1` é a linha que mais confunde na sessão, porque
em matemática é falsa. Diz isto em voz alta:
> «Isto não é uma equação. O `=` não quer dizer "é igual a", quer dizer "passa
> a ser". Lê-se da direita para a esquerda: pega no que lá está, soma um, e
> volta a guardar no mesmo sítio.»

## Como se pára um programa em fuga

**Precisas de saber isto antes de entrares na sala**, porque hoje vai
acontecer a meia dúzia de alunos e o pânico é real.

- **`Ctrl + C`** no terminal. É o travão de emergência universal: mata o
  programa que está a correr. Funciona em Windows, macOS e Linux.
- Aparece um `KeyboardInterrupt` em vermelho. **Não é um erro do aluno** —
  é só o Python a dizer «fui interrompido». Diz isto, senão eles pensam que
  partiram alguma coisa.
- Se o ciclo estiver a cuspir texto depressa demais para se ver o que se
  passa, `Ctrl + C` continua a funcionar. Pode ser preciso carregar duas
  vezes.
- No VS Code, se o programa foi lançado pelo botão ▶, o `Ctrl + C` tem de ser
  dado **com o cursor dentro do painel do terminal**, não no editor. Vale a
  pena mostrar isto uma vez, ao vivo.
- O caixote do lixo 🗑 no painel do terminal fecha o terminal inteiro. Também
  resolve, mas é a marreta.

> **Escreve `Ctrl + C` no quadro no início da sessão e deixa lá ficar o dia
> todo.** É o único momento do ano em que uma tecla merece estar no quadro.

Um ciclo infinito que tem um `input()` lá dentro — que é o caso do
`erro-proposital.py` — não bloqueia o computador: fica só a pedir palpites
para sempre. Um ciclo infinito **sem** `input()` enche o ecrã em segundos.
Ambos se param da mesma maneira.

## Demonstração ao vivo (máx. 10 min)

**1. O ciclo mais pequeno que existe (2 min).**
```python
contador = 0
while contador < 3:
    print("ola")
    contador = contador + 1
```
Corre. Saem três `ola`. Antes de correres, pergunta à turma quantos `ola`
vão sair. Vais ouvir 2, 3 e 4 — e é bom que ouças, porque é aí que se percebe
que o `<` importa.

**2. Tira a última linha (1 min).** ← *o momento importante*
Apaga o `contador = contador + 1`. Corre. **Deixa correr uns segundos**, com
o ecrã a encher de `ola`. Depois `Ctrl + C`, com gesto teatral.
> «O ciclo não avariou. Fez o que lhe mandei. Eu é que nunca mudei o
> contador, e a pergunta dele foi sempre a mesma.»

Põe a linha de volta.

**3. `input()` e `int()` (3 min).**
```python
idade = input("Que idade tens? ")
print(idade + 10)
```
Corre e escreve `12`. Rebenta:
```
TypeError: can only concatenate str (not "int") to str
```
Lê o traceback pela mesma ordem da sessão 1: ficheiro, linha, última
mensagem. «`str` é texto, `int` é número. Ele está a dizer que não sabe somar
uma coisa à outra.» Corrige para `int(idade) + 10`. Corre. Funciona.

**4. Constrói o jogo (2 min).** Abre o `esqueleto.py` e mostra só a forma:
sorteia, pergunta, compara, repete. Não escrevas os `elif` — **são o trabalho
deles**. Se os escreveres aqui, a sessão acabou aos 10 minutos.

**5. Corre o `erro-proposital.py` (2 min).** ← *é aqui, no fim*

Não digas nada. Corre. Joga a sério, no projetor, até acertares. Aparece
`Acertaste!` — e logo a seguir `Qual e o teu palpite?` outra vez. Acerta de
novo. E outra vez. Deixa a turma reagir: alguém vai rir-se, alguém vai dizer
«está parvo».

Só então: `Ctrl + C`.

Faz **uma** pergunta e cala-te:
> «O `while` está a perguntar se o `acertou` continua a ser `False`. Alguém
> me diz em que linha é que o `acertou` passa a ser `True`?»

O erro é que falta `acertou = True` dentro do `if palpite == segredo`. Deixa
que seja a turma a encontrá-lo. Depois acrescenta a linha, corre, e o jogo
acaba como deve ser.

> **Anota isto para ti:** este erro é o mesmo do passo 2, vestido de outra
> maneira. Diz-lho, com essas palavras — é a primeira vez no ano que eles
> reconhecem um padrão em vez de decorarem um caso.

## Os três níveis

**🥉 Bronze — "maior" ou "menor" até acertar, sem limite.**
É o `esqueleto.py` com os dois `# TODO:` resolvidos. Toda a gente tem de
chegar aqui. A dificuldade real é uma só: perceber que `<` e `>` respondem à
pergunta de que lado o palpite falhou. Muitos vão trocar as mensagens —
escrevem "maior" quando deviam escrever "menor" — e o jogo fica impossível.
É um bug excelente, porque só se apanha a jogar.

**🥈 Prata — contador, limite de sete, e não rebenta com texto.**
Três acrescentos independentes, e é essa a lição escondida: dá para fazer um
de cada vez e testar entre eles. Quem tentar fazer os três de uma vez vai
passar vinte minutos perdido — vale a pena dizer isto à turma antes.

O `try/except` é **dado como receita**, não explicado. Não abras a caixa das
exceções hoje:
> «Isto lê-se assim: tenta fazer a linha de dentro do `try`; se ela rebentar,
> faz o que está no `except` em vez de parar o programa todo. Copia, usa,
> e um dia perceberás porquê.»

O `continue` também é receita: «volta já ao início do ciclo». Repara que no
`nivel-prata.py` ele está de propósito **antes** do `tentativas + 1`, para
escrever disparates não gastar tentativas. Se alguém puser o contador
primeiro, o jogo passa a castigar erros de escrita — e é uma conversa de
design de jogos muito melhor do que uma conversa de sintaxe.

**🥇 Ouro — o jogo ao contrário: o computador adivinha.**
Inversão completa de papéis, e o salto mental é grande: o programa deixa de
verificar respostas e passa a **ter uma estratégia**.

O ficheiro nomeia a estratégia em comentário — **pesquisa binária** — para
poderes dizer o nome à turma. Diz sempre depois de eles verem funcionar,
nunca antes:
> «Ele arrisca sempre o meio. Seja qual for a resposta, deita fora metade dos
> números que sobravam. Por isso adivinha qualquer número de 1 a 100 em sete
> tentativas ou menos, e por isso é que sete era o limite do nível prata.»

Faz as contas no quadro com a turma: 100 → 50 → 25 → 13 → 7 → 4 → 2 → 1.
Sete passos. Toda a gente adora este momento, e é o primeiro algoritmo com
nome do ano.

Repara que o ficheiro deteta batota (`minimo > maximo`). Isso não é um extra:
**alguém vai fazer batota nos primeiros dois minutos**, garantidamente, e sem
esta verificação o programa dá palpites absurdos e parece avariado.

## Erros que os alunos vão cometer

| Sintoma | Causa | A pergunta a fazer |
|---|---|---|
| O jogo nunca acaba, mesmo depois de acertar | Falta atualizar a variável testada no `while` (`acertou = True`) | «Lê-me em voz alta a pergunta que o `while` faz. Em que linha é que a resposta a essa pergunta muda?» |
| `TypeError: '<' not supported between instances of 'str' and 'int'` | Falta o `int()` à volta do `input()` | «O que é que o `input()` te devolve, sempre? E o que é que o `random.randint()` te devolveu?» |
| Nunca acerta, mesmo escrevendo o número certo | Está a comparar texto com número: falta o `int()` | «Manda o computador escrever o palpite e o segredo lado a lado. Parecem iguais no ecrã — mas serão do mesmo tipo?» |
| `ValueError: invalid literal for int() with base 10: 'ola'` | O `int()` recebeu algo que não é número | «O que é que escreveste quando ele te pediu o palpite? O que devia o programa fazer quando alguém escreve isso?» |
| As pistas estão ao contrário e o jogo é impossível | Trocou `<` por `>`, ou trocou as mensagens | «Faz batota: escreve o segredo no ecrã. Agora dá um palpite de propósito muito baixo. O que é que ele te disse?» |
| O ciclo enche o ecrã e não pára | Ciclo infinito sem `input()` lá dentro | «`Ctrl + C` primeiro. Agora: o que é que muda, dentro do ciclo, a resposta à pergunta do `while`?» |
| `IndentationError`, ou linhas do ciclo a correr uma só vez | O corpo do `while` não está todo indentado | «Quais destas linhas querias tu que se repetissem? Estão todas alinhadas umas com as outras?» |
| O contador dá sempre 1 | `tentativas = tentativas + 1` está fora do ciclo, ou `tentativas = 0` está dentro | «Onde é que puseste o `tentativas = 0`? Quantas vezes é que essa linha corre?» |
| Diz "Restam -3 tentativas" | Contador incrementado antes de se testar o limite | «Segue com o dedo: quando ele diz "restam 0", quantas é que já gastaste? E quantas tinhas?» |

## Aviso de âmbito

Nada foi retirado desta sessão. O 🥈 é que é mais pesado do que parece — são
três funcionalidades — e é normal que metade da turma acabe a sessão a meio
dele. Não é problema: o que interessa mesmo, o `while` com saída, está todo no
🥉, e esse toda a gente atinge.

Se estiveres com a turma atrasada aos 60 minutos, **corta o `try/except`** e
mantém contador e limite. Robustez contra texto é a parte menos importante das
três e a que dá menos prazer.

## Critério de sucesso

Aos 90 minutos, ao olhar para a sala:

- [ ] Toda a gente tem um jogo que **acaba**. Um ciclo que sai é o objetivo da
      sessão inteira.
- [ ] Toda a gente já viu um ciclo infinito **no seu próprio ecrã** e parou-o
      sozinha com `Ctrl + C`, sem chamar ninguém. Isto vale mais do que o 🥈.
- [ ] Ninguém está a olhar para um `TypeError` sem saber o que é. A palavra
      `int()` já ganhou significado.
- [ ] Pelo menos dois pares estão a **jogar o jogo um do outro** — sinal de
      que passaram de "escrever código" para "ter feito uma coisa".

**O sinal mais forte da sessão:** um aluno que provoca o ciclo infinito de
propósito, para se rir, e o pára sozinho. Esse aluno deixou de ter medo do
terminal, e é isso que aqui estamos a comprar.

**Sinal de alarme:** alguém a corrigir o código à sorte, a trocar `<` por `>`
e a correr outra vez, sem ler as mensagens. Pára-o e pede-lhe: «explica-me o
que este ciclo está a fazer, linha a linha». Nove em dez vezes descobre o erro
a meio da própria explicação.
