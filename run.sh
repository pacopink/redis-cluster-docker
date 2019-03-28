#!/bin/sh
REDIS_CONF=/usr/local/bin/redis.conf
REDIS_SERVER=/usr/local/bin/redis-server
#echo "perl -pi -e 's/port.*/port ${REDIS_PORT}/g' ${REDIS_CONF}"|sh
sed -i "s/port.*/port ${REDIS_PORT}/g" ${REDIS_CONF}
sed -i "s/PASSWORD/${REDIS_PASSWORD}/g" ${REDIS_CONF}

${REDIS_SERVER} ${REDIS_CONF}
