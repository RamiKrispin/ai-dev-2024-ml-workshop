#!/usr/bin/env bash

VENV_NAME=$1

python3 -m venv /opt/$VENV_NAME  \
    && export PATH=/opt/$VENV_NAME/bin:$PATH \
    && echo "source /opt/$VENV_NAME/bin/activate" >> ~/.bashrc

apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*
source /opt/$VENV_NAME/bin/activate 

pip install --upgrade pip

pip3 install  --no-cache-dir -r ./requirements/requirements.txt