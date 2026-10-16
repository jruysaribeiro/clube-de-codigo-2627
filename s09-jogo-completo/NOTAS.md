# Sessão 9 — Jogo completo em miniatura

**Estas notas são diferentes das outras.** Não há bronze, prata e ouro: hoje
os pares constroem um jogo pequeno **do princípio ao fim**. O que aqui está
não é uma lista de conceitos novos — é um **plano de gestão de tempo**, porque
é isso que decide se a sessão resulta.

## O que está nesta pasta

Três jogos completos, curtos e legíveis. Não são para distribuir aos alunos no
início: são para **ti** estudares antes, e para mostrares um de cada vez.

| Ficheiro | O jogo | O que demonstra |
|---|---|---|
| `modelo-perseguicao.py` | Um bicho persegue-te. Aguenta o máximo de tempo | Perseguição, pontuação por tempo sobrevivido |
| `modelo-apanhar.py` | Apanha 10 moedas em 30 segundos | Lista de objetos, relógio, condição de vitória **e** de derrota |
| `modelo-esquivar.py` | Caem pedras. Não lhes toques | Objetos que caem e voltam ao topo, movimento só horizontal |

**Os três têm a mesma forma de propósito.** Mesmas cinco palavras, mesmos
nomes (`jogador`, `pontuacao`, `estado`, `comecar_jogo`), mesma ordem. Quem
leu um lê os outros dois em dois minutos. Isso não é preguiça de quem
escreveu — é o objetivo pedagógico: **eles têm de conseguir ler os três e
reconhecer o mesmo esqueleto por baixo**.

Todos têm: movimento, colisão, pontuação, ecrã inicial, ecrã de fim, reinício
com `R`, e um som. Todos correm sem assets nenhuns.

### Uma coisa nova, e só uma

```python
jogador.clamp_ip(ecra.get_rect())
```
`clamp_ip` puxa um retângulo para dentro de outro. É a versão curta dos quatro
`if` que escreveram na sessão 7. Menciona-a de passagem — vale mais como
prémio («aquilo que fizeste à mão já existia feito») do que como matéria nova.

## O que o facilitador precisa de perceber

Hoje não há conceito novo nenhum. **A dificuldade da sessão é toda de
arquitetura e de tempo**, e é a primeira vez no ano que eles a enfrentam.

**Um jogo é um esqueleto mais uma ideia.** Diz isto ao início, com estas
palavras:
> «Todos os jogos que vos vou mostrar têm exatamente o mesmo ficheiro por
> baixo. O que muda são umas vinte linhas. Vocês já sabem escrever essas vinte
> linhas — o que falta hoje é decidir *quais*.»

**Escolher pequeno é uma competência, não uma desistência.** Este é o ensino
mais importante do dia, e vai contra tudo o que os adolescentes querem fazer:
> «Um jogo de trinta segundos que funciona é infinitamente melhor do que um
> jogo enorme que não chega a arrancar. Hoje o objetivo não é o vosso melhor
> jogo. É o vosso **primeiro jogo acabado**.»

**Acabado quer dizer:** arranca no menu, joga-se, acaba, e volta a começar com
`R` sem fechar a janela. Escreve isso no quadro como definição de pronto.

## O plano da sessão, minuto a minuto

Esta é a parte que interessa. **Segue o relógio, não a inspiração.**

### 0–10 min · Mostrar os três modelos

Corre os três, **um de cada vez, dois ou três minutos cada**. Joga-os no
projetor, não os expliques. Só no fim abre um ficheiro — um só — e mostra que
tem 145 linhas, das quais 120 são o esqueleto que eles já conhecem.

> «Já viram este ficheiro. É o vosso. Muda um bocadinho no meio.»

**Não abras os três ficheiros.** Abrir os três consome quinze minutos e passa
a mensagem errada: que hoje é dia de ler código.

### 10–20 min · Escolher, e escrever no papel

**Cada par escolhe um dos três modelos como ponto de partida.** Não «inventem
um jogo». Escolham um dos três. Quem quiser fugir aos três tem de te
convencer em trinta segundos — e a pergunta que os faz voltar à terra é:
«consegues descrever-mo numa frase?»

Depois, **num papel** (papel mesmo, não no editor), cada par escreve três
linhas:

1. **O que o jogador faz** — «foge do bicho», «apanha moedas».
2. **Como se ganha, ou como se perde** — tem de haver pelo menos uma das duas.
3. **Uma coisa só, que torne o jogo diferente do modelo.** Uma. Não três.

Esse papel fica em cima da mesa até ao fim da sessão. É a régua contra a qual
se mede tudo o resto, e é a ele que apontas quando alguém se perder.

> **Vais ter de negociar.** Alguém vai querer um jogo de plataformas com
> gravidade, inventário e chefes finais. A resposta não é «não dá». É: «isso é
> o projeto do 3.º período, e vais tê-lo. Hoje o que interessa é escolher uma
> peça disso que caiba em cinquenta minutos. Qual delas?»

### 20–60 min · Construir

Copiam o modelo escolhido para um ficheiro novo com o nome deles e começam a
mexer. Regras de sala:

- **Correr o programa a cada três ou quatro linhas.** Diz isto alto de vez em
  quando. Quem escreve vinte linhas antes de correr passa vinte minutos a
  procurar um erro que apanharia em três.
- **Constantes primeiro.** Mudar `VELOCIDADE`, `QUANTAS_MOEDAS`, `SEGUNDOS` e
  as cores dá um jogo que parece deles em cinco minutos, e compra a moral
  necessária para o resto.
- **Uma coisa de cada vez.** Fazer, correr, ver funcionar, e só depois começar
  a seguinte.

O teu trabalho aqui é circular e fazer perguntas. Não toques no teclado.

### 60 min · FEATURE FREEZE ← *o momento mais importante da sessão*

Aos 60 minutos, **pára a sala em voz alta**. Sem exceções, sem «só mais uma
coisinha».

> «Congelamento. A partir de agora **ninguém acrescenta nada de novo**. Nos
> próximos vinte minutos só se corrigem coisas partidas e se acaba o que já
> está começado. Se tens uma ideia boa, escreve-a no papel para a próxima
> sessão.»

**Porque é que isto não é negociável:** sem um congelamento, metade da turma
acaba a sessão com o jogo pior do que estava aos 55 minutos, porque começou
uma funcionalidade nova aos 75 e não a acabou. Sair da sala com um jogo
partido depois de o ter tido a funcionar é a experiência mais desmoralizante
que há, e é completamente evitável.

Escreve **FEATURE FREEZE 60'** no quadro logo no início da sessão, com a hora
concreta a que vai acontecer. Assim ninguém é apanhado de surpresa, e a partir
dos 50 minutos começam a gerir-se sozinhos — que é a competência que aqui se
está mesmo a ensinar.

> Diz-lhes que isto tem nome e que é o que se faz na indústria a sério. Um
> adolescente aceita muito melhor uma regra que existe no mundo real do que
> uma regra da sala.

### 60–75 min · Acabar e polir

Só três coisas, por esta ordem:

1. **Corrigir o que está partido.**
2. **Confirmar a lista de "acabado":** menu → jogo → fim → `R` → jogo. Manda-os
   percorrer o ciclo completo três vezes seguidas. É onde aparecem os bugs de
   reinício, e são sempre a mesma coisa: uma variável que o `comecar_jogo()`
   não repõe a zeros.
3. **Título e texto do menu.** Dois minutos, e o jogo passa a parecer um jogo.

### 75–90 min · Jogar os jogos uns dos outros

**Não cortes isto por falta de tempo.** É a parte que faz a sessão valer, e é
o primeiro ensaio geral do Demo Day.

Cada par joga o jogo do par do lado, durante dois minutos, e diz **uma** coisa
que gostou e **uma** pergunta. Uma pergunta, não uma crítica.

Repara em quem vê alguém a jogar o seu jogo pela primeira vez. Vais ver a
mesma reação em toda a gente: descobrem imediatamente três coisas que estão
mal e que nunca tinham notado. Isso é *playtesting*, e não se ensina — vive-se.

## Erros que os alunos vão cometer

| Sintoma | Causa | A pergunta a fazer |
|---|---|---|
| Ao carregar em `R` o jogo recomeça com a pontuação antiga, ou com os inimigos onde estavam | Uma variável não é reposta dentro do `comecar_jogo()` | «O que é que tem de voltar ao princípio quando se recomeça? Está tudo dentro do `comecar_jogo()`?» |
| `UnboundLocalError`, ou o valor não muda fora da função | Falta o nome na linha do `global` | «Essa variável nasce dentro ou fora da função? O que é que a linha do `global` tem de dizer?» |
| O jogo acaba mal começa | A condição de fim já é verdadeira no primeiro ciclo, ou o inimigo nasce em cima do jogador | «Onde é que o inimigo nasce? E o jogador? Já estão a tocar-se na primeira volta?» |
| A pontuação sobe aos milhares | Colisão sem consequência (o mesmo da sessão 8) | «Enquanto estás em cima dele, quantas vezes é que essa pergunta é feita?» |
| Metade dos objetos nunca é apanhada | `remove()` durante o `for` (o mesmo da sessão 8) | «Lembras-te da fila? Qual é a receita que está no quadro?» |
| O jogo fica impossível ao fim de dez segundos | A velocidade cresce sem limite | «Qual é a maior velocidade a que isto ainda dá para jogar? Como é que a impedes de passar daí?» |
| Ecrã preto (outra vez) | Falta o `flip`, ou o `fill` está depois de desenhar | «As cinco palavras, por ordem. Quais é que tens?» |
| O jogo funcionava aos 55 min e está partido aos 80 | Começou uma funcionalidade nova depois do congelamento | «A que horas é que isto funcionava? O que mudaste desde então? Consegues desfazer?» |
| Nada funciona e não se sabe porquê | Escreveu trinta linhas sem correr uma única vez | «Quando é que este programa correu bem pela última vez? Vamos voltar a esse ponto.» |
| O objeto sai do ecrã e nunca mais volta | Falta reaparecer do outro lado | «Depois de ele passar a borda, quem é que o traz de volta? Onde é que isso teria de estar escrito?» |
| Copiou dois modelos para o mesmo ficheiro e nada corre | Duas máquinas de estado e dois ciclos no mesmo ficheiro | «Quantos `while a_correr` tens nesse ficheiro? Quantos é que devias ter?» |

## Aviso de âmbito

**Não foi retirado nada, mas há um risco de tempo que convém teres presente.**

O plano acima dá **quarenta minutos** de construção, e isso chega para
adaptar um modelo — não para escrever um jogo de raiz. Se um par insistir em
começar do zero, deixa, mas avisa-o no início de que quase de certeza não
acaba. Um par que não acabe hoje sai desmoralizado logo antes do bloco de
projeto, que é o pior momento possível do ano para isso acontecer.

**Se a turma estiver claramente atrasada aos 45 minutos**, corta o
*playtesting* dos 75–90 para dez minutos e usa os primeiros cinco para acabar.
Se estiver muito atrasada, antecipa o congelamento para os 50. É preferível um
jogo mais pequeno e acabado.

**Se sobrar tempo**, não deixes acrescentar funcionalidades depois do
congelamento. Manda-os antes ao `projeto/juice.py`: o ecrã a tremer e o objeto
a crescer são cinco linhas cada, não podem partir nada, e transformam
completamente a sensação do jogo. É a melhor coisa que se pode fazer com
quinze minutos a mais.

## Critério de sucesso

Aos 90 minutos:

- [ ] **Todos os pares têm um jogo que se joga do princípio ao fim** e que
      recomeça com `R` sem fechar a janela. É o único critério que conta a
      sério nesta sessão.
- [ ] Todos os jogos têm um ecrã inicial com um título escrito por eles. Não é
      cosmética: é o que faz aquilo deixar de ser "o exercício" e passar a ser
      "o meu jogo".
- [ ] Toda a gente jogou o jogo de pelo menos outro par.
- [ ] Ninguém saiu da sala com o jogo pior do que o tinha aos 60 minutos.

**O sinal mais forte da sessão:** um par que decide **cortar** uma ideia
sozinho, por não caber. Isso não é desistência — é a competência central do
bloco de projeto, e um par que a tenha hoje vai acabar em maio.

**Sinal de alarme:** um par ainda a decidir o que fazer aos 30 minutos. Não os
deixes lá. Escolhe tu: «vais fazer o de apanhar, com naves em vez de moedas.
Começa.» Uma escolha imposta e a funcionar vale mais do que uma escolha
perfeita que nunca chega a ser feita.

---

## Nota para o facilitador, antes da sessão 10

Guarda estes três modelos à mão. No bloco de projeto vais dizer «vai ver como
está feito no `modelo-esquivar.py`» umas vinte vezes, e cada uma dessas vezes
é uma resposta que não deste — que é exatamente como se quer.
