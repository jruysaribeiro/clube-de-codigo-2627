# `juice.py` — sessão 14

## O que é "juice"

Os efeitos que **não mudam nada nas regras** do jogo, mas mudam tudo na
sensação de o jogar. Diz o termo em inglês, é assim que se chama:

> «O jogo funciona exatamente igual com e sem isto. Mas com isto parece um
> jogo a sério, e sem isto parece um trabalho da escola.»

**A sessão 14 é a sessão em que os jogos deles passam a parecer jogos.** Cinco
linhas por efeito. É de longe o melhor retorno de todo o bloco de projeto.

## Como demonstrar (5 min) — a ordem importa

1. Corre o `juice.py`. Carrega em `E` para **desligar** os efeitos.
2. Carrega em `D` (dano) e em `A` (apanhar). Não acontece nada de especial.
3. Carrega em `E` outra vez, para ligar.
4. Carrega em `D` e em `A`.

**Deixa a sala reagir.** É a demonstração mais fácil do ano — o efeito é
imediato e toda a gente quer aquilo no seu jogo. Só depois mostres o código.

## Os dois efeitos

**1. O tremor.** Não se mexe no jogo. Mexe-se em **tudo o que se desenha**, ao
mesmo tempo, uns pixels à sorte para cada lado:
```python
salto_x = random.randint(-8, 8)
salto_y = random.randint(-8, 8)
...
pygame.draw.rect(ecra, COR, jogador.move(salto_x, salto_y))
```
O `move()` devolve um retângulo deslocado **sem mexer no original** — o
jogador continua onde estava, só é *desenhado* noutro sítio. As colisões não
dão por nada.

**2. O crescer.** `inflate()` devolve um retângulo maior à volta do mesmo
centro:
```python
moeda_a_desenhar = moeda.inflate(8, 8)
```
Enquanto o contador não chegar a zero, o objeto é desenhado maior do que é.

**A ideia comum aos dois, e é a que interessa:** um **contador** que vale zero
quando não há efeito, é posto num número quando o efeito começa, e desce até
zero sozinho. É o padrão de qualquer efeito temporário — invulnerabilidade
depois de dano, poder que dura dez segundos, mensagem que aparece e desaparece.

## Onde os alunos se enganam

| Sintoma | A pergunta a fazer |
|---|---|
| O ecrã treme para sempre | «Quem é que faz o contador descer? Essa linha corre em todos os ciclos?» |
| O jogador foge do sítio ao tremer | «Estás a mexer no `jogador`, ou só no que desenhas? O que é que o `move()` devolve?» |
| As colisões passam a falhar durante o tremor | «Mudaste o `jogador` ou mudaste o desenho? O que é que o `colliderect` está a usar?» |
| O objeto fica grande para sempre | «Depois de crescer, o que é que o volta a pôr do tamanho normal?» |
| Só treme uma parte do ecrã | «Quantas coisas é que desenhas? A quantas é que somaste o salto?» |

## Aviso de tempo

Isto é viciante e come uma sessão inteira se deixares. **Dois efeitos por
equipa e chega.** A sessão 14 tem mais que fazer do que tremores.

Se sobrar tempo, o efeito seguinte que vale mesmo a pena não é visual: é
**som**. Um som curto ao apanhar faz mais pela sensação do jogo do que cinco
efeitos de ecrã.
