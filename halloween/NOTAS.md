# Halloween — A Noite dos Doces

Uma sessão especial, fora da sequência. **Apresentas no início, eles
personalizam durante a manhã, e no fim cada par mostra o seu à turma.**

Um Pac-Man às escuras. Apanha todos os doces do labirinto para passar à onda
seguinte. Só vês o que a lanterna ilumina, e **os fantasmas atravessam
paredes**. Aponta-lhes a luz: na luz, dão meia volta e fogem. Cada onda traz
mais um fantasma, e é assim até perderes a última vida. Modo sobrevivência:
**quantas ondas aguentas?**

```
python3 noite-dos-doces.py
```

| | Teclado | Comando (PS5, PS4, Xbox…) |
|---|---|---|
| andar | setas | manípulo **direito** (ou as setas) |
| apontar a lanterna | `W` `A` `S` `D` | manípulo **esquerdo** |
| começar / jogar outra vez | `Espaço` | qualquer botão |
| **com rato** | o rato aponta a lanterna, `W` `A` `S` `D` (ou setas) anda. Liga-se sozinho ao mexer o rato; `M` desliga/liga | |
| trocar os manípulos (canhotos) | `T` (passa a ser WASD a andar e setas a apontar) | **Triângulo** (Y na Xbox) |
| ecrã inteiro (abre assim) | `F` ou `F11` volta à janela | |
| sair | `Esc` | |

Para começar sempre com os manípulos trocados, ou numa janela, há duas
constantes no fim da secção 3: `TROCAR_MANIPULOS` e `ECRA_INTEIRO`.

O comando **treme** no susto e a cada batida do coração quando um fantasma
está perto.

## Como funciona

- **Cinco labirintos**, um por onda: O Cemitério, A Cave, O Labirinto da
  Bruxa, A Mansão, O Campo de Abóboras. Depois do quinto, saem ao calhas (sem
  repetir o anterior), para sempre.
- **Cada onda: mais um fantasma, e todos um bocadinho mais rápidos.** Acordam
  um de cada vez, com 3 segundos de avanço no início.
- **3 vidas**, e uma vida extra a cada 3 ondas.
- **Super-doces** (abóboras a brilhar nos cantos): os fantasmas ficam azuis,
  fogem de ti, e se lhes tocas voltam para o ninho. A bateria da lanterna
  enche.
- **A lanterna assusta.** Um fantasma apanhado no cone de luz treme, dá
  meia volta e foge. Só o cone conta: o brilho à volta do jogador não.
- **A bateria** gasta-se devagar e a luz encolhe. Cada doce recarrega um
  pouco.
- **Recorde** da sessão no ecrã de título e no fim. Bom para a mostra.

## Antes da aula (importante)

**Esta é a primeira vez que vão correr Pygame.** O `pygame-ce` tem de estar
instalado no `.venv` de **todos os computadores antes** de a aula começar. Ver
o `COMO-CORRER.md`. Se não estiver, perdes os primeiros 30 minutos nisso.

Testa também o som e, se o fores usar, o comando:
```
python3 testar-comando.py
```
Mostra no ecrã o nome do comando, os eixos e os botões carregados, e faz o
comando tremer a cada botão. No Mac, o comando da PS5 por Bluetooth
emparelha-se carregando em **PS + Create** até a luz piscar.

**Se os manípulos estiverem trocados** (a lanterna anda com o direito, por
exemplo): no `testar-comando.py` vê que números de eixo mudam com cada
manípulo e acerta o `EIXO_ESQUERDO_X`, `EIXO_ESQUERDO_Y`, `EIXO_DIREITO_X` e
`EIXO_DIREITO_Y`, logo a seguir à linha «NÃO MEXER». Isto é contigo, não com
eles.

## A ideia da aula

O ficheiro tem duas partes, separadas por um bloco de `#####` impossível de
não ver:

1. **«MEXE SÓ AQUI»**: textos, cores, números, labirintos e desenhos. É tudo
   o que eles já sabem: variáveis, texto entre aspas, números e listas.
2. **«NÃO MEXER DAQUI PARA BAIXO»**: o motor. Hoje é para usar, não para
   perceber. Na aula seguinte abre-se e explica-se.

> «Hoje vocês são os *designers*. Há outra pessoa que fez o motor, e vocês
> decidem tudo o que o jogador vê e sente. É assim que se fazem os jogos a
> sério: quem desenha os níveis do Mario não mexe no código da física.»

## O plano dos 90 minutos

| Tempo | O quê |
|---|---|
| 0–10 | **Apresentação.** Projetor, ecrã inteiro (`F`), luzes apagadas, comando na mão de um voluntário. Deixa-o ser apanhado. |
| 10–20 | **A visita guiada à parte de cima.** Abre o ficheiro no projetor e mostra as cinco secções. Faz três mudanças ao vivo: o `TITULO`, um `"O"` dos olhos do fantasma para `"R"`, e uma parede do `LABIRINTO_1` apagada. Corre outra vez. |
| 20–75 | **Personalização**, em pares. Cartão de desafios abaixo, no quadro ou no projetor. |
| 75–90 | **Mostra.** Cada par senta um colega **de outro par** no seu computador. Ninguém joga o seu próprio jogo. Quem chegar mais longe nos jogos dos outros ganha. |

## As três coisas a explicar na visita guiada

**As cores são três números.**
> «(vermelho, verde, azul), cada um de 0 a 255. É como misturar luz, não
> tinta: tudo no máximo dá branco, tudo a zero dá preto.»

**Os desenhos são texto.** Aponta para o `DESENHO_DO_FANTASMA`:
> «Inclinem a cabeça e olhem de longe. Cada letra é um quadradinho. O ponto
> é transparente. A letra diz a cor, e as cores estão na `PALETA`. E a letra
> `O` brilha no escuro: é por isso que só vemos os olhos.»

**Os labirintos também são texto.** Aponta para o `LABIRINTO_1`:
> «`#` é parede, `.` é doce, `S` é super-doce, `J` é onde começas, `F` é
> onde nascem os fantasmas. 14 linhas de 20 letras. Se uma linha estiver
> aberta dos dois lados, é um túnel.»

Mostra a regra de ouro, que serve para os desenhos e para os labirintos:
**todas as linhas entre aspas, com uma vírgula no fim.**

## Cartão de desafios (para o quadro)

🎃 **Primeiro (todos)**
- Muda o `TITULO`, o `SUBTITULO` e as `FRASES_DO_SUSTO`.
- Muda as cores das paredes, do contorno, do chão e da luz.
- Dá nomes teus aos labirintos.

👻 **Depois**
- Redesenha o fantasma: um zombie, uma aranha, uma caveira…
- Redesenha o jogador, o doce e o super-doce.
- Desenha o teu próprio labirinto por cima de um dos cinco.
- Mexe nos números até o jogo estar **difícil mas justo**. Testa com o colega
  do lado.

💀 **Para quem voar**
- Faz um `LABIRINTO_6` novo e acrescenta-o às duas listas (`LABIRINTOS` e
  `NOMES_DOS_LABIRINTOS`).
- Inventa uma cor nova, dá-lhe uma letra na `PALETA` e usa-a num desenho.
- Põe a letra `O` no desenho do jogador: essas partes brilham no escuro.
- Faz um modo impossível: lanterna minúscula, três fantasmas desde o início,
  fantasmas que não têm medo da luz (`FANTASMA_NA_LUZ = 1`). Ou o contrário:
  fantasmas que fogem a correr (`FANTASMA_NA_LUZ = -3`).
- Faz o contrário: o modo para o irmão mais novo.

## Erros previsíveis (e a pergunta a fazer)

São quase todos de pontuação, e estão todos na parte de cima.

| Sintoma | Pergunta |
|---|---|
| `SyntaxError` numa linha de um desenho ou labirinto | «A linha de cima tem a vírgula no fim?» |
| `SyntaxError: unterminated string literal` | «Onde é que abriste aspas e não as fechaste?» |
| Aparecem quadrados **cor-de-rosa choque** no desenho | «Essa letra está na `PALETA`?» (Não é um erro, é o aviso.) |
| `NameError: name 'LILAS' is not defined` | «Criaste a cor `LILAS` lá em cima, antes de a usares?» |
| `ValueError: invalid color argument` | «Uma cor são três números. Quantos tem a tua? Algum passa de 255?» |
| O labirinto aparece com paredes a mais à direita ou em baixo | «Quantas letras tem essa linha? Tem de ter 20.» (O que falta vira parede.) |
| A onda nunca acaba | «Há algum doce fechado entre paredes, onde não se consegue chegar?» |
| O jogador começa num sítio estranho | «Há um `J` no labirinto?» |
| `NameError: name 'LABIRINTO_6'` | «Fizeste o `LABIRINTO_6` **antes** da lista `LABIRINTOS`?» |
| A janela não abre e diz `No module named pygame` | É o `.venv`. Ver «Antes da aula». |

Se um aluno mexeu na parte de baixo e partiu tudo: **Ctrl+Z** até voltar a
funcionar. Por isso é que a regra existe.

## Equilíbrio (testado)

Corremos o jogo com um robô que encontra sempre o caminho mais curto para o
doce mais perto, foge dos fantasmas e lhes aponta a lanterna. **Cada onda
demora cerca de 30 segundos.** O robô chega à onda 12–17 (sem apontar a
lanterna, só à 8–14: apontar conta). Mas joga melhor do
que qualquer pessoa: conta com que eles fiquem entre a onda 3 e a 6. Se a
turma achar difícil demais: `VELOCIDADE_DO_FANTASMA`,
`MAIS_FANTASMAS_POR_ONDA` e `FANTASMA_NA_LUZ`.

## Para a aula seguinte: abrir o motor

O motor tem o mesmo ciclo de cinco passos do `comum/esqueleto.py`
(EVENTOS → LÓGICA → DESENHAR → MOSTRAR → ESPERAR), com os mesmos comentários.
Quatro coisas que vale a pena mostrar:

- **`fazer_desenho()` e `carregar_labirinto()`**: dois `while` um dentro do
  outro, uma linha de cada vez, uma letra de cada vez. É o código que
  transforma o que eles escreveram em imagens e paredes.
- **`mover_jogador()`**: o movimento do Pac-Man. O jogador anda de centro em
  centro de quadrado; quando chega a um, vê se pode virar para onde queres,
  senão continua, senão pára. É por isso que se pode carregar na seta
  *antes* de chegar à curva.
- **A luz é uma multiplicação.** Pinta-se uma superfície escura, soma-se o
  cone de luz (rodado para onde apontas) e **multiplica-se** o ecrã por ela.
  Onde é preto, o ecrã fica preto. É o mesmo truque do Almas Penadas (s11).
- **Os fantasmas atravessam paredes porque ninguém lhes disse que não.** O
  código deles é só «anda na direção do jogador». Pergunta: «como é que os
  obrigávamos a respeitar as paredes?»
