# A Oficina

Escolhe-se um jogo e **uma coisa** dele (um inimigo, uma torre, o mapa).
De um lado fica só o código dessa coisa; do outro, o jogo a correr, a
mudar enquanto se escreve.

Protótipo: por agora só abre **O Cerco** (`s13-o-cerco/o-cerco.py`).

## Correr

Com o ambiente virtual activado (ver `COMO-CORRER.md`, secção 1):

```bash
python3 oficina/oficina.py
```

Abre uma página no browser, com o jogo à esquerda e o código à direita.
O jogo é o verdadeiro, a correr no computador: a página mostra a imagem
dele e passa-lhe o rato e o teclado (clica-se no jogo para jogar, no
código para escrever). Para fechar: `Ctrl+C` no terminal.

Não precisa de internet nem de instalar mais nada.

## O ajudante ("Pedir ajuda")

Se na sala houver um computador com placa gráfica a servir um modelo de
linguagem, a Oficina ganha o botão **Pedir ajuda**: a criança escreve uma
pergunta (ou carrega em "Porque é que dá erro?") e a resposta aparece ali
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

O ajudante dá pistas e explica; não escreve o código pela criança, e
engana-se de vez em quando. As instruções que ele recebe estão no início de
`oficina/ajudante.py`.

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

Depois junta-se o nome à lista em `oficina/jogos/__init__.py`. O editor, o
servidor e a troca de código ao vivo (`oficina.py`, `palco.py`,
`editor.html`) são iguais para todos os jogos, e o ajudante (`ajudante.py`)
também.
