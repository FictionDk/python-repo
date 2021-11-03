#!/bin/bash
set -e
REPO_NAME="stpass"
CONTANER_NAME="random"
VERSION="1.0"
PORT=10006

PWD_DIR="$(cd `dirname $0`; pwd)"
ASSERT_DIR="${PWD_DIR}/source"
CONFIG_DIR="${PWD_DIR}/config"

function remove()
{
    sudo docker rm -f ${CONTANER_NAME} || true
    sudo docker rmi ${REPO_NAME}/${CONTANER_NAME}:${VERSION} || true
}

function build()
{
    sudo docker build -t ${REPO_NAME}/${CONTANER_NAME}:${VERSION} .
}

function run()
{
    sudo docker run -d -p ${PORT}:${PORT} --restart=always --name ${CONTANER_NAME} \
        -v $CONFIG_DIR:/root/config -v $ASSERT_DIR:/root/source \
        ${REPO_NAME}/${CONTANER_NAME}:${VERSION}
}

remove
build
run

#sudo docker volume rm $(sudo docker volume "ls" "-qf" dangling=true) || true
#sudo docker rm -f $(sudo docker ps -a | grep "Exited" | awk '{print $1 }') || true
#sudo docker rmi $(sudo docker images | grep "none" | awk '{print $3}') || true
