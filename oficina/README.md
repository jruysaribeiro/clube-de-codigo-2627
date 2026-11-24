# A Oficina

Escolhe-se um jogo e **uma coisa** dele (um inimigo, uma torre, o mapa).
De um lado fica só o código dessa coisa; do outro, o jogo a correr, a
mudar enquanto se escreve.

Abre cinco jogos: **FADO//NEON** (s10), **Bicharada** (s12), **Bicharada à
Solta** (s15, a Bicharada com um mapa por onde se anda), **O Cerco** (s13) e
**Mãos ao Ar!** (s14, aqui jogado só com o teclado, sem câmara).

## Correr

Com o ambiente virtual activado (ver `COMO-CORRER.md`, secção 1):

```bash
python3 oficina/oficina.py
```

Abre uma página no browser com um cartão por jogo. Dentro de cada jogo
escolhe-se a coisa a mudar, e fica o jogo à esquerda e o código à direita.
O jogo é o verdadeiro, a correr no computador: a página mostra a imagem
dele e passa-lhe o rato e o teclado (clica-se no jogo para jogar, no
código para escrever). Para fechar: `Ctrl+C` no terminal.

Não precisa de internet nem de instalar mais nada.

## Jogar o jogo inteiro

O botão verde **Jogar o jogo inteiro** (na página de cada jogo e ao lado do
código) abre o jogo como ele é, do menu ao fim, com tudo o que já foi
mudado e sem código ao lado. **Voltar** regressa ao bocado que estava
aberto.

A página de cada jogo diz logo à entrada o que lá se pode fazer, e cada
grupo de coisas tem uma frase a explicá-lo (`SOBRE_OS_GRUPOS`, no ficheiro
do jogo em `oficina/jogos/`). O ajudante mostra pedidos já escritos para se
perceber o que se lhe pode pedir (`SUGESTOES`, no `jogos/o_cerco.py`).

## Regras do jogo

Além dos dados, os cinco jogos abrem **regras**. N'O Cerco são quatro: quem
a torre ataca, o que a torre faz ao disparar, o que acontece a um inimigo
atingido e como anda um inimigo. Nos outros: como saem os tiros e o que faz
cada carta (FADO//NEON), quanto magoa um ataque e quem ataca primeiro
(Bicharada; a Bicharada à Solta junta onde se pode andar e que bicho salta da
erva), como salta o Faísca e como se mexe um inimigo (Mãos ao Ar!).
Cada uma é uma função pequena do jogo; mudá-la muda a maneira como o jogo se
comporta. É aqui que se escreve um `if` a sério.

- O palco de uma regra põe o jogo a fazer aquilo que a regra decide (n'O
  Cerco: uma torre de cada, inimigos já a meio do caminho, e um círculo
  amarelo em quem cada torre escolheu).
- Uma regra nova é experimentada mais tempo antes de ser guardada. Se
  rebentar, o jogo volta à anterior e o erro aparece com a linha.
- O código escrito na Oficina não pode usar `import`, `open` nem outras
  coisas que mexem no computador em vez de no jogo (lista em `blocos.py`).
  É uma vedação contra o óbvio, não uma muralha.

Para abrir regras noutro jogo: as funções têm de estar encostadas à margem
no ficheiro do jogo, e a `regiao` devolve as linhas da função (ver `REGRAS`
no `jogos/o_cerco.py`).

## Acontecimentos, desenhos e coisas novas

Nos cinco jogos:

- **Acontecimentos**: funções que vêm vazias e que o jogo chama em certos
  momentos (n'O Cerco: quando começa uma onda, cai um inimigo, um inimigo
  chega ao castelo, se constrói uma torre, se carrega numa tecla, e a cada
  frame). O que lá se escrever passa a acontecer nesse momento; há um
  dicionário `memoria` para guardar coisas de um frame para o outro. É aqui
  que se acrescenta ao jogo algo que ele não tinha. No palco o jogo joga-se
  sozinho, para os acontecimentos acontecerem.
- **Desenhos**: as funções que desenham uma torre, um inimigo, um bicho, o
  herói.
- **Os botões com +**: criam uma cópia do primeiro, com outro nome, no fim
  da lista: um inimigo, uma torre, uma carta, um bicho, um ataque, um
  treinador, um nível. Na Bicharada à Solta há também **+ Nova zona** e
  **+ Novo edifício**. A cópia é posta onde apareça no jogo (o inimigo novo
  d'O Cerco entra na primeira onda), e o aviso diz onde. (No ficheiro do
  jogo em `oficina/jogos/`: `CRIAVEIS` e `novo()`.)

Apagar, escolher de uma lista, marcar caixas e mudar nomes existem nos cinco
jogos, cada um à sua medida. O que cada jogo oferece está no ficheiro dele em
`oficina/jogos/` (`CRIAVEIS`, `apagar()`, `lista()`, `caixas()`,
`renomear()`):

| Jogo | Cria-se e apaga-se | Listas e caixas |
|---|---|---|
| FADO//NEON | inimigos, cartas, ondas especiais, frases | os ataques e os invocados do chefe, os inimigos de uma onda; caixas no arranque do jogo, nos inimigos e nas cartas |
| Bicharada | bichos, ataques, treinadores, tipos | os bichos de um treinador, os ataques de um bicho |
| Bicharada à Solta | o mesmo, e zonas e edifícios | o mesmo, e a caixa «dá a rede no início» |
| O Cerco | inimigos, torres, ondas | os inimigos de uma onda |
| Mãos ao Ar! | inimigos, mundos, níveis | o jeito de um inimigo; caixas nos inimigos, nos mundos e nos níveis |

- **Mudar o nome** (com a coisa aberta) troca o nome em todos os sítios onde
  ela é usada: um ataque nas fichas dos bichos, um bicho nas equipas dos
  treinadores, um tipo nos bichos, nos ataques e na tabela de quem é forte
  contra quem, uma zona no `MUNDO` e nas `PORTAS`. Mudar o nome à mão, no
  código, deixava os outros a chamar pelo antigo.

Nas duas Bicharadas:

- **Apagar** (o botão vermelho, com a coisa aberta) tira do jogo um bicho,
  um ataque ou um treinador, e também dos sítios onde era usado: o bicho sai
  das equipas dos treinadores, o ataque sai dos ataques dos bichos. Quem
  ficaria sem nada fica com outro, e tem de sobrar sempre o bastante para o
  jogo se jogar. Na Bicharada à Solta apagam-se também zonas e edifícios, e
  o número de um treinador apagado sai do mapa (os seguintes descem um).
  O ficheiro de antes fica ao lado, em `.anterior`.
- **Escolher os bichos** (com um treinador aberto) mostra os bichos que
  existem, para se carregar nos que ele leva, pela ordem em que entram. Abre
  sozinho quando se cria um treinador novo, e pode-se voltar lá depois.
- **Escolher os ataques** (com um bicho aberto) faz o mesmo com os ataques
  dele, até quatro. Só aparecem os do tipo do bicho e os normais: um bicho
  de fogo não sabe ataques de água, e a Oficina recusa uma ficha que o diga.
  Um **ataque novo** nasce sem dono: é por aqui que se dá a um bicho.
- Cada **tipo** abre sozinho (a cor dele), com **+ Novo tipo** e **Apagar
  este tipo**: os bichos e os ataques de um tipo apagado passam para o tipo
  que todos podem aprender. Na Bicharada à Solta esse tipo escolhe-se
  (`TIPO_NORMAL`); na Bicharada é sempre o que se chama `normal`.
  (No ficheiro do jogo em `oficina/jogos/`: `apagar()` e `lista()`, e as
  chaves `"apagar"` e `"lista"` que a `regiao` devolve.)

Só na Bicharada à Solta:

- Com um treinador aberto há a caixa **Dá a rede no início**: é ela que diz
  quem dá a primeira rede a quem começa sem bichos. (`caixas()` e a chave
  `"caixas"`.)
- Um bicho tem duas imagens, **De frente** e **De costas**, e o boneco do
  jogador tem três. Os botões por cima do código escolhem em qual delas
  mexem o **Desenhar** e o **Escolher uma imagem**. (A chave `"imagens"`.)
- Um treinador aberto mostra-se em cenas: a dar a rede (se for ele), as
  falas e a luta, e as falas de depois.

Uma função que só corre mais tarde (a de uma tecla, por exemplo) pode
rebentar já depois de guardada: o jogo pára com o erro à vista, e corrige-se
ou carrega-se em **Repor o original**.

## Imagens e sons

Há coisas que no código dizem `"imagem": "soldado.png"`. Quando se abre uma
dessas, aparecem por cima do código os botões **Desenhar** (uma grelha de
16×16 quadradinhos para pintar ali mesmo) e **Escolher uma imagem** (um
ficheiro do computador: PNG, JPG, uma fotografia). O jogo passa a mostrar a
imagem em vez da forma. **Tirar a imagem** volta à forma.

Com `"som": "soldado.wav"` é igual: **Escolher um som** ou **Gravar** (com o
microfone, até 3 segundos; o browser pede autorização da primeira vez). Os
sons ficam em `comum/assets/sons/`, e o jogo guarda os que já leu em
`sons_carregados`, como faz com as imagens.

- A Oficina traz **modelos** de pixel art para todas as imagens dos jogos
  (`oficina/modelos/`, um PNG com o nome de cada imagem). **Usar o modelo**
  põe-no no jogo tal como está; no **Desenhar**, a fila **Começar por um
  modelo** põe qualquer um deles na grelha, para se mudar. Quem os desenha é
  o `oficina/modelos/fazer_modelos.py`: muda-se lá um desenho e corre-se
  outra vez.
- No **Desenhar** há ainda: a grelha de **16×16** ou de **32×32**
  (passa-se de uma para a outra sem perder o desenho); **Espelhar**, que o
  vira da esquerda para a direita; **Trocar cor**, que muda de uma vez todos
  os quadradinhos de uma cor; e, nas coisas com várias imagens, **Copiar o
  desenho** de outra (a de costas a começar pela de frente).
- Com o ajudante ligado, o **Desenhar** tem uma caixa para descrever o boneco
  («um galo vermelho») e o botão **Pedir ao ajudante**: o que ele desenhar
  fica na grelha, para retocar. Um modelo de texto desenha mal: sai um
  rascunho, uns melhores do que outros. (`INSTRUCOES_DO_DESENHO` e
  `desenho()`, no `ajudante.py`.)
- A imagem é encolhida para um quadrado pequeno e guardada em
  `comum/assets/imagens/`, com o nome que está no código. Mudar o nome no
  código é escolher outro ficheiro.
- As imagens não vão para o git. Vão dentro do zip que o **Guardar o meu
  jogo** descarrega, e é assim que passam para outro computador. Sem a
  imagem, o jogo corre na mesma, com a forma.

## O ajudante ("Pedir ajuda")

Se na sala houver um computador com placa gráfica a servir um modelo de
linguagem, a Oficina ganha o botão **Pedir ajuda**: a criança escreve uma
pergunta (ou carrega em "Corrige-me este erro") e a resposta aparece ali
mesmo. Com a pergunta seguem o bocado de código que está aberto e o erro que
estiver à vista; nada sai da rede da sala.

1. Em cada computador com placa gráfica (Windows): `instalar-servidor-windows.bat`.
   No fim mostra o endereço dele.
2. Escrevem-se esses endereços em `oficina/servidores.txt`, um por linha.

Com vários endereços, as perguntas espalham-se por todos, e um computador
desligado é saltado. Cada computador responde a uma pergunta de cada vez:
se o da vez não começar a escrever em 4 segundos é porque está ocupado, e a
mesma pergunta vai também para o seguinte; fica-se com o primeiro que
começar. Sem endereços, o botão não aparece e o resto funciona
como sempre. Para experimentar sem mexer no ficheiro:

```bash
python3 oficina/oficina.py --servidor http://192.168.1.50:11434
```

Os computadores ajudantes só põem o modelo na memória quando chega a
primeira pergunta, que por isso demora mais. Do portátil do professor
trata-se de todos de uma vez:

```bash
python3 oficina/ajudante.py acordar     # antes da sessão: ficam prontos
python3 oficina/ajudante.py adormecer   # no fim: a placa gráfica fica livre
python3 oficina/ajudante.py ver         # só mostra como estão
```

Quando a criança pede uma mudança ("põe-no mais rápido", "corrige-me este
erro"), o ajudante explica o que vai mudar e mostra o bocado já mudado, com
as linhas diferentes a amarelo. O botão **Aplicar no meu código** põe-no no
editor, e daí segue o caminho de sempre: só fica guardado se o jogo o
aceitar, e há um **Desfazer**. Nada muda sem a criança carregar no botão.

Num **mapa** (as zonas da Bicharada à Solta, o mapa d'O Cerco) o ajudante
não escreve o mapa outra vez: um modelo pequeno engana-se a contar as letras
de cada linha, ou devolve o mapa igual. Vê o mapa com as linhas e as colunas
numeradas e responde com ordens pequenas («linhas 6 a 8, colunas 9 a 13: ~»),
que a Oficina aplica. As linhas ficam sempre com o tamanho certo, e se as
ordens não mudarem nada a Oficina di-lo. O aluno vê o mapa já mudado, com o
botão **Aplicar**, como nas outras coisas. (`INSTRUCOES_DO_MAPA`, `grelha()`
e `responder()`, no `ajudante.py`.)

O ajudante engana-se de vez em quando. As instruções que ele recebe estão no
início de `oficina/ajudante.py`.

## O que acontece ao código

- A Oficina mexe no **ficheiro verdadeiro** do jogo. O que a criança muda
  fica no `o-cerco.py` dela, e o jogo corre-se depois como sempre.
- Só é guardado código que **funcionou**: correu no jogo uns instantes sem
  rebentar. Código com erros fica só no editor, com o erro explicado.
- **Guardar o meu jogo** descarrega um zip (`o-cerco.zip`) com o ficheiro do
  jogo e as imagens e os sons que ele usa. **Abrir um jogo guardado** recebe
  esse zip tal como está: troca o jogo da Oficina pelo que lá vem (o que lá
  estava fica ao lado, em `o-cerco.py.anterior`) e põe as imagens e os sons
  nas pastas deles. Também abre um `.py` sozinho, como os que a Oficina
  guardava antes.
- **Repor o original** devolve o bocado aberto ao que era da primeira vez
  que a Oficina abriu o jogo nesse computador (cópia em `oficina/.originais/`).

## Juntar outro jogo

Cada jogo tem um ficheiro em `oficina/jogos/` (ver `o_cerco.py`) que diz:

1. `escolhas(fonte)`: as coisas que se podem escolher;
2. `regiao(fonte, escolha)`: em que linhas está o código de cada uma;
3. `criar_palco(escolha)`: o palco, que põe o jogo a mostrar só essa coisa
   e verifica se o que foi escrito faz sentido.

Se a coisa puder ter imagem, a `regiao` devolve também `"imagem"` (o nome do
PNG escrito no código), e o jogo guarda as imagens que já leu num dicionário
chamado `imagens_carregadas`, que a Oficina esvazia quando a imagem muda.

Depois junta-se o nome à lista em `oficina/jogos/__init__.py`, e uma
fotografia do jogo (480×300, PNG) em `oficina/capas/` com o mesmo nome, para
o cartão dele; sem fotografia o cartão mostra a primeira letra. O editor, o
servidor e a troca de código ao vivo (`oficina.py`, `palco.py`,
`editor.html`) são iguais para todos os jogos, e o ajudante (`ajudante.py`)
também.
