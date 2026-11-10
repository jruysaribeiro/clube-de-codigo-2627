# Sessão 14 — Mãos ao Ar!

Um jogo de plataformas que se joga **sem tocar no computador**: a câmara vê a
mão e o Faísca (o robot) faz o que ela mandar. Um recreio para treinar
(nível 0), vinte níveis em quatro mundos, e o Rei Sucata à espera no último.

```
python3 maos-ao-ar.py
```

**O Faísca anda sozinho.** O jogador só decide para onde, e quando.

| | Com a mão | No teclado |
|---|---|---|
| andar | mostrar a mão à câmara | (anda sozinho) |
| parar | tirar a mão da imagem | seta para baixo |
| virar | levar a mão para o outro lado (passar a linha branca) | setas esquerda / direita |
| correr | levantar a mão acima da linha amarela | `Shift` |
| saltar | fechar o punho | `Espaço` ou seta para cima |
| disparar | apontar com o indicador | `X` |

| Tecla | Faz |
|---|---|
| `P` | pausa |
| `I` | voltar ao treino dos gestos (no título ou na pausa) |
| `T` | jogar só com o teclado (o Faísca anda sem precisar da mão) |
| `C` | experimentar a câmara seguinte |
| `F` ou `F11` | sair do ecrã inteiro / voltar a ele (abre em ecrã inteiro; a constante é `ECRA_INTEIRO`) |
| `Esc` | voltar ao título / sair |
| `N` | **atalho do professor:** dá o nível por passado |

O teclado funciona sempre, mesmo com a câmara ligada. Dá jeito para ajudar
um par que ficou preso.

## Antes da aula (importante)

**Este é o único ficheiro do repositório que precisa de mais do que o
`pygame-ce`.** Precisa do `mediapipe` (que traz o `opencv` e o `numpy`,
cerca de 400 MB) e de um modelo de 8 MB que reconhece mãos.

**O jogo trata disso sozinho na primeira vez que corre**, mas essa primeira
vez precisa de **internet** e demora uns minutos. Por isso:

> **Corre o jogo uma vez em cada computador, antes da aula, com a tua conta.**

O que acontece nessa primeira vez:

1. Experimenta importar cada biblioteca. Se alguma faltar (ou estiver
   estragada), instala-a com o `pip`.
   - Dentro de um `.venv`, ou no Windows: instala diretamente.
   - Com o Python do sistema (o do `instalar-mac.sh` e do
     `instalar-linux.sh`): usa `sudo`, para ficar para **todos os
     utilizadores**, e **pede a palavra-passe de administrador no terminal**.
     Se o `sudo` falhar, instala só para a conta atual.
2. Volta a arrancar sozinho, já com tudo instalado.
3. Descarrega o `hand_landmarker.task` para esta pasta (não vai para o git).
   Se a pasta não deixar escrever (sessão de convidado), guarda-o na pasta
   temporária, e nesse caso descarrega-o outra vez na sessão seguinte.

Se alguma coisa falhar, **o jogo corre na mesma, só com o teclado**, e diz
porquê no terminal e no ecrã de título.

**No Mac**, a primeira vez o sistema pergunta se o Terminal (ou o VS Code)
pode usar a câmara. O jogo espera uns segundos pela resposta. Se alguém
disse que não: Definições do Sistema → Privacidade e Segurança → Câmara.

**Se abrir a câmara errada** (no Mac pode escolher a do iPhone): tecla `C`,
ou muda a constante `CAMARA` no topo do ficheiro.

**Python:** testado num Mac com 3.14 e 3.15; o `mediapipe` também existe para
o 3.12 dos instaladores. Se não houver `mediapipe` para o Python da máquina, o
jogo avisa e fica em modo teclado.

## Como arrumar a sala

- **Luz de frente, não por trás.** Uma janela atrás do aluno estraga tudo.
- A mão a **meio metro ou mais** da câmara, com a palma virada para ela.
- **Uma mão de cada vez.** Com várias mãos na imagem, o jogo escolhe uma, e
  nem sempre a mesma. O colega do par fica ao lado, fora da imagem.
- No canto do ecrã está a imagem da câmara com o esqueleto da mão: verde
  (aberta), azul (punho), vermelho (a apontar). Se o esqueleto não aparece,
  o problema é de luz ou de distância, não do aluno.

## O que o jogador vê, por ordem

1. **Título.** Fecha o punho (ou `Espaço`).
2. **Treino.** Sete gestos, um de cada vez, com a câmara em grande. Cada um
   fica verde quando é feito. `Enter` salta.
3. **Nível 0, o recreio.** Um nível sem perigo, com placas a dizer o que
   experimentar: andar, parar, saltar, disparar, dar meia volta, correr, a
   mola. Aqui **não se perdem corações**.
4. **Níveis 1 a 20.** Quatro corações por nível. Ficar sem eles é recomeçar
   esse nível, não o jogo. Até três estrelas por nível: chegar ao fim, apanhar
   todas as moedas, não perder corações.

| Mundo | Níveis | O que aparece de novo |
|---|---|---|
| O Prado | 1–5 | saltar, buracos, lesmas, correr, dar meia volta, caixotes |
| A Gruta | 6–10 | espinhos, sapos, morcegos, molas, pontes podres, ouriços, javalis |
| O Vulcão | 11–15 | lava, canhões, escaladas aos ziguezagues |
| A Fábrica da Noite | 16–20 | tudo junto, plataformas sobre o vazio, e o Rei Sucata |

## As ideias que valem a pena mostrar

- **A câmara não sabe o que é uma mão.** O `mediapipe` devolve 21 pontos
  (as articulações), e mais nada. Tudo o resto é nosso: ver `classificar_mao()`.
  *«Um dedo está esticado se a ponta estiver mais longe do pulso do que a
  articulação do meio.»* É Pitágoras outra vez (`math.hypot`), como no alcance
  das torres do s13. Pergunta boa: «como é que distinguiam um punho de uma mão
  aberta, só com 21 pontos?»
- **Porque é que o Faísca anda sozinho.** Um gesto demora mais do que uma
  tecla (a câmara dá 30 imagens por segundo, e uma forma só conta à segunda
  imagem). Com um boneco que anda sozinho, o jogador só tem de tomar decisões,
  não de as manter. É uma decisão de *design* por causa de uma limitação
  técnica.
- **As ajudas invisíveis.** `TEMPO_COIOTE` (ainda se pode saltar um instante
  depois de cair da beira) e `TOLERANCIA_SALTO` (um salto pedido cedo demais
  ainda conta). Põe as duas a `0` e pede a alguém para jogar: o jogo é o mesmo
  e parece injusto. Quase todos os jogos de plataformas fazem isto.
- **O jogo corre sem janela.** `passo_do_jogo()` não desenha nada. Foi assim
  que um robot jogou os 21 níveis para provar que todos se passam (ver abaixo).
- **A câmara corre noutro fio** (`threading`), para o jogo não ficar à espera
  dela. É o único sítio do repositório onde isto aparece; é para mostrar que
  existe, não para explicar.

## Escada de personalização

O ficheiro tem o mesmo formato do Halloween: **«MEXE SÓ AQUI»** em cima,
**«NÃO MEXER»** em baixo.

**1. Só dados**
- Mudar as linhas dos gestos: `ZONA_ESQUERDA`, `ZONA_DIREITA`, `LINHA_CORRER`.
  (Alunos mais baixos ou câmara mais alta: desce a `LINHA_CORRER`.)
- Mudar a física: `GRAVIDADE`, `FORCA_SALTO`, `VEL_CORRER`. Lua? Gelatina?
- Desenhar níveis: são listas de texto, uma letra por quadrado. A legenda
  está por cima de `NIVEIS`. Regras: a andar salta-se um buraco de 2, a correr
  de 3, e sobe-se 2 quadrados de cada vez.
- Pôr `"placas"` num nível para contar uma história.
- Mudar cores, mundos, nomes, e os números dos inimigos em `INIMIGOS`.

**2. Pequenas mudanças às regras**
- Um inimigo novo: mais uma letra em `INIMIGOS`, com um dos seis `jeito`s que
  já existem. Sem desenho próprio aparece como um bloco com olhos.
- Um gesto novo em `classificar_mao()`: dois dedos (o «V») para... o quê?
- Tiros com alcance maior mas recarga mais lenta.

**3. Mecânicas novas**
- Salto duplo. Um escudo com o «V». Plataformas que se mexem.
- Guardar o recorde de estrelas num ficheiro.
- Duas mãos, dois jogadores (`num_hands=2` em `ligar_camara()`).

## Os níveis passam-se todos (testado)

Um robot jogou cada nível com o motor verdadeiro, à procura de um caminho
até à saída. Para deixar margem para o atraso dos gestos, também o fez com
um Faísca **mais fraco** (salta 6% menos, anda 7% mais devagar): os 21 níveis
passam-se das duas maneiras. Quase todos se passam até **sem correr**; só os
níveis 10, 15, 18 e 19 têm sítios (dois espinhos seguidos) que pedem corrida.

O robot não joga contra os inimigos. Aí a garantia é outra: **todos os
inimigos morrem a tiro**, os tiros não acabam, e pode-se sempre parar
(tirando a mão) para disparar com calma.

Se desenharem níveis novos e o Faísca não chegar a algum sítio, as perguntas
são as das regras: «quantos quadrados tem esse buraco? e essa parede?»

## Erros previsíveis (e a pergunta a fazer)

| Sintoma | Pergunta |
|---|---|
| «MOSTRA A MÃO» e o Faísca não anda | «Vês o esqueleto verde na imagem do canto? Onde está a luz?» |
| Salta sem ninguém mandar | «O que é que a câmara vê quando rodas a mão de lado? Parece um punho?» |
| Não consegue correr | «Onde está a linha amarela na imagem? A tua mão chega lá?» |
| Vira-se sozinho | «Há outra mão na imagem? De quem?» |
| O nível novo aparece cortado | «Todas as linhas do mapa têm o mesmo número de letras? São 12 linhas?» |
| O Faísca nasce no ar ou num sítio estranho | «Onde está o `P` no mapa? Há mais do que um?» |
| `KeyError` ao carregar o nível | «O nível tem `"nome"`, `"dica"` e `"mapa"`, com as aspas e as vírgulas?» |
| Janela abre mas diz «sem câmara» | Lê a linha laranja no título: diz o motivo. Depois tecla `C`. |
