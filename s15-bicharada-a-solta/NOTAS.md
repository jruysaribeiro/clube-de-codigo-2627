# Sessão 15 — Bicharada à Solta

**É a Bicharada do s12 com um mundo por onde se anda.** Os bichos, os ataques,
os tipos e a batalha são os mesmos; o que muda é o que há entre as batalhas.
O mundo é feito de **zonas**, cada uma do tamanho do ecrã: quem sai por um
lado de uma entra na do lado. Há **edifícios** onde se entra pela porta.
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

**Como se joga:** escolhes três bichos e ficas na aldeia. Na erva alta saltam
bichos à solta; os treinadores estão espalhados pelas zonas (o primeiro está
dentro da mercearia) e desafiam-se indo contra eles, pela ordem que se
quiser. Ganhas a todos, és campeã(o) da feira.

O mundo que vem feito tem nove zonas, três por três, e um edifício:

```
serra    montado   feira
aldeia   ribeira   pinhal
horta    praia     farol
```

## O que muda em relação ao s12

| No s12 | Aqui |
|---|---|
| Quatro treinadores, um atrás do outro | Os treinadores estão nas zonas (as letras `1` a `9`) |
| A equipa é curada antes de cada batalha | Só a casa da avó (`H`) cura, e é lá que se enchem as sopas |
| Perder é recomeçar do início | Acordas onde descansaste pela última vez, com os treinadores vencidos na mesma |
| Só há batalhas contra treinadores | Há bichos à solta na erva alta (`e`), e deles pode-se **Fugir** |

O s12 continua como estava: quem já lá tem um jogo seu não perde nada.

## O que há de novo para mudar

| Coisa | Onde está no código |
|---|---|
| Cada zona, desenhada com letras (20 por linha, 14 linhas) | `ZONAS` |
| Como as zonas se juntam | `MUNDO` |
| Os edifícios: que letra é a porta de que interior | `PORTAS` |
| Onde se pode andar | `pode_andar()` |
| Quando salta um bicho da erva | `ha_batalha_na_erva()`, `SORTE_NA_ERVA` |
| Que bicho salta, e com que nível | `escolher_bicho_selvagem()` |
| O que acontece a cada passo, em casa da avó, a cada frame | `ao_dar_passo()`, `ao_descansar()`, `a_cada_frame()` |
| Os desenhos do mapa | `desenhar_quadrado()`, `desenhar_jogador()`, `desenhar_treinador()` |

Não há limite para as zonas nem para os edifícios: são mais entradas em
`ZONAS`. Os limites são outros: nove treinadores (um algarismo cada), um `P`
no mundo todo, e uma letra livre para cada porta.

Na Oficina:
- cada **zona** abre sozinha, com o boneco lá dentro, e anda só a criança,
  para o mapa não lhe fugir;
- **O mundo** e **As portas** mostram o mundo todo visto de cima, em ponto
  pequeno, com os edifícios por baixo;
- os botões **+ Nova zona** e **+ Novo edifício** criam uma zona de relva (e
  juntam-na ao `MUNDO`) ou uma sala com porta (e põem a casa na aldeia);
- as funções abrem com o boneco a andar sozinho.

A Oficina avisa quando uma zona, um treinador ou uma casa da avó ficam onde
não se chega a pé: é assim que se dá por duas saídas que não batem certo.

## Ideias, por ordem de dificuldade

**1. Só o mapa.** Redesenhar uma zona: um lago, um labirinto de árvores, o
treinador mais forte fechado ao fundo. Trocar zonas de sítio no `MUNDO`.
Uma zona nova, à direita do pinhal (que já tem lá uma saída à espera). Um
ginásio: um edifício com um treinador dentro.

**2. Regras pequenas.** Nadar (passar na água com um bicho de água na
equipa); só bichos de água na praia (`jogador["zona"] == "praia"`); bichos
mais fortes na serra; nunca dois bichos seguidos.

**3. Coisas que o jogo não tem.**
- Uma letra nova: `s` é uma sopa perdida no chão. Precisa de um `if` em
  `ao_dar_passo()` e de um desenho em `desenhar_quadrado()`.
- **Apanhar bichos à solta.** Não vem feito de propósito: é o melhor
  exercício do jogo. A receita está no comentário de `ao_carregar_tecla()`.
- A campeã só aceitar o desafio de quem já venceu os outros.

## Equilíbrio

Não foi afinado como o s12: só foi jogado uma vez de ponta a ponta, por um
robô que treina na erva até ao nível 9, descansa quando a equipa está fraca e
só depois desafia os treinadores (ganhou em 467 passos, com uma derrota pelo
caminho). Os
números a mexer são `NIVEL_INICIAL`, `SOPAS_NA_MOCHILA`,
`SORTE_NA_ERVA`, os níveis em `TREINADORES` e o `random.randint(1, 3)` de
`escolher_bicho_selvagem()`.

## Erros previsíveis (e a pergunta a fazer)

| Sintoma | Pergunta |
|---|---|
| O treinador novo não aparece no mapa | «Que número é ele na lista `TREINADORES`? Esse número está escrito nalguma zona?» |
| O boneco começa num sítio estranho | «Onde está o `P`? Há só um, no mundo todo?» |
| Uma linha da zona fica mais curta | «Quantas letras tem essa linha? E as outras?» (O que falta fica árvores.) |
| Não se passa de uma zona para a do lado | «Há relva na borda das duas, na mesma linha? E no `MUNDO`, estão mesmo lado a lado?» |
| Uma zona aparece toda desalinhada | «Falta uma vírgula no fim de uma linha?» (Sem ela, o Python cola duas linhas numa.) |
| Entra-se na porta e não acontece nada | «A letra está em `PORTAS`? E está escrita lá dentro, na parede do interior?» |
| `UnboundLocalError` em `sopas` | «Qual é a primeira linha da função? Falta o `global sopas`?» |
| O texto de `dizer()` desaparece logo | «No mapa, a caixa dura até ao passo seguinte. Quando é que a chamas?» |
