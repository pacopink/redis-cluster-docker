#!/bin/bash
for i in 0 1 2 3 4 5
do
    docker run --restart always --name redis-node${i} -d -e REDIS_PORT=701${i} -e REDIS_PASSWORD=ericsdad --network host redis-cluster
done
