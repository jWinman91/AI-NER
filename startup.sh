#!/bin/bash

if [ "$(docker ps -a -q -f name=config_db)" ]; then
  if [ ! "$(docker ps -q -f name=config_db)" ]; then
    docker start "$(docker ps -a -q -f name=config_db)"
    sleep 5
  fi
else
  docker run -e COUCHDB_USER=admin -e COUCHDB_PASSWORD=JensIsCool -p 127.0.0.1:5984:5984 -d --name config_db couchdb:latest
  sleep 5
fi

#docker network create JensNetwork
#docker network connect JensNetwork config_db
#docker build --tag ai_ner .
#docker run --network=JensNetwork -p 8000:8000 --name AINER ai_ner

if ps aux | grep -v grep | grep "python app.py" > /dev/null; then
  echo "app.py is already running!"
else
  echo "Starting app.py ..."
  source venv/bin/activate
  python app.py > logs.txt  2>&1 &
  background_pid=$!
  if kill -0 "$background_pid" 2>/dev/null; then
    echo "app.py is running!"
  else
    echo "Something went wrong..."
  fi
fi