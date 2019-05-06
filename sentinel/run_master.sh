#!/bin/bash
IMG="daocloud.io/library/redis:3.2.10-alpine"
docker run --rm --name redis-master --hostname redis-master -ti ${IMG}
