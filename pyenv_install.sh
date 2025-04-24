#!/bin/bash

# 오류 발생 시 스크립트 중단
set -e

sudo apt update
sudo apt install -y make build-essential libssl-dev zlib1g-dev \
  libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
  libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev \
  libffi-dev liblzma-dev git


curl https://pyenv.run | bash

echo "쉘 설정 파일에 pyenv 설정 추가 중..."
{
  echo ''
  echo '# pyenv 설정'
  echo 'export PATH="$HOME/.pyenv/bin:$PATH"'
  echo 'eval "$(pyenv init --path)"'
  echo 'eval "$(pyenv virtualenv-init -)"'
} >> ~/.bashrc

# 현재 세션에 pyenv 적용
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv virtualenv-init -)"

echo "python 3.12.0 install"
pyenv install 3.12.0

echo "pyenv local 3.12.0"
pyenv local 3.12.0

echo "pyenv -v"
pyenv -v

echo "python --version"
python --version


