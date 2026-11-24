# Sessão 15 — Bicharada à Solta

**É a Bicharada do s12 com um mapa por onde se anda.** Os bichos, os ataques,
os tipos e a batalha são os mesmos; o que muda é o que há entre as batalhas.
Como o s12, é uma **base** para os alunos tornarem sua, e foi feito para ser
mexido na Oficina (`python3 oficina/oficina.py`).

```
python3 bicharada-a-solta.py
```

| Tecla | Faz |
|---|---|
| setas | andar pelo mapa, e mexer nos menus |
| `Enter` / `Espaço` | escolher, e passar o texto à frente |
| `Esc` / `Backspace` | voltar atrás (no ecrã de escolha, tira o último bicho) |

**Como se joga:** escolhes três bichos e ficas no mapa. Na erva alta saltam
bichos à solta; os treinadores estão espalhados e desafiam-se indo contra
eles, pela ordem que se quiser. Ganhas a todos os que estão no mapa, és
campeã(o) da feira.

## O que muda em relação ao s12

| No s12 | Aqui |
|---|---|
| Quatro treinadores, um atrás do outro | Os treinadores estão no `MAPA` (as letras `1` a `9`) |
| A equipa é curada antes de cada batalha | Só a casa da avó (`H`) cura, e é lá que se enchem as sopas |
| Perder é recomeçar do início | Acordas onde descansaste pela última vez, com os treinadores vencidos na mesma |
| Só há batalhas contra treinadores | Há bichos à solta na erva alta (`e`), e deles pode-se **Fugir** |

O s12 continua como estava: quem já lá tem um jogo seu não perde nada.

## O que há de novo para mudar

| Coisa | Onde está no código |
|---|---|
| O mapa, desenhado com letras | `MAPA` |
| Onde se pode andar | `pode_andar()` |
| Quando salta um bicho da erva | `ha_batalha_na_erva()`, `SORTE_NA_ERVA` |
| Que bicho salta, e com que nível | `escolher_bicho_selvagem()` |
| O que acontece a cada passo, em casa da avó, a cada frame | `ao_dar_passo()`, `ao_descansar()`, `a_cada_frame()` |
| Os desenhos do mapa | `desenhar_quadrado()`, `desenhar_jogador()`, `desenhar_treinador()` |

Na Oficina, cada uma destas coisas abre num palco já no mapa, com o boneco a
andar sozinho. No `MAPA` anda só a criança, para o mapa não lhe fugir.

## Ideias, por ordem de dificuldade

**1. Só o mapa.** Redesenhar tudo: um lago, um labirinto de árvores, o
treinador mais forte fechado ao fundo. A Oficina avisa se um treinador ficar
onde não se chega.

**2. Regras pequenas.** Nadar (passar na água com um bicho de água na
equipa); só bichos de planta num lado do mapa; nunca dois bichos seguidos.

**3. Coisas que o jogo não tem.**
- Uma letra nova: `s` é uma sopa perdida no chão. Precisa de um `if` em
  `ao_dar_passo()` e de um desenho em `desenhar_quadrado()`.
- **Apanhar bichos à solta.** Não vem feito de propósito: é o melhor
  exercício do jogo. A receita está no comentário de `ao_carregar_tecla()`.
- A campeã só aceitar o desafio de quem já venceu os outros.

## Equilíbrio

Não foi afinado como o s12: só foi jogado uma vez de ponta a ponta, por um
robô que treina na erva até ao nível 9, descansa quando a equipa está fraca e
só depois desafia os treinadores (ganhou, com uma derrota pelo caminho). Os
números a mexer são `NIVEL_INICIAL`, `SOPAS_NA_MOCHILA`,
`SORTE_NA_ERVA`, os níveis em `TREINADORES` e o `random.randint(1, 3)` de
`escolher_bicho_selvagem()`.

## Erros previsíveis (e a pergunta a fazer)

| Sintoma | Pergunta |
|---|---|
| O treinador novo não aparece no mapa | «Que número é ele na lista `TREINADORES`? Esse número está escrito no `MAPA`?» |
| O boneco começa num sítio estranho | «Onde está o `P`? Há só um?» |
| Uma linha do mapa fica mais curta | «Quantas letras tem essa linha? E as outras?» (O que falta fica árvores.) |
| `UnboundLocalError` em `sopas` | «Qual é a primeira linha da função? Falta o `global sopas`?» |
| O texto de `dizer()` desaparece logo | «No mapa, a caixa dura até ao passo seguinte. Quando é que a chamas?» |
