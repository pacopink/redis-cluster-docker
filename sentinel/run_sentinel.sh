#!/bin/bash
IMG="daocloud.io/library/redis:3.2.10-alpine"
PATH_HOME=`pwd`

NAME=redis-sentinel${1}
docker run --rm --name $NAME --hostname $NAME \
    --link redis-master:master \
    -v ${PATH_HOME}/conf/sentinel.conf:/usr/local/bin/sentinel.conf \
    -v ${PATH_HOME}/conf/run_sentinel.sh:/run.sh \
    -ti ${IMG} /run.sh
