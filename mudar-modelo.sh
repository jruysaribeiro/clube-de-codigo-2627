#!/usr/bin/env bash
# Trocar o modelo que o OpenCode usa neste portátil, e testar se ele consegue
# mesmo alterar um ficheiro.
#
# Precisa de o instalar-opencode.sh já ter corrido neste portátil.
# Corre-se com uma conta de administrador (não como convidado):
#
#     sudo bash mudar-modelo.sh                 # usa o qwen2.5:7b
#     sudo bash mudar-modelo.sh qwen2.5:3b      # ou outro modelo do Ollama
#
# Com o modelo noutro computador da sala (um servidor com o Ollama aberto à
# rede), dá-se o endereço a seguir ao modelo. Aí não se descarrega nada aqui:
#
#     sudo bash mudar-modelo.sh qwen2.5:7b http://192.168.1.50:11434
#
# Faz três coisas:
#   1. descarrega o modelo (o qwen2.5:7b são cerca de 4,7 GB)
#   2. liga o OpenCode a esse modelo, com o ajudante curto do clube
#      (instruções pequenas e só as ferramentas de ler e editar: menos espera)
#   3. pede ao modelo uma mudança num ficheiro de teste e diz se resultou
#
# Pode correr-se outra vez sem estragar nada.

set -euo pipefail

MODELO="${1:-qwen2.5:7b}"
CONTEXTO="${CONTEXTO:-16384}"
SERVIDOR="${2:-}"
SERVIDOR="${SERVIDOR%/}"
URL_OLLAMA="${SERVIDOR:-http://127.0.0.1:11434}"

if [ "$(id -u)" -ne 0 ]; then
    echo "Isto precisa de administrador. Corre:  sudo bash $0 $MODELO"
    exit 1
fi
if ! command -v opencode >/dev/null 2>&1; then
    echo "Falta o opencode. Corre primeiro o instalar-opencode.sh."
    exit 1
fi

if [ -z "$SERVIDOR" ]; then
    echo "==> 1/3  Descarregar o modelo $MODELO"
    ollama pull "$MODELO"
else
    echo "==> 1/3  A usar o servidor $SERVIDOR"
    if ! curl -fsS --max-time 10 "$SERVIDOR/api/version" >/dev/null; then
        echo "O servidor $SERVIDOR não responde. Confirma o endereço, que os dois"
        echo "computadores estão na mesma rede, e que o Ollama do servidor aceita"
        echo "ligações de fora (OLLAMA_HOST=0.0.0.0 e a porta 11434 aberta)."
        exit 1
    fi
fi

if ! curl -fsS --max-time 30 "$URL_OLLAMA/api/show" -d "{\"model\":\"$MODELO\"}" \
        | grep -q '"tools"'; then
    echo "O modelo $MODELO não existe em $URL_OLLAMA ou não sabe usar"
    echo "ferramentas: o OpenCode não ia conseguir alterar ficheiros."
    exit 1
fi

echo "==> 2/3  Ligar o OpenCode ao $MODELO"
mkdir -p /etc/opencode
if [ -f /etc/opencode/opencode.json ]; then
    cp /etc/opencode/opencode.json /etc/opencode/opencode.json.anterior
fi
cat > /etc/opencode/opencode.json <<FIM
{
  "\$schema": "https://opencode.ai/config.json",
  "model": "ollama/$MODELO",
  "small_model": "ollama/$MODELO",
  "enabled_providers": ["ollama"],
  "autoupdate": false,
  "share": "disabled",
  "default_agent": "clube",
  "provider": {
    "ollama": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Ollama",
      "options": { "baseURL": "$URL_OLLAMA/v1" },
      "models": {
        "$MODELO": {
          "name": "$MODELO",
          "tool_call": true,
          "limit": { "context": $CONTEXTO, "output": 4096 }
        }
      }
    }
  },
  "agent": {
    "clube": {
      "mode": "primary",
      "description": "Ajudante do Clube de Código",
      "temperature": 0.2,
      "prompt": "És o ajudante do Clube de Código. Ajudas alunos dos 12 aos 18 anos a fazer um jogo em Python com pygame, sempre num único ficheiro. Responde em português de Portugal, com poucas frases.\n\nRegras:\n1. Antes de mudar código, lê o ficheiro com a ferramenta read.\n2. Faz uma mudança pequena de cada vez, com a ferramenta edit. Usa write só para criar um ficheiro novo. Nunca mostres o código só na conversa: altera mesmo o ficheiro.\n3. No edit, o oldString tem de ser copiado tal e qual do ficheiro, com os mesmos espaços e a mesma indentação.\n4. Depois de mudar, explica em duas ou três frases o que mudaste e porquê, para o aluno aprender.\n5. Se o pedido não for claro, faz uma pergunta curta em vez de adivinhar.",
      "permission": {
        "read": "allow", "edit": "allow",
        "bash": "deny", "glob": "deny", "grep": "deny", "list": "deny",
        "task": "deny", "todowrite": "deny", "webfetch": "deny",
        "websearch": "deny", "lsp": "deny", "skill": "deny", "question": "deny"
      }
    }
  }
}
FIM
chmod 644 /etc/opencode/opencode.json

echo "==> 3/3  Teste: pedir ao modelo para mudar um ficheiro"
echo "    Pode demorar vários minutos. Não é para interromper."
# O teste corre como utilizador normal, numa pasta só dele.
UTILIZADOR="${SUDO_USER:-nobody}"
PASTA="$(mktemp -d -p /tmp teste-opencode.XXXXXX)"
printf 'nome = "Clube"\nprint("Ola", nome)\n' > "$PASTA/ola.py"
chmod 777 "$PASTA"
chmod 666 "$PASTA/ola.py"
if command -v runuser >/dev/null 2>&1; then
    COMO=(runuser -u "$UTILIZADOR" --)
else
    COMO=(sudo -u "$UTILIZADOR")
fi

INICIO=$(date +%s)
"${COMO[@]}" env HOME="$PASTA" bash -c \
    "cd '$PASTA' && opencode run 'No ola.py, muda o nome para Maria.'" || true
SEGUNDOS=$(( $(date +%s) - INICIO ))

echo
echo "---- ola.py depois do pedido ----"
cat "$PASTA/ola.py"
echo "---------------------------------"
echo "Tempo: $(( SEGUNDOS / 60 )) min $(( SEGUNDOS % 60 )) s"

# Conta o que o programa faz, não como está escrito: 'Maria' ou "Maria" serve.
if [ "$(python3 "$PASTA/ola.py" 2>/dev/null)" = "Ola Maria" ] \
        && [ "$(grep -c . "$PASTA/ola.py")" -eq 2 ]; then
    echo "PASSOU: o $MODELO alterou o ficheiro e não estragou o resto."
else
    echo "FALHOU: o $MODELO não fez a mudança certa no ficheiro."
    echo "Para voltar ao modelo anterior:"
    echo "  sudo cp /etc/opencode/opencode.json.anterior /etc/opencode/opencode.json"
    exit 1
fi
