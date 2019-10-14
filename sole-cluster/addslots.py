#!/bin/env python2
#coding:utf8
import redis
import sys
import traceback
import time

db = 0
auth = 'ericsson'
node = ["127.0.0.1", 16379]
TOTAL_SLOTS = 16384

r = redis.Redis(*node, password=auth)
print r.cluster("info")
print r.cluster("addslots", *range(0, TOTAL_SLOTS))
