#!/usr/bin/env bash
# Instalar o Python e o pygame-ce num Mac, para TODOS os utilizadores.
#
# Uma vez por Mac, com uma conta de administrador, no Terminal, dentro da
# pasta clube-de-codigo-2627:
#
#     bash instalar-mac.sh
#
# Porquê o Python do python.org: o python3 que vem com o macOS é o 3.9, e o
# pygame-ce já não tem versão para ele. O do python.org instala-se para
# todas as contas do Mac e não é "externally managed" como o do Homebrew.
#
# Pode correr-se outra vez sem estragar nada.

set -euo pipefail

VERSAO=3.12.10
PY=/Library/Frameworks/Python.framework/Versions/3.12/bin/python3.12

# Trabalhar sempre na pasta do repositório, venha o terminal de onde vier.
cd "$(dirname "$0")"

if ! id -Gn | grep -qw admin; then
    echo "Esta conta ($(id -un)) não é de administrador e não pode instalar programas."
    echo "Entra com uma conta de administrador e corre outra vez."
    exit 1
fi

echo "==> 1/3  Python $VERSAO do python.org"
if [ -x "$PY" ]; then
    echo "    Já está instalado."
else
    PKG="$(mktemp -d)/python-$VERSAO-macos11.pkg"
    curl -L --fail -o "$PKG" "https://www.python.org/ftp/python/$VERSAO/python-$VERSAO-macos11.pkg"
    sudo installer -pkg "$PKG" -target /
    rm -f "$PKG"
fi

echo "==> 2/3  pygame-ce para todos os utilizadores"
pip_sistema() {
    sudo -H env PIP_ROOT_USER_ACTION=ignore PIP_DISABLE_PIP_VERSION_CHECK=1 \
        "$PY" -m pip install --no-cache-dir "$@"
}
# Se não houver "wheel" da versão fixa para este Python, instala a mais
# recente (ver requirements.txt).
if ! pip_sistema -r requirements.txt; then
    echo "    A versão fixa falhou. A instalar o pygame-ce mais recente."
    pip_sistema pygame-ce
fi

echo "==> 3/3  Confirmar"
"$PY" -c "import sys, pygame; print('Python', sys.version.split()[0], '| pygame-ce', pygame.version.ver)"

# O python3 que o Terminal encontra primeiro pode ser outro (o do Homebrew,
# por exemplo). Escolher o comando mais curto que já tem o pygame-ce. O
# /usr/bin/python3 fica de fora: sem as ferramentas da Apple, abre uma
# janela a pedir para as instalar.
CMD="$PY"
for c in python3.12 python3; do
    p="$(command -v "$c" || true)"
    if [ -n "$p" ] && [ "$p" != /usr/bin/python3 ] &&
        "$p" -c "import pygame" >/dev/null 2>&1; then
        CMD="$c"
    fi
done

cat <<FIM

Pronto. Em qualquer conta deste Mac, num Terminal NOVO, dentro desta pasta:

    $CMD halloween/noite-dos-doces.py
FIM
