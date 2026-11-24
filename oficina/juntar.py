# JUNTAR JOGOS
# Varias criancas mexem no mesmo jogo, cada uma no seu computador. Isto junta
# o que cada uma fez num jogo so.
#
# Cada jogo que entra traz duas coisas: o jogo de onde partiu (a "base") e o
# jogo como esta agora. A diferenca entre os dois e o que essa crianca fez.
# Juntar e pegar num jogo (o "tronco") e por-lhe em cima o que cada uma fez.
#
# Nao se compara o ficheiro linha a linha, mas coisa a coisa: cada funcao,
# cada constante e, nos dicionarios e nas listas de fichas (BICHOS, ZONAS,
# TREINADORES...), cada ficha. Para cada coisa:
#   - ninguem lhe mexeu: fica como estava;
#   - so um jogo lhe mexeu (ou varios, da mesma maneira): fica a desse jogo;
#   - e nova: junta-se;
#   - dois jogos mexeram-lhe de maneiras diferentes, ou um apagou-a: e uma
#     DUVIDA, que so quem esta a juntar pode resolver.
#
# O ficheiro de cada jogo, em oficina/jogos/, pode ajudar (tudo opcional):
#   juntar_preparar(tronco, jogos)  arruma os jogos antes de se compararem
#                                   (nomes e letras repetidos, por exemplo)
#   juntar_duvida(estado, unidade, chave, tronco, versoes)
#                                   tenta resolver uma duvida sozinho
#   juntar_mostrar(estado, texto)   o texto de uma duvida, para se ler
#   juntar_chamar(unidade, chave, texto)   o nome de uma coisa, para se ler
#                                   ("o bicho Galo" em vez de "Galo (BICHOS)")
#   juntar_acabar(estado, fonte, ordem)   os ultimos acertos, no jogo ja junto

import ast


class Unidade:
    # Um bocado do ficheiro encostado a margem: uma funcao, uma constante, o
    # ciclo do jogo... com os comentarios que tem por cima.
    #   tipo      "inteira", ou "fichas" (um dicionario ou uma lista de fichas,
    #             cada ficha nas suas linhas)
    #   texto     o bocado todo
    #   cabeca, fichas [(chave, texto)], cauda    so nas de fichas
    def __init__(self, nome, texto):
        self.nome = nome
        self.tipo = "inteira"
        self.texto = texto
        self.cabeca = None
        self.fichas = []
        self.cauda = None

    def ficha(self, chave):
        for esta, texto in self.fichas:
            if esta == chave:
                return texto
        return None

    def chaves(self):
        return [chave for chave, _ in self.fichas]


def _nome_do_no(no):
    if isinstance(no, ast.Assign) and len(no.targets) == 1 and isinstance(no.targets[0], ast.Name):
        return no.targets[0].id
    if isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return no.name
    return type(no).__name__


def _fichas_do_no(no):
    # Se o no e NOME = {...} ou NOME = [{...}, ...] com cada ficha nas suas
    # linhas, devolve (o valor, [(chave, primeira linha, ultima)]). Senao None.
    if not (isinstance(no, ast.Assign) and len(no.targets) == 1 and isinstance(no.targets[0], ast.Name)):
        return None
    valor = no.value
    partes = []
    if isinstance(valor, ast.Dict) and valor.keys:
        for chave, este in zip(valor.keys, valor.values):
            if not (isinstance(chave, ast.Constant) and isinstance(chave.value, str)):
                return None
            partes.append((chave.value, chave.lineno, este))
    elif isinstance(valor, ast.List) and valor.elts:
        for este in valor.elts:
            nome = None
            if isinstance(este, ast.Dict):
                for chave, dele in zip(este.keys, este.values):
                    if isinstance(chave, ast.Constant) and chave.value == "nome" and isinstance(dele, ast.Constant):
                        nome = dele.value
            if not isinstance(nome, str):
                return None
            partes.append((nome, este.lineno, este))
    else:
        return None
    if len({parte[0] for parte in partes}) != len(partes):
        return None
    anterior = valor.lineno
    for _, primeira, ultimo in partes:
        if primeira <= anterior:
            return None                  # duas fichas na mesma linha
        anterior = ultimo.end_lineno
    if valor.end_lineno <= anterior:
        return None                      # o } ou o ] na linha da ultima ficha
    return valor, partes


def partir(fonte):
    # O ficheiro de um jogo, partido em unidades: [Unidade, ...], pela ordem.
    arvore = ast.parse(fonte)
    linhas = fonte.split("\n")
    unidades = []
    vistos = {}
    inicio = 1
    for numero, no in enumerate(arvore.body):
        fim = no.end_lineno if numero < len(arvore.body) - 1 else len(linhas)
        nome = _nome_do_no(no)
        vistos[nome] = vistos.get(nome, 0) + 1
        if vistos[nome] > 1 or nome == type(no).__name__:
            nome = nome + " " + str(vistos[nome])
        unidade = Unidade(nome, "\n".join(linhas[inicio - 1:fim]))
        fichas = _fichas_do_no(no)
        if fichas is not None:
            valor, partes = fichas
            unidade.tipo = "fichas"
            unidade.cabeca = "\n".join(linhas[inicio - 1:valor.lineno])
            anterior = valor.lineno
            for chave, _, ultimo in partes:
                ultima = ultimo.end_lineno
                da_ficha = linhas[anterior:ultima]
                # Cada ficha fica com a sua virgula, para poder ter outra a
                # seguir: se nao a tem, poe-se logo a seguir ao valor.
                escrito = da_ficha[-1].encode("utf-8")
                if not escrito[ultimo.end_col_offset:].lstrip().startswith(b","):
                    da_ficha[-1] = (escrito[:ultimo.end_col_offset] + b"," + escrito[ultimo.end_col_offset:]).decode("utf-8")
                unidade.fichas.append((chave, "\n".join(da_ficha)))
                anterior = ultima
            unidade.cauda = "\n".join(linhas[anterior:fim])
        unidades.append(unidade)
        inicio = fim + 1
    if not unidades:
        unidades.append(Unidade("(vazio)", fonte))
    return unidades


def _igual(a, b):
    # Dois textos sao a mesma coisa? (Sem contar com espacos no fim das
    # linhas, linhas em branco no principio e no fim, e a virgula final.)
    if a is None or b is None:
        return a is None and b is None
    return _limpo(a) == _limpo(b)


def _limpo(texto):
    limpo = "\n".join(linha.rstrip() for linha in texto.split("\n")).strip("\n")
    return limpo[:-1] if limpo.endswith(",") else limpo


def pares_no_sitio(antes, agora):
    # Uma ficha a que mudaram o nome continua no mesmo lugar da lista: se na
    # posicao 3 havia "Ze" (que ja nao ha) e agora ha "Ze Novo" (que nao
    # havia), e a mesma ficha. Devolve {nome de agora: nome de antes}.
    pares = {}
    for numero in range(min(len(antes), len(agora))):
        if antes[numero] not in agora and agora[numero] not in antes:
            pares[agora[numero]] = antes[numero]
    return pares


class Juncao:
    def __init__(self, config, decisoes):
        self.config = config
        self.decisoes = decisoes if isinstance(decisoes, dict) else {}
        self.duvidas = []         # [{"id", "titulo", "opcoes": [{"quem", "texto"}]}]
        self.relato = []          # [(quem, o que fez, a que)]
        self.estado = None        # o que o ficheiro do jogo quiser guardar
        self.ordem = {}           # {unidade de fichas: [chave, ...]} no jogo junto

    def mostrar(self, texto):
        mostrar = getattr(self.config, "juntar_mostrar", None)
        return mostrar(self.estado, texto) if mostrar else texto

    def resolver(self, unidade, chave, tronco, versoes):
        # versoes: [(quem, como estava na base desse jogo, como esta agora)].
        # Devolve o texto que fica (None se a coisa deixa de existir).
        candidatos = []           # [(texto ou None, [quem])], so os diferentes
        mexido = False            # o tronco ja nao esta como na base de quem lhe mexeu?
        for quem, antes, agora in versoes:
            if _igual(antes, agora) or _igual(agora, tronco):
                continue
            if tronco is not None and not _igual(antes, tronco):
                mexido = True
            for candidato in candidatos:
                if _igual(candidato[0], agora):
                    candidato[1].append(quem)
                    break
            else:
                candidatos.append((agora, [quem]))
        if not candidatos:
            return tronco
        chamar = getattr(self.config, "juntar_chamar", None)
        exemplo = tronco if tronco is not None else [texto for texto, _ in candidatos if texto is not None][0]
        onde = chamar(unidade, chave, exemplo) if chamar else None
        if onde is None:
            onde = unidade if chave is None else chave + " (" + unidade + ")"
        if len(candidatos) == 1 and candidatos[0][0] is not None and not mexido:
            texto, quem = candidatos[0]
            self.relato.append((quem, "novo" if tronco is None else "mudou", onde))
            return texto
        if len(candidatos) > 1 and all(candidato[0] is not None for candidato in candidatos):
            ajuda = getattr(self.config, "juntar_duvida", None)
            sozinho = ajuda(self.estado, unidade, chave, tronco, versoes) if ajuda else None
            if sozinho is not None:
                self.relato.append(([nome for _, quem in candidatos for nome in quem], "juntei", onde))
                return sozinho

        # Uma duvida: ou ja ha decisao, ou fica a espera (e, entretanto, como
        # estava).
        opcoes = []
        for texto, quem in candidatos:
            if texto is None:
                opcoes.append({"quem": "Apagar (foi apagado em: " + ", ".join(quem) + ")", "texto": None})
            else:
                opcoes.append({"quem": "Como está em: " + ", ".join(quem), "texto": texto})
        if tronco is not None:
            opcoes.append({"quem": "Como já estava no jogo mais recente" if mexido else "Como estava antes", "texto": tronco})
        identidade = unidade + "/" + (chave if chave is not None else "")
        apagado = any(candidato[0] is None for candidato in candidatos)
        if len(candidatos) == 1 and candidatos[0][0] is not None:
            titulo = ("«" + onde + "» foi mudado em: " + ", ".join(candidatos[0][1])
                      + ". Mas o jogo mais recente já tinha outra mudança nisso.")
        elif len(candidatos) == 1:
            titulo = "«" + onde + "» foi apagado em: " + ", ".join(candidatos[0][1]) + ". Apaga-se para todos?"
        elif apagado:
            titulo = "«" + onde + "» foi apagado num jogo e mudado noutro."
        else:
            titulo = "«" + onde + "» foi mudado em mais do que um jogo, de maneiras diferentes."
        decisao = self.decisoes.get(identidade)
        if isinstance(decisao, int) and not isinstance(decisao, bool) and 0 <= decisao < len(opcoes):
            escolhida = opcoes[decisao]
            self.relato.append(([escolhida["quem"]], "escolhido", onde))
            return escolhida["texto"]
        # (Quando a duvida e apagar ou nao, ja vem marcado "nao apagar".)
        sugerida = len(opcoes) - 1 if apagado and tronco is not None else None
        self.duvidas.append({"id": identidade, "titulo": titulo, "sugerida": sugerida,
                             "opcoes": [{"quem": opcao["quem"],
                                         "texto": None if opcao["texto"] is None else self.mostrar(opcao["texto"].strip("\n"))}
                                        for opcao in opcoes]})
        return tronco

    def juntar(self, tronco, jogos):
        # tronco: o codigo do jogo que fica por baixo. jogos: [(quem, a base
        # desse jogo, como esta agora)], tudo em texto. Devolve o codigo junto.
        do_tronco = partir(tronco)
        partidos = [(quem, partir(base), partir(agora)) for quem, base, agora in jogos]

        # A ordem das unidades: a do tronco, e as novas a seguir a que tinham
        # antes delas no jogo de onde vem.
        nomes = [unidade.nome for unidade in do_tronco]
        for _, _, agora in partidos:
            anterior = None
            for unidade in agora:
                if unidade.nome not in nomes:
                    lugar = nomes.index(anterior) + 1 if anterior in nomes else len(nomes)
                    nomes.insert(lugar, unidade.nome)
                anterior = unidade.nome

        def procurar(unidades, nome):
            for unidade in unidades:
                if unidade.nome == nome:
                    return unidade
            return None

        saida = []
        for nome in nomes:
            esta = procurar(do_tronco, nome)
            todas = [(quem, procurar(base, nome), procurar(agora, nome)) for quem, base, agora in partidos]
            presentes = [u for u in [esta] + [u for _, b, a in todas for u in (b, a)] if u is not None]
            if all(unidade.tipo == "fichas" for unidade in presentes):
                texto = self.juntar_fichas(nome, esta, todas)
            else:
                texto = self.resolver(nome, None, esta.texto if esta else None,
                                      [(quem, b.texto if b else None, a.texto if a else None) for quem, b, a in todas])
            if texto is not None:
                saida.append(texto)
        return "\n".join(saida)

    def juntar_fichas(self, nome, esta, todas):
        # Um dicionario ou uma lista de fichas: junta-se ficha a ficha.
        def parte(unidade, qual):
            return getattr(unidade, qual) if unidade is not None else None

        # (Uma ficha a que mudaram o nome no sitio conta como a mesma ficha:
        # fica com a chave que tinha antes.)
        arrumadas = []
        for quem, base, agora in todas:
            fichas = list(agora.fichas) if agora is not None else []
            if base is not None and agora is not None:
                pares = pares_no_sitio(base.chaves(), agora.chaves())
                fichas = [(pares.get(chave, chave), texto) for chave, texto in fichas]
            arrumadas.append((quem, dict(base.fichas) if base is not None else {}, fichas, base, agora))

        if esta is None and all(base is None for _, _, _, base, _ in arrumadas):
            # A unidade toda e nova: so pode vir inteira.
            return self.resolver(nome, None, None, [(quem, None, parte(agora, "texto")) for quem, _, _, _, agora in arrumadas])

        cabeca = self.resolver(nome, "(o início)", parte(esta, "cabeca"),
                               [(quem, parte(base, "cabeca"), parte(agora, "cabeca")) for quem, _, _, base, agora in arrumadas])
        cauda = self.resolver(nome, "(o fim)", parte(esta, "cauda"),
                              [(quem, parte(base, "cauda"), parte(agora, "cauda")) for quem, _, _, base, agora in arrumadas])
        if cabeca is None or cauda is None:
            return None
        chaves = esta.chaves() if esta is not None else []
        for _, _, fichas, _, _ in arrumadas:
            chaves = chaves + [chave for chave, _ in fichas if chave not in chaves]
        do_tronco = dict(esta.fichas) if esta is not None else {}
        textos = []
        self.ordem[nome] = []
        for chave in chaves:
            versoes = []
            for quem, da_base, fichas, base, agora in arrumadas:
                if agora is None and base is None:
                    continue             # este jogo nem tem esta unidade
                versoes.append((quem, da_base.get(chave), dict(fichas).get(chave)))
            texto = self.resolver(nome, chave, do_tronco.get(chave), versoes)
            if texto is not None:
                textos.append(texto)
                self.ordem[nome].append(chave)
        return "\n".join([cabeca] + textos + [cauda])


def juntar(config, tronco, jogos, decisoes=None):
    # Devolve {"fonte", "duvidas", "relato", "avisos"}. Enquanto houver
    # duvidas, a "fonte" ainda nao e para usar.
    juncao = Juncao(config, decisoes)
    avisos = []
    preparar = getattr(config, "juntar_preparar", None)
    if preparar:
        tronco, jogos, juncao.estado, avisos = preparar(tronco, jogos)
    fonte = juncao.juntar(tronco, jogos)
    acabar = getattr(config, "juntar_acabar", None)
    if acabar and not juncao.duvidas:
        fonte = acabar(juncao.estado, fonte, juncao.ordem)
    return {"fonte": fonte, "duvidas": juncao.duvidas, "relato": juncao.relato, "avisos": avisos,
            "estado": juncao.estado}
