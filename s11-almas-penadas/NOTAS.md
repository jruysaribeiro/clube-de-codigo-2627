# Sessão 11 — Almas Penadas

**Mais um contra-exemplo.** Se o FADO//NEON (s10) era o jogo do ano, este é o
jogo que te faz chorar. Um *soulslike* visto de cima, num só ficheiro, sem
assets.

> D. Sebastião desapareceu no nevoeiro em 1578 e prometeu voltar numa manhã
> de nevoeiro. Hoje está nevoeiro.

```
python3 almas-penadas.py
```

Joga-se **só com o teclado**.

| Tecla | Faz |
|---|---|
| `WASD` / setas | mover (`Shift` a manter: correr) |
| `Espaço` | rolar. É invulnerável a meio do rolamento |
| `J` ou `Z` | ataque leve. Três seguidos fazem um combo |
| `K` ou `X` | ataque pesado. Lento, mas parte a postura |
| `L` ou `C` | aparar (*parry*) |
| `Q` | beber caldo verde (cura) |
| `Tab` ou `R` | fixar o alvo |
| `E` / `Enter` | interagir: fogareiros, mensagens, portas, nevoeiro |
| `Esc` | pausa (mostra os controlos todos) |

**A regra mais importante do jogo:** antes de cada golpe, o inimigo brilha.
Brilho **branco** apara-se com `L` e depois um `J` dá um golpe crítico.
Brilho **vermelho** não se apara: rola.

## O que lá está dentro (a lista de verificação de um soulslike)

| Coisa | No jogo |
|---|---|
| Fogueira | Um **fogareiro** com três sardinhas. Acende-se, descansa-se, sobe-se de nível. Descansar faz os inimigos voltarem |
| Frasco de cura | **Caldo verde**. Quatro tigelas, e há uma quinta escondida |
| Almas | Caem quando morres. Se morreres outra vez antes de lá chegar, perdem-se |
| Atalho | Uma porta que **não abre deste lado** |
| Mensagens no chão | «Rola com ESPAÇO. A sério, rola.» |
| Porta de nevoeiro | Antes de cada chefe. Uma vez lá dentro, não se sai |
| Chefe a meio | O **Guarda da Calçada**. Abre o caminho quando cai |
| Chefe final | **D. Sebastião, o Desejado**. A meio da luta o nevoeiro adensa-se, ele teletransporta-se e chama cavaleiros fantasma |
| Fim | Créditos e **Novo Jogo+** (fica-se com o nível, os inimigos ficam mais fortes) |

## As três ideias que valem a pena mostrar

- **O mapa é uma lista de strings.** `#` é parede, `o` é uma ossada, `F` é um
  fogareiro. Mudar uma letra muda o mundo. É a mesma ideia do
  `projeto/niveis-por-configuracao.py`, levada ao limite.
- **A luz é uma multiplicação.** Pinta-se uma superfície escura, somam-se
  círculos de luz por cima (`BLEND_RGB_ADD`) e multiplica-se o ecrã por ela
  (`BLEND_RGB_MULT`). Onde a luz é preta, o ecrã fica preto. São dez linhas.
- **Todos os golpes têm três fases:** anúncio, golpe e recuperação
  (`ante`, `ativo`, `rec` no código). O jogo inteiro é isto. Rola-se no
  anúncio, castiga-se na recuperação.
