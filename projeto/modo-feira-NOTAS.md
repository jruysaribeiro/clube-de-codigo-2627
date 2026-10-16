# `modo-feira.py` — sessão 16

## O problema

Demo Day. O jogo está em cima de uma mesa. Quem chega **nunca o viu**, **não
lê instruções**, carrega em tudo ao mesmo tempo, e **vai-se embora a meio**
sem dizer nada. Não há ninguém da equipa colado à máquina o tempo todo.

Um jogo que funciona na sessão não é a mesma coisa que um jogo que sobrevive a
isto. **A sessão 16 serve para fazer essa transformação**, e a maior parte dela
não é código.

## Os quatro requisitos

**1. Recomeçar com uma tecla, sem fechar a janela.**
Vem do `comum/esqueleto.py` desde a sessão 7 — é por isso que lá está desde o
início. A única coisa a acrescentar: **a mesma tecla nos dois ecrãs**. Se no
menu é o espaço e no fim é o `R`, metade das pessoas fica presa no ecrã de fim.

**2. Voltar sozinho ao menu ao fim de 10 segundos parado.**
```python
ultimo_toque = pygame.time.get_ticks()   # sempre que alguem carrega numa tecla
...
if pygame.time.get_ticks() - ultimo_toque > 10 * 1000:
    comecar_jogo()
    estado = "menu"
```
Sem isto, a terceira pessoa da fila encontra o jogo a meio da partida de
outra, com meia vida e sem perceber nada. **É o requisito que mais melhora um
Demo Day** e o que ninguém se lembra sozinho.

**3. Sem consola visível.**
Zero `print()` no ficheiro. Confirma com uma busca por `print(` antes do dia.
Duas razões: uma janela preta atrás do jogo estraga o efeito, e um `print` a
cada ciclo abranda o jogo mais do que se imagina.

Para lançar sem terminal nenhum:
- **Windows:** muda a extensão de `.py` para **`.pyw`** e faz duplo clique.
- **macOS:** duplo clique no `.py` abre um terminal por trás. Se incomodar,
  põe o jogo em ecrã inteiro (`pygame.FULLSCREEN`) por cima dele.
- Em qualquer sistema: abre a janela **antes** de as pessoas chegarem e não
  lhe toques mais.

**4. Sobreviver a alguém carregar em todas as teclas ao mesmo tempo.**
E vai acontecer, nos primeiros dez minutos, garantidamente.

O ficheiro trata disto por **não ter nenhuma lista de teclas proibidas**:
qualquer `KEYDOWN` conta como sinal de vida, e só umas quantas fazem alguma
coisa. As restantes são ignoradas em silêncio. Não há nenhuma tecla que possa
partir isto.

As quatro setas ao mesmo tempo também não partem nada: as somas anulam-se e o
jogador fica quieto. É o comportamento certo.

## Um teste que dura um minuto e vale a sessão inteira

Faz isto com cada equipa, e faz **tu**, não eles:

1. Senta-te ao computador **sem dizer nada** e sem que te expliquem o jogo.
2. Passa as duas mãos abertas por cima do teclado.
3. Deixa-o parado meio minuto.
4. Perde de propósito e tenta jogar outra vez.
5. Perde outra vez e tenta jogar outra vez.

Se em qualquer momento ficaste sem saber o que fazer, ou o jogo rebentou, ou
não conseguiste recomeçar — **isso é o trabalho da sessão 16**.

## A parte que não é código

Grande parte disto não se resolve a programar:

- **O ecrã inicial diz como se joga**, em duas linhas curtas. «Setas para
  andar. ESPAÇO para jogar.» Nada mais. Ninguém lê o terceiro.
- **O objetivo tem de ser óbvio nos primeiros cinco segundos**, sem ninguém
  explicar.
- **Uma partida dura menos de dois minutos.** Há fila. Se uma partida demora
  cinco minutos, metade das pessoas vai-se embora.
- **Não há nada escrito em letra pequena.** Vê-se de pé, de lado, com má luz.
- **Alguém da equipa fica ao lado da mesa** — não para explicar, mas para ver
  as pessoas a jogar. É a coisa mais útil que vão fazer no dia todo.

## O que dizer à turma na sessão 16

> «Hoje não se acrescenta nada ao jogo. Hoje faz-se com que ele aguente
> desconhecidos. Um jogo que funciona quando são vocês a jogar não é a mesma
> coisa que um jogo que funciona quando é a vossa avó a jogar.»

## Aviso de âmbito

Alguém vai querer usar a sessão 16 para acrescentar aquela funcionalidade que
faltou. Não deixes. É a última sessão antes do Demo Day, e um jogo partido na
véspera não tem como ser reparado a tempo.

A regra é a mesma da sessão 9, e agora já a conhecem: **feature freeze**. Desta
vez para o bloco todo.
