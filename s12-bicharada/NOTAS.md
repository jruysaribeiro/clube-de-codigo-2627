# Sessão 12 — Bicharada

**Ao contrário do s10 e do s11, este é para dar aos alunos.** Não é um
contra-exemplo: é uma **base**. As mecânicas já estão feitas e funcionam. O
trabalho da equipa é torná-lo *seu*: os bichos, os ataques, os treinadores, a
história, e depois as mecânicas que quiserem acrescentar.

```
python3 bicharada.py
```

| Tecla | Faz |
|---|---|
| setas | mexer nos menus |
| `Enter` / `Espaço` | escolher, e passar o texto à frente |
| `Esc` / `Backspace` | voltar atrás (no ecrã de escolha, tira o último bicho) |

**Como se joga:** escolhes três bichos e enfrentas quatro treinadores, um
atrás do outro. Entre batalhas a equipa é curada. Ganhas ao último, és
campeã(o) da feira.

## O que já lá está

| Mecânica | Onde está no código |
|---|---|
| Quatro tipos com vantagens (fogo > planta > água > fogo) | `CORES_TIPO`, `EFICACIA` |
| Vinte ataques: dano, cura, subir/baixar ataque e defesa | `ATAQUES` |
| Sete bichos, cada um com quatro ataques | `BICHOS` |
| Quatro treinadores com equipas cada vez mais fortes | `TREINADORES` |
| Níveis e experiência: cada nível soma 10% aos valores | `valor_no_nivel()`, `ganhar_xp()` |
| Bónus de 25% quando o ataque é do tipo do bicho | `calcular_dano()` |
| Golpes críticos (1 em 16) e ataques que falham | `usar_ataque()` |
| Ordem por velocidade; trocar e comer sopa vêm sempre primeiro | `jogador_escolheu()` |
| Inimigo que escolhe o ataque com mais jeito, com um pouco de sorte | `escolher_ataque_inimigo()` |
| Imagens opcionais: põe `galo.png` em `comum/assets/imagens/` e aparece | `obter_imagem()` |

## A ideia que vale a pena mostrar

**O jogo inteiro são quatro listas de dados lá em cima, e um motor cá em baixo
que as lê.** É o `projeto/niveis-por-configuracao.py` levado a sério. A
primeira tarefa de qualquer equipa é ler os dados, não o motor.

> «Para inventares um bicho, quantas linhas de código tens de mudar?»
> (Resposta: zero. Escreves um dicionário. O motor não sabe nem quer saber
> quantos bichos há.)

A segunda ideia é **a fila de ações** (`fila_acoes`). Um turno não acontece de
uma vez: executa-se uma ação, mostram-se as mensagens que ela deixou e, só
depois do `Enter`, passa-se à seguinte. É isso que faz o jogo parecer um
Pokémon e não uma folha de cálculo.

## Escada de personalização

Por ordem de dificuldade. A maioria das equipas vai passar o primeiro mês nos
dois primeiros degraus, e está muito bem.

**1. Só dados (não se toca em nenhuma função)**
- Inventar bichos novos. Regra de equilíbrio no comentário: vida + ataque +
  defesa + velocidade dá à volta de 85.
- Inventar ataques novos com os efeitos que já existem.
- Mudar os treinadores: nomes, frases, equipas, cores de fundo. Acrescentar
  um quinto.
- Um tipo novo (elétrico? pedra? fantasma?): uma cor em `CORES_TIPO` e uma
  linha em `EFICACIA`.
- Desenhar os bichos (Piskel, Aseprite, papel e telemóvel) e pô-los em
  `comum/assets/imagens/` com o nome que está em `"imagem"`.

**2. Pequenas mudanças às regras**
- Um efeito novo, por exemplo `"sobe_velocidade"`: mais um `elif` em
  `usar_ataque()`.
- Ataques que tiram vida a quem os usa (*recoil*) ou que curam ao bater.
- Limitar quantas vezes se pode usar cada ataque (os PP do Pokémon).
- O inimigo trocar de bicho quando está em desvantagem de tipo.

**3. Mecânicas novas**
- Estados: envenenado, a dormir, queimado. Um campo novo no bicho e umas
  linhas no fim do turno.
- Evoluções: ao chegar ao nível X, o bicho passa a ser outro (`"evolui_para"`
  e `"nivel_evolucao"` no dicionário).
- Apanhar bichos selvagens em vez de os escolher no início.
- Um mapa para andar entre batalhas, com o `labirinto.py` da sessão 12.
- Som, com o `carregar_som()` do esqueleto.

## Equilíbrio (testado)

Corremos 30 jogos com um robô que escolhe a equipa ao calhas, usa sempre o
ataque com mais dano e **nunca troca de bicho**. O resultado:
- Ao primeiro treinador ganha quase sempre.
- O terceiro e o quarto são onde perde, e **ganhou o jogo todo em 4 de 30**.

Um aluno que troque para o bicho com vantagem de tipo ganha bastante mais
vezes. Se a turma achar difícil demais, os números a mexer são
`NIVEL_INICIAL`, `SOPAS_POR_BATALHA`, os níveis em `TREINADORES` e o `12` em
`ganhar_xp(eu, inimigo["nivel"] * 12)`.

> «Afinar números até o jogo ser justo é trabalho de *game designer* a sério.
> Na Nintendo há pessoas que só fazem isto.»

## Erros previsíveis (e a pergunta a fazer)

| Sintoma | Pergunta |
|---|---|
| `KeyError: 'Bicadaa'` ao arrancar uma batalha | «O nome do ataque no bicho está escrito igual ao nome em `ATAQUES`? Letra a letra, com acentos?» |
| `KeyError: 'eletrico'` ao desenhar | «O tipo novo tem cor em `CORES_TIPO`?» |
| O bicho novo não aparece no ecrã de escolha | «Está dentro das chavetas do `BICHOS`, ou ficou fora?» |
| `SyntaxError` perto de um dicionário novo | «Falta uma vírgula no fim da linha de cima?» |
| Um bicho com mais de quatro ataques sai do painel | «Quantas linhas cabem no painel de baixo?» (A resposta é mudar o desenho, ou ficar com quatro.) |
