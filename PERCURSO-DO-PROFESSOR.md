# Percurso do professor

Um caminho ordenado para aprenderes o *stack* antes de outubro.

**Pressupostos:** sabes programar. Não sabes Python nem Pygame. Tens umas
semanas e não tens tempo a perder.

**Total: cerca de 15 horas.** Sete etapas. Podes fazê-las em sete sessões de
duas horas, ou em três fins de semana.

**A regra que faz isto funcionar:** o que estiver marcado **de raiz** escreve-se
à mão, olhando para o ficheiro se for preciso, mas escrevendo. O que estiver
marcado **ler** lê-se e corre-se, e pronto. Copiar e colar o que está marcado
"de raiz" poupa três horas e desperdiça as outras doze — em Pygame há memória
muscular a sério (a ordem dos cinco blocos, o `flip`, o `fill`), e essa não se
lê, escreve-se.

---

## Etapa 0 — Preparar a máquina · 30 min

1. **Python 3.12 ou superior.** `python3 --version`. Se for mais antigo,
   instala pelo [python.org](https://python.org).
2. **Um ambiente virtual, e o `pygame-ce` lá dentro:**
   ```
   cd clube-de-codigo-2627
   python3 -m venv .venv
   source .venv/bin/activate          # Windows: .venv\Scripts\activate.bat
   python3 -m pip install -r requirements.txt
   ```
   O *prompt* passa a começar por `(.venv)`.

   **Isto não é cerimónia.** Em macOS com Homebrew e em Linux, instalar no
   Python do sistema é recusado com `error: externally-managed-environment`.
   O venv é a única via que funciona em todo o lado.

   Repara: `pygame-ce`, a *community edition*. O `import` é `import pygame`,
   igual. **Não instales os dois** na mesma máquina, entram em conflito.
3. **Confirma:**
   ```
   python3 comum/esqueleto.py
   ```
   Deve abrir uma janela com um menu. Barra de espaços começa, setas mexem um
   quadrado azul, `Esc` acaba, `R` recomeça, o X fecha.
4. **Assets (opcional, 15 min):** segue o `comum/assets/LEIA-ME.md`, põe lá um
   `jogador.png` e corre outra vez. A imagem aparece sem mexer em código
   nenhum. Faz isto uma vez e cobre o ano inteiro.

> **Faz esta etapa em todas as máquinas da sala antes de outubro**, não no dia
> da sessão 7. Quinze `pip install` a falhar ao mesmo tempo consomem uma
> sessão inteira.
>
> E enquanto lá estás, **configura o VS Code em cada máquina para usar o
> `.venv`** (`COMO-CORRER.md`, secção 1). Assim ninguém tem de escrever
> `activate` sessão nenhuma — e `ModuleNotFoundError: No module named
> 'pygame'` deixa de poder acontecer. É o melhor quarto de hora que investes
> em setembro.

---

## Etapa 1 — Python, o suficiente e nada mais · 2h

**Lê:** `comum/cheatsheet-v1-python.md`, de uma ponta à outra. Trinta minutos.
É a totalidade do Python que este clube usa. Não há mais.

O que provavelmente te vai bater mal, vindo de outra linguagem:

- **A indentação é sintaxe.** Não há chavetas. Quatro espaços, e o teu editor
  tem de estar configurado para não meter tabulações.
- **Não há declaração de tipos, nem `var`, nem `let`.** `x = 5` cria a
  variável.
- **`input()` devolve sempre `str`.** Sempre. É a fonte de metade dos erros
  dos alunos nas sessões 1 e 2.
- **Não há `++`.** Escreve-se `contador = contador + 1`. Existe `+=`, mas
  neste repositório não se usa, de propósito: `contador = contador + 1` é mais
  fácil de ler em voz alta a quem está a começar.
- **`None` é o `null`.** Aparece quando uma função não devolve nada, e o erro
  que dá — `NoneType` — é o mal-entendido número um da sessão 3.
- **Listas são `[]`, dicionários são `{}`.** Não há mais nada a saber hoje.

**De raiz (1h):** escreve os três programas das sessões 1, 2 e 3 **sem olhar
para as soluções**. Um Mad Libs, um adivinha-o-número com limite de tentativas,
e um gerador de personagens com funções.

Vais demorar menos de uma hora e vais tropeçar exatamente onde os alunos vão
tropeçar. Esse é o objetivo — não é aprender Python, é **sentir onde ele
morde**.

**Compara (30 min):** só agora abre `s01/solucao.py`, `s02/nivel-prata.py` e
`s03/solucao.py`. Repara nas diferenças de estilo, não de lógica: nomes em
português, sem `+=`, sem compreensões, `while` com contador em vez de `range`.
**Não é código bonito de propósito** — é código que se explica em voz alta a
alguém de doze anos.

---

## Etapa 2 — O `esqueleto.py`, a etapa que decide tudo · 3h

> **Esta é a etapa mais importante do percurso.** O `comum/esqueleto.py` é o
> mesmo ficheiro nas sessões 7, 8, 9 e nas oito sessões de projeto. Se o
> souberes de cor, sabes dar o 2.º e o 3.º períodos. Se não, vais passar o ano
> a lê-lo à frente dos alunos.

**Lê (30 min):** `comum/cheatsheet-v2-pygame.md`, com atenção especial a duas
secções: **as cinco palavras** e **`get_pressed()` contra `KEYDOWN`**.

**De raiz (2h):** escreve o `comum/esqueleto.py` **do princípio ao fim, à
mão**, sem copiar e colar. Podes olhar para o original as vezes que quiseres —
mas escreve tu cada linha.

Fá-lo por esta ordem, correndo o programa a cada passo:

1. Janela e ciclo de eventos. Confirma que fecha no X.
2. `fill` + `draw.rect` + `flip`. Confirma que aparece o quadrado.
3. Movimento com `get_pressed()`.
4. `clock.tick(60)`.
5. A máquina de estados: `estado` com `"menu"`, `"jogo"` e `"fim"`.
6. `comecar_jogo()` com o `global`, e o `R` a reiniciar.
7. As funções `carregar_imagem()` e `carregar_som()`, com a degradação
   graciosa.

**Depois, parte-o de propósito (30 min).** É aqui que se aprende a sério, e são
os cinco erros que vais ver a sala toda cometer:

| Tira isto | O que acontece |
|---|---|
| `pygame.display.flip()` | Ecrã preto, **sem erro nenhum** |
| `ecra.fill(...)` | Rasto de tinta pelo ecrã |
| `for evento in pygame.event.get()` | A janela não fecha, o sistema diz que não responde |
| `clock.tick(60)` | O boneco anda a mil |
| Movimento no `KEYDOWN` em vez do `teclas[]` | Só anda se martelares a tecla |

Vê cada um deles com os teus olhos. Em outubro vais reconhecê-los do outro
lado da sala, sem te levantares da cadeira.

---

## Etapa 3 — Colisões e listas · 2h

**Lê (20 min):** `s08/NOTAS.md`, sobretudo a secção de `get_pressed()` contra
`KEYDOWN`. É a distinção que causa metade dos bugs do bloco de projeto.

**De raiz (1h):** parte do teu esqueleto da etapa 2 e acrescenta:
1. uma moeda, e colisão com `colliderect()`;
2. a moeda a mudar de sítio quando é apanhada;
3. uma **lista** de moedas;
4. a pontuação no ecrã.

**Faz o bug de propósito (20 min):** escreve o `remove()` dentro do `for`.
Corre. Vê metade das moedas a não ser apanhada. Depois corrige com a receita
dos sobreviventes.

Este bug vai aparecer-te umas dez vezes entre novembro e maio, disfarçado de
balas, de inimigos e de plataformas. Tens de o reconhecer **pelo sintoma**, não
pelo código.

**Lê (20 min):** os três ficheiros de `s09/`. Repara que são quase o mesmo
ficheiro. É deliberado, e é o que permite dizer a um aluno «vai ver como está
feito no `modelo-esquivar.py`».

---

## Etapa 4 — Ler todo o `projeto/` · 3h

Estes sete recursos são o que vais usar de novembro a maio. Corre **todos** e
mexe nas constantes de cada um. Não escrevas nenhum de raiz — não vale a pena.

| Ficheiro | Tempo | O que tens de perceber |
|---|---|---|
| `mvp-minimo.py` | 10 min | É o esqueleto sem menu. Nada de novo |
| `mecanica-por-genero/apanhar.py` | 10 min | Nada de novo depois da etapa 3 |
| `mecanica-por-genero/esquivar.py` | 15 min | **Reciclar** objetos em vez de os criar |
| `mecanica-por-genero/labirinto.py` | 20 min | **Um eixo de cada vez.** Não é óbvio |
| `mecanica-por-genero/chegar-ao-alvo.py` | 10 min | Condição de vitória |
| **`plataformas-gravidade.py`** | **45 min** | **Ver abaixo** |
| `niveis-por-configuracao.py` | 20 min | Dados contra lógica. Dicionários |
| `dificuldade-crescente.py` | 15 min | Duas linhas. E o tecto obrigatório |
| `hud.py` | 15 min | Desenhar por último. Símbolos em vez de números |
| `juice.py` | 20 min | `move()` e `inflate()`. Contadores que descem |
| `modo-feira.py` | 20 min | Metade não é código |

**Sobre o `plataformas-gravidade.py`:** dá-lhe os 45 minutos a sério, e mexe
nas três constantes até perceberes o que cada uma faz. É de longe a coisa mais
difícil do repositório, e é a única que vais ter mesmo de **dar feita**. Se
não a dominares, uma equipa vai escolher plataformas e vais passar o bloco de
projeto todo com ela.

**Ao ler, faz-te sempre a mesma pergunta:** «qual é o pedaço de dez linhas
que eu tiraria daqui para o jogo de uma equipa?» É essa a operação que vais
fazer vinte vezes durante o ano.

---

## Etapa 5 — Os `NOTAS.md` e o guião de sala · 2h

Lê todos os `NOTAS.md`, por ordem de sessão. Não são documentação: são o
guião. Cada um tem a demonstração ao vivo já escrita, linha a linha.

Enquanto lês, **prepara-te para as demonstrações**. São seis, e vais fazê-las
de pé, ao projetor:

| Sessão | A demonstração |
|---|---|
| 1 | Apagar o `f` da f-string. Aspa por fechar |
| 2 | Ciclo infinito, e pará-lo com `Ctrl + C` |
| 3 | `print` contra `return`, e o `NoneType` |
| 7 | **Ecrã preto sem erro nenhum** |
| 8 | Sessenta balas de uma vez. E as caixas a vermelho |
| 8 | O `remove()` dentro do `for` |

**Ensaia pelo menos a da sessão 7 e a da sessão 8.** Ambas dependem de um
momento de silêncio bem colocado, e isso não sai bem à primeira.

**E interioriza a regra de ouro:** *o facilitador nunca toca no teclado do
aluno.* É por isso que a terceira coluna das tabelas de erros é uma
**pergunta** e não uma instrução. Vai custar-te — apontar para o ecrã e dizer
«falta aí um `f`» demora três segundos e apaga a aprendizagem toda.

---

## Etapa 6 — O ensaio geral · 2h

**Faz a sessão 9 sozinho, a sério, com relógio.**

Escolhe um dos três modelos, dá-te **quarenta minutos**, e faz um jogo teu:
muda o tema, muda uma mecânica, acrescenta um efeito do `juice.py`. Aos 40
minutos, **para**. Vê o que conseguiste.

É o único exercício que te diz a verdade sobre o que cabe em 90 minutos com
adolescentes que programam de quinze em quinze dias. A resposta vai
surpreender-te, e é o número mais útil que vais ter o ano inteiro.

**Depois, o teste do modo feira (15 min):** corre o `projeto/modo-feira.py`.
Passa as duas mãos por cima do teclado. Deixa-o parado meio minuto. Perde e
tenta jogar outra vez. É o que vai acontecer no Demo Day, e é bom que aconteça
primeiro a ti.

---

## Lista de verificação final

**Antes de outubro**, tens de conseguir fazer isto **sem consultar nada**.
Diz cada uma em voz alta, com relógio. Trinta segundos cada.

### Conceitos

- [ ] O que é uma variável, para alguém de doze anos.
- [ ] Porque é que `input()` devolve texto e para que serve o `int()`.
- [ ] Porque é que um `while` fica infinito, e como se pára um programa em
      fuga.
- [ ] A diferença entre `return` e `print`, com uma imagem que se perceba.
- [ ] O que é `None`, e porque é que aparece na sessão 3.
- [ ] O que é uma lista, e porque é que não se lhe tira nada durante um `for`.

### Pygame

- [ ] **As cinco palavras, por ordem**, e o que cada uma faz.
- [ ] Porque é que o ciclo de eventos existe, mesmo quando não se usa o
      teclado.
- [ ] Porque é que o `y` cresce para baixo.
- [ ] A diferença entre `get_pressed()` e `KEYDOWN`, com um exemplo de cada.
- [ ] O que é um `Rect` e para que servem `.left`, `.right`, `.top`,
      `.bottom`.
- [ ] Como funciona a máquina de estados do esqueleto, e onde se lhe mexe.
- [ ] Porque é que o `mixer.pre_init()` tem de vir antes do `pygame.init()`.
- [ ] Porque é que os caminhos se calculam a partir de `Path(__file__)`.

### Diagnóstico — a partir do sintoma, sem ver o código

- [ ] «Está tudo preto e não dá erro nenhum.»
- [ ] «Fica um rasto de tinta atrás do boneco.»
- [ ] «A janela não fecha.»
- [ ] «O meu boneco só anda se eu martelar a tecla.»
- [ ] «Saem sessenta balas de uma vez.»
- [ ] «A pontuação sobe aos milhares.»
- [ ] «Só metade dos objetos é apanhada.»
- [ ] «Às vezes o inimigo passa por cima e não morro.»
- [ ] «Ao carregar em R o jogo recomeça com a pontuação antiga.»

### Sala

- [ ] Fazer as seis demonstrações ao vivo sem consultar as notas.
- [ ] Responder a «não funciona» **com uma pergunta**, sem tocar no teclado.
- [ ] Dizer o que é um *feature freeze* e porque é que é inegociável.
- [ ] Dizer, por experiência própria, o que cabe em 90 minutos.

---

## Se só tiveres um fim de semana

Não é o ideal, mas dá para arrancar. Por ordem de valor:

1. **Etapa 0** (30 min) — não é opcional.
2. **Etapa 2** (3h) — o esqueleto de raiz, e parti-lo de propósito. Se só
   fizeres uma etapa, é esta.
3. **Etapa 1**, a parte de comparar (30 min) — só ler as soluções das sessões
   1 a 3.
4. **Etapa 5** (2h) — os `NOTAS.md` e ensaiar as demonstrações.

São seis horas e chegam para dar as sessões 1 a 7 com segurança. As etapas 3,
4 e 6 podem esperar — mas **faz a etapa 4 antes da sessão 10**, sem falta. O
bloco de projeto sem conheceres o `projeto/` é oito sessões a improvisar.
