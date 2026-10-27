# Como correr tudo o que está aqui

Guia rápido para verificares o repositório de uma ponta à outra.

---

## 1. Preparar, uma vez por máquina

### As sessões 1, 2 e 3 não precisam de nada

Só usam a biblioteca padrão. Basta ter Python:

```bash
python3 --version          # tem de dizer 3.12 ou superior
```

Se for mais antigo, ou não existir, instala pelo
[python.org](https://python.org/downloads). **Não precisas de fazer mais
nada até à sessão 7.**

### Da sessão 7 em diante: um ambiente virtual

O Pygame tem de ser instalado, e **não se instala no Python do sistema**.

Em macOS com Homebrew, e em Linux, isso nem sequer é permitido — o
`pip install` responde:

```
error: externally-managed-environment
× This environment is externally managed
```

Não é um problema teu: é o sistema a proteger o Python de que ele próprio
depende. A solução é a mesma em todo o lado, e é a boa prática de qualquer
forma: **um ambiente virtual**, uma pasta com um Python só para este
repositório.

**Cria-o uma vez, na raiz do repositório:**

```bash
cd clube-de-codigo-2627

python3 -m venv .venv                                   # criar

source .venv/bin/activate                               # macOS e Linux
.venv\Scripts\Activate.ps1                              # Windows PowerShell
.venv\Scripts\activate.bat                              # Windows, cmd antigo

python3 -m pip install -r requirements.txt              # instalar
```

Sabes que está activado porque o *prompt* passa a começar por `(.venv)`.

**Confirma:**

```bash
python3 -c "import pygame; print(pygame.version.ver)"   # 2.5.8
python3 comum/esqueleto.py
```

> **Porquê `pygame-ce` e não `pygame`?** É a *community edition*, mantida
> activamente. O `import` é igual (`import pygame`). **Não instales as duas**
> na mesma máquina — entram em conflito. Está fixa no `requirements.txt` para
> as 15 máquinas da sala ficarem todas iguais.

> **A pasta `.venv/` não se distribui.** São 62 MB e só serve nesta máquina e
> neste sistema. Está no `.gitignore`. Em cada máquina nova repete-se o bloco
> de cima — leva um minuto.

### Em cada sessão, depois disso

Só a activação. A instalação é uma vez, para sempre:

```bash
cd clube-de-codigo-2627
source .venv/bin/activate
```

**Esqueceste-te?** O sintoma é
`ModuleNotFoundError: No module named 'pygame'`. Activa e corre outra vez.

### Melhor: não activar nada, com o VS Code

Se a sala usar VS Code — e vale a pena —, ninguém precisa de escrever
`activate` sessão nenhuma:

1. Abre a pasta `clube-de-codigo-2627` no VS Code (**a pasta toda**, não um
   ficheiro solto).
2. O VS Code deteta o `.venv` sozinho. Se não o fizer:
   `Ctrl+Shift+P` → *Python: Select Interpreter* → o que diz `('.venv')`.
3. A partir daí, o botão ▶ e cada novo terminal já usam o `.venv`.

**Para uma sala com adolescentes de quinze em quinze dias, é isto que
recomendo.** O ritual do `activate` é um modo de falha novo, e um
`ModuleNotFoundError` em quinze máquinas ao mesmo tempo consome uma sessão
inteira. Configura isto nas máquinas antes de outubro.

> **Nota sobre o critério de aceitação.** O `README.md` diz que os ficheiros
> correm com `python3 <ficheiro>.py`, sem variáveis de ambiente. Continua
> verdade: o venv não muda nada dentro dos ficheiros, e nenhum precisa de
> argumentos. Só muda **qual** o `python3` que é chamado. Com o VS Code
> configurado, nem isso se nota.

### Num portátil novo, do zero: passo a passo por sistema

O repositório não tem ficheiro `.env` nem nenhuma configuração secreta:
**basta trazê-lo e instalar o `pygame-ce`**. Uma vez por portátil. Não é
preciso `git`, nem para ti nem para os alunos: a partir daqui, as alterações
são só deles, feitas diretamente nos ficheiros.

#### Primeiro, em todos os sistemas: descarregar o projeto

Descarrega o ZIP por este link (é sempre a versão mais recente):

**<https://github.com/jruysaribeiro/clube-de-codigo-2627/archive/refs/heads/main.zip>**

1. Descompacta-o na pasta das transferências. A pasta vem com o nome
   **`clube-de-codigo-2627-main`**.
2. **Muda-lhe o nome para `clube-de-codigo-2627`**, para os comandos de
   baixo funcionarem tal e qual.

Os comandos abaixo chamam o Python do `.venv` diretamente
(`.venv\Scripts\python` ou `.venv/bin/python`), por isso **não é preciso
activar nada**. Funciona igual em todas as sessões, e no Windows evita o
erro do PowerShell «running scripts is disabled on this system», que o
`activate` costuma dar nos computadores das escolas.

#### Windows (PowerShell)

**Instalar, uma vez — o mais simples:** na pasta `clube-de-codigo-2627`,
botão direito em **`instalar-windows.bat`** → **Executar como
administrador**. Instala o Python (se faltar) e o `pygame-ce` para **todos
os utilizadores** do computador, contas de aluno incluídas. Sem
administrador, um duplo clique normal instala só para a conta atual.

Se o Windows mostrar «O Windows protegeu o seu PC», carrega em **Mais
informações** → **Executar mesmo assim**: é por o ficheiro vir de um ZIP da
Internet.

Depois, em qualquer conta, num terminal **novo** aberto na pasta:

```powershell
py halloween\noite-dos-doces.py
```

**Ou, à mão, com um `.venv`:**

```powershell
cd ~\Downloads\clube-de-codigo-2627
py -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
```

**Correr, em cada sessão:**

```powershell
cd ~\Downloads\clube-de-codigo-2627
.venv\Scripts\python halloween\noite-dos-doces.py
```

Se o `py` não for reconhecido, troca-o por `python`. Se nenhum dos dois
existir, instala o Python pelo [python.org](https://python.org/downloads) e
marca a caixa **«Add python.exe to PATH»** no primeiro ecrã do instalador.

#### Linux (Ubuntu, Debian, Mint...)

**Portáteis com sessão de convidado (Linux Mint, Ubuntu, Debian):**

O convidado não pode usar `sudo` e perde a pasta pessoal ao sair, por isso
um `.venv` não serve: desaparecia em cada sessão. Em vez disso, corre-se
isto uma vez por portátil, **com a sessão iniciada na conta de
administrador** (não como convidado: aí o `sudo` recusa, mesmo com a
palavra-passe certa):

```bash
cd ~/Transferências/clube-de-codigo-2627
bash instalar-linux.sh
```

Instala o `pygame-ce` no Python do sistema, para todos os utilizadores.
Daí em diante, qualquer convidado corre os jogos só com `python3`:

```bash
python3 halloween/noite-dos-doces.py
```

Os ficheiros do convidado apagam-se no fim da sessão: o projeto tem de ser
descarregado em cada sessão, e o trabalho dos alunos guardado numa pen.

**Com contas normais, ou à mão:**

```bash
cd ~/Transferências/clube-de-codigo-2627
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

**Correr, em cada sessão:**

```bash
cd ~/Transferências/clube-de-codigo-2627
.venv/bin/python halloween/noite-dos-doces.py
```

Num Linux em inglês, a pasta chama-se `Downloads` em vez de
`Transferências`.

Se o `python3 -m venv` disser `ensurepip is not available`, falta o pacote
`python3-venv`: `sudo apt install python3-venv` (precisa de administrador).
Sem administrador, usa o `uv`, mais abaixo.

#### macOS

**Instalar, uma vez — o mais simples:** com uma conta de administrador, no
Terminal:

```bash
cd ~/Downloads/clube-de-codigo-2627
bash instalar-mac.sh
```

Pede a palavra-passe de administrador, instala o Python 3.12 do
[python.org](https://python.org/downloads) (o `python3` que vem com o macOS é
o 3.9, antigo demais para o `pygame-ce`) e o `pygame-ce`, para **todas as
contas** do Mac. No fim diz qual o comando a usar, normalmente `python3`.

**Ou, à mão, com um `.venv`:**

```bash
cd ~/Downloads/clube-de-codigo-2627
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

**Correr, em cada sessão:**

```bash
cd ~/Downloads/clube-de-codigo-2627
.venv/bin/python halloween/noite-dos-doces.py
```

Se o terminal pedir para instalar as «ferramentas de linha de comandos» ao
escreveres `python3`, aceita: é a Apple a instalar o Python.

#### Plano B, para quando nada disto dá: `uv`

O `uv` traz o seu próprio Python e não precisa de administrador nem de
`.venv`. Instala-se uma vez e depois é uma linha:

```powershell
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

```bash
# Linux e macOS
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Fecha e volta a abrir o terminal. Depois, dentro da pasta `clube-de-codigo-2627`:

```bash
uv run --with pygame-ce halloween/noite-dos-doces.py
```

> **Para correr outro ficheiro**, troca só o caminho no fim: por exemplo
> `.venv/bin/python s12-bicharada/bicharada.py`. No Windows, as barras são
> ao contrário: `.venv\Scripts\python s12-bicharada\bicharada.py`.

## 2. A regra para correr qualquer ficheiro

**Abre o terminal na pasta do ficheiro e corre-o sem argumentos.**

```bash
cd s01-mad-libs
python3 solucao.py
```

Sem argumentos, sem variáveis de ambiente. Funciona assim para **todos** os
ficheiros deste repositório.

Correr a partir da raiz (`python3 s01-mad-libs/solucao.py`) também funciona em
todos os ficheiros de Pygame — os caminhos dos assets são calculados a partir
de `Path(__file__)`, não da pasta do terminal. A única exceção é o
`s03/nivel-ouro.py`, que grava o `party.txt` **na pasta onde o terminal está
aberto**.

**Nos ficheiros de Pygame:** a janela fecha-se no X, e fecha imediatamente. Se
não fechar, é um bug.

---

## 3. Sessões 1 a 3 — consola

Estas são interativas: escrevem no terminal e esperam que respondas.

```bash
cd s01-mad-libs
python3 esqueleto.py       # escreve o que ele pedir, Enter entre cada
python3 solucao.py
python3 nivel-bronze.py
python3 nivel-prata.py
python3 nivel-ouro.py

cd ../s02-adivinha-numero
python3 solucao.py         # escreve numeros de 1 a 20
python3 nivel-prata.py     # tenta escrever "ola" para veres o try/except
python3 nivel-ouro.py      # Enter, e depois maior / menor / acertaste

cd ../s03-gerador-personagens
python3 solucao.py         # nao pede nada, so escreve
python3 nivel-prata.py     # usa o ferramentas.py
python3 nivel-ouro.py      # cria um party.txt na pasta do terminal
```

**Se não quiseres estar a escrever**, alimenta o programa a partir do
terminal:
```bash
printf 'Rita\ngato\nLisboa\nsopa\nverde\n' | python3 s01-mad-libs/solucao.py
seq 1 100 | python3 s02-adivinha-numero/solucao.py
```

---

## 4. Os ficheiros `erro-proposital.py`

**Estes são para falhar.** Não são bugs — cada um tem um erro plantado, para o
facilitador correr ao vivo. O erro está identificado no `NOTAS.md` da sessão,
nunca no ficheiro.

| Ficheiro | O que esperar |
|---|---|
| `s01/erro-proposital.py` | `SyntaxError: unterminated string literal` |
| `s02/erro-proposital.py` | Nunca acaba, mesmo depois de acertares. **Pára com `Ctrl + C`** |
| `s03/erro-proposital.py` | Escreve um nome e depois `TypeError: ... NoneType ...` |
| `s07/erro-proposital.py` | **Janela toda preta, e nenhuma mensagem de erro.** É esse o ponto |
| `s08/erro-proposital.py` | Corre bem, mas conta metade das moedas e deixa moedas por baixo do jogador |

---

## 5. Sessões 7 a 9 e `projeto/` — Pygame

Abrem uma janela. **Todos correm sem assets nenhuns** — desenham retângulos
coloridos em vez de imagens e ficam em silêncio.

```bash
python3 comum/esqueleto.py                          # o ficheiro central

python3 s07-pygame-janela-movimento/solucao.py      # = comum/esqueleto.py
python3 s07-pygame-janela-movimento/nivel-ouro.py   # setas e WASD, dois jogadores

python3 s08-pygame-colisoes-pontuacao/solucao.py
python3 s08-pygame-colisoes-pontuacao/nivel-prata.py

python3 s09-jogo-completo/modelo-perseguicao.py
python3 s09-jogo-completo/modelo-apanhar.py
python3 s09-jogo-completo/modelo-esquivar.py

python3 projeto/mvp-minimo.py
python3 projeto/niveis-por-configuracao.py
python3 projeto/dificuldade-crescente.py
python3 projeto/hud.py                              # P, V e N mexem no HUD
python3 projeto/juice.py                            # D, A e E
python3 projeto/modo-feira.py

python3 projeto/mecanica-por-genero/apanhar.py
python3 projeto/mecanica-por-genero/esquivar.py
python3 projeto/mecanica-por-genero/labirinto.py
python3 projeto/mecanica-por-genero/chegar-ao-alvo.py
python3 projeto/mecanica-por-genero/plataformas-gravidade.py
```

### Teclas

| Onde | Teclas |
|---|---|
| Quase todos | **Setas** andam · **Espaço** começa · **R** recomeça · **X** fecha |
| `comum/esqueleto.py`, s07 | **Esc** acaba o jogo (leva ao ecrã de fim) |
| `s07/nivel-ouro.py` | **Setas** derrapam · **WASD** não derrapam |
| `s09/modelo-esquivar.py` | Só **esquerda** e **direita** |
| `projeto/hud.py` | **P** pontos · **V** perder vida · **N** nível |
| `projeto/juice.py` | **D** dano · **A** apanhar · **E** ligar/desligar efeitos |
| `plataformas-gravidade.py` | **Setas** andam · **Espaço** salta |

---

## 6. Correr tudo de uma vez, para verificar

Este comando abre e fecha **todas** as janelas, uma a uma, e diz se alguma
rebentou. Cada uma fica aberta uns segundos.

**Com o `.venv` activado** (`source .venv/bin/activate`), a partir da raiz:

```bash
for f in comum/esqueleto.py s0[789]*/*.py projeto/*.py projeto/*/*.py; do
  echo "--- $f"
  python3 "$f" || echo "   ^^^ FALHOU"
done
```

Fecha cada janela no X para passar à seguinte. **O
`s07-pygame-janela-movimento/erro-proposital.py` vai aparecer todo preto** — é
suposto.

Para verificares só que não há erros de sintaxe em lado nenhum, sem abrir
janela nenhuma (este nem precisa do `.venv`):
```bash
python3 -m compileall -q -x '\.venv' . && echo "tudo compila"
```
Este vai queixar-se de **um** ficheiro, o `s01/erro-proposital.py`, e é
exatamente o que se quer.

---

## 7. Assets

As pastas `comum/assets/imagens/` e `comum/assets/sons/` vêm **vazias**, de
propósito. Ver `comum/assets/LEIA-ME.md`.

Para experimentares: põe um PNG chamado **`jogador.png`** em
`comum/assets/imagens/` e corre o `comum/esqueleto.py` outra vez. A imagem
aparece em vez do quadrado azul, **sem mexer numa linha de código**.

---

## 8. Se alguma coisa correr mal

| Sintoma | Causa |
|---|---|
| `ModuleNotFoundError: No module named 'pygame'` | **O `.venv` não está activado.** `source .venv/bin/activate` e corre outra vez. Se persistir, falta instalar: secção 1 |
| `error: externally-managed-environment` | Estás a instalar no Python do sistema. Cria o `.venv` primeiro: secção 1 |
| `ModuleNotFoundError: No module named 'ferramentas'` | Só no s03: o terminal não está na pasta do ficheiro |
| A janela abre preta | Se for o `s07/erro-proposital.py`, é suposto. Nos outros, é bug |
| A janela não fecha no X | É bug |
| Uma imagem não aparece e fica o retângulo | Nome do ficheiro errado, ou pasta errada. É o comportamento normal sem assets |
| O programa parece bloqueado no terminal | É um `input()` à espera de Enter |
| Um ciclo não pára | `Ctrl + C` |

---

## 9. Verificação num servidor, sem ecrã

Em CI ou por SSH, sem monitor, os ficheiros de Pygame precisam de um driver
falso:

```bash
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python3 comum/esqueleto.py
```

Repara que aqui se chama o interpretador do `.venv` **pelo caminho**, sem
activar nada. É o que se faz em CI, onde não há sessão de terminal nenhuma.

Assim abrem e correm sem janela — mas ficam à espera de um `QUIT` que nunca
chega, por isso é preciso matá-los. Serve para apanhar erros de arranque, não
para testar o jogo.
