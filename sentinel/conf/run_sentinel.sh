#!/bin/sh

REDIS_CONF=/usr/local/bin/sentinel.conf
REDIS_SERVER=/usr/local/bin/redis-sentinel

sed "s/MASTER/${MASTER_PORT_6379_TCP_ADDR}/g" ${REDIS_CONF} > ${REDIS_CONF}.2
sed -i "s/PORT/6379/g" ${REDIS_CONF}.2
sed -i "s/MIN_QUORUM/1/g" ${REDIS_CONF}.2

${REDIS_SERVER} ${REDIS_CONF}.2
