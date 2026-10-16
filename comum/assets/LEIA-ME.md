# Assets — o que falta aqui e onde ir buscá-lo

Estas pastas vêm **vazias de propósito**. Não distribuímos imagens nem sons
de terceiros com o repositório, para não haver dúvidas de licença.

**Nada aqui é obrigatório.** Todos os ficheiros de Pygame deste repositório
correm sem estes ficheiros: desenham retângulos coloridos em vez de imagens e
ficam em silêncio em vez de tocar. Os assets tornam as sessões mais bonitas,
não mais possíveis.

## Ficheiros usados pelo código, com os nomes exatos

O código procura estes nomes. Se lhes chamares outra coisa, não são
encontrados — e o programa continua a correr, com retângulos.

### `imagens/`

| Nome exato | Usado em | Sugestão |
|---|---|---|
| `jogador.png` | `esqueleto.py` e tudo o que dele deriva | Personagem vista de cima ou de lado, fundo transparente |
| `moeda.png` | s08, s09 (`modelo-apanhar.py`) | Objeto a apanhar, pequeno e contrastante |
| `inimigo.png` | s09 (`modelo-perseguicao.py`, `modelo-esquivar.py`) | Algo claramente hostil |
| `jogador2.png` | s07 (`nivel-ouro.py`), só se houver dois jogadores | O mesmo boneco noutra cor |
| `fundo.png` | opcional, bloco de projeto | 800×600, ou será esticado para esse tamanho |

Formato **PNG**, com transparência. O tamanho não importa muito: o código faz
`pygame.transform.scale()` para o tamanho que precisa. Ainda assim, imagens
já perto de 48×48 ficam mais nítidas do que imagens de 512×512 encolhidas.

### `sons/`

| Nome exato | Usado em | Sugestão |
|---|---|---|
| `ponto.wav` | `esqueleto.py` e tudo o que dele deriva | Curto, alegre, menos de meio segundo |
| `dano.wav` | s09, bloco de projeto | Curto e seco |
| `fim.wav` | s09, bloco de projeto | Um a dois segundos, no máximo |

Formato **WAV** ou **OGG**. Evita MP3: em algumas máquinas o `pygame.mixer`
tropeça neles. Mantém os efeitos **curtos** — um som de dois segundos que
dispara dez vezes por segundo transforma a sala num inferno.

## Onde ir buscar, tudo CC0

CC0 significa domínio público: usa-se sem atribuição e sem pedir licença.
É a única categoria que recomendamos para trabalho de alunos, porque não
obriga ninguém a gerir créditos.

- **[kenney.nl/assets](https://kenney.nl/assets)** — a primeira paragem.
  Milhares de sprites e sons, todos CC0, todos coerentes entre si. Os packs
  *Platformer Pack*, *Space Shooter Redux* e *Interface Sounds* cobrem
  praticamente tudo o que este clube precisa.
- **[opengameart.org](https://opengameart.org)** — filtra por licença CC0.
  Mais variado, mas mistura estilos: os jogos ficam com ar de colagem.
- **[freesound.org](https://freesound.org)** — sons. Filtra por CC0. Exige
  conta e quase sempre exige cortar e encurtar o ficheiro.

## Como preparar isto antes de outubro

1. Descarrega **um** pack do Kenney (basta um; a coerência visual vale mais
   do que a variedade).
2. Escolhe quatro imagens e três sons.
3. Renomeia-os para os nomes exatos das tabelas acima.
4. Põe as imagens em `imagens/` e os sons em `sons/`.
5. Corre `python3 comum/esqueleto.py`. Se aparecer a tua imagem em vez do
   quadrado azul, está feito.

**Faz isto uma vez e cobre o ano inteiro.** Todas as sessões partilham esta
pasta; não há assets por sessão.

## Se os alunos quiserem trazer os seus

No bloco de projeto (sessões 10 a 17) é natural que queiram. Duas regras:

- **Cada equipa põe os seus numa subpasta com o nome da equipa**, para não
  entupirem esta pasta comum nem se sobreporem uns aos outros.
- **Nada descarregado de uma pesquisa de imagens.** É a conversa sobre
  licenças, e vale a pena tê-la uma vez, a sério, na sessão 10.
