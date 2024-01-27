docker run -e COUCHDB_USER=admin -e COUCHDB_PASSWORD=JensIsCool -p 127.0.0.1:5984:5984 -d --name config_db couchdb:latest
docker network create JensNetwork
docker network connect JensNetwork config_db
docker build --tag ai_ner .
docker run --network=JensNetwork -p 8000:8000 --name AINER ai_ner