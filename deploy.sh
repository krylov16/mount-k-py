#!/bin/bash
echo "Stop container"
docker stop mount-k
docker rm mount-k
docker image rm krylov16/mount-k:latest
echo "Pull image"
docker pull krylov16/mount-k:latest
echo "Start frontend container"
docker run -p 8008:8088 --name mount-k -d krylov16/mount-k:latest
echo "Finish deploying!"