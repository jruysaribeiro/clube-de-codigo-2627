# O palco: corre o jogo verdadeiro, sem janela, e vai trocando bocados do
# codigo enquanto ele corre. A imagem do jogo vai para a pagina do editor,
# e o rato e o teclado vem de la.
#
# Nao se corre a mao: e a oficina.py que o lanca. Os dois falam por linhas
# de JSON: a oficina escreve no nosso stdin, nos respondemos no stdout com
# linhas que comecam por @@.
#
# Como funciona a troca: o jogo chama pygame.display.flip() no fim de cada
# frame. Trocamos essa funcao por uma nossa, que antes de mostrar o frame
# ve se chegou codigo novo e, se chegou, corre so esse bocado dentro do
# jogo. As funcoes do jogo vao buscar MAPA, TORRES, INIMIGOS... pelo nome
# cada vez que precisam, por isso apanham logo os valores novos.
#
# E nessa mesma funcao que tiramos a "fotografia" de cada frame para a
# mandar a oficina, e que entregamos ao jogo os cliques e as teclas que
# vieram da pagina, como se fossem do rato e do teclado verdadeiros.

import argparse
import ast
import importlib
import io
import json
import os
import queue
import socket
import struct
import sys
import threading
import traceback

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)

import blocos  # noqa: E402

QUADROS_DE_PROVA = 20    # frames sem rebentar ate dizermos que o codigo e bom
UM_EM_CADA = 2           # manda-se para a pagina um frame em cada dois (30 por segundo)

# Os nomes que o browser da as teclas que nao sao letras nem numeros.
TECLAS = {
    " ": "K_SPACE", "Enter": "K_RETURN", "Escape": "K_ESCAPE", "Backspace": "K_BACKSPACE",
    "Tab": "K_TAB", "ArrowUp": "K_UP", "ArrowDown": "K_DOWN", "ArrowLeft": "K_LEFT",
    "ArrowRight": "K_RIGHT", "Shift": "K_LSHIFT", "Control": "K_LCTRL", "Alt": "K_LALT",
}


class TeclasCarregadas:
    # O que o jogo recebe de pygame.key.get_pressed(): teclas[pygame.K_a]
    def __init__(self, carregadas):
        self.carregadas = carregadas

    def __getitem__(self, tecla):
        return tecla in self.carregadas


# =====================================================================
#                        FALAR COM A OFICINA
# =====================================================================

saida = sys.stdout
recebidas = queue.Queue()


def enviar(mensagem):
    try:
        saida.write("@@" + json.dumps(mensagem) + "\n")
        saida.flush()
    except (OSError, ValueError):
        pass


class Prints:
    # O que o jogo escreve com print() vai para o editor.
    def write(self, texto):
        if texto.strip() != "":
            enviar({"tipo": "print", "texto": texto.rstrip()})
        return len(texto)

    def flush(self):
        pass


def ouvir():
    for linha in sys.stdin:
        linha = linha.strip()
        if linha == "":
            continue
        try:
            recebidas.put(json.loads(linha))
        except ValueError:
            pass
    recebidas.put({"tipo": "sair"})   # a oficina fechou


# =====================================================================
#                       EXPLICAR UM ERRO
# =====================================================================

def explicar(erro):
    if isinstance(erro, KeyError):
        return "Falta " + repr(erro.args[0]) + ". Apagaste-o, ou mudaste-lhe o nome?"
    if isinstance(erro, NameError):
        nome = getattr(erro, "name", None) or "?"
        return 'O Python não conhece "' + nome + '". Faltam as aspas, ou está mal escrito?'
    if isinstance(erro, ZeroDivisionError):
        return "Há uma divisão por zero: um número que não pode ser 0."
    if isinstance(erro, IndexError):
        return "O jogo pediu uma posição que não existe numa lista."
    if isinstance(erro, (TypeError, ValueError)):
        return "Há um valor do tipo errado: um texto onde devia estar um número, ou ao contrário."
    return "O jogo parou com um erro."


def linhas_do_erro(erro, ficheiro):
    # As linhas do ficheiro do jogo por onde o erro passou, de fora para dentro.
    linhas = []
    for passo in traceback.extract_tb(erro.__traceback__):
        if passo.filename == ficheiro and passo.lineno is not None:
            linhas.append(passo.lineno)
    return linhas


def mensagem_de_erro(erro, ficheiro, numero):
    return {
        "tipo": "erro", "id": numero,
        "texto": explicar(erro),
        "detalhe": type(erro).__name__ + ": " + str(erro),
        "linhas": linhas_do_erro(erro, ficheiro),
    }


# =====================================================================
#                            O PALCO
# =====================================================================

class Sair(BaseException):
    pass


class Corrida:

    def __init__(self, config, escolha, ficheiro, fonte, porta):
        self.rato = (0, 0)
        self.botoes = set()
        self.teclas = set()
        self.contagem = 0
        self.ligacao = None
        if porta:
            self.ligacao = socket.create_connection(("127.0.0.1", porta))
        self.config = config
        self.escolha = escolha
        self.ficheiro = ficheiro
        self.fonte = fonte           # o codigo que esta a correr
        self.fonte_boa = fonte       # o ultimo que correu sem rebentar
        self.em_prova = None         # numero do pedido ainda a ser provado
        self.quadros = 0
        self.foto = None
        self.ns = None
        self.palco = None
        self.flip = None
        self.update = None

    def instalar(self, pygame):
        self.pygame = pygame
        self.flip = pygame.display.flip
        self.update = pygame.display.update
        corrida = self

        def flip(*args, **kwargs):
            corrida.antes_de_mostrar()
            return corrida.flip(*args, **kwargs)

        def update(*args, **kwargs):
            corrida.antes_de_mostrar()
            return corrida.update(*args, **kwargs)

        pygame.display.flip = flip
        pygame.display.update = update
        # Nao ha janela, por isso o rato e o teclado sao os da pagina.
        pygame.mouse.get_pos = lambda: corrida.rato
        pygame.mouse.get_pressed = lambda *args, **kwargs: (1 in corrida.botoes, 2 in corrida.botoes, 3 in corrida.botoes)
        pygame.key.get_pressed = lambda: TeclasCarregadas(corrida.teclas)

    def tecla(self, nome):
        if nome in TECLAS:
            return getattr(self.pygame, TECLAS[nome])
        if len(nome) == 1:
            return ord(nome.lower())
        return None

    def entregar(self, eventos):
        # Transforma o que veio da pagina em eventos do pygame.
        pygame = self.pygame
        for e in eventos:
            if e["tipo"] == "rato":
                antes = self.rato
                self.rato = (int(e["x"]), int(e["y"]))
                pygame.event.post(pygame.event.Event(
                    pygame.MOUSEMOTION, pos=self.rato,
                    rel=(self.rato[0] - antes[0], self.rato[1] - antes[1]),
                    buttons=pygame.mouse.get_pressed()))
            elif e["tipo"] == "botao":
                self.rato = (int(e["x"]), int(e["y"]))
                if e["baixo"]:
                    self.botoes.add(e["botao"])
                    pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=self.rato, button=e["botao"]))
                else:
                    self.botoes.discard(e["botao"])
                    pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONUP, pos=self.rato, button=e["botao"]))
            elif e["tipo"] == "tecla":
                tecla = self.tecla(e["tecla"])
                if tecla is None:
                    continue
                letra = e["tecla"] if len(e["tecla"]) == 1 else ""
                if e["baixo"]:
                    self.teclas.add(tecla)
                    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=tecla, unicode=letra, mod=0, scancode=0))
                else:
                    self.teclas.discard(tecla)
                    pygame.event.post(pygame.event.Event(pygame.KEYUP, key=tecla, unicode=letra, mod=0, scancode=0))
            elif e["tipo"] == "largar":      # a pagina perdeu o foco: larga tudo
                self.teclas.clear()
                self.botoes.clear()

    def fotografar(self):
        # Manda o frame para a oficina: 4 bytes com o tamanho, e o JPEG.
        self.contagem = self.contagem + 1
        if self.ligacao is None or self.contagem % UM_EM_CADA != 0:
            return
        ecra = self.pygame.display.get_surface()
        if ecra is None:
            return
        imagem = io.BytesIO()
        self.pygame.image.save(ecra, imagem, "quadro.jpg")
        dados = imagem.getvalue()
        try:
            self.ligacao.sendall(struct.pack(">I", len(dados)) + dados)
        except OSError:
            raise Sair()

    def antes_de_mostrar(self):
        while True:
            try:
                pedido = recebidas.get_nowait()
            except queue.Empty:
                break
            self.atender(pedido)

        self.palco.quadro(self.ns, self.pygame)
        if self.foto is not None:
            self.pygame.image.save(self.pygame.display.get_surface(), self.foto)
            enviar({"tipo": "foto", "ficheiro": self.foto})
            self.foto = None

        if self.em_prova is not None:
            self.quadros = self.quadros + 1
            if self.quadros >= QUADROS_DE_PROVA:
                self.fonte_boa = self.fonte
                enviar({"tipo": "estavel", "id": self.em_prova})
                self.em_prova = None
        self.fotografar()

    def atender(self, pedido):
        tipo = pedido.get("tipo")
        if tipo == "sair":
            raise Sair()
        if tipo == "entrada":
            self.entregar(pedido["eventos"])
        if tipo == "foto":
            self.foto = pedido["ficheiro"]     # tira-se depois de o palco desenhar
        if tipo == "codigo":
            self.trocar(pedido)
        if tipo == "imagens":
            self.esquecer_imagens()

    def esquecer_imagens(self):
        # Chegou (ou saiu) uma imagem da pasta. Os jogos guardam as imagens
        # que ja leram em "imagens_carregadas": esvazia-se, e eles voltam a
        # ir busca-las ao disco.
        guardadas = (self.ns or {}).get("imagens_carregadas")
        if isinstance(guardadas, dict):
            guardadas.clear()
        if hasattr(self.palco, "ao_mudar_imagens"):
            self.palco.ao_mudar_imagens(self.ns)

    def trocar(self, pedido):
        numero = pedido["id"]
        nova = pedido["fonte"]
        try:
            arvore = ast.parse(nova, self.ficheiro)
            nos = blocos.nos_da_regiao(arvore, pedido["inicio"], pedido["fim"])
            if len(nos) == 0:
                # Apagaram tudo: sem isto, a instrucao inteira (o MAPA, por
                # exemplo) desaparecia do ficheiro e o jogo deixava de abrir.
                enviar({"tipo": "problemas", "id": numero, "avisos": [],
                        "problemas": ["Apagaste tudo. O jogo precisa deste bocado: "
                                      "escreve-o outra vez, ou carrega em Repor o original."]})
                return
            # Uma linha "NOME = ..." apagada nao rebenta logo (o jogo ainda
            # se lembra do valor antigo), mas o ficheiro ficava sem ela e o
            # jogo ja nao abria da proxima vez.
            agora = blocos.nomes_dados(arvore)
            em_falta = [nome for nome in blocos.nomes_dados(ast.parse(self.fonte)) if nome not in agora]
            if em_falta:
                enviar({"tipo": "problemas", "id": numero, "avisos": [],
                        "problemas": ['Falta a linha "' + nome + ' = ...". O jogo precisa dela: '
                                      "escreve-a outra vez, ou carrega em Repor o original."
                                      for nome in em_falta]})
                return
            codigo = compile(ast.Module(body=nos, type_ignores=[]), self.ficheiro, "exec")
            # Primeiro num rascunho: uma copia dos nomes do jogo. Se o
            # bocado novo rebentar ou nao fizer sentido, o jogo nem da por ela.
            rascunho = dict(self.ns)
            exec(codigo, rascunho)
            problemas, avisos = self.palco.verificar(rascunho)
        except Exception as erro:
            enviar(mensagem_de_erro(erro, self.ficheiro, numero))
            return
        if problemas:
            enviar({"tipo": "problemas", "id": numero, "problemas": problemas, "avisos": avisos})
            return

        exec(codigo, self.ns)
        self.fonte = nova
        self.em_prova = numero
        self.quadros = 0
        self.palco.ao_mudar(self.ns)
        enviar({"tipo": "aplicado", "id": numero, "avisos": avisos})

    def correr(self):
        # Corre o jogo. Se rebentar por causa de codigo novo, volta ao
        # ultimo codigo bom e recomeca; a crianca ve o erro no editor.
        while True:
            self.ns = {"__name__": "__main__", "__file__": self.ficheiro}
            self.palco = self.config.criar_palco(self.escolha)
            try:
                exec(compile(self.fonte, self.ficheiro, "exec"), self.ns)
                enviar({"tipo": "fechou"})
                return
            except (Sair, SystemExit, KeyboardInterrupt):
                return
            except Exception as erro:
                enviar(mensagem_de_erro(erro, self.ficheiro, self.em_prova))
                self.em_prova = None
                if self.fonte != self.fonte_boa:
                    self.fonte = self.fonte_boa
                    continue
            # Ate o codigo "bom" rebenta (o ficheiro ja vinha estragado).
            # Ficamos a espera, com um aviso na janela, de codigo novo.
            pedido = self.esperar_por_codigo()
            if pedido is None:
                return
            self.fonte = pedido["fonte"]
            self.fonte_boa = pedido["fonte"]
            self.em_prova = pedido["id"]
            self.quadros = 0

    def esperar_por_codigo(self):
        pygame = self.pygame
        pygame.init()
        ecra = pygame.display.get_surface()
        if ecra is None:
            ecra = pygame.display.set_mode((800, 600))
        letra = pygame.font.SysFont(None, 34)
        relogio = pygame.time.Clock()
        while True:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    enviar({"tipo": "fechou"})
                    return None
            try:
                while True:
                    pedido = recebidas.get_nowait()
                    if pedido.get("tipo") == "sair":
                        return None
                    if pedido.get("tipo") == "codigo":
                        return pedido
            except queue.Empty:
                pass
            ecra.fill((30, 30, 48))
            ecra.blit(letra.render("O jogo parou com um erro.", True, (240, 200, 70)), (60, 240))
            ecra.blit(letra.render("Corrige o código no editor e ele volta sozinho.", True, (240, 240, 240)), (60, 290))
            self.contagem = -1      # este frame vai sempre
            self.fotografar()
            self.flip()
            relogio.tick(20)


def main():
    argumentos = argparse.ArgumentParser()
    argumentos.add_argument("--jogo", required=True)
    argumentos.add_argument("--escolha", required=True)
    argumentos.add_argument("--quadros", type=int, default=0)   # porta para onde vao os frames
    argumentos = argumentos.parse_args()

    for canal in (sys.stdin, sys.stdout):
        canal.reconfigure(encoding="utf-8")
    sys.stdout = Prints()

    config = importlib.import_module("jogos." + argumentos.jogo)
    ficheiro = os.path.join(RAIZ, *config.FICHEIRO.split("/"))
    with open(ficheiro, encoding="utf-8", newline="") as f:
        fonte = f.read().replace("\r\n", "\n")

    # O jogo espera encontrar a pasta dele (para imagens e sons).
    os.chdir(os.path.dirname(ficheiro))
    sys.path.insert(0, os.path.dirname(ficheiro))

    import pygame

    corrida = Corrida(config, argumentos.escolha, ficheiro, fonte, argumentos.quadros)
    corrida.instalar(pygame)
    threading.Thread(target=ouvir, daemon=True).start()
    corrida.correr()
    pygame.quit()


if __name__ == "__main__":
    main()
