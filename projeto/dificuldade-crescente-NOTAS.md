# `dificuldade-crescente.py` — sessão 13

## A ideia, em trinta segundos

A alternativa simples aos níveis: **não há níveis nenhuns**. A velocidade é
que sobe com o tempo.

```python
segundos = (pygame.time.get_ticks() - inicio) // 1000
queda = QUEDA_INICIAL + segundos * SUBIDA_POR_SEGUNDO
```

São mesmo só estas duas linhas. Para muitos jogos é **melhor** do que níveis a
sério: a dificuldade é contínua, cada partida é diferente, e não é preciso
desenhar nível nenhum.

## O que o facilitador tem de saber

**O tecto não é opcional.**
```python
if queda > QUEDA_MAXIMA:
    queda = QUEDA_MAXIMA
```
Sem ele, ao fim de dois minutos os objetos andam tantos pixels por ciclo que
**atravessam o jogador sem lhe tocar**. O jogo fica impossível *e* deixa de
detetar colisões — e o bug parece impossível de encontrar, porque só acontece
depois de se jogar muito tempo.

Este é um bug clássico de fim de bloco de projeto. Se uma equipa te disser «às
vezes o inimigo passa por cima e não morro», a primeira pergunta é: «quantos
pixels é que ele anda em cada volta do ciclo?»

**A curva está toda em três constantes:**
- `QUEDA_INICIAL` — quão fácil começa;
- `SUBIDA_POR_SEGUNDO` — quão depressa aperta. `0.25` é suave; `1.0` é brutal;
- `QUEDA_MAXIMA` — o tecto.

Manda-os afinar estas três a jogar. **É a primeira vez que fazem afinação de
jogo a sério**, e é uma conversa muito melhor do que parece: «quanto tempo é
que queres que uma partida dure?»

## Como escolher entre isto e os níveis

| Usa `dificuldade-crescente.py` | Usa `niveis-por-configuracao.py` |
|---|---|
| Jogo de aguentar o máximo de tempo | Jogo com fases mesmo diferentes |
| Sem fim, pontuação alta | Com fim, com "acabaste" |
| Duas linhas | Uma lista e um bloco que a lê |

Na dúvida, o crescente. É metade do trabalho e resulta bem em quase tudo.
