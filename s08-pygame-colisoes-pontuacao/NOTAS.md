# Sessão 8 — Pygame: colisões e pontuação

Conceitos: `pygame.Rect`, `colliderect()`, listas de objetos, texto no ecrã.

O `esqueleto.py` desta pasta é o mesmo da sessão 7, já com uma moeda
desenhada. A única coisa que falta é reparar que ela foi tocada.

## O que o facilitador precisa de perceber

**Uma colisão é a pergunta mais simples que há: estes dois retângulos estão
sobrepostos *agora*?**
> «Não interessa quem chegou primeiro, nem de que lado, nem a que velocidade.
> É uma pergunta de sim ou não, feita sessenta vezes por segundo: estão
> sobrepostos ou não estão?»

`jogador.colliderect(moeda)` devolve `True` ou `False`. É tudo.

**A caixa da colisão não é o desenho.** É a distinção que resolve metade das
queixas de «apanhei e não contou» ou «nem lhe toquei e morri». O `Rect` é um
retângulo; o boneco desenhado por cima quase nunca enche o retângulo todo, e é
o retângulo que decide.

Na demonstração ao vivo mostra-se isto a sério — ver o passo 3.

**Uma lista guarda muitos objetos e o código é o mesmo para um ou para cem.**
É o segundo grande salto do ano, depois das funções:
> «Deixas de ter uma moeda. Passas a ter uma *lista* de moedas. E repara: o
> código que testa a colisão continua a ser o mesmo, só que agora está dentro
> de um `for`. Com uma moeda ou com mil, escreves o mesmo.»

## `pygame.key.get_pressed()` contra `KEYDOWN` — lê isto com atenção

**Confundir estes dois causa metade dos bugs do bloco de projeto.** Vale a
pena parares a sessão dez minutos para isto, mesmo que custe um nível.

Há duas perguntas diferentes sobre teclas, e não são intermutáveis:

| | `teclas = pygame.key.get_pressed()` | `evento.type == pygame.KEYDOWN` |
|---|---|---|
| **Pergunta** | «esta tecla está em baixo **agora**?» | «esta tecla **acabou de ser** carregada?» |
| **Quantas vezes dispara** | 60 vezes por segundo, enquanto a tecla estiver em baixo | **uma só vez**, no instante em que se carrega |
| **Onde vive** | no bloco da **lógica** | no bloco dos **eventos** |
| **Serve para** | andar, correr, apontar — o que é **contínuo** | saltar, disparar, pausar, começar, escolher — o que é **um acontecimento** |

A frase que resolve tudo, e que vale a pena escrever no quadro:

> **Estado é «estou a segurar». Evento é «carreguei».**

**Como se sente a diferença, ao vivo, em vinte segundos.** Põe o disparo no
sítio errado, de propósito:

```python
# no bloco da LOGICA, com o get_pressed — ERRADO para disparar
if teclas[pygame.K_SPACE]:
    balas.append(pygame.Rect(jogador.x, jogador.y, 8, 8))
```
Carrega no espaço durante um segundo: **saem sessenta balas**. A sala ri-se e
percebe imediatamente.

```python
# no bloco dos EVENTOS, com o KEYDOWN — CERTO para disparar
if evento.type == pygame.KEYDOWN and evento.key == pygame.K_SPACE:
    balas.append(pygame.Rect(jogador.x, jogador.y, 8, 8))
```
Uma bala por carregar.

E ao contrário, que é o erro simétrico e igualmente comum:
```python
# no bloco dos EVENTOS, com KEYDOWN — ERRADO para andar
if evento.type == pygame.KEYDOWN and evento.key == pygame.K_LEFT:
    jogador.x = jogador.x - VELOCIDADE
```
O boneco anda 5 pixels, pára, e só volta a andar se largares e voltares a
carregar. Este é o «o meu boneco só anda se eu martelar a tecla».

**A regra prática para o resto do ano:**
- **anda-se** com `get_pressed()`, na lógica;
- **acontece** com `KEYDOWN`, nos eventos.

O `esqueleto.py` já usa os dois, e usa-os bem: as setas com `get_pressed()`, e
a barra de espaços do menu com `KEYDOWN`. Aponta para as duas linhas e mostra
que a escolha não foi por acaso.

## Demonstração ao vivo (máx. 10 min)

**1. Repete as cinco palavras (30 seg).** EVENTOS → LÓGICA → DESENHAR →
MOSTRAR → ESPERAR. Faz a turma dizê-las contigo. Todas as sessões.

**2. `colliderect` (2 min).** Abre o `esqueleto.py`. A moeda já lá está e já
lhe passas por cima — e não acontece nada.
```python
        if jogador.colliderect(moeda):
            pontuacao = pontuacao + 1
```
Corre. A pontuação **dispara aos milhares** enquanto estás em cima da moeda.
Deixa acontecer, é ótimo:
> «Está errado? Não. Está a fazer exatamente o que eu escrevi, sessenta vezes
> por segundo. Enquanto eu estiver em cima dela, ela continua a ser apanhada.»

Acrescenta o `mudar_moeda_de_sitio()`. Resolve-se sozinho — a moeda deixa de
estar debaixo do jogador. **Esta é a lição:** o problema não era a colisão,
era não haver nada a mudar depois dela.

**3. As caixas a vermelho (2 min).** ← *a técnica a ensinar*

No `solucao.py`, no bloco de desenhar, há duas linhas comentadas. Tira-lhes o
`#`:
```python
        pygame.draw.rect(ecra, (255, 0, 0), jogador, 2)
        pygame.draw.rect(ecra, (255, 0, 0), moeda, 2)
```
O `2` no fim é a espessura do traço — sem ele o retângulo sai cheio e tapa o
sprite.

Corre. Aparecem as caixas por cima dos bonecos. Anda até quase tocar:
> «Repara que a colisão dispara quando as **caixas** se tocam, não quando os
> desenhos se tocam. Se o teu boneco for um círculo dentro de um quadrado, vai
> parecer que morres sem te tocarem.»

Agora **volta a pôr os `#`**, à frente deles, e diz porquê:
> «Isto é uma lente para ver o que está a acontecer, não faz parte do jogo.
> Liga-se para perceber, desliga-se a seguir. Vão precisar disto no bloco de
> projeto mais vezes do que imaginam.»

Esta técnica é das coisas mais úteis do ano inteiro. Um par que a domine
resolve sozinho bugs que de outra forma custariam meia sessão.

**4. `get_pressed` contra `KEYDOWN` (3 min).** Faz a demonstração das
sessenta balas, da secção acima. É o momento em que se paga a dívida do bloco
de projeto todo.

**5. Corre o `erro-proposital.py` (3 min).** ← *é aqui, no fim*

Este não rebenta e não avisa de nada. Faz contas erradas, e só se vê a jogar.

Aparecem 16 moedas encostadas umas às outras, no meio do ecrã. **Passa por
cima delas com o boneco, de uma vez só.** Repara no que acontece, e aponta:

- a pontuação sobe **8**, não 16;
- ficam moedas **visíveis debaixo do jogador**, que não são apanhadas;
- o contador «No ecrã» não bate certo com os pontos.

Deixa a turma reagir. Depois mostra o código:
```python
        for moeda in moedas:
            if jogador.colliderect(moeda):
                pontuacao = pontuacao + 1
                moedas.remove(moeda)
```

Explica com a imagem da fila, que é a que resulta melhor:
> «Imaginem uma fila de pessoas e eu a passar por elas com o dedo, a contar.
> Se eu tirar uma pessoa da fila, toda a gente atrás dela **anda um lugar para
> a frente** — mas o meu dedo já avançou. Saltei uma pessoa sem a ver. É
> exatamente isto que o Python está a fazer.»

Por isso são apanhadas metade: uma sim, uma não.

**A receita correta**, que está no `nivel-prata.py`:
```python
        sobreviventes = []
        for moeda in moedas:
            if jogador.colliderect(moeda):
                pontuacao = pontuacao + 1
                tocar(som_ponto)
            else:
                sobreviventes.append(moeda)
        moedas = sobreviventes
```
> «Não se tira ninguém da fila. Faz-se uma fila **nova** com quem fica, e no
> fim troca-se uma pela outra.»

Escreve no quadro: **«nunca tires nada de uma lista enquanto a percorres»**.
Deixa lá ficar até ao fim do ano. Este bug vai voltar no bloco de projeto,
disfarçado de balas, de inimigos e de plataformas.

> **Nota sobre o valor deste erro:** é o primeiro erro do ano que não dá
> mensagem nenhuma **e** dá um resultado errado. O `flip` em falta dava ecrã
> preto — pelo menos era óbvio. Este parece que funciona. Diz isso à turma:
> «os erros que vos vão custar tempo a sério são os que não se queixam».

## Os três níveis

**🥉 Bronze — uma moeda que reaparece noutro sítio ao ser apanhada.**
É o `esqueleto.py` com o `# TODO:` resolvido. Toda a gente tem de chegar aqui,
e chega em quinze minutos. A dificuldade real não é o `colliderect` — é
perceber que **alguma coisa tem de mudar depois da colisão**, senão ela
dispara para sempre. Quem tiver a pontuação aos milhares percebeu a colisão e
falta-lhe a consequência.

**🥈 Prata — várias moedas ao mesmo tempo, e a pontuação no ecrã.**
O nível central da sessão, e onde está a ideia grande: **uma lista**.

Duas dificuldades a sério:
1. **Percorrer a lista** com um `for`, tanto para colidir como para desenhar.
   São dois `for` diferentes, em dois blocos diferentes — e é isso que
   confunde. Quem só puser um vai ter moedas invisíveis ou moedas eternas.
2. **Tirar da lista sem estragar tudo.** É a receita dos sobreviventes. Vai
   custar. Repete a imagem da fila as vezes que forem precisas.

*Texto no ecrã:* o `mostrar_texto()` já vem feito no esqueleto desde a sessão
7 e ninguém reparou nele. Hoje ganha uso. O único senão previsível é o
`TypeError` de somar texto com número — daí o `str(pontuacao)`.

**🥇 Ouro — bichos que andam sozinhos e tiram vidas.**
Ver o **Aviso de âmbito** já a seguir: esta é a versão reduzida.

Três ideias novas e todas úteis ao bloco de projeto:
- **Coisas que se mexem sem ninguém carregar em teclas.** É a primeira vez.
  Se `bicho.x` cresce em cada volta do ciclo, o bicho anda. Não é preciso mais
  nada, e isso surpreende-os.
- **Reaparecer do outro lado.** `if bicho.left > LARGURA: bicho.right = 0`.
  Dois pixels de código e um mundo que parece infinito.
- **A invulnerabilidade improvisada.** Depois de levar dano, o jogador é
  atirado para o meio do ecrã. Sem isto perdiam-se as três vidas em meio
  segundo, porque no ciclo seguinte ainda se está sobreposto ao mesmo bicho.
  **Vale a pena mandá-los tirar essa linha e ver o que acontece.** É a mesma
  lição do 🥉 — a colisão dispara 60 vezes por segundo — mas agora dói.

## Aviso de âmbito

**O 🥇 foi reduzido.** O desafio original pedia três coisas: objetos que tiram
vidas, um temporizador de 60 segundos, e objetos que se movem sozinhos.
Ficaram **duas**: os bichos que se movem sozinhos e tiram vidas.

**Porquê:** o `esqueleto.py`, com a máquina de estados, o som e a degradação
graciosa dos assets, ocupa sozinho cerca de 120 das 150 linhas permitidas.
Sobram ~30 linhas por ficheiro, o que dá para **uma** mecânica nova bem
escrita, não para três. Enfiar as três à força daria um ficheiro ilegível — e
90 minutos não chegam para as três com adolescentes que programam de quinze em
quinze dias.

**O temporizador não se perdeu.** São quatro linhas, e ficam aqui prontas a
colar para quem chegar cedo ao fim do 🥇:

```python
# em cima, com as constantes
SEGUNDOS = 60

# dentro do comecar_jogo()
fim_do_tempo = pygame.time.get_ticks() + SEGUNDOS * 1000

# no bloco da logica
segundos = (fim_do_tempo - pygame.time.get_ticks()) // 1000
if segundos <= 0:
    estado = "fim"
```
Precisa de `global fim_do_tempo, segundos` na linha do `global`, e de uma
linha de `mostrar_texto` para o relógio aparecer.

**Onde está a funcionar, já escrito:** `s09/modelo-apanhar.py` (recolher N
objetos antes de o tempo acabar) e `projeto/dificuldade-crescente.py`. Se
alguém quiser o relógio, manda-o ler um desses ficheiros — ler código que
funciona é exatamente o que se quer no bloco de projeto.

## Erros que os alunos vão cometer

| Sintoma | Causa | A pergunta a fazer |
|---|---|---|
| A pontuação dispara aos milhares | Colisão sem consequência: o objeto continua debaixo do jogador | «Quantas vezes por segundo é que essa pergunta é feita? Enquanto estás em cima da moeda, a resposta muda?» |
| Só metade das moedas é apanhada, e ficam moedas debaixo do jogador | `remove()` durante o `for` sobre a mesma lista | «Lembras-te da fila? Quando tiras uma pessoa do meio, o que acontece a quem vem atrás? E onde é que o teu dedo já ia?» |
| `RuntimeError` ou moedas que ressuscitam | Variante do mesmo: mexer na lista enquanto se percorre | «Estás a mexer na lista que estás a percorrer? Qual é a receita que escrevemos no quadro?» |
| As moedas não aparecem | Falta o `for` no bloco de desenhar, ou desenha só `moedas[0]` | «Quantas moedas tens na lista? E quantas é que mandas desenhar?» |
| Apanha-se sem lhes tocar, ou não conta estando por cima | A caixa do `Rect` não coincide com o desenho | «Liga as caixas a vermelho. Agora olha outra vez: onde é que elas se tocam?» |
| `TypeError: can only concatenate str (not "int") to str` | Faltou o `str()` à volta da pontuação | «O `mostrar_texto` quer texto. O que é que a `pontuacao` é?» |
| O boneco só anda se martelar a tecla | Movimento no `KEYDOWN` em vez de `get_pressed()` | «Quantas vezes dispara o `KEYDOWN` se eu carregar e ficar a segurar? Que pergunta é que tu querias mesmo fazer?» |
| Saem sessenta balas de uma vez | Disparo no `get_pressed()` em vez do `KEYDOWN` | «"Estou a segurar" ou "acabei de carregar" — qual das duas é disparar?» |
| `AttributeError: 'list' object has no attribute 'colliderect'` | Chamou `colliderect` na lista em vez de em cada `Rect` | «O que é que está dentro dessa lista? A lista sabe colidir, ou quem sabe colidir é o que está lá dentro?» |
| As três vidas desaparecem de uma vez | Falta afastar o jogador depois do dano | «Depois de levares dano, no ciclo seguinte, ainda estás em cima do bicho?» |
| Tudo funciona mas o ecrã fica preto | O `flip` outra vez, ou o `fill` a seguir ao desenho | «Das cinco palavras, quais é que tens e por que ordem?» |
| `IndexError: list index out of range` | Está a usar índices à mão em vez de `for moeda in moedas` | «Precisas mesmo do número da posição, ou só queres cada moeda uma vez?» |

## Critério de sucesso

Aos 90 minutos:

- [ ] **Toda a gente tem uma colisão a funcionar** e uma consequência a
      seguir. É o mínimo não negociável.
- [ ] Toda a gente tem um número no ecrã que sobe quando se apanha uma coisa.
      É o momento em que aquilo passa a ser um **jogo** e não uma demonstração.
- [ ] Pelo menos metade tem uma **lista** de objetos e percorre-a com um `for`.
- [ ] Toda a gente consegue dizer a diferença entre `get_pressed()` e
      `KEYDOWN` por palavras suas. Pergunta a três alunos à saída. Se não
      souberem, repete na sessão 9 — vais pagá-lo caro no bloco de projeto.
- [ ] Pelo menos um par usou as caixas a vermelho para perceber um bug seu.

**O sinal mais forte da sessão:** um aluno que, ao ver as moedas a
comportarem-se de forma estranha, liga as caixas a vermelho **sem ninguém lhe
dizer**. Esse aluno passou de escrever código a investigar código, e é a
diferença entre acabar o projeto em maio e não acabar.

**Sinal de alarme:** um par com a pontuação aos milhares que decide que «está
bom assim» e segue em frente. Não está bom, e o mesmo bug vai voltar no
projeto disfarçado de outra coisa. Pergunta: «quantos pontos vale mesmo uma
moeda?»
