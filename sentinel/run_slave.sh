#!/bin/bash
IMG="daocloud.io/library/redis:3.2.10-alpine"
PATH_HOME=`pwd`

NAME=redis-slave
docker run --rm --name $NAME --hostname $NAME \
    --link redis-master:master \
    -v ${PATH_HOME}/conf/redis.conf:/usr/local/bin/redis.conf \
    -v ${PATH_HOME}/conf/run_slave.sh:/run_slave.sh \
    -ti ${IMG} /run_slave.sh
