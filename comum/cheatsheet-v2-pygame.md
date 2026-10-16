# Cheat sheet v2 — Pygame

Para a sessão 7 em diante. Imprime em papel.
A v1 continua a valer: isto acrescenta, não substitui.

O Pygame já está instalado nas máquinas da sala, dentro de um ambiente
virtual. Se aparecer `ModuleNotFoundError: No module named 'pygame'`, o
ambiente não está activado — chama o facilitador.

---

## AS CINCO PALAVRAS

Todos os jogos deste clube têm estes cinco blocos, **sempre por esta ordem**:

> ## EVENTOS → LÓGICA → DESENHAR → MOSTRAR → ESPERAR

1. **EVENTOS** — o que aconteceu? Fecharam a janela? Carregaram numa tecla?
2. **LÓGICA** — as contas. Onde é que as coisas passam a estar.
3. **DESENHAR** — pintar tudo numa folha invisível.
4. **MOSTRAR** — pôr a folha no ecrã.
5. **ESPERAR** — travar, para não correr a mil à hora.

**Quando não souberes onde pôr uma linha, a resposta é uma destas cinco
palavras.**

---

## O esqueleto mínimo

```python
import pygame

pygame.init()
ecra = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

jogador = pygame.Rect(400, 300, 48, 48)

a_correr = True
while a_correr:

    # 1. EVENTOS
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            a_correr = False

    teclas = pygame.key.get_pressed()

    # 2. LOGICA
    if teclas[pygame.K_LEFT]:
        jogador.x = jogador.x - 5

    # 3. DESENHAR
    ecra.fill((18, 18, 28))
    pygame.draw.rect(ecra, (70, 130, 230), jogador)

    # 4. MOSTRAR
    pygame.display.flip()

    # 5. ESPERAR
    clock.tick(60)

pygame.quit()
```

---

## Coordenadas do ecrã

```
 (0,0) ------------------> x cresce para a DIREITA
   |
   |          O (0,0) e o canto de CIMA a ESQUERDA.
   |          Para SUBIR, o y tem de DIMINUIR.
   v
 y cresce para BAIXO
```

---

## O `Rect` — o retângulo que serve para tudo

```python
r = pygame.Rect(x, y, largura, altura)
```

| Atributo | O que é |
|---|---|
| `r.x`  `r.y` | canto superior esquerdo |
| `r.left` `r.right` `r.top` `r.bottom` | as quatro bordas |
| `r.centerx` `r.centery` `r.center` | o centro |
| `r.width` `r.height` | tamanho |

Todos se podem **ler e escrever**. `r.right = 800` empurra o retângulo todo.

```python
r.colliderect(outro)          # estao sobrepostos AGORA? True ou False
r.clamp_ip(ecra.get_rect())   # puxa o r para dentro do ecra
r.move(dx, dy)                # devolve um COPIA deslocada (nao mexe no r)
r.inflate(dx, dy)             # devolve uma copia maior, mesmo centro
r.collidepoint(x, y)          # o ponto esta dentro? (util para o rato)
```

---

## Teclado — as duas perguntas diferentes

> ### Estado é «estou a segurar». Evento é «carreguei».

**`pygame.key.get_pressed()`** — no bloco da **LÓGICA**.
Pergunta «está em baixo **agora**?». Dispara 60 vezes por segundo.
Para **andar**, correr, apontar.
```python
teclas = pygame.key.get_pressed()
if teclas[pygame.K_LEFT]:
    jogador.x = jogador.x - 5
```

**`KEYDOWN`** — no bloco dos **EVENTOS**.
Pergunta «**acabou de ser** carregada?». Dispara **uma** vez.
Para **saltar**, disparar, pausar, começar, escolher.
```python
for evento in pygame.event.get():
    if evento.type == pygame.KEYDOWN:
        if evento.key == pygame.K_SPACE:
            saltar()
```

Trocá-los dá sempre um destes dois bugs:
- disparo no `get_pressed()` → **saem 60 balas por segundo**;
- movimento no `KEYDOWN` → **só anda se martelares a tecla**.

**Nomes de teclas:** `K_LEFT` `K_RIGHT` `K_UP` `K_DOWN` `K_SPACE` `K_RETURN`
`K_ESCAPE` `K_a` … `K_z` `K_0` … `K_9`

---

## Desenhar

```python
ecra.fill((18, 18, 28))                      # apagar tudo. SEMPRE primeiro
pygame.draw.rect(ecra, cor, rect)            # retangulo cheio
pygame.draw.rect(ecra, cor, rect, 2)         # so o contorno, 2 px
pygame.draw.circle(ecra, cor, (x, y), raio)
pygame.draw.line(ecra, cor, (x1, y1), (x2, y2), 3)
ecra.blit(imagem, rect)                      # colar uma imagem
```

**Cores** são três números de 0 a 255: `(vermelho, verde, azul)`.
`(0,0,0)` preto · `(255,255,255)` branco · `(255,0,0)` vermelho

> **Truque para ver colisões:** desenha os `Rect` a vermelho por cima dos
> sprites com `pygame.draw.rect(ecra, (255,0,0), r, 2)`. Vês onde estão as
> caixas a sério. Apaga a linha quando perceberes.

---

## Texto

```python
fonte = pygame.font.SysFont(None, 36)        # uma vez, no inicio

desenho = fonte.render("Pontos: " + str(pontuacao), True, (255,255,255))
ecra.blit(desenho, (20, 20))
```

> ⚠️ Números têm de passar por **`str()`**, senão dá `TypeError`.

---

## Imagens e sons

```python
from pathlib import Path
PASTA = Path(__file__).parent.parent / "comum" / "assets"

imagem = pygame.image.load(PASTA / "imagens" / "jogador.png").convert_alpha()
imagem = pygame.transform.scale(imagem, (48, 48))

pygame.mixer.pre_init(44100, -16, 2, 512)    # ANTES do pygame.init()
som = pygame.mixer.Sound(PASTA / "sons" / "ponto.wav")
som.play()
```

> ⚠️ Usa sempre `Path(__file__).parent`. Com `"assets/x.png"` o programa só
> funciona se o terminal estiver aberto na pasta certa.

---

## Tempo

```python
clock.tick(60)                       # trava nos 60 ciclos por segundo
agora = pygame.time.get_ticks()      # milissegundos desde o arranque

# um relogio de 30 segundos
fim = pygame.time.get_ticks() + 30 * 1000            # quando comeca
segundos = (fim - pygame.time.get_ticks()) // 1000   # em cada ciclo
```

---

## Receitas

**Não sair do ecrã**
```python
jogador.clamp_ip(ecra.get_rect())
```

**Tirar coisas de uma lista** — nunca `remove()` durante o `for`
```python
sobreviventes = []
for moeda in moedas:
    if jogador.colliderect(moeda):
        pontuacao = pontuacao + 1
    else:
        sobreviventes.append(moeda)
moedas = sobreviventes
```

**Reaparecer do outro lado**
```python
if pedra.top > ALTURA:
    pedra.bottom = 0
    pedra.x = random.randint(0, LARGURA - PEDRA)
```

**Perseguir o jogador**
```python
if bicho.x < jogador.x:
    bicho.x = bicho.x + 2
if bicho.x > jogador.x:
    bicho.x = bicho.x - 2
```

**Paredes** — um eixo de cada vez, mover e desfazer
```python
jogador.x = jogador.x + passo_x
for parede in paredes:
    if jogador.colliderect(parede):
        jogador.x = jogador.x - passo_x
# e so depois o mesmo para o y
```

**Máquina de estados**
```python
estado = "menu"          # "menu", "jogo" ou "fim"
if estado == "jogo":
    ...
```

---

## Quando alguma coisa corre mal

| Sintoma | Quase de certeza |
|---|---|
| **Ecrã todo preto, sem erro nenhum** | Falta o `pygame.display.flip()` |
| Rasto de tinta pelo ecrã | Falta o `ecra.fill()` no início do desenhar |
| A janela não fecha, "não responde" | Falta o `for evento in pygame.event.get()` |
| O boneco sobe quando devia descer | O `y` cresce para baixo |
| O boneco anda a mil | Falta o `clock.tick(60)` |
| Só anda se martelar a tecla | Movimento no `KEYDOWN`; usa `get_pressed()` |
| Saem 60 balas de uma vez | Disparo no `get_pressed()`; usa `KEYDOWN` |
| A pontuação sobe aos milhares | Colisão sem consequência: nada muda depois dela |
| Metade dos objetos não é apanhada | `remove()` durante o `for` |
| A imagem não aparece, fica o retângulo | Nome ou pasta errados |
| `pygame.error: video system not initialized` | Falta o `pygame.init()`, ou está depois |
| `TypeError: ... str ... int` | Falta o `str()` à volta de um número |
