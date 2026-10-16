# `mvp-minimo.py` — sessão 11

## Para que serve

É o ficheiro que **cada equipa copia para arrancar**. Sessenta linhas: uma
janela, um quadrado, setas, e o quadrado não sai do ecrã.

MVP quer dizer *mínimo produto viável*: a coisa mais pequena que já é alguma
coisa. Vale a pena explicar o termo — é vocabulário de indústria e eles gostam.

## Como usar na sessão

1. Cada equipa copia o ficheiro para a sua pasta com o nome do jogo:
   `sopa-espacial.py`, `fuga-da-cantina`, o que for.
2. Corre-o. Funciona. **Antes de escreverem uma linha, já têm um programa que
   corre.** Isto vale mais do que parece: o bloco de projeto começa com uma
   vitória em vez de uma página em branco.
3. Mexem nas constantes do topo. Cor, tamanho, velocidade. Cinco minutos, e
   aquilo já parece deles.

## O que dizer

> «Não há nada aqui que vocês não saibam. É a sessão 7 outra vez, sem o menu.
> A partir daqui é tudo vosso.»

## Quando passar para o `comum/esqueleto.py`

O `mvp-minimo.py` **não tem menu, nem ecrã de fim, nem reinício**. É de
propósito — na sessão 11 nada disso interessa ainda.

Assim que o jogo tiver uma maneira de acabar (normalmente na sessão 13 ou 14),
a equipa muda-se para o `comum/esqueleto.py`, que já traz tudo isso feito, e
traz para lá o que já escreveu. **Avisa-os disto na sessão 11**, senão alguém
constrói uma máquina de estados à mão e perde uma sessão inteira a fazer o que
já estava feito.

Sem falta antes da sessão 16: o `modo-feira.py` exige o menu e o reinício.

## Aviso

A tentação de acrescentar «só mais uma coisinha» a este ficheiro antes de o
dar é enorme. Não o faças. O valor dele é caber num ecrã e não meter medo.
