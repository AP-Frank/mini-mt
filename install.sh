#!/bin/bash

REPO="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# first we install python 3.7
cd ~

sudo apt update
sudo apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev wget

wget https://www.python.org/ftp/python/3.7.3/Python-3.7.3.tar.xz
tar -xf Python-3.7.3.tar.xz

cd Python-3.7.3
./configure

make -j 4

sudo make altinstall

sudo -H pip3.7 install -U pipenv

cd "$REPO"
pipenv install
