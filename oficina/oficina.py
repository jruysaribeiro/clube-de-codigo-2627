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
#     --verificar       so ve se este computador esta pronto para uma sessao
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
import hashlib
import importlib
import io
import json
import os
import queue
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
from urllib.request import urlopen

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)

import ajudante as modulo_do_ajudante  # noqa: E402
import blocos  # noqa: E402
import juntar as modulo_de_juntar  # noqa: E402
from jogos import JOGOS  # noqa: E402

ORIGINAIS = os.path.join(AQUI, ".originais")
JOGAR = "jogar"               # a "escolha" que quer dizer: o jogo inteiro (ver palco.py)
CAPAS = os.path.join(AQUI, "capas")       # a fotografia de cada jogo, para o cartao dele
# Os modelos de pixel art: um PNG para cada imagem que os jogos sabem
# mostrar, com o mesmo nome (galo.png). Usam-se tal como estao, ou serve de
# comeco no editor de desenho. (Quem os desenha e o fazer_modelos.py.)
MODELOS = os.path.join(AQUI, "modelos")
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
PASTA_DA_BASE = "base"            # no zip: o jogo de onde se partiu (ve "A base", mais abaixo)
ZIP_MAXIMO = 60000000             # bytes, tudo somado e fora do zip
ZIP_FICHEIROS = 500
LEIA_ME = ("Este é um jogo guardado na Oficina.\n\n"
           "Para continuares a mexer nele: abre a Oficina, entra no jogo, carrega em\n"
           "\"Abrir um jogo guardado\" e escolhe este ficheiro zip, tal como está.\n"
           "O jogo, as imagens e os sons vão cada um para o seu sítio.\n\n"
           "Para juntares o que fizeste ao jogo de um colega (ou ao da turma): na\n"
           "Oficina dele, \"Juntar jogos\", e escolhe este ficheiro.\n\n"
           "(A pasta \"base\" tem o jogo de onde partiste: é com ela que a Oficina\n"
           "descobre o que mudaste.)\n")
PACIENCIA = 6                 # segundos sem o jogo mostrar um frame: ficou preso
ARRANQUE = 60                 # segundos que um jogo pode levar a mostrar o primeiro (um computador lento)
PROVA = 15                    # segundos que o jogo tem para mostrar que o codigo novo corre (ve desprender)


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


def trocar_ficheiro(provisorio, caminho):
    # Poe o ficheiro novo no lugar do antigo, de uma vez. No Windows, um
    # antivirus (ou outro programa) a espreitar o ficheiro nao deixa troca-lo
    # durante uns instantes: tenta-se outra vez antes de desistir.
    for tentativa in range(40):
        try:
            os.replace(provisorio, caminho)
            return
        except PermissionError:
            if tentativa == 39:
                raise
            time.sleep(0.05)


def escrever_bytes(caminho, conteudo):
    with open(caminho + ".novo", "wb") as f:
        f.write(conteudo)
    trocar_ficheiro(caminho + ".novo", caminho)


def escrever(caminho, texto, fim_de_linha):
    escrever_bytes(caminho, texto.replace("\n", fim_de_linha).encode("utf-8"))


def caminho_do_original(config):
    return os.path.join(ORIGINAIS, os.path.basename(config.FICHEIRO))


def guardar_original(config):
    # Da primeira vez que se abre um jogo, fica uma copia do ficheiro tal
    # como estava. E dai que vem o botao "Repor o original".
    destino = caminho_do_original(config)
    if not os.path.exists(destino):
        os.makedirs(ORIGINAIS, exist_ok=True)
        shutil.copyfile(caminho_do_jogo(config), destino)


# --- A base: o jogo de onde se partiu ---
# Para juntar o que varias criancas fizeram (ve o juntar.py) e preciso saber
# de onde cada uma partiu. A Oficina guarda aqui esse jogo: o que veio no
# ultimo "Abrir um jogo guardado" ou "Juntar jogos" (ou, se nunca houve
# nenhum, o original). Vai dentro de cada zip do "Descarregar o meu jogo".
BASES = os.path.join(AQUI, ".bases")


def caminho_da_base(config):
    return os.path.join(BASES, os.path.basename(config.FICHEIRO))


def impressao(conteudo):
    return hashlib.sha1(conteudo).hexdigest()


def ficheiros_do_jogo(fonte):
    # As imagens e os sons de que o codigo fala e que existem nas pastas:
    # [(tipo, nome, caminho)].
    nomes = set()
    try:
        for no in ast.walk(ast.parse(fonte)):
            if isinstance(no, ast.Constant) and isinstance(no.value, str):
                nomes.add(no.value)
    except (SyntaxError, ValueError):
        return []
    lista = []
    for tipo in PASTAS_DO_ZIP:
        pasta, regra, _, _ = FICHEIROS[tipo]
        for nome in sorted(nomes):
            if regra.fullmatch(nome) and os.path.isfile(os.path.join(pasta, nome)):
                lista.append((tipo, nome, os.path.join(pasta, nome)))
    return lista


def ler_base(config):
    # (o codigo da base, {"feito": quando, "imagens": {"imagens/galo.png": a
    # impressao digital do ficheiro nessa altura}}).
    caminho = caminho_da_base(config)
    if os.path.exists(caminho):
        fonte, _ = ler(caminho)
        try:
            with open(caminho + ".json", encoding="utf-8") as f:
                info = json.load(f)
        except (OSError, ValueError):
            info = {}
    else:
        original = caminho_do_original(config)
        fonte, _ = ler(original if os.path.exists(original) else caminho_do_jogo(config))
        info = {}
    return fonte, info_certa(info)


def info_certa(info):
    info = info if isinstance(info, dict) else {}
    feito = info.get("feito")
    imagens = info.get("imagens")
    return {"feito": feito if isinstance(feito, (int, float)) and not isinstance(feito, bool) else 0,
            "imagens": {str(k): str(v) for k, v in imagens.items()} if isinstance(imagens, dict) else {}}


def guardar_base(config, fonte, info=None):
    # Sem "info", a base e de agora: fica com a hora e com as impressoes
    # digitais das imagens e dos sons que o jogo usa neste momento.
    if info is None:
        info = {"feito": time.time(), "imagens": {}}
        for tipo, nome, caminho in ficheiros_do_jogo(fonte):
            with open(caminho, "rb") as f:
                info["imagens"][PASTAS_DO_ZIP[tipo] + "/" + nome] = impressao(f.read())
    os.makedirs(BASES, exist_ok=True)
    escrever(caminho_da_base(config), fonte, "\n")
    escrever_bytes(caminho_da_base(config) + ".json", json.dumps(info).encode("utf-8"))


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
        # O ultimo codigo que correu no jogo sem rebentar e ainda nao foi
        # guardado: (o numero do pedido, o ficheiro inteiro). So vai para o
        # ficheiro quando a crianca carrega em "Guardar alteracoes".
        self.provado = None
        self.a_provar = None         # (numero, hora) do codigo que o jogo esta a experimentar
        # Cada vez que se abre uma coisa (ou o jogo inteiro) ha um numero novo.
        # A pagina manda-o com cada pedido: um pedido com um numero antigo vem
        # de outro separador (ou de antes de a Oficina voltar a arrancar), que
        # ainda julga ter aberta outra coisa, e nao se lhe faz a vontade.
        self.abertura = int(time.time() * 1000) % 1000000000
        # Para dar por um jogo preso: quando foi lancado, a ultima vez que deu
        # sinal de vida (um frame, uma mensagem), se ja chegou ao primeiro frame, e
        # a ultima vez que a pagina perguntou por ele.
        self.lancado = 0
        self.sinal = 0
        self.arrancou = False
        self.pronto_desde = 0        # quando chegou ao primeiro frame
        self.perguntado = 0
        self.fila_do_jogo = None     # o que ha para dizer ao jogo (ve escrever_ao_jogo)
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
                    self.sinal = time.time()
                    if not self.arrancou:
                        self.arrancou = True
                        self.pronto_desde = self.sinal
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
        self.lancado = time.time()
        self.sinal = self.lancado
        self.arrancou = False
        self.fila_do_jogo = queue.Queue()
        threading.Thread(target=self.escrever_ao_jogo, args=(processo, self.fila_do_jogo), daemon=True).start()
        threading.Thread(target=self.ouvir, args=(processo,), daemon=True).start()

    def escrever_ao_jogo(self, processo, fila):
        # (Corre a parte.) Quem escreve ao jogo e so este fio. Um jogo preso
        # deixa de ler o que se lhe escreve e, com o cano cheio, quem escreve
        # fica parado: se fosse quem tem a tranca da sessao, a Oficina inteira
        # ficava parada com ele, e ja nem dava para o fechar.
        while True:
            linha = fila.get()
            if linha is None:
                return
            try:
                processo.stdin.write(linha)
                processo.stdin.flush()
            except (OSError, ValueError):
                return

    def parar(self):
        processo = self.processo
        fila = self.fila_do_jogo
        self.processo = None
        self.fila_do_jogo = None
        if processo is not None and processo.poll() is None:
            fila.put(json.dumps({"tipo": "sair"}) + "\n")
            try:
                processo.wait(timeout=1.5)
            except subprocess.TimeoutExpired:
                processo.kill()
        if fila is not None:
            fila.put(None)

    def viva(self):
        return self.processo is not None and self.processo.poll() is None

    def dizer(self, pedido):
        if not self.viva():
            self.lancar()
        self.fila_do_jogo.put(json.dumps(pedido) + "\n")

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
                    self.sinal = time.time()
                    if not self.arrancou:
                        self.arrancou = True
                        self.pronto_desde = self.sinal
                    if mensagem.get("tipo") != "pronto":     # (essa e so o sinal de que arrancou)
                        self.receber(mensagem)

    def receber(self, mensagem):
        pedido = self.pedidos.get(mensagem.get("id"))
        if mensagem["tipo"] in ("estavel", "erro", "problemas", "fechou"):
            if self.a_provar is not None and mensagem.get("id") in (None, self.a_provar[0]):
                self.a_provar = None
        if mensagem["tipo"] == "estavel" and pedido is not None:
            # Correu uns frames sem rebentar: ja pode ser guardado. (Guardar
            # e com o botao: ve guardar, mais abaixo.)
            self.provado = (mensagem["id"], pedido[2])
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
            if mensagem["linha"] is None and mensagem.get("linhas"):
                # O erro nao esta no bocado aberto: diz-se em que coisa esta,
                # para se poder ir la corrigi-la.
                mensagem["onde"] = self.onde_fica(mensagem["linhas"][-1], pedido[2] if pedido is not None else None)
        self.mensagens.append(mensagem)
        del self.mensagens[:-200]
        self.contador = self.contador + 1
        mensagem["n"] = self.contador

    def onde_fica(self, linha, fonte=None):
        # A coisa da Oficina (um bicho, uma funcao...) onde esta uma linha do
        # ficheiro do jogo: {"escolha", "titulo", "grupo"}, ou None se essa
        # linha nao e de nenhuma. Havendo varias (uma onda, e as ondas
        # todas), fica a mais pequena.
        try:
            if fonte is None:
                fonte, _ = ler(caminho_do_jogo(self.config))
            melhor = None
            for escolha in self.config.escolhas(fonte):
                regiao = self.config.regiao(fonte, escolha["id"])
                if regiao is None or not regiao["inicio"] <= linha <= regiao["fim"]:
                    continue
                tamanho = regiao["fim"] - regiao["inicio"]
                if melhor is None or tamanho < melhor[0]:
                    melhor = (tamanho, {"escolha": escolha["id"], "titulo": escolha["titulo"], "grupo": escolha["grupo"]})
            if melhor is None or melhor[1]["escolha"] == self.escolha:
                return None
            return melhor[1]
        except Exception:
            return None          # e so uma ajuda: se nao se descobrir, o erro mostra-se como dantes

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
                    "instrucoes": getattr(config, "INSTRUCOES", None),
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
            self.provado = None
            self.mensagens = []
            self.a_provar = None
            self.abertura = self.abertura + 1
            self.lancar()
            return {
                "abertura": self.abertura,
                "codigo": "\n".join(blocos.tirar_margem(bloco, self.margem)),
                "titulo": regiao["titulo"], "ajuda": regiao["ajuda"], "dica": regiao["dica"],
                "jogo": config.NOME, "desde": self.contador, "imagem": self.estado_da_imagem(),
                "som": self.estado_do_ficheiro("som"),
                "sugestoes": regiao.get("sugestoes") or [],
                # O que dizem os botoes de apagar esta coisa e de escolher de
                # uma lista (None se aqui nao os ha).
                "apagar": regiao.get("apagar"), "lista": regiao.get("lista"),
                "renomear": regiao.get("renomear"),
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
            self.provado = None
            self.mensagens = []
            self.a_provar = None
            self.abertura = self.abertura + 1
            self.lancar()
            return {"jogo": config.NOME, "desde": self.contador, "abertura": self.abertura}

    def nome_escrito(self, bloco):
        # Se a crianca mudou, no codigo, o nome da coisa aberta (e essa coisa
        # tem "Mudar o nome"), devolve o nome novo. Senao, None.
        if not hasattr(self.config, "renomear"):
            return None
        fonte = "\n".join(self.antes + blocos.por_margem(bloco, self.margem) + self.depois)
        try:
            regiao = self.config.regiao(fonte, self.escolha)
        except (SyntaxError, ValueError):
            return None
        if not regiao or not regiao.get("renomear"):
            return None
        novo = regiao.get("titulo")
        if not isinstance(novo, str) or novo == self.titulo or novo == self.escolha:
            return None
        return novo

    def mudar_nome_escrito(self, novo):
        # Muda o nome no ficheiro, em todos os sitios onde a coisa e usada
        # (como o botao "Mudar o nome"), e abre o jogo outra vez ja com ele:
        # o resto do que a crianca escreveu segue depois, pelo caminho de
        # sempre. Devolve (a frase a contar o que se fez, None) ou (None, o
        # motivo por que nao deu).
        caminho = caminho_do_jogo(self.config)
        fonte, fim_de_linha = ler(caminho)
        try:
            nova, _, aviso = self.config.renomear(fonte, self.escolha, novo)
            compile(nova, self.config.FICHEIRO, "exec")
            regiao = self.config.regiao(nova, self.escolha)
            if regiao is None:
                raise ValueError("deixei de encontrar a coisa com o nome novo")
        except (SyntaxError, ValueError) as erro:
            return None, str(erro)
        escrever(caminho, nova, fim_de_linha)
        linhas = nova.split("\n")
        self.antes = linhas[:regiao["inicio"] - 1]
        self.depois = linhas[regiao["fim"]:]
        self.titulo = regiao["titulo"]
        self.pedidos = {}
        self.provado = None
        self.a_provar = None
        self.lancar()
        return aviso, None

    def codigo(self, texto, mudar_nome=False):
        with self.tranca:
            if self.config is None or self.escolha == JOGAR:
                raise Falha("Ainda não escolheste nada.")
            bloco = texto.replace("\r\n", "\n").rstrip().split("\n")
            if all(linha.strip() == "" or linha.lstrip().startswith("#") for linha in bloco):
                # Sem isto, apagar a ficha de um inimigo (ou de um bicho, de
                # uma onda...) tirava-o do jogo sem o tirar dos sitios onde
                # e usado, e o jogo parava mais tarde, ja longe daqui.
                return {"ok": False, "erro": {
                    "linha": None,
                    "texto": "Apagaste o código todo. O jogo precisa deste bocado: escreve-o outra vez, ou carrega em "
                             "«Repor o original». Para tirar uma coisa do jogo há o botão vermelho de apagar, "
                             "nas coisas que se podem apagar.",
                    "detalhe": ""}}
            # O nome da coisa foi mudado no codigo? Da primeira vez so se
            # avisa a pagina, que espera que a crianca acabe de o escrever e
            # volta a mandar o codigo com "mudar_nome".
            aviso_do_nome = None
            nome = self.nome_escrito(bloco)
            if nome is not None:
                if not mudar_nome:
                    return {"ok": False, "nome": {"antigo": self.titulo, "novo": nome}}
                aviso_do_nome, motivo = self.mudar_nome_escrito(nome)
                if motivo is not None:
                    return {"ok": False, "erro": {"linha": 1, "texto": "Não deu para mudar o nome: " + motivo,
                                                  "detalhe": "O nome antigo era \"" + str(self.titulo) + "\"."}}
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
            if aviso_do_nome is not None:
                return {"ok": True, "id": self.numero, "titulo": self.titulo, "aviso": aviso_do_nome}
            return {"ok": True, "id": self.numero}

    def guardar(self, numero):
        # O botao "Guardar alteracoes": o codigo que esta a correr no jogo
        # sem erros vai para o ficheiro. "numero" e o pedido que a pagina
        # julga estar provado: se entretanto se escreveu mais, ainda nao da.
        with self.tranca:
            if self.config is None or self.escolha == JOGAR:
                raise Falha("Ainda não escolheste nada.")
            if self.provado is None or self.provado[0] != numero:
                raise Falha("Ainda não dá para guardar: o jogo ainda está a experimentar o que escreveste, "
                            "ou há um erro. Espera um bocadinho e tenta outra vez.")
            escrever(caminho_do_jogo(self.config), self.provado[1], self.fim_de_linha)
            self.provado = None
            return {"ok": True}

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
        # gigante, um ciclo sem fim). Um jogo a correr mostra frames sem
        # parar: se esta vivo e deixou de os mostrar, fecha-se e abre-se outra
        # vez com o ultimo ficheiro bom. Tanto faz se ficou preso com o codigo
        # que acabou de chegar ou mais tarde (numa funcao que so corre quando
        # se carrega numa tecla, por exemplo).
        agora = time.time()
        parado = agora - self.perguntado > 2
        self.perguntado = agora
        if not self.viva():
            if self.processo is not None and self.a_provar is not None:
                # O jogo fechou-se sozinho com o codigo que estava a
                # experimentar (um "raise SystemExit", ou rebentou de vez):
                # abre-se outra vez como estava, com o aviso.
                numero = self.a_provar[0]
                self.a_provar = None
                self.lancar()
                self.receber({"tipo": "erro", "id": numero, "linhas": [],
                              "texto": "O jogo fechou-se com este código. Voltei a abri-lo como estava antes.",
                              "detalhe": "o jogo deixou de correr enquanto experimentava o código"})
            return
        if parado:
            # Ninguem perguntava pelo jogo ha um bocado (o computador esteve
            # a dormir, a pagina esteve escondida): a paciencia conta de agora.
            self.sinal = agora
            return
        # (Ate ao primeiro frame da-se mais tempo: num computador lento, so
        # abrir o pygame leva uns segundos.)
        preso = agora - self.sinal >= (PACIENCIA if self.arrancou else ARRANQUE)
        # Ha codigo que nao prende o jogo mas o deixa a passo de caracol (um
        # ciclo com milhoes de voltas em cada frame): ainda mostra um frame de
        # vez em quando, mas nunca mais acaba de experimentar o codigo.
        lento = (self.a_provar is not None and self.arrancou
                 and agora - max(self.a_provar[1], self.pronto_desde) >= PROVA)
        if not preso and not lento:
            return
        numero = self.a_provar[0] if self.a_provar is not None else None
        calado = round(agora - self.sinal)
        self.a_provar = None
        self.processo.kill()
        self.lancar()
        if preso and numero is not None:
            texto = ("O jogo ficou preso com este código. Há algum número grande demais, "
                     "ou um ciclo que nunca acaba? Voltei a abrir o jogo como estava antes.")
            detalhe = "sem dar sinal durante " + str(calado) + " segundos"
        elif preso:
            texto = ("O jogo ficou preso e deixou de responder. Há um ciclo que nunca acaba, "
                     "ou um número grande demais, numa das coisas que mudaste? Voltei a abri-lo.")
            detalhe = "sem dar sinal durante " + str(calado) + " segundos"
        else:
            texto = ("O jogo ficou lento demais com este código. Há um ciclo com voltas a mais, "
                     "ou algum número grande demais? Voltei a abrir o jogo como estava antes.")
            detalhe = "ao fim de " + str(PROVA) + " segundos ainda não tinha acabado de o experimentar"
        self.receber({"tipo": "erro", "id": numero, "linhas": [], "texto": texto, "detalhe": detalhe})

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
            self.abertura = self.abertura + 1
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
        if estado is not None and not estado["erro"]:
            estado["modelo"] = os.path.isfile(os.path.join(MODELOS, estado["nome"]))
        if estado is not None and len(self.imagens) > 1:
            estado["opcoes"] = [imagem["nome"] for imagem in self.imagens]
            estado["qual"] = self.qual_imagem
            # Quais delas ja existem: e de uma dessas que se pode copiar o
            # desenho para comecar outra (a de costas a partir da de frente).
            pasta, forma = FICHEIROS["imagem"][0], FICHEIROS["imagem"][1]
            estado["ha_opcoes"] = [bool(forma.fullmatch(str(imagem["ficheiro"])))
                                   and os.path.isfile(os.path.join(pasta, str(imagem["ficheiro"])))
                                   for imagem in self.imagens]
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
            escrever_bytes(caminho, conteudo)
            self.avisar_dos_ficheiros()
            # (A imagem leva tambem quais sao as outras imagens da coisa.)
            return {tipo: self.estado_da_imagem() if tipo == "imagem" else self.estado_do_ficheiro(tipo)}

    def tirar_ficheiro(self, tipo):
        with self.tranca:
            caminho = self.caminho_do_ficheiro(tipo)
            if os.path.isfile(caminho):
                os.remove(caminho)
            self.avisar_dos_ficheiros()
            # (A imagem leva tambem quais sao as outras imagens da coisa.)
            return {tipo: self.estado_da_imagem() if tipo == "imagem" else self.estado_do_ficheiro(tipo)}

    def ler_ficheiro(self, tipo, qual=None):
        # qual: nas coisas com varias imagens, o numero de outra que nao a
        # escolhida (para copiar o desenho dela).
        with self.tranca:
            caminho = self.caminho_do_ficheiro(tipo)
            if tipo == "imagem" and qual is not None:
                pasta, forma = FICHEIROS["imagem"][0], FICHEIROS["imagem"][1]
                if not 0 <= qual < len(self.imagens) or not forma.fullmatch(str(self.imagens[qual]["ficheiro"])):
                    raise Falha("Essa imagem não existe.")
                caminho = os.path.join(pasta, self.imagens[qual]["ficheiro"])
            if not os.path.isfile(caminho):
                raise Falha("Ainda não há.")
            with open(caminho, "rb") as f:
                return f.read()

    def modelos(self):
        # Os nomes dos modelos que ha, com o da imagem aberta em primeiro.
        nomes = sorted(nome for nome in os.listdir(MODELOS) if nome.lower().endswith(".png")) \
            if os.path.isdir(MODELOS) else []
        meu = self.imagem if isinstance(self.imagem, str) else None
        if meu in nomes:
            nomes.remove(meu)
            nomes.insert(0, meu)
        return {"modelos": nomes, "meu": meu if meu in nomes else None}

    def ler_modelo(self, nome):
        if not FICHEIROS["imagem"][1].fullmatch(str(nome)) or not os.path.isfile(os.path.join(MODELOS, str(nome))):
            raise Falha("Esse modelo não existe.")
        with open(os.path.join(MODELOS, str(nome)), "rb") as f:
            return f.read()

    # --- Criar uma coisa nova ---

    def criar(self, jogo, grupo, qual=None):
        # Um inimigo novo, uma torre nova: quem sabe faze-los e o ficheiro
        # do jogo em oficina/jogos/, que devolve o ficheiro ja com a coisa
        # nova la dentro (uma copia de uma que ja existia, com outro nome).
        with self.tranca:
            config = configuracao(jogo)
            criaveis = getattr(config, "CRIAVEIS", {})
            if grupo not in criaveis:
                raise Falha("Aqui não dá para criar isso.")
            # (Um grupo com varios botoes "+": o CRIAVEIS dele e uma lista, e
            # "qual" diz em qual se carregou.)
            varios = isinstance(criaveis[grupo], list)
            if varios and qual not in criaveis[grupo]:
                raise Falha("Aqui não dá para criar isso.")
            guardar_original(config)
            caminho = caminho_do_jogo(config)
            fonte, fim_de_linha = ler(caminho)
            try:
                nova, escolha, aviso = config.novo(fonte, grupo, qual) if varios else config.novo(fonte, grupo)
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

    def renomear(self, nome):
        # Muda o nome a coisa aberta em todos os sitios onde esta escrito
        # (quem sabe quais sao e o ficheiro do jogo em oficina/jogos/).
        with self.tranca:
            config = self.config
            if config is None or self.escolha == JOGAR or not hasattr(config, "renomear"):
                raise Falha("A isto não se pode mudar o nome aqui.")
            caminho = caminho_do_jogo(config)
            fonte, fim_de_linha = ler(caminho)
            try:
                nova, escolha, aviso = config.renomear(fonte, self.escolha, nome)
                compile(nova, config.FICHEIRO, "exec")
                if escolha not in [e["id"] for e in config.escolhas(nova)]:
                    raise ValueError("deixei de encontrar a coisa com o nome novo")
            except (SyntaxError, ValueError) as erro:
                raise Falha("Não deu para mudar o nome: " + str(erro))
            self.parar()
            self.config = None
            shutil.copyfile(caminho, caminho + ".anterior")
            escrever(caminho, nova, fim_de_linha)
            return {"escolha": escolha, "aviso": aviso}

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

    def desenhar(self, dados):
        # No editor de desenho: o aluno descreve um boneco, e o ajudante
        # devolve os quadradinhos pintados (um rascunho, para retocar).
        pedido = str(dados.get("pedido") or "").strip()
        if pedido == "":
            raise Falha("Escreve primeiro o que queres que ele desenhe.")
        resposta = "".join(self.ajudante.perguntar(modulo_do_ajudante.mensagens_do_desenho(pedido)))
        cores, frase, ordens = modulo_do_ajudante.desenho(resposta)
        if all(cor is None for cor in cores):
            raise Falha("O ajudante não conseguiu desenhar isso. Tenta descrever de outra maneira.")
        return {"lado": modulo_do_ajudante.LADO_DO_DESENHO, "pixeis": cores, "texto": frase}

    # --- Levar o jogo para casa e traze-lo de volta ---

    def descarregar(self, jogo):
        # Um zip com o ficheiro do jogo e as imagens e os sons de que ele
        # fala (os nomes escritos no codigo que existam nas pastas): e tudo o
        # que e preciso para continuar noutro computador.
        config = configuracao(jogo)
        nome = os.path.basename(config.FICHEIRO)
        with open(caminho_do_jogo(config), "rb") as f:
            jogo_em_bytes = f.read()
        base, info = ler_base(config)
        memoria = io.BytesIO()
        with zipfile.ZipFile(memoria, "w", zipfile.ZIP_DEFLATED) as pacote:
            pacote.writestr(nome, jogo_em_bytes)
            pacote.writestr("LEIA-ME.txt", LEIA_ME)
            try:
                for tipo, ficheiro, caminho in ficheiros_do_jogo(jogo_em_bytes.decode("utf-8")):
                    pacote.write(caminho, PASTAS_DO_ZIP[tipo] + "/" + ficheiro)
            except UnicodeDecodeError:
                pass             # um jogo estragado vai na mesma, so sem imagens
            # O jogo de onde se partiu, para o "Juntar jogos".
            pacote.writestr(PASTA_DA_BASE + "/" + nome, base)
            pacote.writestr(PASTA_DA_BASE + "/base.json", json.dumps(info))
        return os.path.splitext(nome)[0] + ".zip", memoria.getvalue()

    def abrir_pacote(self, config, dados):
        # O que vem num jogo guardado: (o codigo do jogo, [(tipo, nome,
        # conteudo), ...] com as imagens e os sons, e a base: (o codigo de
        # onde se partiu, a informacao dela) ou None). Um ficheiro .py
        # sozinho, como os que a Oficina guardava antes, tambem serve.
        if not zipfile.is_zipfile(io.BytesIO(dados)):
            try:
                return dados.decode("utf-8"), [], None
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
            base = None
            da_base = {caminhos[e].partition("/")[2]: e for e in entradas if caminhos[e].startswith(PASTA_DA_BASE + "/")}
            escrita = da_base.get(os.path.basename(config.FICHEIRO))
            if escrita is not None and escrita.file_size <= ZIP_MAXIMO:
                info = {}
                if "base.json" in da_base and da_base["base.json"].file_size <= FICHEIRO_MAXIMO:
                    try:
                        info = json.loads(pacote.read(da_base["base.json"]).decode("utf-8"))
                    except ValueError:
                        info = {}
                base = (pacote.read(escrita).decode("utf-8").replace("\r\n", "\n"), info_certa(info))
            return fonte, ficheiros, base
        except (zipfile.BadZipFile, UnicodeDecodeError, RuntimeError, OSError):
            raise Falha("Não consegui ler esse ficheiro: está estragado, ou não é um jogo guardado pela Oficina.")

    def carregar(self, jogo, fonte, pacote=None):
        # "pacote" e o ficheiro que a crianca escolheu, em base64: o zip que o
        # "Descarregar o meu jogo" da, ou um .py sozinho. ("fonte" e so o codigo.)
        with self.tranca:
            config = configuracao(jogo)
            ficheiros = []
            base = None
            if pacote is not None:
                try:
                    dados = base64.b64decode(str(pacote), validate=True)
                except ValueError:
                    raise Falha("O ficheiro chegou estragado. Tenta outra vez.")
                fonte, ficheiros, base = self.abrir_pacote(config, dados)
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
                escrever_bytes(os.path.join(pasta, nome), conteudo)
            # De onde este jogo partiu: o que o zip disser ou, se nao disser
            # (um jogo sozinho, ou um zip antigo), ele proprio.
            if base is not None:
                guardar_base(config, base[0], base[1])
            else:
                guardar_base(config, fonte)
            return {"ok": True, "imagens": len([f for f in ficheiros if f[0] == "imagem"]),
                    "sons": len([f for f in ficheiros if f[0] == "som"])}

    # --- Juntar jogos ---

    def juntar(self, jogo, pacotes, decisoes=None):
        # Junta ao jogo que esta neste computador o que vem noutros jogos
        # guardados (ve o juntar.py). pacotes: [{"nome", "dados" em base64}].
        # Enquanto houver duvidas nao se escreve nada: devolve-as, e a pagina
        # volta a pedir com as decisoes.
        with self.tranca:
            config = configuracao(jogo)
            if not isinstance(pacotes, list) or len(pacotes) == 0:
                raise Falha("Escolhe pelo menos um jogo guardado para juntar ao teu.")
            if len(pacotes) > 40:
                raise Falha("São jogos demais de uma vez: junta até 40.")
            caminho = caminho_do_jogo(config)
            daqui, fim_de_linha = ler(caminho)
            base_daqui, info_daqui = ler_base(config)
            avisos = []

            # Quem entra: este computador, e cada jogo escolhido.
            entram = [{"quem": "este computador", "base": base_daqui, "info": info_daqui, "agora": daqui, "ficheiros": {}}]
            for tipo, nome, onde in ficheiros_do_jogo(daqui):
                with open(onde, "rb") as f:
                    entram[0]["ficheiros"][(tipo, nome)] = f.read()
            for numero, pacote in enumerate(pacotes):
                pacote = pacote if isinstance(pacote, dict) else {}
                nome = re.sub(r"\.(zip|py)$", "", str(pacote.get("nome") or "jogo " + str(numero + 1)), flags=re.IGNORECASE)[:40]
                while nome in [outro["quem"] for outro in entram]:
                    nome = nome + " (outro)"
                try:
                    dados = base64.b64decode(str(pacote.get("dados")), validate=True)
                except ValueError:
                    raise Falha('O ficheiro "' + nome + '" chegou estragado. Tenta outra vez.')
                if str(pacote.get("nome", "")).lower().endswith(".zip") and not zipfile.is_zipfile(io.BytesIO(dados)):
                    raise Falha('"' + nome + '" não é um jogo guardado pela Oficina.')
                fonte, ficheiros, base = self.abrir_pacote(config, dados)
                fonte = fonte.replace("\r\n", "\n")
                try:
                    reconhecido = len(config.escolhas(fonte)) > 0
                except (SyntaxError, ValueError):
                    raise Falha('O jogo "' + nome + '" tem um erro de Python e não dá para juntar. Abre-o e corrige-o primeiro.')
                if not reconhecido:
                    raise Falha('"' + nome + '" não parece ser o ' + config.NOME + ".")
                if base is None:
                    avisos.append('"' + nome + '" não diz de que jogo partiu (é de uma Oficina mais antiga): comparei-o '
                                  "com o jogo de onde este computador partiu.")
                    base = (base_daqui, dict(info_daqui))
                entram.append({"quem": nome, "base": base[0], "info": base[1], "agora": fonte,
                               "ficheiros": {(tipo, nome_dele): conteudo for tipo, nome_dele, conteudo in ficheiros}})

            # As imagens e os sons. Um ficheiro so conta como "desta crianca"
            # se nao for igual ao que ela tinha quando partiu. Dois ficheiros
            # diferentes com o mesmo nome: se sao de coisas novas, o segundo
            # muda de nome (e o codigo dessa crianca tambem); se sao de uma
            # coisa que ja existia, fica o primeiro.
            todos = {chave for entra in entram for chave in entra["ficheiros"]}
            donos = {}
            for entra in entram:
                for (tipo, nome), conteudo in list(entra["ficheiros"].items()):
                    marca = impressao(conteudo)
                    if entra["info"]["imagens"].get(PASTAS_DO_ZIP[tipo] + "/" + nome) == marca:
                        continue
                    if (tipo, nome) not in donos:
                        donos[(tipo, nome)] = (marca, entra["quem"], conteudo)
                    elif donos[(tipo, nome)][0] != marca:
                        del entra["ficheiros"][(tipo, nome)]
                        if '"' + nome + '"' in entra["base"]:
                            avisos.append('"' + nome + '" foi mudado em mais do que um jogo: ficou o de «'
                                          + donos[(tipo, nome)][1] + "».")
                            continue
                        corpo, ponto, fim = nome.rpartition(".")
                        numero = 2
                        while (tipo, corpo + "-" + str(numero) + ponto + fim) in todos:
                            numero = numero + 1
                        novo = corpo + "-" + str(numero) + ponto + fim
                        todos.add((tipo, novo))
                        entra["ficheiros"][(tipo, novo)] = conteudo
                        entra["agora"] = entra["agora"].replace('"' + nome + '"', '"' + novo + '"')
                        donos[(tipo, novo)] = (marca, entra["quem"], conteudo)
                        avisos.append('Havia dois "' + nome + '" diferentes: o de «' + entra["quem"]
                                      + '» passou a chamar-se "' + novo + '".')

            # O tronco: a base mais recente de todas.
            tronco = max(entram, key=lambda entra: entra["info"]["feito"])["base"]
            # (Nao tem de ser a base de todos: de cada jogo conta so o que
            # mudou desde a base dele.)
            try:
                junto = modulo_de_juntar.juntar(config, tronco, [(e["quem"], e["base"], e["agora"]) for e in entram], decisoes)
                if not junto["duvidas"]:
                    compile(junto["fonte"], config.FICHEIRO, "exec")
                    if len(config.escolhas(junto["fonte"])) == 0:
                        raise ValueError("o jogo ficou sem nada")
            except Falha:
                raise
            except Exception as erro:
                raise Falha("Não consegui juntar estes jogos (" + type(erro).__name__ + ": " + str(erro)[:200]
                            + "). Não mudei nada.")
            avisos = avisos + junto["avisos"]
            if junto["duvidas"]:
                return {"duvidas": junto["duvidas"], "avisos": avisos}

            guardar_original(config)
            self.parar()
            self.config = None
            shutil.copyfile(caminho, caminho + ".anterior")
            escrever(caminho, junto["fonte"], fim_de_linha)
            for entra in entram[1:]:
                for (tipo, nome), conteudo in entra["ficheiros"].items():
                    pasta = FICHEIROS[tipo][0]
                    destino = os.path.join(pasta, nome)
                    dono = donos.get((tipo, nome))
                    if (dono is not None and dono[1] == entra["quem"]) or (dono is None and not os.path.exists(destino)):
                        os.makedirs(pasta, exist_ok=True)
                        escrever_bytes(destino, conteudo)
            # (Um ficheiro a que o jogo mudou o nome ao juntar: ve o
            # "renomeados" do juntar_preparar.)
            estado = junto.get("estado")
            for quem, antigo, novo in estado.get("renomeados", []) if isinstance(estado, dict) else []:
                for entra in entram:
                    for tipo in PASTAS_DO_ZIP:
                        conteudo = entra["ficheiros"].get((tipo, antigo))
                        _, regra, _, _ = FICHEIROS[tipo]
                        if entra["quem"] == quem and conteudo is not None and regra.fullmatch(str(novo)):
                            os.makedirs(FICHEIROS[tipo][0], exist_ok=True)
                            escrever_bytes(os.path.join(FICHEIROS[tipo][0], novo), conteudo)
            guardar_base(config, junto["fonte"])
            frases = {"novo": "Novo", "mudou": "Mudado", "juntei": "Juntei as mudanças de vários", "escolhido": "Escolheste"}
            feito = [frases[que] + ": " + onde + " — " + ", ".join(quem) for quem, que, onde in junto["relato"]
                     if quem != ["este computador"]]
            return {"ok": True, "feito": feito, "avisos": avisos}


sessao = Sessao()


# =====================================================================
#                           O SERVIDOR
# =====================================================================

OUTRO_SEPARADOR = ("Esta página ficou para trás: a Oficina foi aberta noutro separador, "
                   "ou voltou a arrancar. Carrega em «Continuar aqui».")


class Servidor(ThreadingHTTPServer):

    # No Windows, "reutilizar o endereco" deixa dois programas ficarem com a
    # mesma porta: uma segunda Oficina abria por cima da primeira e os pedidos
    # da pagina iam ora para uma, ora para a outra.
    allow_reuse_address = os.name != "nt"

    def handle_error(self, request, client_address):
        # Uma pagina que fecha a meio de um pedido nao e um erro: nao enche o
        # terminal. O resto mostra-se, numa linha.
        erro = sys.exc_info()[1]
        if not isinstance(erro, (ConnectionError, TimeoutError)):
            print("Erro da Oficina: " + type(erro).__name__ + ": " + str(erro))


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
        except ConnectionError:
            pass                    # a pagina fechou
        except Exception as erro:   # um erro nosso: mostra-se, nao se esconde
            self.responder(500, {"falha": "Erro da Oficina: " + type(erro).__name__ + ": " + str(erro)})

    def do_GET(self):
        url = urlparse(self.path)
        parametros = parse_qs(url.query)
        if url.path == "/":
            with open(os.path.join(AQUI, "editor.html"), "rb") as f:
                self.responder(200, f.read(), "text/html; charset=utf-8")
        elif url.path == "/api/ola":
            # Para uma Oficina que arranca saber que ja ha outra aberta, e se
            # e a desta pasta (ve main).
            self.responder(200, {"oficina": AQUI})
        elif url.path == "/api/jogos":
            self.tratar(sessao.lista_de_jogos)
        elif url.path == "/api/ajudante":
            # "ligados": quantos computadores ajudantes estao a atender
            # (None enquanto ainda se esta a ver).
            self.responder(200, {"ha": sessao.ajudante.ha(), "total": len(sessao.ajudante.servidores),
                                 "ligados": sessao.ajudante.quantos_ligados()})
        elif url.path == "/api/estado":
            desde = int(parametros.get("desde", ["0"])[0])
            abertura = parametros.get("abertura", [None])[0]
            if abertura is not None and abertura != str(sessao.abertura):
                self.responder(409, {"falha": OUTRO_SEPARADOR})
            else:
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
            qual = parametros.get("qual", [""])[0]
            try:
                dados = sessao.ler_ficheiro(tipo, int(qual) if qual.isdigit() else None)
                self.responder(200, dados, "image/png" if tipo == "imagem" else "audio/wav")
            except Falha as falha:
                self.responder(404, {"falha": str(falha)})
        elif url.path == "/api/modelos":
            self.tratar(sessao.modelos)
        elif url.path == "/api/modelo":
            try:
                self.responder(200, sessao.ler_modelo(parametros.get("nome", [""])[0]), "image/png")
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
        if not isinstance(dados, dict):
            self.responder(400, {"falha": "Pedido mal feito."})
            return
        if dados.get("abertura") is not None and dados["abertura"] != sessao.abertura:
            # Um separador que ficou para tras (ve "abertura", na Sessao). O
            # rato e as teclas dele deitam-se fora sem aviso: sao pedidos que
            # ja vinham a caminho quando se abriu outra coisa.
            if caminho == "/api/entrada":
                self.responder(200, {"ok": True})
            else:
                self.responder(409, {"falha": OUTRO_SEPARADOR})
            return
        if caminho == "/api/abrir":
            self.tratar(lambda: sessao.abrir(dados.get("jogo"), str(dados.get("escolha"))))
        elif caminho == "/api/jogar":
            self.tratar(lambda: sessao.jogar(dados.get("jogo")))
        elif caminho == "/api/codigo":
            self.tratar(lambda: sessao.codigo(str(dados.get("codigo", "")), dados.get("mudar_nome") is True))
        elif caminho == "/api/guardar":
            self.tratar(lambda: sessao.guardar(dados.get("id")))
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
        elif caminho == "/api/renomear":
            self.tratar(lambda: sessao.renomear(dados.get("nome")))
        elif caminho == "/api/lista":
            self.tratar(lambda: sessao.lista(dados))
        elif caminho == "/api/caixas":
            self.tratar(lambda: sessao.caixas(dados))
        elif caminho == "/api/qual-imagem":
            self.tratar(lambda: sessao.escolher_imagem(dados.get("qual")))
        elif caminho == "/api/criar":
            self.tratar(lambda: sessao.criar(dados.get("jogo"), str(dados.get("grupo")), dados.get("qual")))
        elif caminho == "/api/desenho":
            try:
                self.responder(200, sessao.desenhar(dados))
            except Falha as falha:
                self.responder(400, {"falha": str(falha)})
            except modulo_do_ajudante.Indisponivel as falha:
                self.responder(503, {"falha": str(falha)})
        elif caminho == "/api/pergunta":
            self.pergunta(dados)
        elif caminho == "/api/carregar":
            self.tratar(lambda: sessao.carregar(dados.get("jogo"), dados.get("fonte"), dados.get("pacote")))
        elif caminho == "/api/juntar":
            self.tratar(lambda: sessao.juntar(dados.get("jogo"), dados.get("pacotes"), dados.get("decisoes")))
        elif caminho == "/api/foto":      # para testes: tira uma fotografia a janela
            self.tratar(lambda: sessao.dizer({"tipo": "foto", "ficheiro": str(dados.get("ficheiro"))}) or {"ok": True})
        else:
            self.responder(404, {"falha": "Não existe."})


def verificar():
    # Para o professor, antes de uma sessao: ve se neste computador esta tudo
    # pronto, sem abrir a pagina e sem mexer em jogo nenhum. Devolve True se sim.
    #     python3 oficina/oficina.py --verificar
    tudo_bem = True

    def linha(certo, texto):
        nonlocal tudo_bem
        if certo is False:
            tudo_bem = False
        print(("  ok     " if certo else "  FALHA  " if certo is False else "  nota   ") + texto)

    print("A verificar a Oficina neste computador...")
    linha(sys.version_info >= (3, 9), "Python " + sys.version.split()[0])
    try:
        import pygame
        linha(True, "pygame-ce " + pygame.version.ver)
    except ImportError:
        linha(False, "Falta o pygame: activa o ambiente virtual, ou corre o instalar (ver COMO-CORRER.md, secção 1).")
        return False

    # Da para escrever onde a Oficina escreve?
    pastas = [AQUI] + [FICHEIROS[tipo][0] for tipo in FICHEIROS]
    for nome in JOGOS:
        try:
            pastas.append(os.path.dirname(caminho_do_jogo(configuracao(nome))))
        except Exception:
            pass
    for pasta in dict.fromkeys(pastas):
        try:
            os.makedirs(pasta, exist_ok=True)
            experiencia = os.path.join(pasta, ".oficina-a-verificar")
            escrever_bytes(experiencia, b"ola")
            os.remove(experiencia)
        except OSError as erro:
            linha(False, "Não consigo escrever em " + pasta + " (" + str(erro) + "): as crianças não iam conseguir guardar.")
    if tudo_bem:
        linha(True, "Dá para escrever nas pastas dos jogos, das imagens e dos sons.")

    # Cada jogo: le-se, e corre ate mostrar o primeiro frame.
    for nome in JOGOS:
        try:
            config = configuracao(nome)
            fonte, _ = ler(caminho_do_jogo(config))
            compile(fonte, config.FICHEIRO, "exec")
            coisas = len(config.escolhas(fonte))
        except Exception as erro:
            linha(False, nome + ": não se consegue ler (" + type(erro).__name__ + ": " + str(erro)[:120] + ").")
            continue
        if coisas == 0:
            linha(False, config.NOME + ": a Oficina não encontra nada para mudar no ficheiro.")
            continue
        inicio = time.time()
        sessao.jogar(nome)
        while time.time() - inicio < ARRANQUE and sessao.viva() and sessao.quadro is None:
            time.sleep(0.05)
        demorou = time.time() - inicio
        time.sleep(1)                # mais um bocadinho a correr, para apanhar um erro logo a seguir
        erros = [m for m in sessao.mensagens if m["tipo"] == "erro"]
        correu = sessao.viva() and sessao.quadro is not None and not erros
        sessao.fechar()
        if not correu:
            motivo = (erros[0].get("detalhe") or erros[0].get("texto")) if erros else "não chegou a mostrar nada"
            linha(False, config.NOME + ": o jogo não corre (" + str(motivo)[:160] + ").")
            continue
        linha(True, config.NOME + ": " + str(coisas) + " coisas para mudar; abre em " + str(round(demorou, 1)) + " s.")
        if demorou > 8:
            linha(None, "Este computador é lento a abrir os jogos: da primeira vez a imagem demora a aparecer.")
        original = caminho_do_original(config)
        if os.path.exists(original) and ler(original)[0] != fonte:
            linha(None, config.NOME + ": neste computador o jogo já foi mudado (não é o original). "
                        "Para recomeçar do zero: git checkout -- " + config.FICHEIRO)

    # O ajudante.
    servidores = sessao.ajudante.servidores
    if not servidores:
        linha(None, "Sem computadores ajudantes (oficina/servidores.txt vazio): não há botão «Pedir ajuda».")
    else:
        sessao.ajudante.ver_ligados()
        ligados = sessao.ajudante.ligados
        linha(None if ligados < len(servidores) else True,
              "Ajudante: " + str(ligados) + " de " + str(len(servidores)) + " computadores a atender."
              + ("" if ligados else " As crianças vão ver «O ajudante não responde agora»."))
    print("Está tudo pronto." if tudo_bem else "HÁ COISAS A RESOLVER (as linhas que dizem FALHA).")
    return tudo_bem


def main():
    argumentos = argparse.ArgumentParser(description="A Oficina do Clube de Código")
    argumentos.add_argument("--verificar", action="store_true",
                            help="vê se este computador está pronto para uma sessão, e sai")
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
    if argumentos.verificar:
        certo = verificar()
        sessao.parar()
        sys.exit(0 if certo else 1)
    try:
        import pygame  # noqa: F401
    except ImportError:
        print("Falta o pygame. Activa o ambiente virtual primeiro (ver COMO-CORRER.md, secção 1).")
        sys.exit(1)

    servidor = None
    for porta in range(argumentos.porta, argumentos.porta + 20):
        try:
            servidor = Servidor(("127.0.0.1", porta), Pedido)
            break
        except OSError:
            pass
        # A porta esta ocupada. Se for por uma Oficina desta mesma pasta, nao
        # se abre outra: as duas a mexer nos mesmos ficheiros desfaziam o
        # trabalho uma da outra. Mostra-se a que ja esta aberta.
        endereco = "http://127.0.0.1:" + str(porta)
        try:
            with urlopen(endereco + "/api/ola", timeout=2) as resposta:
                outra = json.loads(resposta.read()).get("oficina")
        except (OSError, ValueError, AttributeError):
            outra = None
        if outra is not None and os.path.normcase(str(outra)) == os.path.normcase(AQUI):
            print("A Oficina já estava aberta em " + endereco + " (noutra janela do terminal).")
            print("Não abri outra: uso essa. Para a fechar, Ctrl+C nessa janela.")
            if not argumentos.sem_navegador:
                webbrowser.open(endereco)
            sys.exit(0)
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
