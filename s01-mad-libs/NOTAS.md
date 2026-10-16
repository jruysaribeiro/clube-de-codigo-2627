# Sessão 1 — Gerador de histórias malucas

Conceitos: `print`, variáveis, `input()`, f-strings, comentários.

## O que o facilitador precisa de perceber

Quatro ideias. Cada uma cabe em 30 segundos, e é assim que se dizem em voz
alta, sem jargão:

**Uma variável é uma etiqueta colada a uma coisa.**
> «Escrevo `nome = "Rita"`. A partir daqui, sempre que eu escrever `nome`, o
> computador vai lá buscar "Rita". É uma etiqueta. E posso colá-la noutra
> coisa a qualquer momento — é por isso que se chama variável.»

**`input()` pára o programa e espera.**
> «Esta linha faz três coisas: escreve a pergunta no ecrã, pára tudo até
> alguém carregar no Enter, e guarda o que a pessoa escreveu. O programa fica
> mesmo parado — não está avariado, está à espera de ti.»

**`input()` devolve sempre texto.** Não é preciso dizer isto hoje, mas é
preciso *saber* hoje, porque é a fundação de toda a sessão 2. Se alguém
perguntar «e se eu escrever um número?», a resposta é: «continua a ser texto,
para o computador. Na próxima sessão vais ver porque é que isso é um
problema.»

**A f-string mete variáveis dentro do texto.**
> «Reparem no `f` antes das aspas. Ele avisa o Python: dentro deste texto há
> chavetas, e o que está dentro das chavetas não é para escrever tal e qual —
> é para ir buscar. Sem o `f`, aparece no ecrã `{nome}`, mesmo assim, com
> chavetas e tudo.»

Vale a pena mostrar isso de propósito: apaga o `f`, corre, mostra o resultado
absurdo, põe o `f` outra vez. Cinco segundos, e a ideia fica presa.

**Sobre os comentários:** o `#` não é decoração. Diz aos alunos que o
computador não lê aquela linha, e que os comentários existem para o próprio —
o que escreverem hoje é para o eu de daqui a duas semanas, que já se esqueceu
de tudo. Neste clube, com sessões de quinze em quinze dias, isto não é uma
frase feita: é literalmente verdade.

## Demonstração ao vivo (máx. 10 min)

Escreve no projetor, de raiz, sem colar. Vão vendo o ficheiro a crescer.

**1. Só um `print` (1 min).**
```python
print("Ola!")
```
Corre. Sai `Ola!`. Ponto. «Isto é um programa. Já está.»

**2. Uma variável (2 min).**
```python
nome = "Rita"
print(nome)
print("nome")
```
Corre. Sai `Rita` e depois `nome`. Pergunta à turma porquê **antes** de
explicares. Alguém acerta. As aspas fazem a diferença: com aspas é texto tal
e qual, sem aspas é a etiqueta.

**3. `input()` (2 min).**
```python
nome = input("Como te chamas? ")
print(nome)
```
Corre. **Deixa o cursor a piscar uns segundos sem escrever nada.** «Reparem:
está parado. Não avariou. Está à espera.» Escreve um nome. Enter.

**4. A f-string (2 min).**
```python
print(f"Ola, {nome}! Bem-vindo ao clube.")
```
Corre. Depois **apaga o `f`** e corre outra vez: aparece `Ola, {nome}!`.
«Foi o `f` que fez a diferença.» Põe o `f` de volta.

**5. Corre o `erro-proposital.py` (3 min).** ← *é aqui, no fim*

Não digas o que está mal. Corre. Rebenta:

```
  File "erro-proposital.py", line 9
    animal = input("Escreve um animal: )
                   ^
SyntaxError: unterminated string literal (detected at line 9)
```

Ensina a **ler o traceback**, e faz esta leitura em voz alta, sempre pela
mesma ordem — é o hábito que se está a instalar, mais do que o erro de hoje:

1. **Qual é o ficheiro?** `erro-proposital.py`.
2. **Qual é a linha?** A 9. Vai lá.
3. **O que diz a última linha da mensagem?** `unterminated string literal` —
   «uma frase entre aspas que nunca acabou».
4. **O que aponta a setinha `^`?** Onde o Python se perdeu.

Depois pergunta à turma o que falta, e **deixa-os encontrar**. O erro é uma
aspa por fechar no fim de `"Escreve um animal: `. Corrige, corre, funciona.

> **A frase para repetir todas as sessões:** «O computador está a dizer-te
> onde está o problema. A mensagem vermelha é ajuda, não é castigo.»
> Metade do medo de programar morre aqui, na primeira sessão.

## Os três níveis

Todos partem do mesmo `esqueleto.py`. O que muda é a ambição, e cada nível
tem uma dificuldade genuína, não é só «mais do mesmo».

**🥉 Bronze — cinco `input()`, história e perguntas trocadas.**
Prova que perceberam a mecânica: pedir, guardar, usar. A dificuldade real é
sem código nenhum — é inventar uma história em que as cinco palavras encaixem
com graça. Muitos vão passar mais tempo a escrever a história do que Python,
e isso está certo.

**🥈 Prata — oito ou mais `input()`, vários parágrafos, título em ASCII.**
Duas dificuldades novas. Com oito variáveis, esquecer-se de uma passa a ser
provável: é a primeira vez que precisam de se organizar. E a arte ASCII traz
a barra invertida — para desenhar um `\` num `print` é preciso escrever `\\`.
Não expliques *escape sequences*; dá a receita: «para aparecer uma barra
destas, tens de escrever duas».

**🥇 Ouro — a história varia sozinha.**
Salto qualitativo: o programa deixa de fazer sempre a mesma coisa. Entram
três conceitos de uma vez — `import`, a lista, e `random.choice()`. A lista é
o que interessa a longo prazo (sessão 3 vive dela), mas hoje não a expliques
a fundo: «é uma caixa com várias coisas lá dentro, e o `random.choice` tira
uma à sorte». Chega.

O `nivel-ouro.py` sorteia para variáveis **antes** do `print`, de propósito.
Sortear dentro do `print` funciona, mas fica ilegível — e se um aluno chegar
lá sozinho, vale a pena mostrar-lhe as duas versões lado a lado e perguntar
qual é que ele consegue explicar mais depressa.

## Erros que os alunos vão cometer

A terceira coluna é a **pergunta a fazer**. Não toques no teclado do aluno,
e não leias a resposta em voz alta — é a diferença entre o aluno resolver e o
aluno ver-te resolver.

| Sintoma | Causa | A pergunta a fazer |
|---|---|---|
| `SyntaxError: unterminated string literal` | Falta uma aspa a fechar | «O Python diz que a linha 9 tem uma frase que nunca acabou. Consegues contar comigo as aspas dessa linha?» |
| Aparece `{nome}` no ecrã, com chavetas | Falta o `f` antes das aspas | «Compara essa linha com uma que esteja a funcionar. Qual é a única letra que está numa e não está na outra?» |
| `NameError: name 'nome' is not defined` | Escreveu `Nome` com maiúscula, ou trocou uma letra | «O Python diz que nunca ouviu falar de `Nome`. Vai à linha onde a criaste — está escrita exatamente da mesma maneira?» |
| `NameError` numa variável que existe mesmo | Usou a variável **acima** da linha que a cria | «O computador lê de cima para baixo, como tu. Quando chega a esta linha, já passou pela linha onde criaste a variável?» |
| O programa parece bloqueado, não faz nada | Está num `input()` à espera de Enter | «Olha para o ecrã: o que é que o programa te pediu na última linha que escreveu?» |
| `IndentationError: unexpected indent` | Deixou um espaço no início da linha | «O Python diz que esta linha começa demasiado à direita. Põe o cursor mesmo antes do `p` e carrega em Home — para onde é que ele salta?» |
| A pergunta e a resposta colam-se: `Como te chamas?Rita` | Falta um espaço antes da aspa de fecho, no texto do `input()` | «Onde é que o computador começa a escrever a tua resposta? Como é que lhe darias mais espaço?» |
| A história sai toda na mesma linha | Vários `print` sem nada a separar, ou usou vírgulas em vez de vários `print` | «Cada `print` escreve uma linha. Quantos `print` tens, e quantas linhas querias?» |

**Erro de facilitador, e é o mais comum de todos:** apontar para o ecrã e
dizer «falta aí um `f`». Custa três segundos e apaga a aprendizagem toda.
Se estiveres com pressa, a versão curta honesta é: «tens um erro entre a
linha 8 e a linha 12» — reduz o espaço de procura sem dar a resposta.

## Critério de sucesso

**A sala está a rir-se.** É mesmo este o indicador, e não é uma brincadeira:
esta sessão é a que decide se eles voltam daqui a duas semanas. Se estiverem
a mostrar histórias uns aos outros e a rir-se, a sessão resultou, mesmo que
alguém tenha ficado no bronze.

Ao olhar para a sala, aos 90 minutos:

- [ ] **Toda a gente** tem um programa que corre e escreve uma história. Sem
      exceções — este é o mínimo não negociável da sessão 1.
- [ ] Toda a gente viu pelo menos um erro vermelho no *seu próprio* ecrã e
      saiu dele. Quem não teve um erro hoje vai ter um susto na sessão 2.
- [ ] Pelo menos metade da turma chegou ao 🥉, com uma história inventada por
      eles e não a do esqueleto.
- [ ] Ninguém saiu da sala sem ter corrido o seu programa **em voz alta** para
      o par do lado.

Se alguém chegou ao 🥇, ótimo — mas não é critério. Ninguém deve sair desta
sessão com a ideia de que programar é difícil. Sai com a ideia de que
programar dá para fazer disparates, que é exatamente onde queremos que
estejam antes da sessão 2.

**Sinal de alarme:** um aluno calado, com o ecrã igual ao do início, aos 40
minutos. Não é preguiça, é quase sempre um erro que ele não se atreveu a
mostrar. Vai lá e pergunta: «mostras-me o vermelho?»
