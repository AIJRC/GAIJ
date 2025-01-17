#!/bin/bash

# Update system and install necessary dependencies
sudo apt-get update

sudo docker run \
  --name=neo4j \
  -d \
  -p 7474:7474 -p 7687:7687 \
  -v $HOME/neo4j/data:/data \
  -v $HOME/neo4j/import:/var/lib/neo4j/import \
  -v $HOME/neo4j/logs:/logs \
  -v $HOME/neo4j/conf:/conf \
  --env NEO4J_AUTH=neo4j/test \
  neo4j