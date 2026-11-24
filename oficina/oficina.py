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
import ast
import atexit
import base64
import importlib
import io
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
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)

import ajudante as modulo_do_ajudante  # noqa: E402
import blocos  # noqa: E402
from jogos import JOGOS  # noqa: E402

ORIGINAIS = os.path.join(AQUI, ".originais")
JOGAR = "jogar"               # a "escolha" que quer dizer: o jogo inteiro (ver palco.py)
CAPAS = os.path.join(AQUI, "capas")       # a fotografia de cada jogo, para o cartao dele
# Imagens e sons: a pasta onde os jogos os procuram, como tem de ser o nome,
# como comeca um ficheiro desses, e um nome de exemplo.
FICHEIROS = {
    "imagem": (os.path.join(RAIZ, "comum", "assets", "imagens"),
               re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.-]{0,59}\.png", re.IGNORECASE), b"\x89PNG\r\n\x1a\n", "dragao.png"),
    "som": (os.path.join(RAIZ, "comum", "assets", "sons"),
            re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.-]{0,59}\.wav", re.IGNORECASE), b"RIFF", "explosao.wav"),
}
FICHEIRO_MAXIMO = 1500000         # bytes (a pagina ja os encolhe antes de os mandar)
# Um jogo guardado e um zip: o ficheiro do jogo e, nestas pastas, as imagens
# e os sons que ele usa.
PASTAS_DO_ZIP = {"imagem": "imagens", "som": "sons"}
ZIP_MAXIMO = 60000000             # bytes, tudo somado e fora do zip
ZIP_FICHEIROS = 500
LEIA_ME = ("Este é um jogo guardado na Oficina.\n\n"
           "Para continuares a mexer nele: abre a Oficina, entra no jogo, carrega em\n"
           "\"Abrir um jogo guardado\" e escolhe este ficheiro zip, tal como está.\n"
           "O jogo, as imagens e os sons vão cada um para o seu sítio.\n")
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
        # Um bocado pode ter varias imagens (um bicho de frente e de costas):
        # [{"nome": "De frente", "ficheiro": "galo.png"}, ...], e qual delas
        # esta escolhida. "imagem" e sempre a escolhida.
        self.imagens = []
        self.qual_imagem = 0
        self.som = None              # e o do WAV
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
        with self.ha_quadro:
            self.quadro = None       # senao a pagina mostrava a ultima imagem do jogo anterior
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
            jogo = {"id": nome, "nome": config.NOME, "descricao": config.DESCRICAO, "escolhas": [], "erro": None,
                    "grupos": getattr(config, "SOBRE_OS_GRUPOS", {}),
                    "criaveis": getattr(config, "CRIAVEIS", {}),
                    "capa": os.path.isfile(os.path.join(CAPAS, nome + ".png"))}
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
            self.qual_imagem = 0
            self.acertar_imagem(regiao)
            self.som = regiao.get("som")
            self.pedidos = {}
            self.mensagens = []
            self.a_provar = None
            self.lancar()
            return {
                "codigo": "\n".join(blocos.tirar_margem(bloco, self.margem)),
                "titulo": regiao["titulo"], "ajuda": regiao["ajuda"], "dica": regiao["dica"],
                "jogo": config.NOME, "desde": self.contador, "imagem": self.estado_da_imagem(),
                "som": self.estado_do_ficheiro("som"),
                "sugestoes": regiao.get("sugestoes") or [],
                # O que dizem os botoes de apagar esta coisa e de escolher de
                # uma lista (None se aqui nao os ha).
                "apagar": regiao.get("apagar"), "lista": regiao.get("lista"),
                "caixas": bool(regiao.get("caixas")),
            }

    def jogar(self, jogo):
        # O jogo inteiro, como ele e, com tudo o que ja foi mudado: para
        # experimentar a serio. Aqui nao ha codigo aberto.
        with self.tranca:
            config = configuracao(jogo)
            self.jogo = jogo
            self.config = config
            self.escolha = JOGAR
            self.antes = []
            self.depois = []
            self.margem = ""
            self.titulo = ""
            self.ajuda = ""
            self.acertar_imagem(None)
            self.som = None
            self.pedidos = {}
            self.mensagens = []
            self.a_provar = None
            self.lancar()
            return {"jogo": config.NOME, "desde": self.contador}

    def codigo(self, texto):
        with self.tranca:
            if self.config is None or self.escolha == JOGAR:
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
            if self.config is None or self.escolha == JOGAR:
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
            "texto": "O jogo ficou preso com este código. Há algum número grande demais, "
                     "ou um ciclo que nunca acaba? "
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
                "som": self.estado_do_ficheiro("som"),
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

    # --- A imagem e o som do bocado aberto ---
    # Ha coisas que no codigo dizem "imagem": "soldado.png" ou "som":
    # "soldado.wav". O jogo procura esses ficheiros em comum/assets/ e, se os
    # encontrar, mostra a imagem em vez da forma e toca o som. A crianca
    # escolhe (ou desenha, ou grava) na pagina, e fica guardado la com esse nome.

    def ver_imagem(self, fonte):
        # (Tambem ve o som: os dois nomes vem do mesmo sitio.)
        try:
            regiao = self.config.regiao(fonte, self.escolha)
        except (SyntaxError, ValueError):
            return
        self.acertar_imagem(regiao)
        self.som = regiao.get("som") if regiao else None

    def acertar_imagem(self, regiao):
        # Que imagem esta aberta: a unica que a coisa tem ou, se tem varias,
        # a que estiver escolhida.
        self.imagens = (regiao or {}).get("imagens") or []
        self.imagem = regiao.get("imagem") if regiao else None
        if self.imagens:
            self.qual_imagem = min(self.qual_imagem, len(self.imagens) - 1)
            self.imagem = self.imagens[self.qual_imagem]["ficheiro"]

    def escolher_imagem(self, qual):
        # A crianca escolheu outra das imagens da coisa (a de costas, por exemplo).
        with self.tranca:
            if not isinstance(qual, int) or isinstance(qual, bool) or not 0 <= qual < len(self.imagens):
                raise Falha("Essa imagem não existe.")
            self.qual_imagem = qual
            self.imagem = self.imagens[qual]["ficheiro"]
            return {"imagem": self.estado_da_imagem()}

    def caixas(self, dados):
        # As caixas para marcar de uma coisa (ve "caixas" no ficheiro do jogo
        # em oficina/jogos/). Como na lista: trabalha-se sobre o codigo do
        # editor, e o codigo mudado volta para la.
        with self.tranca:
            config = self.config
            if config is None or self.escolha == JOGAR or not hasattr(config, "caixas"):
                raise Falha("Aqui não há caixas para marcar.")
            fonte, _ = ler(caminho_do_jogo(config))
            try:
                return config.caixas(fonte, self.escolha, str(dados.get("codigo", "")), dados.get("chave"),
                                     dados.get("valor"))
            except (SyntaxError, ValueError) as erro:
                texto = str(erro)
                raise Falha(texto[:1].upper() + texto[1:])

    def estado_do_ficheiro(self, tipo):
        # None: este bocado nao usa imagem (ou som) nenhuma.
        pasta, forma, _, exemplo = FICHEIROS[tipo]
        nome = self.imagem if tipo == "imagem" else self.som
        if self.config is None or not isinstance(nome, str):
            return None
        if not forma.fullmatch(nome):
            return {"nome": nome, "ha": False, "versao": 0,
                    "erro": "O nome tem de acabar em " + exemplo[-4:] + " e só pode ter letras sem acentos, "
                            'números, - e _ (por exemplo "' + exemplo + '").'}
        caminho = os.path.join(pasta, nome)
        if not os.path.isfile(caminho):
            return {"nome": nome, "ha": False, "versao": 0, "erro": None}
        return {"nome": nome, "ha": True, "versao": os.stat(caminho).st_mtime_ns, "erro": None}

    def estado_da_imagem(self):
        estado = self.estado_do_ficheiro("imagem")
        if estado is not None and len(self.imagens) > 1:
            estado["opcoes"] = [imagem["nome"] for imagem in self.imagens]
            estado["qual"] = self.qual_imagem
        return estado

    def caminho_do_ficheiro(self, tipo):
        estado = self.estado_do_ficheiro(tipo)
        if estado is None:
            raise Falha("Este bocado não usa " + ("nenhuma imagem." if tipo == "imagem" else "nenhum som."))
        if estado["erro"]:
            raise Falha(estado["erro"])
        return os.path.join(FICHEIROS[tipo][0], estado["nome"])

    def avisar_dos_ficheiros(self):
        if self.viva():
            self.dizer({"tipo": "imagens"})

    def por_ficheiro(self, tipo, dados):
        # A pagina manda sempre um PNG pequeno (ou um WAV curto), em base64.
        with self.tranca:
            caminho = self.caminho_do_ficheiro(tipo)
            pasta, _, inicio, _ = FICHEIROS[tipo]
            try:
                conteudo = base64.b64decode(str(dados or ""), validate=True)
            except ValueError:
                raise Falha("O ficheiro chegou estragado. Tenta outra vez.")
            if not conteudo.startswith(inicio) or (tipo == "som" and conteudo[8:12] != b"WAVE"):
                raise Falha("Isso não é " + ("uma imagem" if tipo == "imagem" else "um som") + " que eu saiba ler.")
            if len(conteudo) > FICHEIRO_MAXIMO:
                raise Falha("Esse ficheiro é grande demais.")
            os.makedirs(pasta, exist_ok=True)
            with open(caminho + ".novo", "wb") as f:
                f.write(conteudo)
            os.replace(caminho + ".novo", caminho)
            self.avisar_dos_ficheiros()
            return {tipo: self.estado_do_ficheiro(tipo)}

    def tirar_ficheiro(self, tipo):
        with self.tranca:
            caminho = self.caminho_do_ficheiro(tipo)
            if os.path.isfile(caminho):
                os.remove(caminho)
            self.avisar_dos_ficheiros()
            return {tipo: self.estado_do_ficheiro(tipo)}

    def ler_ficheiro(self, tipo):
        with self.tranca:
            caminho = self.caminho_do_ficheiro(tipo)
            if not os.path.isfile(caminho):
                raise Falha("Ainda não há.")
            with open(caminho, "rb") as f:
                return f.read()

    # --- Criar uma coisa nova ---

    def criar(self, jogo, grupo):
        # Um inimigo novo, uma torre nova: quem sabe faze-los e o ficheiro
        # do jogo em oficina/jogos/, que devolve o ficheiro ja com a coisa
        # nova la dentro (uma copia de uma que ja existia, com outro nome).
        with self.tranca:
            config = configuracao(jogo)
            if grupo not in getattr(config, "CRIAVEIS", {}):
                raise Falha("Aqui não dá para criar isso.")
            guardar_original(config)
            caminho = caminho_do_jogo(config)
            fonte, fim_de_linha = ler(caminho)
            try:
                nova, escolha, aviso = config.novo(fonte, grupo)
                compile(nova, config.FICHEIRO, "exec")
                if escolha not in [e["id"] for e in config.escolhas(nova)]:
                    raise ValueError("a coisa nova não apareceu")
            except (SyntaxError, ValueError) as erro:
                raise Falha("Não consegui criar: " + str(erro))
            self.parar()
            self.config = None
            escrever(caminho, nova, fim_de_linha)
            return {"escolha": escolha, "aviso": aviso}

    # --- Apagar uma coisa, e escolher de uma lista ---

    def apagar(self):
        # Quem sabe apagar e o ficheiro do jogo em oficina/jogos/, que devolve
        # o ficheiro ja sem a coisa. O que la estava fica ao lado, em
        # ".anterior", por se ter apagado sem querer.
        with self.tranca:
            config = self.config
            if config is None or self.escolha == JOGAR or not hasattr(config, "apagar"):
                raise Falha("Aqui não dá para apagar isso.")
            caminho = caminho_do_jogo(config)
            fonte, fim_de_linha = ler(caminho)
            try:
                nova, aviso = config.apagar(fonte, self.escolha)
                compile(nova, config.FICHEIRO, "exec")
            except (SyntaxError, ValueError) as erro:
                raise Falha("Não deu para apagar: " + str(erro))
            self.parar()
            self.config = None
            shutil.copyfile(caminho, caminho + ".anterior")
            escrever(caminho, nova, fim_de_linha)
            return {"aviso": aviso}

    def lista(self, dados):
        # Sem "escolhidos": a lista de onde se escolhe, e o que esta escolhido
        # no codigo do editor. Com "escolhidos": esse codigo ja mudado, que a
        # pagina poe no editor e manda como se tivesse sido escrito.
        with self.tranca:
            config = self.config
            if config is None or self.escolha == JOGAR or not hasattr(config, "lista"):
                raise Falha("Aqui não há nada para escolher de uma lista.")
            fonte, _ = ler(caminho_do_jogo(config))
            try:
                return config.lista(fonte, self.escolha, str(dados.get("codigo", "")), dados.get("escolhidos"))
            except (SyntaxError, ValueError) as erro:
                texto = str(erro)
                raise Falha(texto[:1].upper() + texto[1:])

    # --- O ajudante ---

    def perguntar(self, dados):
        # Devolve a resposta aos bocadinhos. O codigo e o erro vem da
        # pagina: e o que o aluno esta a ver, mesmo que ainda nao funcione.
        with self.tranca:
            if self.config is None or self.escolha == JOGAR:
                raise Falha("Ainda não escolheste nada.")
            pergunta = str(dados.get("pergunta") or "").strip()
            if pergunta == "":
                raise Falha("Escreve a tua pergunta primeiro.")
            mensagens = modulo_do_ajudante.mensagens(
                self.config.NOME, self.titulo, self.ajuda, dados.get("codigo"),
                dados.get("erro"), dados.get("linha"), dados.get("conversa"), pergunta)
        # (Num mapa, o modelo responde com ordens, e e aqui que se aplicam.)
        return modulo_do_ajudante.responder(self.ajudante.perguntar(mensagens), dados.get("codigo"))

    # --- Levar o jogo para casa e traze-lo de volta ---

    def descarregar(self, jogo):
        # Um zip com o ficheiro do jogo e as imagens e os sons de que ele
        # fala (os nomes escritos no codigo que existam nas pastas): e tudo o
        # que e preciso para continuar noutro computador.
        config = configuracao(jogo)
        nome = os.path.basename(config.FICHEIRO)
        with open(caminho_do_jogo(config), "rb") as f:
            jogo_em_bytes = f.read()
        nomes = set()
        try:
            for no in ast.walk(ast.parse(jogo_em_bytes.decode("utf-8"))):
                if isinstance(no, ast.Constant) and isinstance(no.value, str):
                    nomes.add(no.value)
        except (SyntaxError, ValueError):
            pass                 # um jogo com um erro vai na mesma, so sem imagens
        memoria = io.BytesIO()
        with zipfile.ZipFile(memoria, "w", zipfile.ZIP_DEFLATED) as pacote:
            pacote.writestr(nome, jogo_em_bytes)
            pacote.writestr("LEIA-ME.txt", LEIA_ME)
            for tipo, pasta_no_zip in PASTAS_DO_ZIP.items():
                pasta, regra, _, _ = FICHEIROS[tipo]
                for ficheiro in sorted(nomes):
                    caminho = os.path.join(pasta, ficheiro)
                    if regra.fullmatch(ficheiro) and os.path.isfile(caminho):
                        pacote.write(caminho, pasta_no_zip + "/" + ficheiro)
        return os.path.splitext(nome)[0] + ".zip", memoria.getvalue()

    def abrir_pacote(self, config, dados):
        # O que vem num jogo guardado: (o codigo do jogo, [(tipo, nome,
        # conteudo), ...] com as imagens e os sons). Um ficheiro .py sozinho,
        # como os que a Oficina guardava antes, tambem serve.
        if not zipfile.is_zipfile(io.BytesIO(dados)):
            try:
                return dados.decode("utf-8"), []
            except UnicodeDecodeError:
                raise Falha("Esse ficheiro não é um jogo guardado pela Oficina.")
        try:
            pacote = zipfile.ZipFile(io.BytesIO(dados))
            entradas = [e for e in pacote.infolist() if not e.is_dir() and not e.filename.startswith("__MACOSX/")]
            if len(entradas) > ZIP_FICHEIROS or sum(e.file_size for e in entradas) > ZIP_MAXIMO:
                raise Falha("Esse ficheiro é grande demais para ser um jogo guardado.")
            # (Quem abriu o zip e o voltou a fechar pode ter metido tudo
            # dentro de uma pasta: tira-se essa pasta do caminho.)
            pastas = {e.filename.partition("/")[0] for e in entradas if "/" in e.filename}
            fora = len(pastas) == 1 and all("/" in e.filename for e in entradas)
            caminhos = {e: (e.filename.partition("/")[2] if fora else e.filename) for e in entradas}
            jogos = [e for e in entradas if "/" not in caminhos[e] and caminhos[e].endswith(".py")]
            certos = [e for e in jogos if caminhos[e] == os.path.basename(config.FICHEIRO)]
            if not jogos:
                raise Falha("Não encontrei nenhum jogo dentro desse ficheiro.")
            fonte = pacote.read((certos or jogos)[0]).decode("utf-8")
            ficheiros = []
            for entrada in entradas:
                pasta, _, nome = caminhos[entrada].partition("/")
                for tipo, pasta_no_zip in PASTAS_DO_ZIP.items():
                    _, regra, inicio, _ = FICHEIROS[tipo]
                    if pasta != pasta_no_zip or not regra.fullmatch(nome) or entrada.file_size > FICHEIRO_MAXIMO:
                        continue
                    conteudo = pacote.read(entrada)
                    if conteudo.startswith(inicio) and (tipo != "som" or conteudo[8:12] == b"WAVE"):
                        ficheiros.append((tipo, nome, conteudo))
            return fonte, ficheiros
        except (zipfile.BadZipFile, UnicodeDecodeError, RuntimeError, OSError):
            raise Falha("Não consegui ler esse ficheiro: está estragado, ou não é um jogo guardado pela Oficina.")

    def carregar(self, jogo, fonte, pacote=None):
        # "pacote" e o ficheiro que a crianca escolheu, em base64: o zip que o
        # "Guardar o meu jogo" da, ou um .py sozinho. ("fonte" e so o codigo.)
        with self.tranca:
            config = configuracao(jogo)
            ficheiros = []
            if pacote is not None:
                try:
                    dados = base64.b64decode(str(pacote), validate=True)
                except ValueError:
                    raise Falha("O ficheiro chegou estragado. Tenta outra vez.")
                fonte, ficheiros = self.abrir_pacote(config, dados)
            fonte = str(fonte or "").replace("\r\n", "\n")
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
            # So depois de o jogo ter sido aceite: as imagens e os sons que
            # vinham com ele, cada um na sua pasta.
            for tipo, nome, conteudo in ficheiros:
                pasta = FICHEIROS[tipo][0]
                os.makedirs(pasta, exist_ok=True)
                with open(os.path.join(pasta, nome) + ".novo", "wb") as f:
                    f.write(conteudo)
                os.replace(os.path.join(pasta, nome) + ".novo", os.path.join(pasta, nome))
            return {"ok": True, "imagens": len([f for f in ficheiros if f[0] == "imagem"]),
                    "sons": len([f for f in ficheiros if f[0] == "som"])}


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
                tipo = "application/zip" if resposta[0].endswith(".zip") else "text/x-python; charset=utf-8"
                self.responder(200, resposta[1], tipo,
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
            # "ligados": quantos computadores ajudantes estao a atender
            # (None enquanto ainda se esta a ver).
            self.responder(200, {"ha": sessao.ajudante.ha(), "total": len(sessao.ajudante.servidores),
                                 "ligados": sessao.ajudante.quantos_ligados()})
        elif url.path == "/api/estado":
            desde = int(parametros.get("desde", ["0"])[0])
            self.tratar(lambda: sessao.estado(desde))
        elif url.path == "/api/quadro":
            self.quadro(int(parametros.get("depois", ["0"])[0]))
        elif url.path == "/api/capa":
            nome = parametros.get("jogo", [""])[0]
            caminho = os.path.join(CAPAS, nome + ".png")
            if nome in JOGOS and os.path.isfile(caminho):
                with open(caminho, "rb") as f:
                    self.responder(200, f.read(), "image/png")
            else:
                self.responder(404, {"falha": "Não existe."})
        elif url.path in ("/api/imagem", "/api/som"):
            tipo = url.path[5:]
            try:
                self.responder(200, sessao.ler_ficheiro(tipo), "image/png" if tipo == "imagem" else "audio/wav")
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
        elif caminho == "/api/jogar":
            self.tratar(lambda: sessao.jogar(dados.get("jogo")))
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
        elif caminho in ("/api/imagem", "/api/som"):
            self.tratar(lambda: sessao.por_ficheiro(caminho[5:], dados.get("dados")))
        elif caminho in ("/api/tirar-imagem", "/api/tirar-som"):
            self.tratar(lambda: sessao.tirar_ficheiro(caminho[11:]))
        elif caminho == "/api/apagar":
            self.tratar(sessao.apagar)
        elif caminho == "/api/lista":
            self.tratar(lambda: sessao.lista(dados))
        elif caminho == "/api/caixas":
            self.tratar(lambda: sessao.caixas(dados))
        elif caminho == "/api/qual-imagem":
            self.tratar(lambda: sessao.escolher_imagem(dados.get("qual")))
        elif caminho == "/api/criar":
            self.tratar(lambda: sessao.criar(dados.get("jogo"), str(dados.get("grupo"))))
        elif caminho == "/api/pergunta":
            self.pergunta(dados)
        elif caminho == "/api/carregar":
            self.tratar(lambda: sessao.carregar(dados.get("jogo"), dados.get("fonte"), dados.get("pacote")))
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
