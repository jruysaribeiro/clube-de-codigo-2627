# Sessão 13 — O Cerco

**Ao contrário do s10 e do s11, este é para dar aos alunos.** É uma **base**
de *tower defense*: as mecânicas estão feitas e funcionam. O trabalho da
equipa é torná-lo *seu*: o mapa, as torres, os inimigos, as ondas, o tema.

> Guimarães, 1128. Aqui nasceu Portugal. Convinha que não morresse já hoje.

```
python3 o-cerco.py
```

Joga-se **com o rato**, e as teclas ajudam.

| Tecla | Faz |
|---|---|
| `1` `2` `3` `4` (ou clicar na barra de baixo) | escolher a torre a construir |
| clique esquerdo | construir na relva, ou escolher uma torre já feita |
| clique direito / `Esc` | cancelar a escolha |
| `U` | melhorar a torre escolhida (até ao nível 3) |
| `V` | vender a torre escolhida (devolve 60%) |
| `Espaço` | mandar vir a próxima onda |
| `F` | velocidade a dobrar |
| `P` | pausa |

**Como se ganha:** aguenta as dez ondas. A última traz o General.

## O que já lá está

| Mecânica | Onde está no código |
|---|---|
| Mapa desenhado em texto, com caminho encontrado sozinho | `MAPA`, `encontrar_caminho()` |
| Quatro torres com quatro comportamentos diferentes | `TORRES`, `atualizar_torres()` |
| ↳ Besteiro: setas que perseguem o alvo | efeito `"tiro"` |
| ↳ Trabuco: pedra que rebenta e magoa à volta | efeito `"explosao"` |
| ↳ Caldeirão de azeite: magoa pouco, mas abranda todos os que estão perto | efeito `"area"` |
| ↳ Padeira de Aljubarrota: pazada forte, alcance curto | efeito `"golpe"` |
| Quatro inimigos (rápido, normal, tanque, chefe) | `INIMIGOS` |
| Dez ondas, cada uma uma lista de grupos | `ONDAS`, `comecar_onda()` |
| Ouro, vidas, bónus por onda, melhorar e vender | `construir()`, `melhorar()`, `vender()` |
| As torres atacam o inimigo que vai mais à frente | `escolher_alvo()` |
| Números a voar e círculos a crescer | `efeitos`, `texto_a_voar()` |
| Alcance meio transparente debaixo do rato | `desenhar_alcance()` |

## As ideias que valem a pena mostrar

- **O mapa é uma lista de strings**, como no Almas Penadas. Mudar o caminho é
  mudar letras. A função `encontrar_caminho()` começa no `E`, anda sempre para
  o quadrado de caminho ao lado que ainda não visitou, e pára no `C`. Mostra
  ao vivo: muda o mapa, corre outra vez, os inimigos seguem o caminho novo.
- **Alcance é distância, não colisão.** O `colliderect` serve para
  retângulos. O alcance de uma torre é um círculo, por isso usa-se Pitágoras
  (`math.hypot`). Bom momento para a pergunta «onde é que já viram isto nas
  aulas de Matemática?»
- **A receita dos sobreviventes** (do `apanhar.py`) aparece três vezes:
  inimigos, projéteis, efeitos. Quem a percebeu numa, percebe as três.
- **Velocidade x2 é só correr a lógica duas vezes** por cada desenho. Duas
  linhas.

## Escada de personalização

**1. Só dados (não se toca em nenhuma função)**
- Desenhar mapas novos. Regras: o caminho tem um quadrado de largura e não
  pode tocar em si próprio.
- Inventar torres novas com os quatro efeitos que já existem.
- Inventar inimigos e ondas. Uma onda é uma lista; um grupo é um dicionário.
- Mudar o tema por completo: zombies contra plantas, vírus contra glóbulos
  brancos, a escola contra os trabalhos de casa.

**2. Pequenas mudanças às regras**
- Uma torre que escolhe o inimigo **mais forte** em vez do que vai à frente
  (`escolher_alvo()`).
- Inimigos com armadura (tiram sempre X ao dano) ou que só levam de certas
  torres.
- Uma torre que dá ouro de tantos em tantos segundos (uma mina, um mercado).
- Melhorias que mudam a torre, e não só os números (ao nível 3 o Besteiro
  dispara duas setas).

**3. Mecânicas novas**
- Vários mapas, um a seguir ao outro (`projeto/niveis-por-configuracao.py`).
- Caminhos com bifurcação (o `encontrar_caminho()` tem de passar a aceitar
  dois).
- Um poder especial com tempo de recarga: chuva de pedras onde se clica.
- Inimigos que nascem de outros quando morrem.
- Ecrã de fim com estatísticas: quanto matou cada torre.

## Equilíbrio (testado)

Corremos o jogo com dois robôs:
- Um **bom**, que põe as torres nos sítios com mais caminho à volta: **ganha
  sempre**, normalmente com 10 a 20 vidas.
- Um **descuidado**, que põe as torres em qualquer sítio ao lado do caminho e
  gasta ouro em melhorias cedo demais: **perde quase sempre**, entre a onda 4
  e a 10.

É mais ou menos o que se quer: ganha quem pensa onde pôr as torres. Os números
a mexer são `OURO_INICIAL`, `VIDAS_INICIAIS`, `VIDA_EXTRA_POR_ONDA` e
`BONUS_POR_ONDA`.

> «Se houver uma torre que ganha o jogo sozinha, o jogo está mal equilibrado.
> Experimentem só com Besteiros, só com Padeiras... qual é a mais forte pelo
> preço?»

## Erros previsíveis (e a pergunta a fazer)

| Sintoma | Pergunta |
|---|---|
| No terminal: «O caminho do MAPA nao chega ao C!» | «Há algum buraco no caminho? E há algum sítio onde o caminho toca em si próprio?» |
| Os inimigos saltam um bocado do caminho | «Onde é que o caminho se encosta a ele próprio?» |
| `KeyError` com o nome de um inimigo | «O nome na onda está escrito igual ao nome em `INIMIGOS`, com acentos?» |
| Uma torre nova não tem tecla | «Que tecla tem no `"tecla"`? E há mais de quatro botões a caber na barra de baixo?» |
| O mapa fica cortado ou com buracos pretos | «Todas as linhas do `MAPA` têm o mesmo número de letras?» |
