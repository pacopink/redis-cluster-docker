#!/bin/bash
docker run --restart always --name sole-redis-cluster -d -e REDIS_PORT=16379 -e REDIS_PASSWORD=ericsson --network host redis-cluster
