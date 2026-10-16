# Sessão 10 — Jogo do Ano

**Estas notas são diferentes das outras.** Na sessão 9 dissemos aos alunos,
com estas palavras:

> «Escolher pequeno é uma competência, não uma desistência.»

Esta pasta é o contra-exemplo. **Não é para dar aos alunos como modelo.** É
para lhes mostrar no fim de uma aula, com as luzes apagadas, e dizer:

> «Isto é o que acontece quando ninguém escolhe pequeno. Um ficheiro, mil e
> tal linhas, zero assets. Vocês já conhecem cada peça que está aqui dentro.
> Só que está tudo ao mesmo tempo.»

## O que está nesta pasta

| Ficheiro | O que é |
|---|---|
| `fado-neon.py` | FADO//NEON. Um roguelite twin-stick de saudade. Jogo do Ano 2026 (segundo o próprio jogo) |

```
python3 fado-neon.py
```

Joga-se **só com o teclado**. O rato é opcional.

| Tecla | Faz |
|---|---|
| `WASD` | mover |
| setas | disparar nessa direção (à Binding of Isaac) |
| `Espaço` / `Shift` | investida (dash), invulnerável durante |
| `E` | **LASER**, quando a barra por baixo dos corações encher (enche a matar) |
| `1` `2` `3`, ou `←` `→` e `Enter` | escolher melhoria entre ondas |
| `T` | tiro automático (aponta sozinho, ideal para demonstrar no projetor) |
| `Esc` / `P` | pausa |
| `F` · `M` · `B` · `C` · `F3` | ecrã inteiro · música · bloom · efeito CRT · FPS |

Com rato: aponta-se com ele, o clique esquerdo dispara, o direito investe e o
do meio dispara o laser.

**Como se ganha:** sobrevive a 10 ondas. O Saudosista aparece na onda 5 e na
onda 10, e na segunda vez varre a arena com lasers. Quem o derrota vê os
créditos e pode continuar no modo infinito.

## O que lá está dentro, e em que sessão o viram

A piada é esta: **não há nada aqui que eles não conheçam.** Só há muito.

| No FADO//NEON | Onde aprenderam a peça |
|---|---|
| Ecrã de título, jogo, fim, `R` para recomeçar | S09: o esqueleto de estados |
| Ondas que ficam mais difíceis | `projeto/dificuldade-crescente.py` |
| Tremor de ecrã, partículas, números a voar | `projeto/juice.py`, só que com esteroides |
| Corações, pontuação, combo | `projeto/hud.py` |
| Quatro tipos de inimigo e um chefe | `projeto/mecanica-por-genero/` |
| Melhorias em cartas | Listas da S03 |

E o que é **mesmo** novo, para os curiosos:

- **O som é todo sintetizado.** `gerar_varrimento()` escreve a onda número a
  número para dentro de um `array`. A música (Lá menor, Fá, Dó, Mi: a cadência
  andaluza) é composta da mesma forma ao arrancar o jogo.
- **A grelha do fundo é uma malha de molas.** Cada ponto é puxado para o seu
  sítio e para a média dos vizinhos. As explosões empurram-na e a onda
  propaga-se sozinha.
- **O bloom é um truque.** Encolhe-se o ecrã com `smoothscale`, volta-se a
  esticar (fica desfocado) e soma-se por cima com `BLEND_RGB_ADD`. São cinco
  linhas.

## Se um aluno perguntar «posso fazer isto no meu projeto?»

Sim, depois de ter um jogo acabado. Antes não. Aponta-lhe para a definição
de pronto que está no quadro desde a sessão 9.
