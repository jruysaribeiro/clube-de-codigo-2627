# A OFICINA
# Escolhes um jogo e uma coisa dele (um inimigo, uma torre, o mapa). De um
# lado fica so o codigo dessa coisa; do outro, o jogo a correr, a mudar
# enquanto escreves.
#
# Correr, com o ambiente virtual activado (ver COMO-CORRER.md):
#
#     python3 oficina/oficina.py
#
# Abre uma pagina no browser: o jogo a esquerda, o codigo a direita.
# O jogo e o verdadeiro, a correr neste computador; a pagina so mostra a
# imagem dele e manda-lhe o rato e o teclado.
# Para fechar: Ctrl+C aqui no terminal.
#
#     --sem-navegador   nao abre o browser (abre tu http://127.0.0.1:8765)
#     --porta 9000      usa outra porta
#     --servidor http://192.168.1.50:11434
#                       um computador ajudante (pode repetir-se); sem isto
#                       valem os que estiverem em oficina/servidores.txt
#     --modelo qwen2.5:7b   obriga o ajudante a usar esse modelo
#
# Nao precisa de internet nem de instalar mais nada. O botao "Pedir ajuda"
# so aparece se houver um computador ajudante na rede (ver ajudante.py).

import argparse
import atexit
import base64
import importlib
import json
import os
import re
import shutil
import socket
import struct
import subprocess
import sys
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)

import ajudante as modulo_do_ajudante  # noqa: E402
import blocos  # noqa: E402
from jogos import JOGOS  # noqa: E402

ORIGINAIS = os.path.join(AQUI, ".originais")
IMAGENS = os.path.join(RAIZ, "comum", "assets", "imagens")    # onde os jogos procuram as imagens
NOME_DE_IMAGEM = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.-]{0,59}\.png", re.IGNORECASE)
PNG = b"\x89PNG\r\n\x1a\n"       # todos os ficheiros PNG comecam assim
IMAGEM_MAXIMA = 1500000           # bytes (a pagina ja a encolhe antes de a mandar)
PACIENCIA = 6                 # segundos a espera de um jogo que nao responde


# =====================================================================
#                          LER E ESCREVER O JOGO
# =====================================================================

def configuracao(jogo):
    if jogo not in JOGOS:
        raise Falha("Não conheço esse jogo.")
    return importlib.import_module("jogos." + jogo)


def caminho_do_jogo(config):
    return os.path.join(RAIZ, *config.FICHEIRO.split("/"))


def ler(caminho):
    # Devolve o texto com \n e o fim de linha que o ficheiro usava.
    with open(caminho, encoding="utf-8", newline="") as f:
        texto = f.read()
    fim_de_linha = "\r\n" if "\r\n" in texto else "\n"
    return texto.replace("\r\n", "\n"), fim_de_linha


def escrever(caminho, texto, fim_de_linha):
    provisorio = caminho + ".novo"
    with open(provisorio, "w", encoding="utf-8", newline="") as f:
        f.write(texto.replace("\n", fim_de_linha))
    os.replace(provisorio, caminho)


def caminho_do_original(config):
    return os.path.join(ORIGINAIS, os.path.basename(config.FICHEIRO))


def guardar_original(config):
    # Da primeira vez que se abre um jogo, fica uma copia do ficheiro tal
    # como estava. E dai que vem o botao "Repor o original".
    destino = caminho_do_original(config)
    if not os.path.exists(destino):
        os.makedirs(ORIGINAIS, exist_ok=True)
        shutil.copyfile(caminho_do_jogo(config), destino)


class Falha(Exception):
    pass


def explicar_sintaxe(erro):
    texto = erro.msg or ""
    if "forgot a comma" in texto:
        return "Parece faltar uma vírgula."
    if "was never closed" in texto:
        return "Abriste um ( [ ou { que nunca chegaste a fechar."
    if "unterminated string" in texto:
        return "Faltam as aspas a fechar o texto."
    if "unmatched" in texto or "does not match" in texto:
        return "Há um ) ] ou } a mais, ou trocado."
    if "indent" in texto:
        return "Os espaços no início desta linha não batem certo."
    if "expected ':'" in texto:
        return "Faltam os dois pontos ( : )."
    return "O Python não percebe esta linha."


# =====================================================================
#                             A SESSAO
# =====================================================================
# So ha uma: um computador, uma crianca, um jogo aberto de cada vez.

class Sessao:

    def __init__(self):
        self.tranca = threading.RLock()
        self.jogo = None
        self.config = None
        self.escolha = None
        self.antes = []
        self.depois = []
        self.margem = ""
        self.titulo = ""
        self.ajuda = ""
        self.imagem = None           # o nome do PNG que o bocado aberto usa, se usar
        self.ajudante = modulo_do_ajudante.Ajudante()
        self.fim_de_linha = "\n"
        self.processo = None
        self.mensagens = []          # o que o jogo nos foi dizendo
        self.contador = 0            # numero da ultima mensagem
        self.numero = 0              # numero do ultimo pedido de codigo
        self.pedidos = {}            # numero -> (inicio, fim, fonte)
        self.a_provar = None         # (numero, hora) do codigo que o jogo esta a experimentar
        # A imagem do jogo: o palco liga-se a esta porta e manda os frames.
        self.quadro = None
        self.numero_do_quadro = 0
        self.ha_quadro = threading.Condition()
        self.porta_dos_quadros = socket.create_server(("127.0.0.1", 0))
        threading.Thread(target=self.receber_ligacoes, daemon=True).start()

    # --- A imagem do jogo ---

    def receber_ligacoes(self):
        while True:
            ligacao, _ = self.porta_dos_quadros.accept()
            threading.Thread(target=self.receber_quadros, args=(ligacao,), daemon=True).start()

    def receber_quadros(self, ligacao):
        # Cada frame vem como 4 bytes com o tamanho, seguidos do JPEG.
        ficheiro = ligacao.makefile("rb")
        try:
            while True:
                cabeca = ficheiro.read(4)
                if len(cabeca) < 4:
                    return
                dados = ficheiro.read(struct.unpack(">I", cabeca)[0])
                with self.ha_quadro:
                    self.quadro = dados
                    self.numero_do_quadro = self.numero_do_quadro + 1
                    self.ha_quadro.notify_all()
        except OSError:
            pass
        finally:
            ligacao.close()

    def proximo_quadro(self, ultimo):
        # Espera por um frame mais novo do que o ultimo que a pagina viu.
        with self.ha_quadro:
            if self.numero_do_quadro == ultimo:
                self.ha_quadro.wait(timeout=1)
            return self.numero_do_quadro, self.quadro

    # --- A janela do jogo ---

    def lancar(self):
        self.parar()
        ambiente = dict(os.environ)
        ambiente["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
        ambiente["PYTHONIOENCODING"] = "utf-8"
        ambiente["SDL_VIDEODRIVER"] = "dummy"     # sem janela: a imagem vai para a pagina
        processo = subprocess.Popen(
            [sys.executable, os.path.join(AQUI, "palco.py"), "--jogo", self.jogo, "--escolha", self.escolha,
             "--quadros", str(self.porta_dos_quadros.getsockname()[1])],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, env=ambiente,
            encoding="utf-8", errors="replace", bufsize=1,
        )
        self.processo = processo
        threading.Thread(target=self.ouvir, args=(processo,), daemon=True).start()

    def parar(self):
        processo = self.processo
        self.processo = None
        if processo is not None and processo.poll() is None:
            try:
                processo.stdin.write(json.dumps({"tipo": "sair"}) + "\n")
                processo.stdin.flush()
                processo.wait(timeout=1.5)
            except (OSError, ValueError, subprocess.TimeoutExpired):
                processo.kill()

    def viva(self):
        return self.processo is not None and self.processo.poll() is None

    def dizer(self, pedido):
        if not self.viva():
            self.lancar()
        try:
            self.processo.stdin.write(json.dumps(pedido) + "\n")
            self.processo.stdin.flush()
        except (OSError, ValueError):
            pass

    def ouvir(self, processo):
        for linha in processo.stdout:
            linha = linha.rstrip("\n")
            if linha.startswith("@@"):
                try:
                    mensagem = json.loads(linha[2:])
                except ValueError:
                    continue
            elif linha.strip() != "":
                mensagem = {"tipo": "print", "texto": linha}
            else:
                continue
            with self.tranca:
                if processo is self.processo:
                    self.receber(mensagem)

    def receber(self, mensagem):
        pedido = self.pedidos.get(mensagem.get("id"))
        if mensagem["tipo"] in ("estavel", "erro", "problemas", "fechou"):
            if self.a_provar is not None and mensagem.get("id") in (None, self.a_provar[0]):
                self.a_provar = None
        if mensagem["tipo"] == "estavel" and pedido is not None:
            # Correu uns frames sem rebentar: agora sim, vai para o ficheiro.
            escrever(caminho_do_jogo(self.config), pedido[2], self.fim_de_linha)
            self.ver_imagem(pedido[2])       # o nome da imagem pode ter mudado
            for numero in [n for n in self.pedidos if n <= mensagem["id"]]:
                del self.pedidos[numero]
        if mensagem["tipo"] == "erro":
            # As linhas vem contadas no ficheiro inteiro; o editor so
            # conhece as do bocado que esta a mostrar.
            mensagem["linha"] = None
            if pedido is not None:
                dentro = [l for l in mensagem.get("linhas", []) if pedido[0] <= l <= pedido[1]]
                if dentro:
                    mensagem["linha"] = dentro[-1] - pedido[0] + 1
        self.mensagens.append(mensagem)
        del self.mensagens[:-200]
        self.contador = self.contador + 1
        mensagem["n"] = self.contador

    # --- O que o editor pede ---

    def lista_de_jogos(self):
        jogos = []
        for nome in JOGOS:
            try:
                config = configuracao(nome)
            except ImportError:
                continue        # esse jogo ainda nao tem ficheiro em oficina/jogos/
            jogo = {"id": nome, "nome": config.NOME, "descricao": config.DESCRICAO, "escolhas": [], "erro": None}
            try:
                fonte, _ = ler(caminho_do_jogo(config))
                jogo["escolhas"] = config.escolhas(fonte)
            except (OSError, SyntaxError) as erro:
                jogo["erro"] = "Não consegui ler " + config.FICHEIRO + ": " + str(erro)
            jogos.append(jogo)
        return {"jogos": jogos}

    def abrir(self, jogo, escolha):
        with self.tranca:
            config = configuracao(jogo)
            guardar_original(config)
            fonte, fim_de_linha = ler(caminho_do_jogo(config))
            try:
                regiao = config.regiao(fonte, escolha)
            except SyntaxError as erro:
                raise Falha("O ficheiro do jogo tem um erro na linha " + str(erro.lineno) + ".")
            if regiao is None:
                raise Falha("Não encontrei isso no ficheiro do jogo.")
            linhas = fonte.split("\n")
            bloco = linhas[regiao["inicio"] - 1:regiao["fim"]]
            self.jogo = jogo
            self.config = config
            self.escolha = escolha
            self.fim_de_linha = fim_de_linha
            self.antes = linhas[:regiao["inicio"] - 1]
            self.depois = linhas[regiao["fim"]:]
            self.margem = blocos.margem_comum(bloco)
            self.titulo = regiao["titulo"]
            self.ajuda = regiao["ajuda"]
            self.imagem = regiao.get("imagem")
            self.pedidos = {}
            self.mensagens = []
            self.a_provar = None
            self.lancar()
            return {
                "codigo": "\n".join(blocos.tirar_margem(bloco, self.margem)),
                "titulo": regiao["titulo"], "ajuda": regiao["ajuda"], "dica": regiao["dica"],
                "jogo": config.NOME, "desde": self.contador, "imagem": self.estado_da_imagem(),
            }

    def codigo(self, texto):
        with self.tranca:
            if self.config is None:
                raise Falha("Ainda não escolheste nada.")
            bloco = texto.replace("\r\n", "\n").rstrip().split("\n")
            inicio = len(self.antes) + 1
            fim = inicio + len(bloco) - 1
            fonte = "\n".join(self.antes + blocos.por_margem(bloco, self.margem) + self.depois)
            try:
                compile(fonte, self.config.FICHEIRO, "exec")
            except SyntaxError as erro:
                linha = (erro.lineno or inicio) - inicio + 1
                texto_do_erro = explicar_sintaxe(erro)
                if linha > len(bloco):
                    # O Python so deu pelo erro mais abaixo, ja fora do bocado.
                    linha = len(bloco)
                    texto_do_erro = "Falta fechar alguma coisa no fim: uma vírgula, um } ou um ]."
                return {"ok": False, "erro": {"linha": max(1, linha), "texto": texto_do_erro,
                                              "detalhe": "SyntaxError: " + str(erro.msg)}}
            except ValueError as erro:
                return {"ok": False, "erro": {"linha": None, "texto": "O Python não aceita este código.",
                                              "detalhe": str(erro)}}
            self.numero = self.numero + 1
            self.pedidos[self.numero] = (inicio, fim, fonte)
            self.a_provar = (self.numero, time.time())
            self.dizer({"tipo": "codigo", "id": self.numero, "fonte": fonte, "inicio": inicio, "fim": fim})
            return {"ok": True, "id": self.numero}

    def original(self):
        with self.tranca:
            if self.config is None:
                raise Falha("Ainda não escolheste nada.")
            fonte, _ = ler(caminho_do_original(self.config))
            regiao = self.config.regiao(fonte, self.escolha)
            if regiao is None:
                raise Falha("Isto não existia no jogo original: foi inventado depois.")
            bloco = fonte.split("\n")[regiao["inicio"] - 1:regiao["fim"]]
            return {"codigo": "\n".join(blocos.tirar_margem(bloco, blocos.margem_comum(bloco)))}

    def desprender(self):
        # Ha codigo que nao rebenta mas deixa o jogo preso (um numero
        # gigante, um ciclo sem fim). Se o jogo aceitou codigo e depois se
        # calou, fecha-se e abre-se outra vez com o ultimo ficheiro bom.
        if self.a_provar is None or time.time() - self.a_provar[1] < PACIENCIA:
            return
        numero = self.a_provar[0]
        self.a_provar = None
        if self.processo is not None:
            self.processo.kill()
        self.lancar()
        self.receber({
            "tipo": "erro", "id": numero, "linhas": [],
            "texto": "O jogo ficou preso com este código. Há algum número grande demais? "
                     "Voltei a abrir o jogo como estava antes.",
            "detalhe": "sem resposta ao fim de " + str(PACIENCIA) + " segundos",
        })

    def estado(self, desde):
        with self.tranca:
            self.desprender()
            return {
                "mensagens": [m for m in self.mensagens if m["n"] > desde],
                "viva": self.viva(),
                "imagem": self.estado_da_imagem(),
            }

    def entrada(self, eventos):
        # O rato e o teclado da pagina, para o jogo.
        with self.tranca:
            if self.viva() and isinstance(eventos, list):
                self.dizer({"tipo": "entrada", "eventos": eventos})
            return {"ok": True}

    def reabrir(self):
        with self.tranca:
            if self.config is None:
                raise Falha("Ainda não escolheste nada.")
            self.lancar()
            return {"ok": True}

    def fechar(self):
        with self.tranca:
            self.parar()
            self.config = None
            return {"ok": True}

    # --- A imagem do bocado aberto ---
    # Ha coisas que no codigo dizem "imagem": "soldado.png". O jogo procura
    # esse ficheiro em comum/assets/imagens/ e, se o encontrar, desenha a
    # imagem em vez da forma. A crianca escolhe uma imagem na pagina e ela
    # e guardada la, com esse nome.

    def ver_imagem(self, fonte):
        try:
            regiao = self.config.regiao(fonte, self.escolha)
        except (SyntaxError, ValueError):
            return
        self.imagem = regiao.get("imagem") if regiao else None

    def estado_da_imagem(self):
        # None: este bocado nao usa imagem nenhuma.
        if self.config is None or not isinstance(self.imagem, str):
            return None
        if not NOME_DE_IMAGEM.fullmatch(self.imagem):
            return {"nome": self.imagem, "ha": False, "versao": 0,
                    "erro": 'O nome da imagem tem de acabar em .png e só pode ter letras sem acentos, '
                            'números, - e _ (por exemplo "dragao.png").'}
        caminho = os.path.join(IMAGENS, self.imagem)
        if not os.path.isfile(caminho):
            return {"nome": self.imagem, "ha": False, "versao": 0, "erro": None}
        return {"nome": self.imagem, "ha": True, "versao": os.stat(caminho).st_mtime_ns, "erro": None}

    def caminho_da_imagem(self):
        estado = self.estado_da_imagem()
        if estado is None:
            raise Falha("Este bocado não usa nenhuma imagem.")
        if estado["erro"]:
            raise Falha(estado["erro"])
        return os.path.join(IMAGENS, estado["nome"])

    def avisar_das_imagens(self):
        if self.viva():
            self.dizer({"tipo": "imagens"})

    def por_imagem(self, dados):
        # A pagina manda sempre um PNG, ja pequeno, escrito em base64.
        with self.tranca:
            caminho = self.caminho_da_imagem()
            try:
                imagem = base64.b64decode(str(dados or ""), validate=True)
            except ValueError:
                raise Falha("A imagem chegou estragada. Tenta outra vez.")
            if not imagem.startswith(PNG):
                raise Falha("Isso não é uma imagem que eu saiba ler.")
            if len(imagem) > IMAGEM_MAXIMA:
                raise Falha("Essa imagem é grande demais.")
            os.makedirs(IMAGENS, exist_ok=True)
            with open(caminho + ".novo", "wb") as f:
                f.write(imagem)
            os.replace(caminho + ".novo", caminho)
            self.avisar_das_imagens()
            return {"imagem": self.estado_da_imagem()}

    def tirar_imagem(self):
        with self.tranca:
            caminho = self.caminho_da_imagem()
            if os.path.isfile(caminho):
                os.remove(caminho)
            self.avisar_das_imagens()
            return {"imagem": self.estado_da_imagem()}

    def ler_imagem(self):
        with self.tranca:
            caminho = self.caminho_da_imagem()
            if not os.path.isfile(caminho):
                raise Falha("Ainda não há imagem.")
            with open(caminho, "rb") as f:
                return f.read()

    # --- O ajudante ---

    def perguntar(self, dados):
        # Devolve a resposta aos bocadinhos. O codigo e o erro vem da
        # pagina: e o que o aluno esta a ver, mesmo que ainda nao funcione.
        with self.tranca:
            if self.config is None:
                raise Falha("Ainda não escolheste nada.")
            pergunta = str(dados.get("pergunta") or "").strip()
            if pergunta == "":
                raise Falha("Escreve a tua pergunta primeiro.")
            mensagens = modulo_do_ajudante.mensagens(
                self.config.NOME, self.titulo, self.ajuda, dados.get("codigo"),
                dados.get("erro"), dados.get("linha"), dados.get("conversa"), pergunta)
        return self.ajudante.perguntar(mensagens)

    # --- Levar o jogo para casa e traze-lo de volta ---

    def descarregar(self, jogo):
        config = configuracao(jogo)
        with open(caminho_do_jogo(config), "rb") as f:
            return os.path.basename(config.FICHEIRO), f.read()

    def carregar(self, jogo, fonte):
        with self.tranca:
            config = configuracao(jogo)
            fonte = fonte.replace("\r\n", "\n")
            try:
                escolhas = config.escolhas(fonte)
            except (SyntaxError, ValueError) as erro:
                raise Falha("Esse ficheiro tem um erro de Python e não dá para abrir: " + str(erro))
            if len(escolhas) == 0:
                raise Falha("Esse ficheiro não parece ser o " + config.NOME + ".")
            guardar_original(config)
            self.parar()
            self.config = None
            caminho = caminho_do_jogo(config)
            _, fim_de_linha = ler(caminho)
            shutil.copyfile(caminho, caminho + ".anterior")   # por se enganarem no ficheiro
            escrever(caminho, fonte, fim_de_linha)
            return {"ok": True}


sessao = Sessao()


# =====================================================================
#                           O SERVIDOR
# =====================================================================

class Pedido(BaseHTTPRequestHandler):

    protocol_version = "HTTP/1.1"     # a pagina pede 30 imagens por segundo: a ligacao fica aberta

    def log_message(self, *args):
        pass

    def responder(self, codigo, corpo, tipo="application/json; charset=utf-8", extra=None):
        if not isinstance(corpo, bytes):
            corpo = json.dumps(corpo).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(corpo)))
        self.send_header("Cache-Control", "no-store")
        for nome, valor in (extra or {}).items():
            self.send_header(nome, valor)
        self.end_headers()
        self.wfile.write(corpo)

    def tratar(self, accao):
        try:
            resposta = accao()
            if isinstance(resposta, tuple):
                self.responder(200, resposta[1], "text/x-python; charset=utf-8",
                               {"Content-Disposition": 'attachment; filename="' + resposta[0] + '"'})
            else:
                self.responder(200, resposta)
        except Falha as falha:
            self.responder(400, {"falha": str(falha)})
        except BrokenPipeError:
            pass
        except Exception as erro:   # um erro nosso: mostra-se, nao se esconde
            self.responder(500, {"falha": "Erro da Oficina: " + type(erro).__name__ + ": " + str(erro)})

    def do_GET(self):
        url = urlparse(self.path)
        parametros = parse_qs(url.query)
        if url.path == "/":
            with open(os.path.join(AQUI, "editor.html"), "rb") as f:
                self.responder(200, f.read(), "text/html; charset=utf-8")
        elif url.path == "/api/jogos":
            self.tratar(sessao.lista_de_jogos)
        elif url.path == "/api/ajudante":
            self.responder(200, {"ha": sessao.ajudante.ha()})
        elif url.path == "/api/estado":
            desde = int(parametros.get("desde", ["0"])[0])
            self.tratar(lambda: sessao.estado(desde))
        elif url.path == "/api/quadro":
            self.quadro(int(parametros.get("depois", ["0"])[0]))
        elif url.path == "/api/imagem":
            try:
                self.responder(200, sessao.ler_imagem(), "image/png")
            except Falha as falha:
                self.responder(404, {"falha": str(falha)})
        elif url.path == "/api/descarregar":
            self.tratar(lambda: sessao.descarregar(parametros.get("jogo", [""])[0]))
        else:
            self.responder(404, {"falha": "Não existe."})

    def quadro(self, depois):
        # A imagem do jogo: um frame de cada vez. A pagina diz qual foi o
        # ultimo que viu e fica a espera ate haver um mais novo.
        numero, dados = sessao.proximo_quadro(depois)
        try:
            if numero == depois or dados is None:
                self.responder(204, b"")
            else:
                self.responder(200, dados, "image/jpeg", {"X-Quadro": str(numero)})
        except OSError:
            pass      # a pagina fechou

    def pergunta(self, dados):
        # A resposta do ajudante vai para a pagina a medida que e escrita.
        # So se comeca a responder quando chega o primeiro bocado: ate la
        # ainda se pode dizer a pagina que nao deu.
        try:
            pedacos = sessao.perguntar(dados)
            primeiro = next(pedacos, None)
        except Falha as falha:
            self.responder(400, {"falha": str(falha)})
            return
        except modulo_do_ajudante.Indisponivel as falha:
            self.responder(503, {"falha": str(falha)})
            return
        if primeiro is None:
            self.responder(503, {"falha": "O ajudante não disse nada. Pergunta outra vez."})
            return
        try:
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Connection", "close")     # sem tamanho: acaba quando a ligacao fechar
            self.end_headers()
            self.wfile.write(primeiro.encode("utf-8"))
            for pedaco in pedacos:
                self.wfile.write(pedaco.encode("utf-8"))
        except modulo_do_ajudante.Indisponivel as falha:
            try:
                self.wfile.write(("\n\n(" + str(falha) + ")").encode("utf-8"))
            except OSError:
                pass
        except OSError:
            pass      # a pagina fechou
        finally:
            pedacos.close()

    def do_POST(self):
        # So aceitamos pedidos vindos da nossa propria pagina.
        corpo = self.rfile.read(int(self.headers.get("Content-Length") or 0))
        origem = self.headers.get("Origin")
        if origem is not None and origem != "http://" + self.headers.get("Host", ""):
            self.responder(403, {"falha": "Pedido de fora."})
            return
        try:
            dados = json.loads(corpo or b"{}")
        except ValueError:
            self.responder(400, {"falha": "Pedido mal feito."})
            return
        caminho = urlparse(self.path).path
        if caminho == "/api/abrir":
            self.tratar(lambda: sessao.abrir(dados.get("jogo"), str(dados.get("escolha"))))
        elif caminho == "/api/codigo":
            self.tratar(lambda: sessao.codigo(str(dados.get("codigo", ""))))
        elif caminho == "/api/original":
            self.tratar(sessao.original)
        elif caminho == "/api/entrada":
            self.tratar(lambda: sessao.entrada(dados.get("eventos")))
        elif caminho == "/api/reabrir":
            self.tratar(sessao.reabrir)
        elif caminho == "/api/fechar":
            self.tratar(sessao.fechar)
        elif caminho == "/api/imagem":
            self.tratar(lambda: sessao.por_imagem(dados.get("dados")))
        elif caminho == "/api/tirar-imagem":
            self.tratar(sessao.tirar_imagem)
        elif caminho == "/api/pergunta":
            self.pergunta(dados)
        elif caminho == "/api/carregar":
            self.tratar(lambda: sessao.carregar(dados.get("jogo"), str(dados.get("fonte", ""))))
        elif caminho == "/api/foto":      # para testes: tira uma fotografia a janela
            self.tratar(lambda: sessao.dizer({"tipo": "foto", "ficheiro": str(dados.get("ficheiro"))}) or {"ok": True})
        else:
            self.responder(404, {"falha": "Não existe."})


def main():
    argumentos = argparse.ArgumentParser(description="A Oficina do Clube de Código")
    argumentos.add_argument("--porta", type=int, default=8765)
    argumentos.add_argument("--sem-navegador", action="store_true")
    argumentos.add_argument("--servidor", action="append", default=[],
                            help="endereço de um computador ajudante (pode repetir-se)")
    argumentos.add_argument("--modelo", help="o modelo que o ajudante usa")
    argumentos = argumentos.parse_args()

    servidores, modelo = modulo_do_ajudante.ler_ficheiro()
    if argumentos.servidor:
        servidores = [modulo_do_ajudante.endereco_certo(s) for s in argumentos.servidor]
        servidores = [s for s in servidores if s]
    sessao.ajudante = modulo_do_ajudante.Ajudante(servidores, argumentos.modelo or modelo)

    os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
    try:
        import pygame  # noqa: F401
    except ImportError:
        print("Falta o pygame. Activa o ambiente virtual primeiro (ver COMO-CORRER.md, secção 1).")
        sys.exit(1)

    servidor = None
    for porta in range(argumentos.porta, argumentos.porta + 20):
        try:
            servidor = ThreadingHTTPServer(("127.0.0.1", porta), Pedido)
            break
        except OSError:
            continue
    if servidor is None:
        print("Não encontrei uma porta livre. Tenta: --porta 9000")
        sys.exit(1)

    atexit.register(sessao.parar)
    endereco = "http://127.0.0.1:" + str(servidor.server_address[1])
    print("A Oficina está aberta em " + endereco)
    if servidores:
        print("Ajudante: " + ", ".join(servidores))
    print("Para fechar: Ctrl+C")
    if not argumentos.sem_navegador:
        webbrowser.open(endereco)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nAté à próxima.")


if __name__ == "__main__":
    main()
