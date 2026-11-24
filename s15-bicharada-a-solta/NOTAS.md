# Sessão 15 — Bicharada à Solta

**É a Bicharada do s12 com um mundo por onde se anda.** Os bichos, os ataques,
os tipos e a batalha são os mesmos; o que muda é tudo o que há à volta:
um mundo de **zonas**, **edifícios** onde se entra, **treinadores** que
falam, bichos que se **apanham** com redes, e uma **loja**.
Como o s12, é uma **base** para os alunos tornarem sua, e foi feito para ser
mexido na Oficina (`python3 oficina/oficina.py`).

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

## O que muda em relação ao s12

| No s12 | Aqui |
|---|---|
| Escolhes três bichos à entrada | Começas sem nenhum, e apanha-los |
| Quatro treinadores, um atrás do outro | Os treinadores estão nas zonas (as letras `1` a `9`), e falam |
| A equipa é curada antes de cada batalha | Só a casa da avó (`H`) cura |
| Três sopas por batalha | As sopas e as redes levam-se na mochila, e compram-se |
| Perder é recomeçar do início | Acordas onde descansaste pela última vez |
| Só há batalhas contra treinadores | Há bichos à solta na erva alta (`e`): luta-se, foge-se ou apanham-se |
| Um bicho, uma imagem | Uma de frente e uma de costas (a do teu, na batalha) |

O s12 continua como estava: quem já lá tem um jogo seu não perde nada.

## O que há para mudar

| Coisa | Onde está no código |
|---|---|
| Cada zona, desenhada com letras (20 por linha, 14 linhas) | `ZONAS` |
| Como as zonas se juntam | `MUNDO` |
| Os edifícios: que letra é a porta de que interior | `PORTAS` |
| O que se vende, e por quanto | `LOJA` |
| O teu boneco: a cor e as três imagens | `JOGADOR` |
| As falas, as perguntas e quem dá a rede | `TREINADORES` (`falas`, `falas_depois`, `falas_rede`, `da_rede`) |
| Onde se pode andar | `pode_andar()` |
| Quando salta um bicho da erva, e qual | `ha_batalha_na_erva()`, `escolher_bicho_selvagem()` |
| Quando se consegue apanhar um bicho | `consegue_apanhar()` |
| Quantas moedas dá uma batalha | `premio_da_batalha()` |
| O que se recebe ao comprar | `receber_compra()` |
| O que acontece a cada passo, em casa da avó, a cada frame, ao apanhar, ao responder | `ao_dar_passo()`, `ao_descansar()`, `a_cada_frame()`, `ao_apanhar()`, `ao_responder()` |
| Os desenhos | `desenhar_quadrado()`, `desenhar_jogador()`, `desenhar_treinador()`, `desenhar_bicho_de_costas()` |

Não há limite para as zonas nem para os edifícios: são mais entradas em
`ZONAS`. Os limites são outros: nove treinadores no mapa (um algarismo cada),
um `P` no mundo todo, uma letra livre para cada porta, e seis bichos na equipa.

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
- **O mundo** e **As portas** mostram o mundo todo visto de cima;
- **+ Nova zona**, **+ Novo edifício**, **+ Novo treinador**, **+ Novo
  bicho**, **+ Novo ataque** criam, e o botão vermelho **Apagar** tira (e
  acerta o resto: o `MUNDO`, as `PORTAS`, os números no mapa, as equipas);
- um **treinador** aberto mostra-se em cenas: a dar a rede (se for ele), as
  falas e a luta, e as falas de depois. Tem a caixa **Dá a rede no início**
  e a lista **Escolher os bichos**;
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

**1. Só dados.** Redesenhar uma zona. Uma zona nova, à direita do pinhal
(que já tem lá uma saída à espera). Um ginásio: um edifício com um treinador
dentro. Falas novas, e uma pergunta com três respostas. Uma coisa nova na
loja. Desenhar o teu boneco e os bichos, de frente e de costas.

**2. Regras pequenas.** Nadar (passar na água com um bicho de água na
equipa); só bichos de água na praia (`jogador["zona"] == "praia"`); só se
apanha um bicho com menos de metade da vida; os treinadores pagarem o dobro.

**3. Coisas que o jogo não tem.**
- Uma letra nova: `s` é uma sopa perdida no chão. Precisa de um `if` em
  `ao_dar_passo()` e de um desenho em `desenhar_quadrado()`.
- Uma **Pomada** na loja que cura a equipa toda: uma linha na `LOJA` e um
  `elif` em `receber_compra()`.
- Uma resposta com consequências: quem diz à Tia da Mercearia que não quer
  lutar leva uma sopa (`ao_responder()`).
- A campeã só aceitar o desafio de quem já venceu os outros.

## Equilíbrio

Não foi afinado como o s12: só foi jogado de ponta a ponta por um robô, que
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
| Não se passa de uma zona para a do lado | «Há relva na borda das duas, na mesma linha? E no `MUNDO`, estão mesmo lado a lado?» |
| Uma zona aparece toda desalinhada | «Falta uma vírgula no fim de uma linha?» (Sem ela, o Python cola duas linhas numa.) |
| Entra-se na porta e não acontece nada | «A letra está em `PORTAS`? E está escrita lá dentro, na parede do interior?» |
| Compra-se uma coisa nova e não acontece nada | «O `receber_compra()` sabe o que fazer com esse nome? Está escrito igual ao da `LOJA`?» |
| Uma pergunta dá erro ao abrir | «Tem `"pergunta"` e `"respostas"`? As respostas estão entre `{ }`, cada uma com o que ele diz?» |
| `UnboundLocalError` em `sopas`, `redes` ou `moedas` | «Qual é a primeira linha da função? Falta o `global`?» |
| O texto de `dizer()` desaparece logo | «No mapa, a caixa dura até ao passo seguinte. Quando é que a chamas?» |
