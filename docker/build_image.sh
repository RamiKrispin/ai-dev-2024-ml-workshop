#!/bin/bash

echo "Build the docker"

# Identify the CPU type (M1 vs Intel)
if [[ $(uname -m) ==  "aarch64" ]] ; then
  CPU="arm64"
elif [[ $(uname -m) ==  "arm64" ]] ; then
  CPU="arm64"
else
  CPU="amd64"
fi


label="ai-dev"
tag="$CPU.0.0.1"
image="rkrispin/$label:$tag"

docker build . -f Dockerfile \
               --progress=plain \
               --build-arg QUARTO_VER="1.5.45" \
               --build-arg VENV_NAME="ai_dev_workshop" \
               -t $image

if [[ $? = 0 ]] ; then
echo "Pushing docker..."
docker push $image
else
echo "Docker build failed"
fi