#!/usr/bin/env bash
# Instalar o pygame-ce para TODOS os utilizadores de um Linux Mint (ou
# Ubuntu/Debian), incluindo as sessões de convidado.
#
# Corre-o UMA vez por portátil, com uma conta de administrador (não como
# convidado), dentro da pasta clube-de-codigo-2627:
#
#     bash instalar-linux.sh
#
# Depois disso, qualquer pessoa, convidados incluídos, corre os jogos só com
#
#     python3 halloween/noite-dos-doces.py
#
# Porquê sem .venv: a pasta pessoal do convidado apaga-se ao terminar a
# sessão, e o convidado não pode usar sudo. Por isso o pygame-ce fica no
# Python do sistema, em /usr/local, que sobrevive e não mexe nos pacotes do
# apt. O pygame-ce não depende de mais nada, por isso não arrasta nada atrás.
#
# Pode correr-se outra vez sem estragar nada.

set -euo pipefail

# Trabalhar sempre na pasta do repositório, venha o terminal de onde vier.
cd "$(dirname "$(readlink -f "$0")")"

# O sudo pede a palavra-passe de quem está ligado, e o convidado não tem
# direito a sudo: nem com a palavra-passe certa funciona.
if [ "$(id -u)" -ne 0 ] && ! id -nG | grep -qwE 'sudo|admin'; then
    echo "Esta conta ($(id -un)) não pode instalar programas."
    echo "Termina a sessão, entra com a conta de administrador e corre outra vez."
    exit 1
fi

echo "==> 1/4  Pacotes do sistema (python3, pip)"
sudo apt-get update
sudo apt-get install -y python3 python3-pip

echo "==> 2/4  Retirar o pygame do apt, se existir (entra em conflito com o pygame-ce)"
if dpkg -s python3-pygame >/dev/null 2>&1; then
    sudo apt-get remove -y python3-pygame
fi

echo "==> 3/4  pygame-ce para todos os utilizadores"
# As variáveis PIP_* funcionam com pips novos e velhos (Mint 21 e 22); um
# pip que não as conheça ignora-as. A primeira autoriza instalar fora de um
# venv no Mint 22; a segunda cala o aviso de correr como root.
pip_sistema() {
    sudo -H env PIP_BREAK_SYSTEM_PACKAGES=1 PIP_ROOT_USER_ACTION=ignore \
        python3 -m pip install --no-cache-dir "$@"
}
# Se não houver "wheel" da versão fixa para este Python, instala a mais
# recente (ver requirements.txt).
if ! pip_sistema -r requirements.txt; then
    echo "    A versão fixa falhou. A instalar o pygame-ce mais recente."
    pip_sistema pygame-ce
fi

echo "==> 4/4  Confirmar, como utilizador normal"
python3 -c "import sys, pygame; print('Python', sys.version.split()[0], '| pygame-ce', pygame.version.ver)"

cat <<'FIM'

Pronto. Em qualquer sessão, convidado incluído, dentro da pasta do projeto:

    python3 halloween/noite-dos-doces.py

Atenção: os ficheiros do convidado apagam-se ao terminar a sessão.
O que os alunos quiserem guardar tem de ir para uma pen.
FIM
