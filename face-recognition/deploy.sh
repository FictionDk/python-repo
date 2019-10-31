#!/bin/bash
set -e
REPO_NAME="stpass"
CONTANER_NAME="face_compare"
VERSION="1.0"

function remove()
{
    sudo docker rm -f ${CONTANER_NAME} || true
    sudo docker rmi ${REPO_NAME}/${CONTANER_NAME}:${VERSION} || true
}

function buildImage()
{
    remove
    sudo docker build -t ${REPO_NAME}/${CONTANER_NAME} .
}

buildImage
sudo docker run -d -p 5001:5001 --restart=always --name ${CONTANER_NAME} ${REPO_NAME}/${CONTANER_NAME}

sudo docker volume rm $(sudo docker volume "ls" "-qf" dangling=true) || true
sudo docker rm -f $(sudo docker ps -a | grep "Exited" | awk '{print $1 }') || true
sudo docker rmi $(sudo docker images | grep "none" | awk '{print $3}') || true
