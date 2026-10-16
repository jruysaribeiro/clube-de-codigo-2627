# `mecanica-por-genero/` — sessão 12

Cinco ficheiros, cinco técnicas. Cada um corre sozinho, com
`python3 <ficheiro>.py`, e usa só retângulos coloridos — sem imagens, sem
sons, sem menu. É de propósito: quanto menos houver à volta, mais visível
fica a técnica.

| Ficheiro | O género | A técnica que demonstra |
|---|---|---|
| `apanhar.py` | recolher coisas | Lista de objetos + a receita dos sobreviventes |
| `esquivar.py` | não tocar em nada | **Reciclar** objetos: saem por baixo, voltam por cima |
| `labirinto.py` | paredes | Mover e desfazer, **um eixo de cada vez** |
| `chegar-ao-alvo.py` | ir de A a B | Condição de vitória + o alvo a mudar de sítio |
| `plataformas-gravidade.py` | plataformas | Gravidade, chão e salto. **Ver o aviso abaixo** |

## Como usar na sessão 12

Cada equipa já escolheu o género do seu jogo. **Manda cada equipa correr e ler
o ficheiro do seu género** — um só, o seu. Vinte minutos a ler e a mexer nas
constantes vale mais do que qualquer explicação tua.

Depois, a conversa que interessa: «o que é que este ficheiro faz que o teu
jogo precisa?» A resposta é normalmente um bloco de dez linhas, e a tarefa da
sessão é trazê-lo para o ficheiro deles.

## As duas técnicas que valem por si

**Reciclar, no `esquivar.py`.** Os objetos nunca são criados nem destruídos:
quando saem por baixo, voltam para cima noutro sítio. A lista tem sempre o
mesmo tamanho.
> «Se criasses uma pedra nova de cada vez, ao fim de cinco minutos tinhas
> milhares e o jogo ficava lento. Assim tens sempre oito.»

**Um eixo de cada vez, no `labirinto.py`.** É a única técnica de colisão com
paredes que funciona bem sem matemática nenhuma: mexe-se no `x`, e se ficou
dentro de uma parede desfaz-se o `x`; depois mexe-se no `y`, e se ficou dentro
de uma parede desfaz-se o `y`.

Vale a pena mostrar ao vivo o que acontece **se se fizerem os dois juntos**: o
jogador cola-se às paredes e não consegue deslizar ao longo delas. É um bug
que qualquer equipa com paredes vai ter, e reconhecê-lo poupa meia sessão.

## Aviso sobre o `plataformas-gravidade.py`

**Gravidade e colisão com o chão são muito mais difíceis do que tudo o resto
do ano.** Este ficheiro existe para poderes **dar isto feito**.

Não é para descobrirem sozinhos. Não é sequer para perceberem à primeira. Se
uma equipa quiser um jogo de plataformas, a sequência certa é:

1. **copiar o ficheiro e pô-lo a correr**;
2. mexer nas três constantes (`GRAVIDADE`, `FORCA_DO_SALTO`, `QUEDA_MAXIMA`)
   até o salto ter a sensação que eles querem;
3. mudar a lista `plataformas` para desenhar o nível deles;
4. **só depois**, se sobrar tempo e vontade, ler os comentários e perceber
   porquê.

Diz-lhes isto à frente: «isto é código para copiar. Toda a gente faz assim.
Perceber vem depois de funcionar.» Tirar-lhes a vergonha de copiar é metade do
trabalho aqui.

**As três coisas que eles vão querer mudar e que quase de certeza partem:**

- **Saltar com `teclas[]` em vez de `KEYDOWN`.** Resultado: voa. Saltaria 60
  vezes por segundo. A pergunta: «saltar é "estou a segurar" ou "carreguei"?»
- **Tirar o `QUEDA_MAXIMA`.** Resultado: numa queda longa o jogador atravessa
  o chão e desaparece. A pergunta: «quantos pixels é que ele anda num ciclo, ao
  fim de dois segundos a cair? E que espessura tem o chão?»
- **Fazer o `x` e o `y` ao mesmo tempo.** Resultado: cola-se às paredes, ou
  fica preso nos cantos. A pergunta: «quando bateste, foi no chão ou na
  parede? Como é que o programa sabe?»

**Uma equipa por turma, no máximo, devia fazer plataformas.** Se três equipas
quiserem, convence duas a fazer outra coisa — vais passar o bloco de projeto
todo nesta pasta e as outras equipas ficam sem ti.
