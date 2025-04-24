#!/bin/bash

set -e

apt update && apt install -y make build-essential libssl-dev zlib1g-dev \
  libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
  libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev \
  libffi-dev liblzma-dev git ca-certificates

export PYENV_ROOT="/root/.pyenv"
export PATH="$PYENV_ROOT/bin:$PYENV_ROOT/shims:$PATH"

curl https://pyenv.run | bash

echo "pyenv 설치 후 환경 설정"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv virtualenv-init -)"

echo "python 3.12.0 install 시작"
pyenv install 3.12.0

echo "pyenv local 설정"
pyenv local 3.12.0

echo "pyenv 버전:"
pyenv -v
echo "python 버전:"
python --version
