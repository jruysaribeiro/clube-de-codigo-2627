# O AJUDANTE
# Leva as perguntas da Oficina a um modelo de linguagem que corre noutro
# computador da sala (um dos computadores com placa grafica, com o Ollama
# aberto a rede: ver instalar-servidor-windows.bat).
#
# Os enderecos desses computadores estao em oficina/servidores.txt. Havendo
# varios, cada pergunta vai para um diferente, a vez; se esse nao atender, ou
# estiver ocupado com a pergunta de outro aluno, passa-se ao seguinte. Sem enderecos nao ha ajudante, e a Oficina funciona
# como sempre.
#
# So usa o que ja vem com o Python.
#
# Este ficheiro tambem se corre a mao, do portatil do professor, para tratar
# dos servidores todos de uma vez:
#
#     python3 oficina/ajudante.py acordar     antes da sessao: poe o modelo na
#                                             memoria de cada um, para ninguem
#                                             esperar pela primeira resposta
#     python3 oficina/ajudante.py adormecer   no fim: tira o modelo da memoria,
#                                             e a placa grafica fica livre
#     python3 oficina/ajudante.py ver         so mostra como estao

import http.client
import json
import os
import queue
import random
import re
import socket
import sys
import threading
import time
from urllib.parse import urlparse

AQUI = os.path.dirname(os.path.abspath(__file__))
FICHEIRO = os.path.join(AQUI, "servidores.txt")

PORTA = 11434             # a porta do Ollama
LIGAR = 3                 # segundos para um servidor atender
ESPERAR = 180             # segundos a espera da resposta (a primeira demora: o modelo vai para a memoria)
CARREGAR = 300            # segundos que um servidor pode levar a por o modelo na memoria
DESCANSO = 30             # segundos sem voltar a tentar um servidor que falhou
PRESSA = 4                # segundos sem comecar a escrever: esta ocupado, pergunta-se tambem a outro
VALIDADE = 15             # segundos que vale a ultima vez que se viu quem esta ligado
RESPOSTA_MAXIMA = 3000    # tokens: trava um modelo que nao se cala
CODIGO_MAXIMO = 6000      # letras do codigo que se mandam ao modelo
TEXTO_MAXIMO = 1500       # letras de cada pergunta, erro ou resposta antiga
CONVERSA_MAXIMA = 6       # mensagens anteriores que o modelo ainda ve

INSTRUCOES = """És o ajudante da Oficina do Clube de Código. Falas com alunos dos 12 aos 18 anos que estão a mudar um jogo feito em Python com pygame. Responde sempre em português de Portugal, a tratar por tu, em poucas frases e com palavras simples.

Regras:
1. O aluno vê só um bocado do ficheiro do jogo. O resto do jogo existe e funciona: fala só desse bocado.
2. Quando o aluno só quer perceber (o que faz isto, o que quer dizer aquilo), explica e não mudes nada. Para mostrares uma linha de exemplo usa um bloco ```python.
3. Quando o aluno te pede para mudar, acrescentar ou corrigir alguma coisa, ou quando há um erro que sabes corrigir: diz primeiro, em uma ou duas frases, o que vais mudar e porquê. Depois escreve o bocado INTEIRO, já com a mudança, dentro de um bloco que começa por ```oficina e acaba em ```. O aluno carrega no botão Aplicar e o teu bloco fica no lugar do código dele, por isso:
   - copia todas as outras linhas tal e qual, com os mesmos espaços no início, as mesmas vírgulas e os mesmos comentários;
   - muda só o que foi pedido;
   - escreve um único bloco ```oficina por resposta, e nunca só uma parte do bocado lá dentro;
   - se o bocado for uma função, a primeira linha (def ...) fica igual, usa só o que o jogo já tem e nunca escrevas import;
   - se o bocado tiver um mapa feito de linhas de letras, todas as linhas têm de continuar com o mesmo número de letras: troca uma letra por outra, sem acrescentar nem tirar nenhuma.
4. Se houver um erro, diz em que linha está e o que quer dizer.
5. Se não souberes, ou o pedido não for claro, di-lo ou faz uma pergunta curta. Não inventes.
6. Só ajudas com o jogo e com programação. Se te pedirem outra coisa, diz com simpatia que aqui só tratas do jogo."""


# Quando o bocado aberto e um mapa de letras, o modelo recebe estas
# instrucoes em vez das de cima. Pedir-lhe o mapa todo outra vez nao da: um
# modelo pequeno engana-se a contar as letras de cada linha, ou devolve o
# mapa igual. Assim ve o mapa com as linhas e as colunas numeradas e
# responde com ORDENS pequenas, que a Oficina aplica (ver responder).
INSTRUCOES_DO_MAPA = """És o ajudante da Oficina do Clube de Código. Falas com alunos dos 12 aos 18 anos que estão a mudar o mapa de um jogo. Responde sempre em português de Portugal, a tratar por tu, em poucas frases e com palavras simples.

O mapa é uma grelha de letras: cada letra é um quadrado. Vês o mapa com as linhas e as colunas numeradas: a linha 1 é a de cima, a coluna 1 é a da esquerda.

Regras:
1. Quando o aluno só quer perceber (o que quer dizer uma letra, como se faz uma coisa), explica e não escrevas ordens.
2. Quando o aluno pede uma mudança ao mapa, NÃO escrevas o mapa outra vez. Diz numa frase o que vais fazer e depois escreve as ordens dentro de um bloco ```mapa, uma por linha, exatamente com estas palavras:
linha 6, colunas 9 a 13: ~
linhas 6 a 8, colunas 9 a 13: ~
linha 3, coluna 5: H
   Cada ordem pinta um retângulo com UMA letra. As ordens fazem-se por ordem: a de baixo pinta por cima da de cima. É a Oficina que faz as mudanças no mapa.
3. Usa só letras que o mapa já conhece (estão explicadas mais abaixo). O que não tem letra própria faz-se com as que há: uma casa, um balcão ou um muro são paredes; uma ponte é relva por cima da água; uma ilha é relva no meio da água.
4. Faz uma mudança que se veja bem: um lago ou um rio ocupam várias linhas e várias colunas.
5. Não apagues a partida, os números nem as portas, a não ser que o aluno peça.
6. Na dúvida, não faças perguntas: faz a mudança que te parecer melhor e diz o que fizeste. O aluno vê o resultado e pode desfazer. Só perguntas se não fizeres mesmo ideia do que ele quer.
7. Só ajudas com o jogo e com programação. Se te pedirem outra coisa, diz com simpatia que aqui só tratas do jogo."""

# No editor de desenho, o aluno descreve um boneco e o modelo desenha-o com
# ordens de pintar numa grelha de 16 por 16 (ver desenho). Um modelo de texto
# deste tamanho desenha mal: sai um rascunho para o aluno retocar.
CORES_DO_DESENHO = {
    "vermelho": "#e03c3c", "laranja": "#ff8a3c", "amarelo": "#f0c846", "verde": "#5fd07a",
    "verde-escuro": "#2e8b57", "azul": "#3c5adc", "azul-claro": "#46b4e6", "roxo": "#9b5ade",
    "rosa": "#ff78b4", "castanho": "#784628", "bege": "#ffd2aa", "preto": "#000000",
    "branco": "#ffffff", "cinzento": "#9a9ab4", "nada": None,
}
# Outros nomes que o modelo da as mesmas cores.
OUTROS_NOMES = {"marrom": "castanho", "castanho-escuro": "castanho", "cinza": "cinzento", "cinzento-claro": "cinzento",
                "azul-escuro": "azul", "verde-claro": "verde", "cor-de-rosa": "rosa", "violeta": "roxo",
                "lilás": "roxo", "creme": "bege", "cor-de-pele": "bege", "dourado": "amarelo",
                "transparente": "nada", "vazio": "nada"}
LADO_DO_DESENHO = 16

INSTRUCOES_DO_DESENHO = """És o ajudante de desenho da Oficina do Clube de Código. Desenhas bonecos pequenos em pixel art para um jogo, numa grelha de 16 linhas por 16 colunas: a linha 1 é a de cima, a coluna 1 é a da esquerda. A grelha começa vazia (transparente).

Responde com UMA frase curta, em português de Portugal, a dizer o que desenhaste, e depois as ordens de pintar dentro de um bloco ```desenho, uma por linha, exatamente com estas palavras:
linhas 5 a 12, colunas 4 a 13: vermelho
linha 7, coluna 6: branco
Cada ordem pinta um retângulo CHEIO com UMA cor. As ordens fazem-se por ordem: a de baixo pinta por cima da de cima.
As cores que há: """ + ", ".join(CORES_DO_DESENHO) + """. ("nada" apaga: usa-o só para arredondar os cantos, nunca no meio do boneco.)

Como desenhar:
1. Primeiro o corpo: um ou dois retângulos grandes e cheios, ao centro, que ocupem a maior parte da grelha.
2. Depois as partes que saem do corpo: cabeça, patas, asas, cauda, orelhas, com retângulos mais pequenos.
3. Por cima, os pormenores: dois olhos (um quadradinho branco com um preto), boca ou bico, riscas.
4. Usa entre 12 e 25 ordens, e pelo menos duas cores.
Visto de costas não se veem os olhos nem a boca.

Um exemplo, para «um sapo verde»:
```desenho
linhas 6 a 13, colunas 3 a 14: verde
linha 6, coluna 3: nada
linha 6, coluna 14: nada
linhas 3 a 6, colunas 4 a 7: verde
linhas 3 a 6, colunas 10 a 13: verde
linhas 4 a 5, colunas 5 a 6: branco
linhas 4 a 5, colunas 11 a 12: branco
linha 5, coluna 6: preto
linha 5, coluna 11: preto
linha 10, colunas 6 a 11: verde-escuro
linhas 11 a 12, colunas 6 a 11: bege
linhas 14 a 15, colunas 3 a 5: verde-escuro
linhas 14 a 15, colunas 12 a 14: verde-escuro
```
Desenha sempre o que o aluno pedir, mesmo que seja difícil: não faças perguntas."""

# Uma linha de um mapa, no codigo: espacos, o texto entre aspas e a virgula.
LINHA_DE_MAPA = re.compile(r'^(\s*)"([^"\\]*)"(,?)\s*$')
# Uma ordem do modelo: "linhas 6 a 8, colunas 9 a 13: ~"
ORDEM = re.compile(r"linhas?\s+(\d+)(?:\s*(?:a|até|ate|-)\s*(\d+))?\s*,?\s*(?:e\s+)?colunas?\s+(\d+)"
                   r"(?:\s*(?:a|até|ate|-)\s*(\d+))?\s*[:=]\s*(.+)$", re.IGNORECASE)


class Indisponivel(Exception):
    # Nao ha ajudante, ou nenhum servidor respondeu. O texto e para o aluno.
    pass


class Calado(Exception):
    # Um servidor que comecou a responder e se calou sem dizer nada.
    pass


def endereco_certo(texto):
    # "192.168.1.50" -> "http://192.168.1.50:11434"
    texto = texto.strip().rstrip("/")
    if "://" not in texto:
        texto = "http://" + texto
    url = urlparse(texto)
    if not url.hostname:
        return None
    return url.scheme + "://" + url.hostname + ":" + str(url.port or PORTA)


def ler_ficheiro(caminho=FICHEIRO):
    # Devolve (enderecos, modelo). Um endereco por linha; "modelo = nome"
    # obriga a usar esse modelo; o que vem depois de # nao conta.
    enderecos = []
    modelo = None
    try:
        with open(caminho, encoding="utf-8") as f:
            linhas = f.read().splitlines()
    except OSError:
        return enderecos, modelo
    for linha in linhas:
        linha = linha.split("#")[0].strip()
        if linha == "":
            continue
        nome, igual, valor = linha.partition("=")
        if igual and nome.strip().lower() == "modelo":
            modelo = valor.strip() or None
            continue
        try:
            endereco = endereco_certo(linha)
        except ValueError:
            endereco = None
        if endereco and endereco not in enderecos:
            enderecos.append(endereco)
    return enderecos, modelo


def cortar(texto, maximo):
    texto = str(texto or "").strip()
    if len(texto) > maximo:
        texto = texto[:maximo] + "\n[...]"
    return texto


def grelha(codigo):
    # As linhas de mapa de um bocado de codigo: [(numero da linha no bocado,
    # espacos antes, as letras, a virgula), ...]. Vem vazia se o bocado nao e
    # um mapa: num mapa quase todas as linhas sao letras entre aspas, e
    # nenhuma tem palavras separadas por espacos (isso sao frases).
    linhas = str(codigo or "").replace("\r\n", "\n").split("\n")
    filas = []
    for numero, linha in enumerate(linhas):
        acerto = LINHA_DE_MAPA.match(linha)
        if acerto:
            filas.append((numero, acerto.group(1), acerto.group(2), acerto.group(3)))
    com_texto = [linha for linha in linhas if linha.strip() != ""]
    if len(filas) < 3 or len(filas) < len(com_texto) - 3:
        return []
    for _, _, letras, _ in filas:
        if len(letras) < 4 or re.search(r"[A-Za-zÀ-ÿ]{2,} [A-Za-zÀ-ÿ]{2,}", letras.strip()):
            return []
    return filas


def mapa_numerado(filas):
    # O mapa como o modelo o ve, com uma regua por cima e o numero de cada linha.
    largura = max(len(letras) for _, _, letras, _ in filas)
    dezenas = "".join(str(coluna // 10 % 10) if coluna >= 10 else " " for coluna in range(1, largura + 1))
    unidades = "".join(str(coluna % 10) for coluna in range(1, largura + 1))
    texto = ["colunas:   " + dezenas, "           " + unidades]
    for numero, (_, _, letras, _) in enumerate(filas, 1):
        texto.append("linha %2d:  %s" % (numero, letras))
    return "\n".join(texto)


def aplicar_ordens(codigo, resposta):
    # Faz no mapa as ordens que o modelo escreveu. Devolve (o codigo novo,
    # quantos quadrados mudaram). As linhas nunca mudam de tamanho.
    linhas = str(codigo or "").replace("\r\n", "\n").split("\n")
    filas = grelha(codigo)
    letras = [list(fila[2]) for fila in filas]
    antes = [list(fila) for fila in letras]
    for texto in resposta.split("\n"):
        ordem = ORDEM.search(texto.strip())
        if not ordem:
            continue
        linha1 = int(ordem.group(1))
        linha2 = int(ordem.group(2) or linha1)
        coluna1 = int(ordem.group(3))
        coluna2 = int(ordem.group(4) or coluna1)
        letra = ordem.group(5).strip().strip("`").strip()
        if len(letra) >= 3 and letra[0] in "\"'" and letra[-1] in "\"'":
            letra = letra[1:-1]
        if letra.lower() in ("espaço", "espaco", "um espaço", "nada"):
            letra = " "
        if len(letra) != 1 or letra in "\"\\":
            continue
        for linha in range(min(linha1, linha2), max(linha1, linha2) + 1):
            for coluna in range(min(coluna1, coluna2), max(coluna1, coluna2) + 1):
                if 1 <= linha <= len(letras) and 1 <= coluna <= len(letras[linha - 1]):
                    letras[linha - 1][coluna - 1] = letra
    mudados = sum(1 for a, d in zip(antes, letras) for x, y in zip(a, d) if x != y)
    for (numero, espacos, _, virgula), fila in zip(filas, letras):
        linhas[numero] = espacos + '"' + "".join(fila) + '"' + virgula
    return "\n".join(linhas), mudados


def responder(pedacos, codigo):
    # A resposta do modelo, tal como vai para a pagina. Quase sempre e a que
    # ele escreve. Num mapa, as ordens dele nao se mostram: aplicam-se, e no
    # lugar delas vai o mapa ja mudado, num bloco ```oficina (o mesmo que o
    # modelo escreve nas outras coisas, com o botao Aplicar).
    if not grelha(codigo):
        yield from pedacos
        return
    tudo = ""
    enviado = 0
    for pedaco in pedacos:
        tudo = tudo + pedaco
        # Vai-se mostrando a conversa ate comecarem as ordens (e so linhas
        # inteiras, para nao mostrar o inicio de uma ordem).
        corte = re.search(r"```|^\s*linhas?\s+\d", tudo, re.MULTILINE | re.IGNORECASE)
        ate = corte.start() if corte else tudo.rfind("\n") + 1
        if ate > enviado:
            yield tudo[enviado:ate]
            enviado = ate
    corte = re.search(r"```|^\s*linhas?\s+\d", tudo, re.MULTILINE | re.IGNORECASE)
    if corte is None:
        yield tudo[enviado:]         # so conversa: nao havia ordens
        return
    novo, mudados = aplicar_ordens(codigo, tudo[corte.start():])
    if mudados == 0:
        yield ("\n\nNão consegui mudar nada no mapa com este pedido. Diz-me onde queres a mudança, "
               "por exemplo: «um lago nas linhas 5 a 8, a meio».")
        return
    yield "\n\n```oficina\n" + novo + "\n```\n"


def mensagens_do_desenho(pedido):
    return [{"role": "system", "content": INSTRUCOES_DO_DESENHO},
            {"role": "user", "content": cortar(pedido, 600)}]


def desenho(resposta):
    # O que o modelo desenhou: (as cores dos 16x16 quadradinhos, linha a
    # linha, cada uma "#rrggbb" ou None; a frase dele; quantas ordens fez).
    lado = LADO_DO_DESENHO
    cores = [None] * (lado * lado)
    ordens = 0
    for texto in resposta.split("\n"):
        ordem = ORDEM.search(texto.strip())
        if not ordem:
            continue
        nome = ordem.group(5).strip().strip("`.,;").lower().replace(" ", "-")
        nome = OUTROS_NOMES.get(nome, nome)
        if nome not in CORES_DO_DESENHO:
            continue
        ordens = ordens + 1
        linha1 = int(ordem.group(1))
        linha2 = int(ordem.group(2) or linha1)
        coluna1 = int(ordem.group(3))
        coluna2 = int(ordem.group(4) or coluna1)
        for linha in range(min(linha1, linha2), max(linha1, linha2) + 1):
            for coluna in range(min(coluna1, coluna2), max(coluna1, coluna2) + 1):
                if 1 <= linha <= lado and 1 <= coluna <= lado:
                    cores[(linha - 1) * lado + coluna - 1] = CORES_DO_DESENHO[nome]
    frase = re.split(r"```|^\s*linhas?\s+\d", resposta, maxsplit=1, flags=re.MULTILINE | re.IGNORECASE)[0]
    return cores, " ".join(frase.split())[:200], ordens


def sem_blocos(texto):
    # Uma resposta antiga sem os blocos de codigo: num mapa, ver os mapas que
    # ja escreveu levava o modelo a escrever outro, em vez das ordens.
    return re.sub(r"```.*?(```|$)", "(aqui estava o mapa mudado)", str(texto or ""), flags=re.DOTALL)


def mensagens(jogo, titulo, ajuda, codigo, erro, linha, conversa, pergunta):
    # O que o modelo recebe: as instrucoes, o bocado que o aluno tem aberto
    # (como esta agora no editor), o erro que a Oficina lhe mostra, a
    # conversa ate aqui e a pergunta.
    linhas = str(codigo or "").replace("\r\n", "\n").split("\n")
    filas = grelha(codigo)
    contexto = [INSTRUCOES_DO_MAPA if filas else INSTRUCOES, "",
                "O jogo chama-se " + str(jogo) + ". O aluno tem aberto este bocado: " + str(titulo) + "."]
    if ajuda:
        contexto += ["", "O que quer dizer cada coisa desse bocado:", cortar(ajuda, 3000)]
    if filas:
        contexto += ["", "O mapa, como o aluno o tem agora:", mapa_numerado(filas)]
    else:
        contexto += ["", "O código, como o aluno o tem agora:", "```python",
                     cortar("\n".join(linhas), CODIGO_MAXIMO), "```"]
    if erro:
        contexto += ["", "A Oficina está a mostrar este aviso ao aluno:", cortar(erro, TEXTO_MAXIMO)]
        if isinstance(linha, int) and 1 <= linha <= len(linhas):
            contexto += ["A linha " + str(linha) + " é esta: " + linhas[linha - 1].strip()]
    else:
        contexto += ["", "Neste momento o código não dá erro nenhum."]

    resposta = [{"role": "system", "content": "\n".join(contexto)}]
    anteriores = conversa if isinstance(conversa, list) else []
    for fala in anteriores[-CONVERSA_MAXIMA:]:
        if isinstance(fala, dict) and fala.get("texto"):
            papel = "assistant" if fala.get("quem") == "ajudante" else "user"
            texto = sem_blocos(fala["texto"]) if filas and papel == "assistant" else fala["texto"]
            resposta.append({"role": papel, "content": cortar(texto, TEXTO_MAXIMO)})
    resposta.append({"role": "user", "content": cortar(pergunta, TEXTO_MAXIMO)})
    return resposta


class Ajudante:

    def __init__(self, enderecos=(), modelo=None):
        self.servidores = list(enderecos)
        self.modelo = modelo
        self.tranca = threading.Lock()
        # Cada portatil comeca num servidor ao calhas: assim a sala
        # espalha-se pelos servidores todos.
        self.vez = random.randrange(len(self.servidores)) if self.servidores else 0
        self.de_castigo = {}      # servidor -> hora ate a qual nao vale a pena tentar
        self.modelos = {}         # servidor -> modelo que ele tem
        self.ligados = None       # quantos servidores atenderam da ultima vez (None: ainda nao se viu)
        self.visto = 0            # quando foi isso
        self.a_ver = False

    def ha(self):
        return len(self.servidores) > 0

    def quantos_ligados(self):
        # Quantos servidores estao a atender, para a luzinha da pagina. Ver
        # isso pode demorar uns segundos (um computador desligado nao
        # responde logo), por isso faz-se a parte: aqui devolve-se o que se
        # viu da ultima vez e, se ja for velho, manda-se ver outra vez.
        with self.tranca:
            velho = time.time() - self.visto > VALIDADE
            if self.ha() and velho and not self.a_ver:
                self.a_ver = True
                threading.Thread(target=self.ver_ligados, daemon=True).start()
            return self.ligados

    def ver_ligados(self):
        atendeu = []

        def um(servidor):
            try:
                self.pedir(servidor, "GET", "/api/version", espera=LIGAR)
                atendeu.append(servidor)
            except (OSError, http.client.HTTPException, ValueError):
                pass

        fios = [threading.Thread(target=um, args=(servidor,)) for servidor in self.servidores]
        for fio in fios:
            fio.start()
        for fio in fios:
            fio.join()
        with self.tranca:
            self.ligados = len(atendeu)
            self.visto = time.time()
            self.a_ver = False

    def ordem(self):
        # Os servidores pela ordem em que se vao tentar: a vez de cada um,
        # com os que falharam ha pouco no fim.
        with self.tranca:
            n = len(self.servidores)
            rodados = [self.servidores[(self.vez + i) % n] for i in range(n)]
            self.vez = (self.vez + 1) % n
            agora = time.time()
            bons = [s for s in rodados if self.de_castigo.get(s, 0) <= agora]
            return bons + [s for s in rodados if s not in bons]

    def ligar(self, servidor, espera):
        url = urlparse(servidor)
        classe = http.client.HTTPSConnection if url.scheme == "https" else http.client.HTTPConnection
        ligacao = classe(url.hostname, url.port, timeout=LIGAR)
        ligacao.connect()
        ligacao.sock.settimeout(espera)
        return ligacao

    def pedir(self, servidor, metodo, caminho, corpo=None, espera=10):
        ligacao = self.ligar(servidor, espera)
        try:
            dados = None if corpo is None else json.dumps(corpo).encode("utf-8")
            ligacao.request(metodo, caminho, body=dados, headers={"Content-Type": "application/json"})
            resposta = ligacao.getresponse()
            texto = resposta.read()
            if resposta.status != 200:
                raise OSError("resposta " + str(resposta.status))
            return json.loads(texto)
        finally:
            ligacao.close()

    def modelo_de(self, servidor):
        # O modelo a usar nesse servidor: o do servidores.txt, ou entao o
        # que ele tiver (primeiro os que ja estao na memoria). Saltam-se os
        # que nao conversam (ha modelos que so servem para comparar textos).
        if self.modelo:
            return self.modelo
        if servidor in self.modelos:
            return self.modelos[servidor]
        nomes = []
        for caminho in ("/api/ps", "/api/tags"):
            for m in self.pedir(servidor, "GET", caminho).get("models", []):
                if m.get("name") and m["name"] not in nomes:
                    nomes.append(m["name"])
        for nome in nomes:
            capacidades = self.pedir(servidor, "POST", "/api/show", {"model": nome}).get("capabilities")
            if capacidades is None or "completion" in capacidades:
                self.modelos[servidor] = nome
                return nome
        raise OSError("sem nenhum modelo para conversar")

    def comecar(self, tentativa, mensagens, fila):
        # (Corre a parte.) Faz a pergunta a um servidor e espera que ele
        # comece a escrever. Um servidor ocupado com outra pergunta so comeca
        # quando chegar a nossa vez. No fim poe a tentativa na fila.
        servidor = tentativa["servidor"]
        try:
            modelo = self.modelo_de(servidor)
            ligacao = self.ligar(servidor, ESPERAR)
            tentativa["ligacao"] = ligacao
            if tentativa["largada"]:
                raise OSError("ja nao e precisa")
            corpo = {"model": modelo, "messages": mensagens, "stream": True,
                     "options": {"temperature": 0.3, "num_predict": RESPOSTA_MAXIMA}}
            if modelo.startswith("gpt-oss"):
                # Este modelo pensa antes de responder, e a pensar muito
                # gasta as palavras todas sem chegar a dizer nada.
                corpo["think"] = "low"
            ligacao.request("POST", "/api/chat", body=json.dumps(corpo).encode("utf-8"),
                            headers={"Content-Type": "application/json"})
            resposta = ligacao.getresponse()
            if resposta.status != 200:
                detalhe = resposta.read(300).decode("utf-8", "replace")
                raise OSError("resposta " + str(resposta.status) + " " + detalhe)
            linha = b""
            while linha.strip() == b"":
                linha = resposta.readline()
                if linha == b"":
                    raise OSError("a ligação fechou antes do fim")
            tentativa["resposta"] = resposta
            tentativa["linha"] = linha
        except (OSError, http.client.HTTPException, ValueError, AttributeError) as erro:
            tentativa["erro"] = erro
        if tentativa["largada"]:
            self.largar(tentativa)
        fila.put(tentativa)

    def largar(self, tentativa):
        # Fecha a ligacao: o servidor deixa de escrever (ou tira a pergunta
        # da fila dele) e fica livre para os outros.
        tentativa["largada"] = True
        ligacao = tentativa.get("ligacao")
        if ligacao is not None:
            try:
                if ligacao.sock is not None:
                    # Acorda quem estiver a espera de ler desta ligacao.
                    ligacao.sock.shutdown(socket.SHUT_RDWR)
            except (OSError, AttributeError):
                pass
            try:
                ligacao.close()
            except (OSError, AttributeError):
                pass

    def ler(self, tentativa):
        # Da o texto da resposta de quem comecou a escrever, aos bocadinhos.
        servidor = tentativa["servidor"]
        resposta = tentativa["resposta"]
        linha = tentativa["linha"]
        disse = False        # ja mandou algum texto
        try:
            while True:
                if linha == b"":
                    raise OSError("a ligação fechou antes do fim")
                if linha.strip() != b"":
                    parte = json.loads(linha)
                    if parte.get("error"):
                        raise OSError(str(parte["error"]))
                    # (O que um modelo "pensa" antes de responder vem
                    # noutro campo, e nao se mostra.)
                    texto = (parte.get("message") or {}).get("content")
                    if texto:
                        disse = True
                        yield texto
                    if parte.get("done"):
                        break
                linha = resposta.readline()
        except (OSError, http.client.HTTPException, ValueError) as erro:
            if disse:
                raise Indisponivel("O ajudante deixou de responder a meio. Pergunta outra vez.") from erro
            raise Calado(str(erro) or type(erro).__name__) from erro
        if not disse:
            # Acontece: o modelo gasta as palavras todas a pensar.
            print("Ajudante: " + servidor + " acabou sem dizer nada (" + str(parte.get("done_reason"))
                  + ", " + str(parte.get("eval_count")) + " tokens).")
            raise Indisponivel("O ajudante ficou a pensar e não chegou a responder. "
                               "Pede-lhe uma coisa mais pequena, ou pergunta de outra maneira.")

    def perguntar(self, mensagens):
        # Da a resposta aos bocadinhos, a medida que o modelo a escreve.
        #
        # Pergunta-se ao servidor da vez. Se ele nao comecar a escrever em
        # PRESSA segundos e porque esta ocupado com a pergunta de outro
        # aluno: faz-se a mesma pergunta tambem ao seguinte, e assim por
        # diante. Fica-se com o primeiro que comecar e largam-se os outros.
        if not self.ha():
            raise Indisponivel("Esta Oficina não tem ajudante ligado.")
        por_tentar = self.ordem()
        a_espera = []        # tentativas que ainda nao comecaram a escrever
        fila = queue.Queue()
        falhas = []

        def falhou(servidor, erro):
            # Este nao serve agora: descansa um bocado.
            falhas.append(servidor + ": " + (str(erro) or type(erro).__name__))
            self.modelos.pop(servidor, None)
            self.de_castigo[servidor] = time.time() + DESCANSO

        try:
            while por_tentar or a_espera:
                if por_tentar:
                    tentativa = {"servidor": por_tentar.pop(0), "largada": False}
                    a_espera.append(tentativa)
                    threading.Thread(target=self.comecar, args=(tentativa, mensagens, fila), daemon=True).start()
                try:
                    pronta = fila.get(timeout=PRESSA if por_tentar else None)
                except queue.Empty:
                    continue         # ocupado: pergunta-se tambem ao seguinte
                if pronta not in a_espera:
                    continue         # uma que ja tinha sido largada
                a_espera.remove(pronta)
                if "erro" in pronta:
                    self.largar(pronta)
                    falhou(pronta["servidor"], pronta["erro"])
                    continue
                # Este comecou a escrever: e com ele que se fica. Os outros
                # ficam livres (e voltam a lista, para o caso de este se calar).
                for outra in a_espera:
                    self.largar(outra)
                    por_tentar.append(outra["servidor"])
                a_espera = [pronta]
                self.de_castigo.pop(pronta["servidor"], None)
                try:
                    yield from self.ler(pronta)
                    return
                except Calado as erro:
                    # Calou-se sem dizer nada (desligaram-no?): tenta-se outro.
                    falhou(pronta["servidor"], erro)
                    self.largar(pronta)
                    a_espera = []
        finally:
            # Tambem quando o aluno fecha a pagina a meio: os servidores
            # deixam de escrever uma resposta que ja ninguem le.
            for tentativa in a_espera:
                self.largar(tentativa)
        print("Ajudante: nenhum servidor respondeu.")
        for falha in falhas:
            print("    " + falha)
        raise Indisponivel("O ajudante não responde agora. Chama o professor, ou tenta daqui a bocado.")


# =====================================================================
#                 TRATAR DOS SERVIDORES, A MAO
# =====================================================================

def na_memoria(ajudante, servidor):
    # O que o servidor tem na memoria agora: [(modelo, parte que esta na placa grafica), ...]
    modelos = []
    for m in ajudante.pedir(servidor, "GET", "/api/ps").get("models", []):
        na_placa = 100 * m.get("size_vram", 0) // max(1, m.get("size", 1))
        modelos.append((m.get("name", "?"), str(na_placa) + "% na placa gráfica"))
    return modelos


def tratar(ajudante, servidor, accao):
    # Devolve a frase a mostrar para esse servidor.
    try:
        if accao == "acordar":
            inicio = time.time()
            modelo = ajudante.modelo_de(servidor)
            # Um pedido sem pergunta nenhuma so serve para o modelo ir para a memoria.
            ajudante.pedir(servidor, "POST", "/api/generate", {"model": modelo}, CARREGAR)
            demorou = " (" + str(round(time.time() - inicio)) + " s)"
        if accao == "adormecer":
            for modelo, _ in na_memoria(ajudante, servidor):
                ajudante.pedir(servidor, "POST", "/api/generate", {"model": modelo, "keep_alive": 0}, 60)
            time.sleep(1)
        modelos = na_memoria(ajudante, servidor)
    except (OSError, http.client.HTTPException, ValueError) as erro:
        return "NÃO RESPONDE (" + (str(erro) or type(erro).__name__) + "). Está ligado, e com a sessão iniciada?"
    if len(modelos) == 0:
        return "ligado, sem modelo na memória: a placa gráfica está livre"
    frase = "pronto: " + ", ".join(nome + ", " + placa for nome, placa in modelos)
    return frase + demorou if accao == "acordar" else frase


def main():
    accoes = ("acordar", "adormecer", "ver")
    if len(sys.argv) != 2 or sys.argv[1] not in accoes:
        print("Usa:  python3 oficina/ajudante.py acordar | adormecer | ver")
        sys.exit(1)
    accao = sys.argv[1]
    enderecos, modelo = ler_ficheiro()
    if not enderecos:
        print("Não há servidores em " + FICHEIRO)
        sys.exit(1)
    if accao == "acordar":
        print("A pôr o modelo na memória de cada servidor. Pode demorar um minuto ou dois...")
    ajudante = Ajudante(enderecos, modelo)
    frases = {}

    def um(servidor):
        frases[servidor] = tratar(ajudante, servidor, accao)

    # Todos ao mesmo tempo: senao esperava-se por um de cada vez.
    fios = [threading.Thread(target=um, args=(servidor,)) for servidor in enderecos]
    for fio in fios:
        fio.start()
    for fio in fios:
        fio.join()
    for servidor in enderecos:
        print("  " + urlparse(servidor).hostname + ": " + frases[servidor])
    if any(frase.startswith("NÃO RESPONDE") for frase in frases.values()):
        sys.exit(2)


if __name__ == "__main__":
    main()
