#!/usr/bin/env bash
# Instalar o OpenCode (assistente de programação) num portátil Linux Mint,
# Ubuntu ou Debian, para TODOS os utilizadores, convidados incluídos, com um
# modelo pequeno a correr no próprio portátil (sem GPU, sem contas, sem nuvem).
#
# Instala e liga quatro coisas:
#   1. Ollama            o programa que corre o modelo (serviço do sistema)
#   2. o modelo          qwen2.5-coder:1.5b, cerca de 1 GB
#   3. OpenCode          em /usr/local/bin, já configurado para falar com o Ollama
#   4. extensão OpenCode no VS Code de cada utilizador e dos convidados
#
# Corre-o UMA vez por portátil, a partir da pen, com uma conta de
# administrador (não como convidado). Precisa de internet (descarrega ~3 GB):
#
#     sudo bash instalar-opencode.sh
#
# Outro modelo:
#
#     sudo MODELO=qwen2.5-coder:3b bash instalar-opencode.sh
#
# Um servidor partilhado em vez de um modelo em cada portátil (não instala o
# Ollama nem o modelo; o servidor tem de ter o Ollama com OLLAMA_HOST=0.0.0.0):
#
#     sudo bash instalar-opencode.sh http://192.168.1.50:11434
#
# Pode correr-se outra vez sem estragar nada.

set -euo pipefail

MODELO="${MODELO:-qwen2.5-coder:1.5b}"
# O OpenCode manda instruções longas ao modelo. Com o contexto por omissão do
# Ollama (4096) elas são cortadas e o modelo deixa de conseguir editar ficheiros.
CONTEXTO="${CONTEXTO:-16384}"
SERVIDOR="${1:-}"
SERVIDOR="${SERVIDOR%/}"
EXTENSAO="sst-dev.opencode"

if [ "$(id -u)" -ne 0 ]; then
    echo "Isto precisa de administrador. Corre:  sudo bash $0"
    exit 1
fi

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

if [ -n "$SERVIDOR" ]; then
    URL_OLLAMA="$SERVIDOR"
else
    URL_OLLAMA="http://127.0.0.1:11434"
fi

ollama_responde() { curl -fsS --max-time 5 "$URL_OLLAMA/api/version" >/dev/null 2>&1; }

esperar_ollama() {
    for _ in $(seq 1 30); do
        ollama_responde && return 0
        sleep 1
    done
    return 1
}

echo "==> 1/5  Pacotes do sistema"
export DEBIAN_FRONTEND=noninteractive
# Um repositório de terceiros avariado não deve impedir a instalação.
apt-get update || echo "    (apt-get update deu erros; a continuar com as listas que há)"
# O gpg é preciso para o VS Code registar a chave do seu repositório.
apt-get install -y curl ca-certificates tar unzip zstd gpg

if [ -z "$SERVIDOR" ]; then
    echo "==> 2/5  Ollama e o modelo $MODELO"
    # São mais de 1 GB: não se volta a descarregar se já cá estiver.
    if command -v ollama >/dev/null 2>&1; then
        echo "    O Ollama já está instalado ($(ollama --version 2>/dev/null | tail -1))"
    else
        curl -fsSL https://ollama.com/install.sh | sh
    fi

    if [ -d /run/systemd/system ]; then
        mkdir -p /etc/systemd/system/ollama.service.d
        cat > /etc/systemd/system/ollama.service.d/clube.conf <<FIM
[Service]
Environment="OLLAMA_CONTEXT_LENGTH=$CONTEXTO"
Environment="OLLAMA_KEEP_ALIVE=30m"
FIM
        systemctl daemon-reload
        systemctl enable ollama
        systemctl restart ollama
    else
        # Sem systemd (contentores, por exemplo): arrancar o Ollama à mão.
        OLLAMA_CONTEXT_LENGTH="$CONTEXTO" OLLAMA_KEEP_ALIVE=30m \
            nohup ollama serve >/var/log/ollama-clube.log 2>&1 &
    fi

    if ! esperar_ollama; then
        echo "O Ollama instalou mas não responde em $URL_OLLAMA."
        echo "Vê o que se passa com:  journalctl -u ollama -n 30"
        exit 1
    fi
    ollama pull "$MODELO"
else
    echo "==> 2/5  A usar o servidor $SERVIDOR (não se instala o Ollama aqui)"
    if ! ollama_responde; then
        echo "O servidor $SERVIDOR não responde. Confirma o endereço, a rede e"
        echo "que o Ollama do servidor está a correr com OLLAMA_HOST=0.0.0.0."
        exit 1
    fi
fi

# O OpenCode só edita ficheiros se o modelo souber chamar ferramentas.
if ! curl -fsS --max-time 30 "$URL_OLLAMA/api/show" -d "{\"model\":\"$MODELO\"}" \
        | grep -q '"tools"'; then
    echo "AVISO: o modelo $MODELO não existe em $URL_OLLAMA ou não sabe usar"
    echo "       ferramentas. O OpenCode vai conversar mas não vai editar ficheiros."
fi

echo "==> 3/5  OpenCode para todos os utilizadores"
# O instalador oficial instala em \$HOME/.opencode/bin. Dá-se-lhe uma pasta
# temporária como HOME e copia-se o programa para /usr/local/bin.
curl -fsSL https://opencode.ai/install -o "$TMP/instalar-opencode"
HOME="$TMP" bash "$TMP/instalar-opencode" --no-modify-path
# Se a versão mais recente já estiver instalada, o instalador não descarrega
# nada e não há ficheiro para copiar: fica o que já lá está.
if [ -f "$TMP/.opencode/bin/opencode" ]; then
    install -m 755 "$TMP/.opencode/bin/opencode" /usr/local/bin/opencode
elif [ ! -x /usr/local/bin/opencode ]; then
    echo "O instalador do OpenCode não deixou o programa onde se esperava."
    exit 1
fi

echo "==> 4/5  Ligar o OpenCode ao modelo"
# /etc/opencode vale para todos os utilizadores e ganha a qualquer outra
# configuração. Só o Ollama fica disponível: nada do que os alunos escrevem
# sai para serviços na nuvem, e não há partilha de conversas.
mkdir -p /etc/opencode
cat > /etc/opencode/opencode.json <<FIM
{
  "\$schema": "https://opencode.ai/config.json",
  "model": "ollama/$MODELO",
  "small_model": "ollama/$MODELO",
  "enabled_providers": ["ollama"],
  "autoupdate": false,
  "share": "disabled",
  "provider": {
    "ollama": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Ollama",
      "options": {
        "baseURL": "$URL_OLLAMA/v1"
      },
      "models": {
        "$MODELO": {
          "name": "$MODELO",
          "tool_call": true,
          "limit": {
            "context": $CONTEXTO,
            "output": 4096
          }
        }
      }
    }
  }
}
FIM
chmod 644 /etc/opencode/opencode.json

echo "==> 5/5  Extensão OpenCode no VS Code"
if command -v code >/dev/null 2>&1; then
    EDITOR_CLI=code;   PASTA_EXT=.vscode/extensions
elif command -v codium >/dev/null 2>&1; then
    EDITOR_CLI=codium; PASTA_EXT=.vscode-oss/extensions
else
    echo "    Não há VS Code neste portátil. A instalar."
    case "$(dpkg --print-architecture)" in
        amd64) ARQ=x64 ;;
        arm64) ARQ=arm64 ;;
        *) echo "Arquitetura sem VS Code: $(dpkg --print-architecture)"; exit 1 ;;
    esac
    curl -fL "https://code.visualstudio.com/sha/download?build=stable&os=linux-deb-$ARQ" \
        -o "$TMP/code.deb"
    echo "code code/add-microsoft-repo boolean true" | debconf-set-selections
    apt-get install -y "$TMP/code.deb"
    EDITOR_CLI=code;   PASTA_EXT=.vscode/extensions
fi

FALHAS=0

# Contas normais: cada uma instala a extensão na sua própria pasta.
while IFS=: read -r nome _ uid _ _ casa shell; do
    [ "$uid" -ge 1000 ] && [ "$uid" -lt 60000 ] || continue
    [ -d "$casa" ] || continue
    case "$shell" in */nologin|*/false) continue ;; esac
    echo "    $nome"
    if ! sudo -u "$nome" -H "$EDITOR_CLI" --install-extension "$EXTENSAO" --force \
            >"$TMP/ext.log" 2>&1; then
        sed 's/^/        /' "$TMP/ext.log"
        FALHAS=1
    fi
done < /etc/passwd

# Convidados e contas criadas mais tarde: a pasta pessoal nasce como cópia do
# "skel", por isso a extensão vai para lá.
for skel in /etc/skel /etc/guest-session/skel; do
    [ -d "$skel" ] || continue
    echo "    $skel (convidados e contas novas)"
    mkdir -p "$skel/$PASTA_EXT"
    if ! "$EDITOR_CLI" --no-sandbox --user-data-dir "$TMP/vscode-dados" \
            --extensions-dir "$skel/$PASTA_EXT" \
            --install-extension "$EXTENSAO" --force >"$TMP/ext.log" 2>&1; then
        sed 's/^/        /' "$TMP/ext.log"
        FALHAS=1
    fi
    chmod -R a+rX "$skel/${PASTA_EXT%%/*}"
done

echo "==> Confirmar"
echo "    OpenCode $(opencode --version)"
# Como utilizador sem privilégios, para provar que não depende do root.
if command -v runuser >/dev/null 2>&1; then
    COMO_NINGUEM=(runuser -u nobody --)
else
    COMO_NINGUEM=(sudo -u nobody)
fi
CASA_TESTE="$(mktemp -d -p /tmp)"
chmod 777 "$CASA_TESTE"
if "${COMO_NINGUEM[@]}" env HOME="$CASA_TESTE" \
        opencode models 2>/dev/null | grep -qxF "ollama/$MODELO"; then
    echo "    O OpenCode vê o modelo ollama/$MODELO"
else
    echo "    AVISO: o OpenCode não mostra o modelo ollama/$MODELO."
    echo "    Corre  opencode models  para ver o que ele encontra."
    FALHAS=1
fi

if [ "$FALHAS" -ne 0 ]; then
    echo
    echo "Instalado, mas com avisos: lê as linhas acima."
    exit 1
fi

cat <<FIM

Pronto. Em qualquer sessão, convidado incluído:

  - No VS Code: abrir a pasta do projeto e carregar em Ctrl+Esc
    (ou no botão do OpenCode, no canto superior direito).
  - No terminal: entrar na pasta do projeto e escrever  opencode

Modelo: $MODELO em $URL_OLLAMA
A primeira resposta demora mais: o modelo tem de ser carregado para a memória.
FIM
