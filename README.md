# Clube de Código 2026/27

Materiais de programação para um clube de jovens dos 12 aos 18 anos.
17 sessões quinzenais de 1h30 ao longo do ano letivo.

## O que é preciso para correr isto

- **Python 3.12 ou superior** (CPython).
- **`pygame-ce`**, e só a partir da sessão 7, num **ambiente virtual**:
  ```
  python3 -m venv .venv
  source .venv/bin/activate          # Windows: .venv\Scripts\activate.bat
  python3 -m pip install -r requirements.txt
  ```
  As sessões 1 a 3 usam apenas a biblioteca padrão: **não é preciso instalar
  nada** até à sessão 7.
- **Nada mais.** Sem `numpy`, sem `requests`, sem rede. Tudo corre offline.

> **O ambiente virtual não é opcional.** Em macOS com Homebrew e em Linux, o
> `pip install` no Python do sistema é recusado com
> `error: externally-managed-environment`. O `COMO-CORRER.md` explica isto,
> e explica como configurar o VS Code para ninguém ter de escrever `activate`
> em cada sessão.

> Escolhemos `pygame-ce` (a *community edition*) e usamo-la em todo o
> repositório. O `import` é `import pygame`, igual ao `pygame` clássico — mas
> não instales os dois na mesma máquina, entram em conflito.

## Como correr qualquer ficheiro

Abre o terminal na pasta do ficheiro e:

```
python3 solucao.py
```

Sem argumentos, sem variáveis de ambiente. Todos os ficheiros deste
repositório funcionam assim. Se um ficheiro de Pygame não fechar ao clicares
no X, é um bug — abre um problema.

**O `COMO-CORRER.md` tem o guia completo:** o que esperar de cada ficheiro, as
teclas de cada um, os `erro-proposital.py` que são suposto falhar, e um
comando para verificar o repositório todo de uma vez.

## Porque é que não há `s04`, `s05` e `s06`

As sessões 4, 5 e 6 são o bloco **Astro Pi**, com Sense HAT e hardware
próprio. Esse bloco tem materiais em separado e **não faz parte deste
repositório**. O salto na numeração é intencional: não faltam ficheiros.

## Estrutura

```
clube-de-codigo-2627/
├── README.md                     ← este ficheiro
├── PERCURSO-DO-PROFESSOR.md      ← por onde o facilitador começa
├── COMO-CORRER.md                ← como preparar, correr e verificar tudo
├── requirements.txt              ← a única dependência: pygame-ce
├── comum/
│   ├── esqueleto.py              ← o ficheiro central do 2.º e 3.º períodos
│   ├── cheatsheet-v1-python.md   ← para as sessões 1 a 3
│   ├── cheatsheet-v2-pygame.md   ← para a sessão 7 em diante
│   └── assets/                   ← vem vazia, ver assets/LEIA-ME.md
├── s01-mad-libs/                 ← print, variáveis, input, f-strings
├── s02-adivinha-numero/          ← while, if/elif/else, random, int()
├── s03-gerador-personagens/      ← def, parâmetros, return, listas
├── s07-pygame-janela-movimento/  ← nasce aqui o esqueleto.py
├── s08-pygame-colisoes-pontuacao/← Rect, colliderect, listas de objetos
├── s09-jogo-completo/            ← três jogos-modelo curtos
└── projeto/                      ← recursos para as sessões 10 a 17
```

## O que há em cada pasta de sessão

| Ficheiro | Para quem | O que é |
|---|---|---|
| `esqueleto.py` | alunos | Corre e faz algo visível, mas está incompleto. Os `# TODO:` são perguntas, não respostas |
| `solucao.py` | facilitador | Implementação de referência. Estuda-se **antes** da aula |
| `nivel-bronze.py` | facilitador | Solução do desafio 🥉 |
| `nivel-prata.py` | facilitador | Solução do desafio 🥈 |
| `nivel-ouro.py` | facilitador | Solução do desafio 🥇 |
| `erro-proposital.py` | projetor | Tem **um** erro plantado, para correr ao vivo e ler o traceback com a turma. Qual é o erro está no `NOTAS.md`, nunca no ficheiro |
| `NOTAS.md` | facilitador | Guião da sessão: o que explicar, a demonstração ao vivo, os erros previsíveis e o critério de sucesso |

Os ficheiros `nivel-*.py` **não se distribuem aos alunos**. São o mapa do
facilitador para saber onde cada par pode chegar e o que perguntar a seguir.

## As pastas de assets vêm vazias

`comum/assets/imagens/` e `comum/assets/sons/` não têm ficheiros e isso é
deliberado: não distribuímos imagens nem sons de terceiros com este
repositório, para não haver dúvidas de licença.

**Todos os ficheiros de Pygame correm à mesma sem assets** — desenham
retângulos coloridos em vez de imagens e ficam em silêncio em vez de tocar.
Nenhuma sessão fica bloqueada por faltarem os ficheiros.

O `comum/assets/LEIA-ME.md` diz que ficheiros são precisos, com que nomes
exatos, e onde os ir buscar (bancos CC0, sobretudo o Kenney.nl).

## Regras de estilo do código deste repositório

Escritas para serem lidas por adolescentes que programam de quinze em quinze
dias, não para impressionar ninguém:

- Nomes de variáveis e funções **em português**, sem acentos: `pontuacao`,
  `jogador_rect`, `gerar_personagem()`.
- Comentários em **português europeu**: ecrã, ficheiro, rato, guardar.
- **Sem classes**, sem `pygame.sprite`, sem herança. Funções e listas.
  As colisões fazem-se com `pygame.Rect` e `colliderect()`.
- Sem compreensões de lista, sem `lambda`, sem type hints, sem decoradores.
  Quando a solução elegante precisa de um conceito que ainda não foi
  ensinado, fica a solução longa e óbvia.
- Constantes em MAIÚSCULAS no topo do ficheiro (`LARGURA = 800`), porque é
  o primeiro sítio onde um aluno mexe.

## A regra de ouro

**O facilitador nunca toca no teclado do aluno.** Por isso os `NOTAS.md`
listam, para cada erro previsível, a *pergunta* a fazer — e não a correção
a ditar.
