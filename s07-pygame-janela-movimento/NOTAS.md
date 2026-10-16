# Sessão 7 — Pygame: janela e movimento

Conceitos: o ciclo do jogo, `pygame.Rect`, `pygame.key.get_pressed()`,
coordenadas do ecrã.

> **Esta é a sessão mais importante do ano.** Não pelo que se aprende hoje —
> hoje aprende-se muito pouco — mas porque nasce aqui o `esqueleto.py`, que é
> o mesmo ficheiro nas sessões 8, 9 e nas oito sessões de projeto. O
> `solucao.py` desta pasta **é** o `comum/esqueleto.py`, byte a byte. Podes
> confirmar com `diff solucao.py ../comum/esqueleto.py`.
>
> O verdadeiro currículo do 2.º e 3.º períodos é a familiaridade com este
> ficheiro. Tudo o resto é acrescento.

**Antes desta sessão, verifica que o `pygame-ce` está instalado em todas as
máquinas da sala.** Uma sessão inteira já se perdeu, algures no mundo, com
`pip install` a falhar em quinze portáteis ao mesmo tempo.

## O que o facilitador precisa de perceber

**O jogo é um desenho refeito 60 vezes por segundo.** É a ideia grande, e a
única que tem mesmo de ficar hoje:
> «Não há nada a mexer-se. O computador apaga o ecrã todo e desenha tudo de
> novo, sessenta vezes por segundo. Como um caderno de folhas em que se
> desenha o boneco um bocadinho mais à frente em cada folha. O movimento está
> nos vossos olhos, não no programa.»

**Os cinco blocos.** Diz estas cinco palavras em voz alta, por esta ordem, em
todas as sessões até junho. Hoje diz-as três vezes:

> **EVENTOS → LÓGICA → DESENHAR → MOSTRAR → ESPERAR**

1. **Eventos** — o que aconteceu desde a última volta? Fecharam a janela?
   Carregaram numa tecla?
2. **Lógica** — as contas. Onde é que as coisas passam a estar.
3. **Desenhar** — pintar tudo na folha invisível.
4. **Mostrar** — pôr a folha no ecrã.
5. **Esperar** — travar, para não correr a mil à hora.

Quando um aluno perguntar «onde é que ponho isto?», a resposta é sempre uma
das cinco palavras. É por isso que elas existem.

**O `Rect` é um retângulo com posição.** Quatro números: `x`, `y`, largura,
altura. E traz extras muito úteis, que valem mais do que parecem:
`jogador.left`, `.right`, `.top`, `.bottom`, `.centerx`. O 🥈 vive deles.

**As coordenadas do ecrã são ao contrário do que se aprende em matemática.**
O `(0, 0)` é o **canto superior esquerdo**, e o **`y` cresce para baixo**.
> «Para subir, subtrai-se ao `y`. Sim, é estranho. É assim em todos os ecrãs
> do mundo, e daqui a duas semanas já não te lembras que achaste estranho.»

Esta é a primeira coisa que toda a gente erra. Não a expliques antes de
alguém tropeçar nela — a lição prende muito melhor com o boneco a ir para o
lado errado no ecrã do próprio.

**`pygame.key.get_pressed()` responde «a tecla está carregada *agora*?»**
Como está dentro do ciclo, é lida 60 vezes por segundo — é isso que faz o
movimento ser contínuo enquanto se segura a tecla. Hoje chega dizer isto. Na
sessão 8 esta distinção volta a sério, e é lá que se resolve de vez.

**Coisas que já vêm feitas e que hoje não se explicam.** O esqueleto traz a
máquina de estados, o som e o reinício com `R` **já a funcionar**. É de
propósito: foi assim que se conseguiu dar Pygame em três sessões em vez de
quatro. Diz à turma o que fazem, em duas frases, e segue:
> «Há uma variável chamada `estado` que diz em que ecrã estamos: menu, jogo ou
> fim. Não lhe mexam hoje. Na sessão 9 vão precisar dela e aí falamos.»

## Sobre os assets — lê isto antes da aula

`comum/assets/` vem **vazia**. Todos os ficheiros correm à mesma: onde havia
de estar uma imagem aparece um retângulo colorido, e onde havia de estar um
som há silêncio.

Se quiseres imagens a sério na sessão 7 — e vale a pena, porque muda a energia
da sala —, segue o `comum/assets/LEIA-ME.md`. São dez minutos, uma vez, e
cobre o ano inteiro. Basta pôr um `jogador.png` na pasta: **nenhum ficheiro
precisa de ser alterado**, a imagem aparece sozinha.

## Demonstração ao vivo (máx. 10 min)

Escreve de raiz no projetor. Este é o único momento do ano em que vale a pena
escrever um ciclo de jogo do zero à frente deles — a partir daqui é sempre o
esqueleto.

**1. A janela mais pequena que existe (2 min).**
```python
import pygame
pygame.init()
ecra = pygame.display.set_mode((800, 600))
```
Corre. A janela aparece **e desaparece logo**. Deixa acontecer.
> «O programa acabou. Chegou ao fim do ficheiro e foi-se embora. Se queremos
> a janela aberta, alguém tem de estar sempre a fazer alguma coisa.»

**2. O ciclo (2 min).**
```python
a_correr = True
while a_correr:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            a_correr = False
```
Corre. A janela fica. **Clica no X.** Fecha.

Agora **apaga o `for` inteiro** e corre outra vez. A janela fica — mas o X não
faz nada, e ao fim de uns segundos o sistema diz que o programa não responde.
> «O `QUIT` é o sistema a bater à porta a dizer "carregaram no X". Se
> ninguém for atender, ele julga que o programa está pendurado.»

Isto vale ouro: explica de uma vez por que razão o ciclo de eventos existe, e
nenhum aluno volta a apagá-lo.

**3. Desenhar e mostrar (2 min).**
```python
    ecra.fill((18, 18, 28))
    pygame.draw.rect(ecra, (70, 130, 230), jogador)
    pygame.display.flip()
```
Corre. Quadrado azul. Agora **tira o `ecra.fill(...)`** e mexe no quadrado:
fica um rasto de tinta pelo ecrã.
> «Não estamos a mover nada. Estamos a desenhar por cima. O `fill` é a
> borracha, e é por isso que ele vem sempre primeiro.»

**4. Mexer (1 min).** Liga as setas e anda. Depois **experimenta ao contrário
de propósito**: põe `jogador.y = jogador.y + 5` no `K_UP`. O boneco desce.
> «Reparem: no ecrã, o `y` cresce para baixo.»

**5. Corre o `erro-proposital.py` (3 min).** ← *é aqui, no fim*

Este é diferente de todos os anteriores, e vale a pena preparares o momento.
Corre. A janela abre. **Está tudo preto.** Carrega na barra de espaços, mexe
nas setas — nada. E o terminal está **limpo**: nenhum vermelho, nenhum
traceback, nenhuma pista.

Deixa o silêncio durar. Depois:
> «Não há mensagem de erro nenhuma. O programa está a correr lindamente, sem
> uma única queixa. Está a desenhar tudo — o menu, o jogador, os pontos — só
> que numa folha que nunca chega a mostrar a ninguém.»

Pergunta:
> «Das nossas cinco palavras — eventos, lógica, desenhar, mostrar, esperar —
> qual é que falta aqui?»

Falta o `pygame.display.flip()`. Acrescenta-o e corre. Aparece tudo.

> **A lição desta sessão não é a linha que falta, é esta:** um programa pode
> estar errado e não se queixar. O ecrã preto é o sintoma mais comum do ano
> inteiro. A partir de hoje, quando alguém disser «não aparece nada», a
> primeira pergunta é sempre: **«tens o `flip`?»**

Escreve isso no quadro. Vais apontar para lá até junho.

## Os três níveis

**🥉 Bronze — mexer nas constantes.**
Cor de fundo, tamanho e cor do quadrado, velocidade. **Não se mexe numa única
linha do ciclo do jogo** — só nos números do topo. Confere o `nivel-bronze.py`:
os valores antigos estão em comentário ao lado dos novos.

Parece pouco. Não é. Estabelece o hábito que sustenta o resto do ano: **as
constantes em maiúsculas são o primeiro sítio onde se mexe.** Toda a gente
tem de chegar aqui, e chega em dez minutos, o que liberta a hora restante para
os outros níveis.

Um bónus que resulta sempre: manda-os pôr `VELOCIDADE = 60` e correr. O boneco
teleporta-se de um lado ao outro do ecrã. Riem-se, e ficam a perceber o que a
velocidade realmente é — pixels por volta do ciclo.

**🥈 Prata — não sair do ecrã, e trocar o quadrado por uma imagem.**

*Os limites* são o exercício sério de hoje. A técnica do `nivel-prata.py` é
deliberadamente a preguiçosa: **deixa sair e depois puxa para trás**.
```python
if jogador.left < 0:
    jogador.left = 0
```
Muitos alunos vão tentar o contrário — impedir o movimento com um `if` antes
de somar. Também funciona, e dá o dobro do trabalho porque são quatro
condições combinadas com quatro teclas. Se um par lá chegar por esse caminho,
**deixa-o terminar** e só depois mostra a outra versão. A conversa
«corrigir depois é mais fácil do que prevenir antes» é uma boa conversa, e não
se pode ter antes de eles terem sofrido a primeira.

Aqui é que os extras do `Rect` compensam: com `.left` e `.right` são quatro
linhas óbvias. Com `x` e `x + largura` são quatro linhas com contas.

*A imagem* é a parte fácil e a que dá mais alegria: **não é preciso mexer no
código**. Basta pôr um `jogador.png` em `comum/assets/imagens/`. Diz isto de
forma explícita, porque é a primeira vez no ano que colhem o fruto de código
escrito com cuidado por outra pessoa:
> «Repara que ninguém teve de mudar nada. A função já estava preparada para
> os dois casos, desde a primeira aula de Pygame.»

**🥇 Ouro — aceleração e atrito, e/ou um segundo jogador.**
O `nivel-ouro.py` traz **os dois** de propósito, no mesmo ficheiro e lado a
lado: as setas com aceleração, o WASD com velocidade constante. Assim
sente-se a diferença com as mãos, que é a única maneira de a perceber.

A ideia é grande e vale a pena dizê-la devagar:
> «Até agora as teclas mexiam na posição. Agora mexem na **velocidade**, e é
> a velocidade que mexe na posição. Uma camada a mais — e de repente o boneco
> tem peso.»

O `ATRITO = 0.92` é o valor a mandar mexer:
- `0.80` → trava a seco, quase como o movimento normal;
- `0.99` → gelo, impossível de controlar, e muito divertido durante cinco
  minutos.

Manda-os experimentar os dois. Descobrir que uma constante define a *sensação*
de um jogo é a primeira aula a sério de design de jogos do ano.

Na sala, propõe **uma** das duas coisas a cada par. Fazer as duas é trabalho
para uma sessão inteira. O segundo jogador é o caminho mais acessível e
prepara bem os jogos de dois do bloco de projeto; a aceleração é mais
interessante e prepara melhor a gravidade das plataformas.

## Erros que os alunos vão cometer

| Sintoma | Causa | A pergunta a fazer |
|---|---|---|
| Ecrã todo preto, nenhuma mensagem de erro | Falta o `pygame.display.flip()` | «Das nossas cinco palavras, qual é a que falta no teu ficheiro?» |
| O boneco deixa rasto de tinta pelo ecrã | Falta o `ecra.fill(...)` no início do bloco de desenhar | «Antes de desenhares o boneco na posição nova, o que é que aconteceu ao da posição antiga?» |
| A janela abre e o sistema diz que não responde | Falta o `for evento in pygame.event.get()` | «Quando clicas no X, alguém está a atender? Onde é que o teu programa trata do `QUIT`?» |
| O boneco desce quando se carrega para cima | O `y` cresce para baixo | «Se o zero é lá em cima e o 600 é cá em baixo, para subir o `y` tem de ficar maior ou mais pequeno?» |
| O boneco anda aos saltos, teleporta-se | `VELOCIDADE` demasiado alta | «Quantos pixels é que ele anda de cada vez que o ciclo dá uma volta? E quantas voltas dá por segundo?» |
| O boneco só anda enquanto se martela a tecla | Pôs o movimento no `KEYDOWN` em vez de usar o `teclas[]` | «O `KEYDOWN` acontece quantas vezes se eu carregar e ficar a segurar? Uma, ou sessenta por segundo?» |
| O boneco anda a mil, sem controlo nenhum | Falta o `clock.tick(FPS)` | «Quantas voltas por segundo é que o teu ciclo está a dar? O que é que devia estar a travá-lo?» |
| `AttributeError: 'Rect' object has no attribute 'X'` | Escreveu `jogador.X` com maiúscula | «O Python distingue maiúsculas de minúsculas. Compara com a linha onde criaste o `Rect`.» |
| `pygame.error: video system not initialized` | Chamou `set_mode` ou `Rect` antes do `pygame.init()` | «Por que ordem é que o computador lê o ficheiro? A linha do `init` já passou quando chega aqui?» |
| A imagem não aparece, fica o quadrado | Nome do ficheiro errado, ou está na pasta errada | «Abre o `LEIA-ME.md` dos assets e lê-me o nome exato que o código procura. Agora lê-me o nome do teu ficheiro.» |
| O boneco pisca ou desaparece | `flip()` chamado dentro do `if`, ou o `fill` depois de desenhar | «Percorre-me as cinco palavras pela ordem certa. A tua ordem é a mesma?» |
| O jogo fica encravado no menu | Está a testar `evento.key` sem verificar antes se `evento.type` é `KEYDOWN` | «Todos os eventos têm uma tecla? O que é que o evento de fechar a janela tem no `evento.key`?» |

## Aviso de âmbito

**Nada foi retirado, mas foi entregue muito mais do que se ensina.** É o
compromisso central desta sessão e convém teres-lhe os olhos abertos:

O esqueleto traz a **máquina de estados** (`menu`/`jogo`/`fim`), o **som já
inicializado** e o **reinício com `R`** já a funcionar. Nada disso se explica
hoje. Os alunos herdam-nos prontos nas sessões 7 e 8, e só lhes mexem na
sessão 9.

Isto foi o que pagou a redução do bloco de Pygame de quatro sessões para três.
Tem um custo real: durante duas sessões há código no ficheiro deles que eles
não escreveram nem percebem. Duas maneiras de gerir isso:

- **Sê explícito.** «Isto vem feito, é para vocês usarem, e daqui a duas
  sessões vão perceber como funciona.» Adolescentes lidam bem com isto se for
  dito à frente. Lidam muito mal com a sensação de que há magia escondida.
- **Não deixes que lhe mexam hoje.** Quem mexer no `estado` na sessão 7 fica
  com o menu partido e perde a sessão inteira. Se alguém insistir, é sinal de
  que está pronto para o 🥇 — manda-o para lá.

## Critério de sucesso

Aos 90 minutos:

- [ ] **Toda a gente tem uma janela aberta com uma coisa que se mexe com as
      setas.** É o mínimo não negociável, e é o momento em que a programação
      deixa de ser texto no terminal.
- [ ] Toda a gente já teve o **ecrã preto** e saiu dele. Este vai acontecer a
      metade da sala sozinho, sem ajuda nenhuma.
- [ ] Toda a gente consegue dizer as **cinco palavras** por ordem. Pergunta a
      dois ou três alunos à saída, em voz alta. Se hesitarem, repete-as na
      próxima sessão logo ao início.
- [ ] Toda a gente chegou ao 🥉 — mexeu nas constantes e viu o jogo mudar.
- [ ] Pelo menos metade tem o boneco a respeitar os limites do ecrã.
- [ ] Ninguém saiu da sala com uma janela que não fecha no X.

**O sinal mais forte da sessão:** um aluno que muda uma constante, corre, não
gosta, e muda outra vez — sem perguntar nada a ninguém. Esse aluno percebeu o
ciclo de trabalho todo (mexer → correr → ver → mexer) e vai passar bem o resto
do ano.

**Sinal de alarme:** um par a escrever muito código. Nesta sessão quem escreve
muito está perdido — o trabalho de hoje são vinte linhas, no máximo. Vai lá e
pergunta: «mostras-me a janela a correr?»
