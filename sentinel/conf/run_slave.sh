#!/bin/sh

REDIS_CONF=/usr/local/bin/redis.conf
REDIS_SERVER=/usr/local/bin/redis-server

sed "s/__MASTER__/${MASTER_PORT_6379_TCP_ADDR} 6379/g" ${REDIS_CONF} > ${REDIS_CONF}.2

${REDIS_SERVER} ${REDIS_CONF}.2
