# `hud.py` — sessão 13

## O que é

HUD é a informação desenhada **por cima** do jogo: pontuação, vidas, nível,
tempo. Não faz parte do mundo do jogo — faz parte do ecrã.

O ficheiro corre sem jogo nenhum, e mexe-se nele com o teclado (`P` pontos,
`V` perder uma vida, `N` nível), para se poder experimentar sem ter de jogar.

## As três regras

1. **O HUD desenha-se sempre em último.** Se o desenhares antes do jogo, fica
   tapado por ele. Aponta para o sítio onde ele está no ficheiro: depois de
   tudo, mesmo antes do `flip`.
2. **O que é mais importante fica no canto superior esquerdo.** É para lá que
   os olhos vão primeiro.
3. **Números passam por `str()`.** Senão é `TypeError`. Já sabem isto da
   sessão 8, mas vão esquecer-se.

## O que vale a pena mostrar

**Símbolos em vez de números.** As vidas estão desenhadas como três
quadradinhos vermelhos, não como `Vidas: 3`. A meio de um jogo lê-se muito mais
depressa — vê-se sem ler.

> «Quantas vidas tenho? Com o número, tens de ler. Com os quadrados, vês.»

**A barra.** São dois retângulos: um escuro por baixo, que é o máximo, e um
colorido por cima, que é o que resta. É a receita de qualquer barra de vida,
de energia ou de progresso, e serve para tudo.

## Erros previsíveis

| Sintoma | A pergunta a fazer |
|---|---|
| O texto não aparece | «Em que ordem é que desenhas as coisas? O que é que fica por cima de quê?» |
| `TypeError: ... str ... int` | «O `render` quer texto. O que é que a pontuação é?» |
| O texto pisca ou fica com rasto | «Onde está o `ecra.fill()` em relação ao teu texto?» |
| A barra desaparece quando a vida chega a zero | «Que largura tem a barra quando o valor é zero? Isso desenha alguma coisa?» |
| O HUD tapa o jogo | «Onde é que o jogador precisa de ver? Que cantos é que estão sempre livres?» |
