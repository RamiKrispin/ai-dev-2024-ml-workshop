#!/usr/bin/env bash

apt-get update && apt-get install -y --no-install-recommends \
    sudo \
    wget \
    git \
     && rm -rf /var/lib/apt/lists/*