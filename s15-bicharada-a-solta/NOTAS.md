# Sessão 15 — Bicharada à Solta

**Batalhas por turnos, à moda do Pokémon, com bichos muito portugueses e um
mundo por onde se anda.** Um mundo de **zonas**, **edifícios** onde se entra,
**treinadores** que falam, bichos que se **apanham** com redes, e uma **loja**.
É uma **base** para os alunos tornarem sua, e foi feito para ser mexido na
Oficina (`python3 oficina/oficina.py`).

```
python3 bicharada-a-solta.py
```

| Tecla | Faz |
|---|---|
| setas | andar pelo mapa, e mexer nos menus |
| `Enter` / `Espaço` | escolher, passar o texto à frente, responder |
| `Esc` / `Backspace` | voltar atrás, sair da loja, virar costas a uma conversa |

## Como se joga

1. **Começas sem bichos e sem redes.** Sem uma coisa nem outra não se entra
   na erva alta, e sem bichos nenhum treinador luta.
2. **O Mestre Zacarias dá-te uma rede** (anda contra ele). É um treinador
   como os outros, com a caixa «dá a rede no início» marcada.
3. **Na erva alta apanhas o teu primeiro bicho.** Enquanto não tens nenhum,
   apanha-se sempre. Depois é preciso magoar o bicho um bocadinho primeiro:
   com a vida toda escapa-se sempre da rede.
4. **Quando voltas ao Mestre Zacarias, faz-te uma luta de treino.**
5. Daí em diante: mais bichos (até seis), sopas e redes na mercearia com as
   moedas das batalhas, a casa da avó para curar, e os treinadores pela
   ordem que se quiser. Ganhas a todos, és campeã(o) da feira.

O mundo que vem feito tem nove zonas, três por três, e um edifício (a
mercearia, na aldeia, com a Tia da Mercearia e o balcão lá dentro):

```
serra    montado   feira
aldeia   ribeira   pinhal
horta    praia     farol
```

## O que há para mudar

| Coisa | Onde está no código |
|---|---|
| Cada zona, desenhada com letras (20 por linha, 14 linhas) | `ZONAS` |
| Como as zonas se juntam | `MUNDO` |
| Os blocos: todos os quadrados das zonas (relva, árvores, água, mobília, areia, neve...) e o que cada um faz | `BLOCOS` |
| Os edifícios: que letra é a porta de que interior | `PORTAS` |
| O que se vende, e por quanto | `LOJA` |
| O teu boneco: a cor e as três imagens | `JOGADOR` |
| As falas, as perguntas, quem dá a rede e o boneco de cada treinador | `TREINADORES` (`falas`, `falas_depois`, `falas_rede`, `da_rede`, `imagem`) |
| Os ataques que um bicho sabe, e os que aprende a um certo nível | `BICHOS` (`ataques`, `aprende`), `ataques_de()` |
| O tamanho de cada bicho na batalha (1.0 é o normal) | `BICHOS` (`tamanho`), `tamanho_na_batalha()` |
| Onde se pode andar | `pode_andar()` |
| Quando salta um bicho da erva, e qual | `ha_batalha_na_erva()`, `escolher_bicho_selvagem()` |
| Quando se consegue apanhar um bicho | `consegue_apanhar()` |
| Quantas moedas dá uma batalha | `premio_da_batalha()` |
| O que se recebe ao comprar | `receber_compra()` |
| O que acontece a cada passo, em casa da avó, a cada frame, ao apanhar, ao responder | `ao_dar_passo()`, `ao_descansar()`, `a_cada_frame()`, `ao_apanhar()`, `ao_responder()` |
| Os desenhos | `desenhar_bloco()`, `desenho_feito()`, `desenhar_quadrado()`, `desenhar_jogador()`, `desenhar_treinador()`, `desenhar_bicho_de_costas()` |

Não há limite para as zonas nem para os edifícios: são mais entradas em
`ZONAS`. Os limites são outros: nove treinadores no mapa (um algarismo cada),
um `P` no mundo todo, uma letra livre para cada porta, e seis bichos na equipa.

### Os ataques que se aprendem

```python
"ataques": ["Bicada", "Cocoricó"],
"aprende": {"Crista em Brasa": 6, "Estalido": 9},
```

Os de `ataques` sabe-os desde o início; os de `aprende` passam a aparecer no
menu quando o bicho chega a esse nível (e o jogo avisa: «aprendeu Estalido!»).
Um bicho só sabe ataques do tipo dele ou do tipo normal.

### As falas

```python
"falas": [
    "Bom dia! As compras são ali ao balcão.",
    {"pergunta": "Ou vens para lutar comigo?",
     "respostas": {"Sim": "Então prepara-te!", "Agora não": "Faz bem."},
     "sem_luta": "Agora não"},
],
```

Um texto é uma fala, que passa com `Enter`. Uma pergunta tem as respostas à
escolha e o que o treinador diz a cada uma; `sem_luta` é a resposta que acaba
a conversa sem batalha. Para uma resposta ter consequências (uma sopa, menos
moedas), é o acontecimento `ao_responder()`.

## Na Oficina

- cada **zona** abre sozinha, com o boneco lá dentro, e anda só a criança;
- **todos os quadrados das zonas são blocos**, também os que já vinham com o
  jogo: a relva, a erva alta, as árvores, a água, a casa da avó, as paredes,
  o soalho e a mobília. Cada um abre em **Blocos**, e pode mudar de nome, de
  cor, de desenho (há um modelo de pixel art para cada um) e de regras: uma
  árvore por onde se passa, outro bloco que cura a equipa (`"faz": "cura"`)
  ou abre a loja (`"faz": "loja"`). Enquanto não tiverem imagem, o jogo
  desenha-os como sempre desenhou. A relva, o soalho, a parede e o «nada»
  não se apagam;
- os blocos de **dentro** de um edifício não são os de **fora** (a parede
  serve nos dois sítios). A ajuda de cada zona mostra só os que servem para
  essa zona, e a Oficina avisa quando um está no sítio errado;
- **O mundo** e **As portas** mostram o mundo todo visto de cima;
- **+ Novo bloco** cria um quadrado novo para as zonas: fica com uma letra
  livre, dá-se-lhe um nome, desenha-se (ou começa-se por um modelo) e diz-se
  nas caixas se se anda por cima dele, se saltam de lá bichos e se é para
  dentro dos edifícios. Depois escreve-se a letra dele nas zonas. A ajuda de
  cada zona diz os blocos que há nesse momento. É assim que se fazem outros
  sítios: uma praia de areia, uma serra de neve, um deserto de catos. Além
  dos que já vinham com o jogo há mais oito: areia, palmeira, canas, rocha,
  neve, cato, flores e ponte;
- **+ Nova zona**, **+ Novo edifício**, **+ Novo treinador**, **+ Novo
  bicho**, **+ Novo ataque**, **+ Novo tipo** criam, e o botão vermelho
  **Apagar** tira (e acerta o resto: o `MUNDO`, as `PORTAS`, os números no
  mapa, as equipas);
- **Mudar o nome** troca o nome de uma zona, um bicho, um ataque ou um tipo
  em todos os sítios onde é usado;
- um **treinador** aberto mostra-se em cenas: a dar a rede (se for ele), as
  falas e a luta, e as falas de depois. Tem a caixa **Dá a rede no início**
  e a lista **Escolher os bichos**;
- um **bicho** tem a lista **Escolher os ataques** (só os do tipo dele e os
  normais), e um ataque novo nasce sem dono;
- a Oficina traz **modelos** de pixel art para todos os bichos (de frente e
  de costas), para o teu boneco, para os treinadores e para os blocos:
  usam-se como estão, ou servem de começo;
- cada **treinador** tem a sua imagem no mapa (`imagem`), que se desenha com
  «Desenhar». Sem imagem é um boneco de formas, com a camisola da `cor_fundo`;
- um **bicho** tem as imagens **De frente** e **De costas**, e o **teu
  boneco** três (de frente, de costas, de lado): os botões por cima do código
  escolhem qual se desenha ou se troca. Quem não tiver imagem é desenhado
  com formas;
- **A loja** abre ao balcão, com moedas para experimentar;
- as funções abrem com o boneco a andar sozinho: foge dos bichos, ou
  atira-lhes a rede, ou vai responder às perguntas, conforme a função.

A Oficina avisa quando uma zona, um treinador ou uma casa da avó ficam onde
não se chega a pé, e quando nenhum treinador dá a rede (sem ela o jogo não
arranca).

## Ideias, por ordem de dificuldade

**1. Só dados.** Redesenhar uma zona. Um bloco novo: lava, gelo, um muro,
uma estrada, um piano para dentro de casa. Uma zona nova, à direita do pinhal
(que já tem lá uma saída à espera). Um ginásio: um edifício com um treinador
dentro. Falas novas, e uma pergunta com três respostas. Uma coisa nova na
loja. Desenhar o teu boneco e os bichos, de frente e de costas.

**2. Regras pequenas.** Nadar (passar na água com um bicho de água na
equipa); só bichos de água na praia (`jogador["zona"] == "praia"`); só se
apanha um bicho com menos de metade da vida; os treinadores pagarem o dobro.

**3. Coisas que o jogo não tem.**
- Um bloco que faz alguma coisa: uma sopa perdida no chão. É um bloco novo
  (em Blocos) e um `if` em `ao_dar_passo()` com a letra dele.
- Uma **Pomada** na loja que cura a equipa toda: uma linha na `LOJA` e um
  `elif` em `receber_compra()`.
- Uma resposta com consequências: quem diz à Tia da Mercearia que não quer
  lutar leva uma sopa (`ao_responder()`).
- A campeã só aceitar o desafio de quem já venceu os outros.

## Equilíbrio

Não foi afinado a sério: só foi jogado de ponta a ponta por um robô, que
apanha o primeiro bicho, compra uma rede, apanha um segundo, treina na erva
até ao nível 9 e só depois desafia os treinadores (ganhou em cerca de 400
passos, com uma derrota pelo caminho). Os números a mexer são
`NIVEL_INICIAL`, `SOPAS_NA_MOCHILA`, `MOEDAS_INICIAIS`, `SORTE_NA_ERVA`, os
preços da `LOJA`, os níveis em `TREINADORES`, e as contas de
`consegue_apanhar()` e de `premio_da_batalha()`.

## Erros previsíveis (e a pergunta a fazer)

| Sintoma | Pergunta |
|---|---|
| Não se consegue entrar na erva alta | «Já falaste com quem dá a rede? Há algum treinador com a caixa marcada?» |
| O treinador novo não aparece no mapa | «Que número é ele na lista `TREINADORES`? Esse número está escrito nalguma zona?» |
| O boneco começa num sítio estranho | «Onde está o `P`? Há só um, no mundo todo?» |
| Não se passa de uma zona para a do lado | «Há um bloco por onde se anda na borda das duas, na mesma linha? E no `MUNDO`, estão mesmo lado a lado?» |
| Uma zona aparece toda desalinhada | «Falta uma vírgula no fim de uma linha?» (Sem ela, o Python cola duas linhas numa.) |
| A porta de um edifício deixou de funcionar depois de lhe mudarem o nome | «Mudaste o nome no código, ou com o botão **Mudar o nome**?» (Só o botão acerta o `MUNDO` e as `PORTAS`.) |
| Entra-se na porta e não acontece nada | «A letra está em `PORTAS`? E está escrita lá dentro, na parede do interior?» |
| Compra-se uma coisa nova e não acontece nada | «O `receber_compra()` sabe o que fazer com esse nome? Está escrito igual ao da `LOJA`?» |
| Uma pergunta dá erro ao abrir | «Tem `"pergunta"` e `"respostas"`? As respostas estão entre `{ }`, cada uma com o que ele diz?» |
| `UnboundLocalError` em `sopas`, `redes` ou `moedas` | «Qual é a primeira linha da função? Falta o `global`?» |
| O texto de `dizer()` desaparece logo | «No mapa, a caixa dura até ao passo seguinte. Quando é que a chamas?» |
