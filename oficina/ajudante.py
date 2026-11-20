# O AJUDANTE
# Leva as perguntas da Oficina a um modelo de linguagem que corre noutro
# computador da sala (um dos computadores com placa grafica, com o Ollama
# aberto a rede: ver instalar-servidor-windows.bat).
#
# Os enderecos desses computadores estao em oficina/servidores.txt. Havendo
# varios, cada pergunta vai para um diferente, a vez; se um nao atender,
# passa-se ao seguinte. Sem enderecos nao ha ajudante, e a Oficina funciona
# como sempre.
#
# So usa o que ja vem com o Python.

import http.client
import json
import os
import random
import threading
import time
from urllib.parse import urlparse

AQUI = os.path.dirname(os.path.abspath(__file__))
FICHEIRO = os.path.join(AQUI, "servidores.txt")

PORTA = 11434             # a porta do Ollama
LIGAR = 3                 # segundos para um servidor atender
ESPERAR = 180             # segundos a espera da resposta (a primeira demora: o modelo vai para a memoria)
DESCANSO = 30             # segundos sem voltar a tentar um servidor que falhou
RESPOSTA_MAXIMA = 1500    # tokens: trava um modelo que nao se cala
CODIGO_MAXIMO = 6000      # letras do codigo que se mandam ao modelo
TEXTO_MAXIMO = 1500       # letras de cada pergunta, erro ou resposta antiga
CONVERSA_MAXIMA = 6       # mensagens anteriores que o modelo ainda ve

INSTRUCOES = """És o ajudante da Oficina do Clube de Código. Falas com alunos dos 12 aos 18 anos que estão a mudar um jogo feito em Python com pygame. Responde sempre em português de Portugal, a tratar por tu, em poucas frases e com palavras simples.

Regras:
1. O aluno vê só um bocado do ficheiro do jogo. O resto do jogo existe e funciona: fala só desse bocado.
2. Dá pistas e explica o porquê. Podes mostrar uma ou duas linhas corrigidas, nunca o bocado inteiro reescrito: quem escreve é o aluno.
3. Se houver um erro, diz em que linha está, o que quer dizer e como se resolve.
4. Se não souberes, ou o pedido não for claro, di-lo ou faz uma pergunta curta. Não inventes.
5. Só ajudas com o jogo e com programação. Se te pedirem outra coisa, diz com simpatia que aqui só tratas do jogo."""


class Indisponivel(Exception):
    # Nao ha ajudante, ou nenhum servidor respondeu. O texto e para o aluno.
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


def mensagens(jogo, titulo, ajuda, codigo, erro, linha, conversa, pergunta):
    # O que o modelo recebe: as instrucoes, o bocado que o aluno tem aberto
    # (como esta agora no editor), o erro que a Oficina lhe mostra, a
    # conversa ate aqui e a pergunta.
    linhas = str(codigo or "").replace("\r\n", "\n").split("\n")
    contexto = [INSTRUCOES, "", "O jogo chama-se " + str(jogo) + ". O aluno tem aberto este bocado: " + str(titulo) + "."]
    if ajuda:
        contexto += ["", "O que quer dizer cada coisa desse bocado:", cortar(ajuda, 3000)]
    contexto += ["", "O código, como o aluno o tem agora:", "```python", cortar("\n".join(linhas), CODIGO_MAXIMO), "```"]
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
            resposta.append({"role": papel, "content": cortar(fala["texto"], TEXTO_MAXIMO)})
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

    def ha(self):
        return len(self.servidores) > 0

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

    def pedir(self, servidor, metodo, caminho, corpo=None):
        ligacao = self.ligar(servidor, 10)
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

    def perguntar(self, mensagens):
        # Da a resposta aos bocadinhos, a medida que o modelo a escreve.
        if not self.ha():
            raise Indisponivel("Esta Oficina não tem ajudante ligado.")
        falhas = []
        for servidor in self.ordem():
            ligacao = None
            try:
                try:
                    modelo = self.modelo_de(servidor)
                    ligacao = self.ligar(servidor, ESPERAR)
                    corpo = {"model": modelo, "messages": mensagens, "stream": True,
                             "options": {"temperature": 0.3, "num_predict": RESPOSTA_MAXIMA}}
                    ligacao.request("POST", "/api/chat", body=json.dumps(corpo).encode("utf-8"),
                                    headers={"Content-Type": "application/json"})
                    resposta = ligacao.getresponse()
                    if resposta.status != 200:
                        detalhe = resposta.read(300).decode("utf-8", "replace")
                        raise OSError("resposta " + str(resposta.status) + " " + detalhe)
                except (OSError, http.client.HTTPException, ValueError) as erro:
                    # Este nao serve agora: descansa um bocado e tenta-se o seguinte.
                    falhas.append(servidor + ": " + (str(erro) or type(erro).__name__))
                    self.modelos.pop(servidor, None)
                    self.de_castigo[servidor] = time.time() + DESCANSO
                    continue
                self.de_castigo.pop(servidor, None)
                try:
                    for linha in resposta:
                        if linha.strip() == b"":
                            continue
                        parte = json.loads(linha)
                        if parte.get("error"):
                            raise OSError(str(parte["error"]))
                        # (O que um modelo "pensa" antes de responder vem
                        # noutro campo, e nao se mostra.)
                        texto = (parte.get("message") or {}).get("content")
                        if texto:
                            yield texto
                        if parte.get("done"):
                            break
                except (OSError, http.client.HTTPException, ValueError) as erro:
                    raise Indisponivel("O ajudante deixou de responder a meio. Pergunta outra vez.") from erro
                return
            finally:
                # Tambem quando o aluno fecha a pagina a meio: o servidor
                # deixa de escrever uma resposta que ja ninguem le.
                if ligacao is not None:
                    ligacao.close()
        print("Ajudante: nenhum servidor respondeu.")
        for falha in falhas:
            print("    " + falha)
        raise Indisponivel("O ajudante não responde agora. Chama o professor, ou tenta daqui a bocado.")
