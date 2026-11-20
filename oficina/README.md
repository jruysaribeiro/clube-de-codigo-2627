# A Oficina

Escolhe-se um jogo e **uma coisa** dele (um inimigo, uma torre, o mapa).
De um lado fica só o código dessa coisa; do outro, o jogo a correr, a
mudar enquanto se escreve.

Abre quatro jogos: **FADO//NEON** (s10), **Bicharada** (s12), **O Cerco** (s13)
e **Mãos ao Ar!** (s14, aqui jogado só com o teclado, sem câmara).

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

N'O Cerco, além dos dados (inimigos, torres, mapa), abrem-se quatro
**regras**: quem a torre ataca, o que a torre faz ao disparar, o que acontece
a um inimigo atingido e como anda um inimigo. Cada uma é uma função pequena
do jogo; mudá-la muda a maneira como o jogo se comporta. É aqui que se
escreve um `if` a sério.

- O palco das regras tem uma torre de cada e inimigos já a meio do caminho,
  e marca com um círculo amarelo quem cada torre escolheu.
- Uma regra nova é experimentada mais tempo antes de ser guardada. Se
  rebentar, o jogo volta à anterior e o erro aparece com a linha.
- O código escrito na Oficina não pode usar `import`, `open` nem outras
  coisas que mexem no computador em vez de no jogo (lista em `blocos.py`).
  É uma vedação contra o óbvio, não uma muralha.

Para abrir regras noutro jogo: as funções têm de estar encostadas à margem
no ficheiro do jogo, e a `regiao` devolve as linhas da função (ver `REGRAS`
no `jogos/o_cerco.py`).

## Imagens

Há coisas que no código dizem `"imagem": "soldado.png"`. Quando se abre uma
dessas, aparece por cima do código o botão **Escolher uma imagem**: a
criança escolhe um ficheiro do computador (PNG, JPG, uma fotografia) e o jogo
passa a desenhá-lo em vez da forma. **Tirar a imagem** volta à forma.

- A imagem é encolhida para um quadrado pequeno e guardada em
  `comum/assets/imagens/`, com o nome que está no código. Mudar o nome no
  código é escolher outro ficheiro.
- As imagens ficam só nesse computador: não vão para o git, nem dentro do
  ficheiro que o **Guardar o meu jogo** descarrega. Sem a imagem, o jogo
  corre na mesma, com a forma.

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
desligado é saltado. Sem endereços, o botão não aparece e o resto funciona
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

O ajudante engana-se de vez em quando. As instruções que ele recebe estão no
início de `oficina/ajudante.py`.

## O que acontece ao código

- A Oficina mexe no **ficheiro verdadeiro** do jogo. O que a criança muda
  fica no `o-cerco.py` dela, e o jogo corre-se depois como sempre.
- Só é guardado código que **funcionou**: correu no jogo uns instantes sem
  rebentar. Código com erros fica só no editor, com o erro explicado.
- **Guardar o meu jogo** descarrega o ficheiro inteiro. **Abrir um jogo
  guardado** troca o jogo da Oficina por esse ficheiro (o que lá estava
  fica ao lado, em `o-cerco.py.anterior`).
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
