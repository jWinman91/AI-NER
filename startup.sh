#!/bin/bash

if ! docker network ls --format '{{.Name}}' | grep -wq "JensNetwork"; then
  docker network create JensNetwork
fi

if [ "$(docker ps -a -q -f name=config_db)" ]; then
  if [ ! "$(docker ps -q -f name=config_db)" ]; then
    docker start "$(docker ps -a -q -f name=config_db)"
    sleep 5
  fi
else
  docker run --network=JensNetwork -e COUCHDB_USER=admin -e COUCHDB_PASSWORD=JensIsCool -p 5984:5984 -d --name config_db couchdb:latest
  sleep 5
fi

if [ ! "$(docker ps -q -f name=AINER)" ]; then
  docker build --tag ai_ner .
  docker run --network=JensNetwork -p 8000:8000 --name AINER ai_ner
else
  echo "Container is already running!"
fi