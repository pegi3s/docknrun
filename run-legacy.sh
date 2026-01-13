#!/bin/bash

docker build ./ -t pegi3s/docknrun-legacy -f Dockerfile.legacy

xhost +

docker run --rm -ti -e USERID=$UID -e USER=$USER -e DISPLAY=$DISPLAY \
    -v /var/db:/var/db:Z -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v $HOME/.Xauthority:/home/developer/.Xauthority \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v /tmp:/tmp \
    -v $PWD/data:/data pegi3s/docknrun
