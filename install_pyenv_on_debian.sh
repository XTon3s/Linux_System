#!/bin/bash
#필수 패키지 설치
apt-get update && apt-get install -y \
  build-essential libssl-dev zlib1g-dev libbz2-dev \
  libreadline-dev libsqlite3-dev wget curl llvm \
  libncursesw5-dev xz-utils tk-dev libxml2-dev \
  libxmlsec1-dev libffi-dev liblzma-dev git

# pyenv 설치
curl https://pyenv.run | bash

# pyenv 환경 설정
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

source ~/.bashrc  # 또는 source ~/.zshrc

# python 3.12 설치 및 로컬 설정
pyenv install 3.12

pyenv local 3.12

exit 0
