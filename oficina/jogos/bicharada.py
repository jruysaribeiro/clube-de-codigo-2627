# A Bicharada na Oficina: que coisas se podem escolher, onde esta o codigo
# de cada uma, e o "palco" que mostra so essa coisa a funcionar.
#
# O palco nao e um jogo a parte: e a Bicharada verdadeira, ja dentro de uma
# batalha (sem menu e sem ecra de escolha), com a equipa que interessa para
# ver a coisa escolhida. Quando a batalha acaba, comeca outra igual.

import ast
import difflib

import blocos

NOME = "Bicharada"
FICHEIRO = "s12-bicharada/bicharada.py"
DESCRICAO = "Batalhas por turnos, com bichos muito portugueses."

# Uma frase por grupo, para a pagina do jogo dizer o que la ha.
SOBRE_OS_GRUPOS = {
    "Bichos": "Tipo, vida, ataque, forma, cor. Podes pôr uma imagem tua.",
    "Ataques": "O poder, a precisão e o efeito de cada ataque.",
    "Treinadores": "Quem enfrentas, o que dizem e que bichos levam.",
    "Tipos": "As cores dos tipos, e quem é forte contra quem.",
}

FORMAS = ["circulo", "quadrado", "triangulo", "gota"]
EFEITOS = ["dano", "cura", "sobe_ataque", "sobe_defesa", "baixa_ataque", "baixa_defesa"]

TECLAS = " Setas e Enter para jogar, Esc para voltar atrás."

DICAS = {
    "bicho": "O teu bicho é o de baixo, e os ataques dele estão à vista."
             " Muda um número e vê a ficha lá em cima." + TECLAS,
    "ataque": "O teu bicho já tem este ataque escolhido: carrega em Enter para o usar."
              " Com precisão baixa falha muitas vezes." + TECLAS,
    "treinador": "A batalha é contra este treinador: lê o nome e a frase dele no início."
                 " Enter passa o texto à frente." + TECLAS,
    "tipos": "A tabela do meio diz quem é forte contra quem: a linha ataca, a coluna leva."
             " Levas um bicho de cada tipo para experimentar." + TECLAS,
}

# id da escolha -> (nome da instrucao no ficheiro, titulo)
TIPOS = {
    "tipos:cores": ("CORES_TIPO", "As cores dos tipos"),
    "tipos:eficacia": ("EFICACIA", "Quem é forte contra quem"),
}


# =====================================================================
#                    ONDE ESTA O CODIGO DE CADA COISA
# =====================================================================

def _fichas(no):
    # As fichas de um dicionario {"nome": {...}, ...} ou de uma lista
    # [{...}, ...] escritos no codigo: [(nome, ficha, primeira, ultima), ...].
    # O nome e None quando a ficha vem de uma lista.
    if no is None:
        return []
    partes = blocos.entradas(no)
    if not partes:
        return []
    if isinstance(no.value, ast.Dict):
        valores = no.value.values
        return [(blocos.texto_constante(chave), valor, primeira, ultima)
                for (chave, primeira, ultima), valor in zip(partes, valores)]
    return [(None, elemento, primeira, ultima) for elemento, primeira, ultima in partes]


def escolhas(fonte):
    arvore = ast.parse(fonte)
    lista = []

    numero = 0
    for nome, _, _, _ in _fichas(blocos.instrucao(arvore, "BICHOS")):
        lista.append({"id": "bicho:" + str(numero), "grupo": "Bichos",
                      "titulo": nome or "Bicho " + str(numero + 1)})
        numero = numero + 1

    numero = 0
    for nome, _, _, _ in _fichas(blocos.instrucao(arvore, "ATAQUES")):
        lista.append({"id": "ataque:" + str(numero), "grupo": "Ataques",
                      "titulo": nome or "Ataque " + str(numero + 1)})
        numero = numero + 1

    numero = 0
    for _, ficha, _, _ in _fichas(blocos.instrucao(arvore, "TREINADORES")):
        nome = blocos.valor_da_chave(ficha, "nome")
        lista.append({"id": "treinador:" + str(numero), "grupo": "Treinadores",
                      "titulo": nome or "Treinador " + str(numero + 1)})
        numero = numero + 1

    for escolha, (instrucao, titulo) in TIPOS.items():
        if blocos.instrucao(arvore, instrucao) is not None:
            lista.append({"id": escolha, "grupo": "Tipos", "titulo": titulo})
    return lista


def regiao(fonte, escolha):
    # Devolve {"inicio", "fim", "ajuda", "titulo", "dica", "imagem"} ou None.
    # "imagem" e o nome do ficheiro escrito na ficha de um bicho; as outras
    # coisas nao tem imagem, e fica None.
    arvore = ast.parse(fonte)
    linhas = fonte.split("\n")
    tipo, _, numero = escolha.partition(":")

    if escolha in TIPOS:
        instrucao, titulo = TIPOS[escolha]
        no = blocos.instrucao(arvore, instrucao)
        if no is None:
            return None
        return {"inicio": no.lineno, "fim": no.end_lineno, "titulo": titulo, "imagem": None,
                "ajuda": blocos.ajuda_acima(linhas, no.lineno), "dica": DICAS["tipos"]}

    nomes = {"bicho": "BICHOS", "ataque": "ATAQUES", "treinador": "TREINADORES"}
    if tipo not in nomes:
        return None
    no = blocos.instrucao(arvore, nomes[tipo])
    partes = _fichas(no)
    if not numero.isdigit() or int(numero) >= len(partes):
        return None
    nome, ficha, inicio, fim = partes[int(numero)]
    imagem = None
    if tipo == "bicho":
        imagem = blocos.valor_da_chave(ficha, "imagem")
    if tipo == "treinador":
        nome = blocos.valor_da_chave(ficha, "nome")
    return {"inicio": inicio, "fim": fim, "titulo": nome or escolha, "imagem": imagem,
            "ajuda": blocos.ajuda_acima(linhas, no.lineno), "dica": DICAS[tipo]}


# =====================================================================
#                 VER SE O QUE FOI ESCRITO FAZ SENTIDO
# =====================================================================
# Antes de uma mudanca entrar no jogo, passa por aqui. Devolve duas listas
# de frases: problemas (a mudanca nao entra) e avisos (entra, mas atencao).
#
# Os dados falam uns dos outros pelo nome: um bicho diz que ataques tem, um
# treinador diz que bichos leva. Quando um nome deixa de existir:
#   - se o engano esta no bocado aberto (um bicho com um ataque que nao
#     ha), e um problema;
#   - se e o bocado aberto que mudou de nome e ha outros a chamar pelo nome
#     antigo, e um aviso que diz onde falta mudar. Assim da para mudar o
#     nome a um ataque ou a um bicho, e o palco aguenta-se ate la.

def _numero(valor):
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


def _cor(valor):
    if not isinstance(valor, (tuple, list)) or len(valor) != 3:
        return False
    for parte in valor:
        if not isinstance(parte, int) or isinstance(parte, bool) or parte < 0 or parte > 255:
            return False
    return True


def _ver_numero(ficha, quem, chave, minimo, maximo, problemas):
    # Numeros gigantes ou negativos nao fazem sentido numa batalha, e
    # alguns (defesa 0) fazem o jogo parar com uma divisao por zero.
    if chave not in ficha:
        problemas.append(quem + ': falta "' + chave + '".')
    elif not _numero(ficha[chave]):
        problemas.append(quem + ': "' + chave + '" tem de ser um número, sem aspas.')
    elif ficha[chave] < minimo:
        problemas.append(quem + ': "' + chave + '" não pode ser menos que ' + str(minimo) + ".")
    elif ficha[chave] > maximo:
        problemas.append(quem + ': "' + chave + '" é grande demais. O máximo é ' + str(maximo) + ".")


def _ver_texto(ficha, quem, chave, problemas):
    if chave not in ficha:
        problemas.append(quem + ': falta "' + chave + '".')
        return False
    if not isinstance(ficha[chave], str):
        problemas.append(quem + ': "' + chave + '" tem de ser um texto entre aspas.')
        return False
    return True


def _ver_cor(ficha, quem, chave, problemas):
    if chave not in ficha:
        problemas.append(quem + ': falta "' + chave + '".')
    elif not _cor(ficha[chave]):
        problemas.append(quem + ': "' + chave + '" são três números de 0 a 255, como (200, 60, 60).')


def _ver_tipo(ficha, quem, tipos, problemas):
    if not _ver_texto(ficha, quem, "tipo", problemas):
        return
    if tipos is not None and ficha["tipo"] not in tipos:
        problemas.append(quem + ': o tipo "' + ficha["tipo"] + '" não tem cor em CORES_TIPO. '
                         "Os tipos que há: " + ", ".join(tipos) + ".")


def _parecido(nome, nomes):
    # Para quem se enganou numa letra: ' Querias dizer "Bicada"?'
    parecidos = difflib.get_close_matches(nome, nomes, 1)
    if parecidos:
        return ' Querias dizer "' + parecidos[0] + '"?'
    return ""


def _ver_tipos(ns, problemas, avisos):
    # Devolve os nomes dos tipos, ou None se nem der para os ler.
    cores = ns.get("CORES_TIPO")
    if not isinstance(cores, dict) or len(cores) == 0:
        problemas.append("CORES_TIPO tem de ter pelo menos um tipo, entre { }.")
        return None
    for tipo, cor in cores.items():
        if not isinstance(tipo, str):
            problemas.append("O nome de um tipo tem de estar entre aspas.")
        elif not _cor(cor):
            problemas.append('A cor do tipo "' + tipo + '" são três números de 0 a 255, como (200, 60, 60).')
    tipos = [tipo for tipo in cores if isinstance(tipo, str)]

    tabela = ns.get("EFICACIA")
    if not isinstance(tabela, dict):
        problemas.append("EFICACIA tem de estar entre { }.")
        return tipos
    sem_cor = []
    for atacante, linha in tabela.items():
        if not isinstance(linha, dict):
            problemas.append('EFICACIA: à frente de "' + str(atacante) + '" vem outro { }, '
                             'como {"planta": 2.0}.')
            continue
        for alvo, vezes in linha.items():
            quem = str(atacante) + " contra " + str(alvo)
            if not _numero(vezes):
                problemas.append("EFICACIA, " + quem + ": tem de ser um número, como 2.0 ou 0.5.")
            elif vezes < 0:
                problemas.append("EFICACIA, " + quem + ": não pode ser menos que zero.")
            elif vezes > 100:
                problemas.append("EFICACIA, " + quem + ": é grande demais. O máximo é 100.")
            for tipo in (atacante, alvo):
                if tipo not in tipos and tipo not in sem_cor:
                    sem_cor.append(tipo)
    for tipo in sem_cor:
        avisos.append('EFICACIA fala do tipo "' + str(tipo) + '", que não tem cor em CORES_TIPO. '
                      "Enquanto não tiver, nenhum bicho pode ser desse tipo.")
    return tipos


def _ver_ataques(ns, tipos, problemas, avisos):
    # Devolve os nomes dos ataques, ou None se nem der para os ler.
    ataques = ns.get("ATAQUES")
    if not isinstance(ataques, dict) or len(ataques) == 0:
        problemas.append("Tem de haver pelo menos um ataque.")
        return None
    for nome, ficha in ataques.items():
        quem = str(nome)
        if not isinstance(nome, str):
            problemas.append("O nome de um ataque tem de estar entre aspas.")
            continue
        if not isinstance(ficha, dict):
            problemas.append(quem + ": a ficha tem de estar entre { }.")
            continue
        _ver_tipo(ficha, quem, tipos, problemas)
        _ver_numero(ficha, quem, "poder", 0, 999, problemas)
        _ver_numero(ficha, quem, "precisao", 0, 999, problemas)
        if _numero(ficha.get("precisao")) and 100 < ficha["precisao"] <= 999:
            avisos.append(quem + ': a "precisao" vai de 0 a 100. Com mais de 100 acerta sempre.')
        if ficha.get("efeito") not in EFEITOS:
            problemas.append(quem + ': o "efeito" tem de ser um destes: ' + ", ".join(EFEITOS) + ".")
    return [nome for nome in ataques if isinstance(nome, str)]


def _ver_imagem(ficha, quem, ns, problemas):
    if not _ver_texto(ficha, quem, "imagem", problemas):
        return
    nome = ficha["imagem"]
    if nome.strip() == "":
        problemas.append(quem + ': a "imagem" não pode ficar vazia. Escreve um nome, como "bicho.png".')
        return
    # Se o ficheiro existe mas nao e uma imagem, o jogo para ao desenhar.
    try:
        caminho = ns["PASTA_ASSETS"] / "imagens" / nome
        if caminho.exists():
            ns["pygame"].image.load(caminho)
    except Exception:
        problemas.append(quem + ': não consegui abrir a imagem "' + nome + '". É mesmo uma imagem (PNG)?')


def _ver_bichos(bichos, ns, tipos, ataques, aberto, problemas, avisos):
    # aberto: e a ficha de um bicho que esta aberta no editor?
    # Devolve os nomes dos bichos, ou None se nem der para os ler.
    if not isinstance(bichos, dict) or len(bichos) == 0:
        problemas.append("Tem de haver pelo menos um bicho.")
        return None
    for nome, ficha in bichos.items():
        quem = str(nome)
        if not isinstance(nome, str):
            problemas.append("O nome de um bicho tem de estar entre aspas.")
            continue
        if not isinstance(ficha, dict):
            problemas.append(quem + ": a ficha tem de estar entre { }.")
            continue
        _ver_tipo(ficha, quem, tipos, problemas)
        _ver_numero(ficha, quem, "vida", 1, 999, problemas)
        _ver_numero(ficha, quem, "ataque", 0, 999, problemas)
        _ver_numero(ficha, quem, "defesa", 1, 999, problemas)
        _ver_numero(ficha, quem, "velocidade", 0, 999, problemas)
        _ver_cor(ficha, quem, "cor", problemas)
        _ver_imagem(ficha, quem, ns, problemas)
        if ficha.get("forma") not in FORMAS:
            avisos.append(quem + ': a "forma" só pode ser ' + ", ".join(FORMAS) + ". Assim fica só com os olhos.")

        lista = ficha.get("ataques")
        if not isinstance(lista, list) or len(lista) == 0:
            problemas.append(quem + ': os "ataques" são uma lista com pelo menos um nome, entre [ ].')
            continue
        if len(lista) > 4:
            avisos.append(quem + ": só cabem 4 ataques no menu da batalha. Os outros ficam fora do ecrã.")
        for ataque in lista:
            if not isinstance(ataque, str):
                problemas.append(quem + ": o nome de um ataque tem de estar entre aspas.")
            elif ataques is not None and ataque not in ataques:
                if aberto:
                    problemas.append(quem + ': o ataque "' + ataque + '" não existe em ATAQUES.'
                                     + _parecido(ataque, ataques))
                else:
                    avisos.append(quem + ' ainda usa o ataque "' + ataque + '", que já não existe. '
                                  "Muda o nome também na ficha desse bicho, senão o jogo pára.")

    minimo = ns.get("TAMANHO_EQUIPA")
    if isinstance(minimo, int) and len(bichos) < minimo:
        problemas.append("Tem de haver pelo menos " + str(minimo) + " bichos, para dar para fazer uma equipa.")
    if len(bichos) > 8:
        avisos.append("No ecrã de escolha só cabem 8 bichos. Os outros ficam tapados.")
    return [nome for nome in bichos if isinstance(nome, str)]


def _ver_treinadores(treinadores, bichos, aberto, problemas, avisos):
    # aberto: e um treinador que esta aberto no editor?
    if not isinstance(treinadores, list) or len(treinadores) == 0:
        problemas.append("Tem de haver pelo menos um treinador.")
        return
    numero = 0
    for ficha in treinadores:
        numero = numero + 1
        quem = "Treinador " + str(numero)
        if not isinstance(ficha, dict):
            problemas.append(quem + ": tem de estar entre { }.")
            continue
        if _ver_texto(ficha, quem, "nome", problemas):
            quem = ficha["nome"]
        _ver_texto(ficha, quem, "frase", problemas)
        _ver_cor(ficha, quem, "cor_fundo", problemas)
        equipa = ficha.get("equipa")
        if not isinstance(equipa, list) or len(equipa) == 0:
            problemas.append(quem + ': a "equipa" é uma lista com pelo menos um bicho, entre [ ].')
            continue
        for membro in equipa:
            if not isinstance(membro, dict):
                problemas.append(quem + ': cada bicho da equipa é assim: {"bicho": "Sardinhão", "nivel": 5}.')
                continue
            _ver_numero(membro, quem, "nivel", 1, 99, problemas)
            if _numero(membro.get("nivel")) and not isinstance(membro["nivel"], int):
                problemas.append(quem + ': o "nivel" tem de ser um número inteiro, sem vírgula.')
            if not _ver_texto(membro, quem, "bicho", problemas):
                continue
            bicho = membro["bicho"]
            if bichos is not None and bicho not in bichos:
                if aberto:
                    problemas.append(quem + ': o bicho "' + bicho + '" não existe em BICHOS.'
                                     + _parecido(bicho, bichos))
                else:
                    avisos.append(quem + ' ainda chama por "' + bicho + '", que já não existe. '
                                  "Muda o nome também na equipa desse treinador, senão o jogo pára.")


# =====================================================================
#                              O PALCO
# =====================================================================

class Palco:

    def __init__(self, escolha):
        tipo, _, numero = escolha.partition(":")
        self.tipo = tipo             # bicho, ataque, treinador ou tipos
        self.numero = int(numero) if numero.isdigit() else 0
        self.preparado = False
        self.redesenhar = False      # a batalha mudou depois de o jogo desenhar
        self.letra = None
        self.letra_pequena = None
        self.meu = None              # o nome do bicho que vai a frente
        self.ataque = None           # o nome do ataque escolhido (se for um ataque)
        self.equipa = []             # os nomes dos bichos que levo
        self.nivel = 5
        # O palco poe no jogo uma versao "segura" de BICHOS e de TREINADORES
        # (ve arrumar). Aqui fica o que o ficheiro diz mesmo, e o que la pus.
        self.escrito = {}
        self.do_palco = {}

    def ler(self, ns, nome):
        # O que o ficheiro diz, mesmo que no jogo esteja a versao do palco.
        valor = ns.get(nome)
        if nome in self.do_palco and valor is self.do_palco[nome]:
            return self.escrito[nome]
        return valor

    def por(self, ns, nome, valor):
        self.escrito[nome] = self.ler(ns, nome)
        self.do_palco[nome] = valor
        ns[nome] = valor

    def verificar(self, ns):
        problemas = []
        avisos = []
        tipos = _ver_tipos(ns, problemas, avisos)
        ataques = _ver_ataques(ns, tipos, problemas, avisos)
        bichos = _ver_bichos(self.ler(ns, "BICHOS"), ns, tipos, ataques,
                             self.tipo == "bicho", problemas, avisos)
        _ver_treinadores(self.ler(ns, "TREINADORES"), bichos,
                         self.tipo == "treinador", problemas, avisos)
        return problemas, avisos

    # --- Preparar e voltar a preparar ---

    def preparar(self, ns, pygame):
        self.letra = pygame.font.SysFont(None, 22)
        self.letra_pequena = pygame.font.SysFont(None, 18)
        self.preparado = True
        self.arrumar(ns)
        self.batalha(ns, None)

    def ao_mudar(self, ns):
        # O codigo mudou. Os bichos que estavam em campo foram feitos com
        # os numeros antigos (criar_bicho copia-os), por isso fazem-se
        # outros e a batalha comeca de novo.
        if not self.preparado:
            return
        self.arrumar(ns)
        self.batalha(ns, None)

    def arrumar(self, ns):
        # Decide quem levo e contra quem, e deixa os dados de maneira que a
        # batalha nao pare: tira os nomes que ja nao existem (um ataque ou
        # um bicho a quem acabaram de mudar o nome).
        ataques = ns["ATAQUES"]
        escritos = self.ler(ns, "BICHOS")
        nomes = list(escritos)

        self.meu = nomes[0]
        self.ataque = None
        if self.tipo == "bicho":
            self.meu = nomes[min(self.numero, len(nomes) - 1)]
        if self.tipo == "ataque":
            self.ataque = list(ataques)[min(self.numero, len(ataques) - 1)]
            self.meu = self.dono(escritos, ataques)

        seguros = {}
        for nome in nomes:
            lista = [ataque for ataque in escritos[nome]["ataques"] if ataque in ataques]
            if nome == self.meu and self.ataque is not None and self.ataque not in lista:
                lista.insert(0, self.ataque)      # ninguem o tinha: fica emprestado
            if len(lista) == 0:
                lista = [list(ataques)[0]]
            seguros[nome] = dict(escritos[nome])
            seguros[nome]["ataques"] = lista
        self.por(ns, "BICHOS", seguros)
        ns["nomes_dos_bichos"] = nomes

        # A minha equipa: o bicho que interessa a frente, e mais dois.
        self.equipa = [self.meu]
        if self.tipo == "tipos":
            vistos = [seguros[self.meu]["tipo"]]
            for nome in nomes:
                if len(self.equipa) < 3 and seguros[nome]["tipo"] not in vistos:
                    self.equipa.append(nome)
                    vistos.append(seguros[nome]["tipo"])
        for nome in nomes:
            if len(self.equipa) < 3 and nome not in self.equipa:
                self.equipa.append(nome)

        # O adversario: o treinador escolhido, ou o primeiro.
        treinadores = self.ler(ns, "TREINADORES")
        adversario = treinadores[0]
        if self.tipo == "treinador":
            adversario = treinadores[min(self.numero, len(treinadores) - 1)]
        membros = [membro for membro in adversario["equipa"] if membro["bicho"] in seguros]
        self.nivel = ns["NIVEL_INICIAL"]
        if self.tipo == "treinador":
            # Para a batalha ser renhida, vou ao nivel do bicho mais forte dele.
            for membro in membros:
                self.nivel = max(self.nivel, membro["nivel"])
        if len(membros) == 0:
            membros = [{"bicho": nomes[0], "nivel": self.nivel}]
        adversario = dict(adversario)
        adversario["equipa"] = membros
        self.por(ns, "TREINADORES", [adversario])
        ns["indice_treinador"] = 0

    def dono(self, bichos, ataques):
        # Que bicho leva o ataque escolhido? O primeiro que o tiver. Se
        # ninguem o tem (e novo, ou mudou de nome agora mesmo), empresta-se
        # a um bicho que ficou com um ataque em falta, ou a um do mesmo tipo.
        for nome, ficha in bichos.items():
            if self.ataque in ficha["ataques"]:
                return nome
        for nome, ficha in bichos.items():
            for ataque in ficha["ataques"]:
                if ataque not in ataques:
                    return nome
        for nome, ficha in bichos.items():
            if ficha["tipo"] == ataques[self.ataque]["tipo"]:
                return nome
        return list(bichos)[0]

    def batalha(self, ns, noticia):
        # Comeca uma batalha com as funcoes do proprio jogo.
        equipa = []
        for nome in self.equipa:
            equipa.append(ns["criar_bicho"](nome, self.nivel))
        ns["minha_equipa"] = equipa
        ns["comecar_batalha"]()
        if self.tipo != "treinador":
            # Sem conversa: direto ao menu dos ataques. Com um treinador
            # fica a conversa, que e onde aparecem o nome e a frase dele.
            ns["mensagens"] = []
            ns["fase"] = "ataques"
            ns["cursor"] = 0
            if self.ataque is not None:
                ns["cursor"] = ns["BICHOS"][self.meu]["ataques"].index(self.ataque)
        if noticia is not None:
            ns["mensagens"].insert(0, noticia)
            ns["fase"] = "texto"
        self.redesenhar = True

    # --- Todos os frames ---

    def quadro(self, ns, pygame):
        if not self.preparado:
            self.preparar(ns, pygame)

        # A batalha acabou? Comeca outra igual.
        if ns["estado"] == "derrota":
            self.batalha(ns, "A tua equipa desmaiou... Vamos outra vez!")
        elif ns["estado"] != "batalha":
            self.batalha(ns, "Ganhaste! Vamos outra vez.")

        if self.redesenhar:
            # O jogo ja tinha desenhado este frame com o que havia antes.
            ns["desenhar_batalha"]()
            self.redesenhar = False
        self.desenhar(ns, pygame)

    def desenhar(self, ns, pygame):
        ecra = ns["ecra"]
        pygame.draw.rect(ecra, ns["PAINEL"], (0, 0, ns["LARGURA"], 32))
        pygame.draw.rect(ecra, ns["AMARELO"], (0, 0, 6, 32))

        texto = ""
        if self.tipo == "bicho":
            ficha = ns["BICHOS"][self.meu]
            soma = ficha["vida"] + ficha["ataque"] + ficha["defesa"] + ficha["velocidade"]
            texto = self.meu + " (" + ficha["tipo"] + "):   vida " + str(ficha["vida"])
            texto = texto + "   ataque " + str(ficha["ataque"]) + "   defesa " + str(ficha["defesa"])
            texto = texto + "   velocidade " + str(ficha["velocidade"]) + "   soma " + str(soma)
        elif self.tipo == "ataque":
            ficha = ns["ATAQUES"][self.ataque]
            texto = self.ataque + ":   tipo " + ficha["tipo"] + "   poder " + str(ficha["poder"])
            texto = texto + "   precisão " + str(ficha["precisao"]) + "   efeito " + ficha["efeito"]
            if self.ataque not in self.escrito["BICHOS"][self.meu]["ataques"]:
                texto = texto + "   (emprestado: nenhum bicho o tem)"
        elif self.tipo == "treinador":
            ficha = ns["TREINADORES"][0]
            partes = []
            for membro in ficha["equipa"]:
                partes.append(membro["bicho"] + " nv " + str(membro["nivel"]))
            texto = ficha["nome"] + ":   " + ",  ".join(partes)
        elif self.tipo == "tipos":
            self.etiquetas(ns, pygame)
            if ns["fase"] != "equipa":       # a lista da equipa ocupa o meio do ecra
                self.tabela(ns, pygame)

        desenho = self.letra.render(texto, True, ns["BRANCO"])
        ecra.blit(desenho, (18, 9))

    def etiquetas(self, ns, pygame):
        # Todos os tipos, cada um com a sua cor, na barra de cima.
        ecra = ns["ecra"]
        x = 18
        for tipo, cor in ns["CORES_TIPO"].items():
            desenho = self.letra.render(tipo, True, ns["PRETO"])
            largura = desenho.get_width() + 18
            pygame.draw.rect(ecra, cor, (x, 7, largura, 19), border_radius=9)
            ecra.blit(desenho, (x + 9, 9))
            x = x + largura + 8

    def tabela(self, ns, pygame):
        # A EFICACIA em quadradinhos, no espaco livre ao meio: a linha e o
        # tipo do ataque, a coluna e o tipo de quem leva. Os numeros vem da
        # funcao do jogo: verde bate mais, vermelho bate menos.
        ecra = ns["ecra"]
        tipos = list(ns["CORES_TIPO"])
        lado = max(18, min(30, 176 // (len(tipos) + 1)))
        largura = lado * (len(tipos) + 1)
        caixa = pygame.Rect(352, 46, largura, largura)
        pygame.draw.rect(ecra, ns["PAINEL"], caixa.inflate(8, 8), border_radius=6)
        pygame.draw.rect(ecra, ns["AMARELO"], caixa.inflate(8, 8), 2, border_radius=6)

        numero = 0
        for tipo in tipos:
            numero = numero + 1
            cor = ns["CORES_TIPO"][tipo]
            meio = numero * lado + lado // 2
            pygame.draw.circle(ecra, cor, (caixa.x + meio, caixa.y + lado // 2), lado // 3)
            pygame.draw.circle(ecra, cor, (caixa.x + lado // 2, caixa.y + meio), lado // 3)

        linha = 0
        for atacante in tipos:
            linha = linha + 1
            coluna = 0
            for alvo in tipos:
                coluna = coluna + 1
                vezes = ns["eficacia"](atacante, alvo)
                texto = "%g" % vezes          # 2.0 fica "2", 0.5 fica "0.5"
                cor = ns["CINZA"]
                if vezes > 1:
                    cor = ns["VERDE"]
                if vezes < 1:
                    cor = ns["VERMELHO"]
                if vezes == 1:
                    texto = "·"
                desenho = self.letra_pequena.render(texto, True, cor)
                centro = (caixa.x + coluna * lado + lado // 2, caixa.y + linha * lado + lado // 2)
                ecra.blit(desenho, desenho.get_rect(center=centro))


def criar_palco(escolha):
    return Palco(escolha)
