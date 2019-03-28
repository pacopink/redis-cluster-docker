#!/bin/env python2
#coding:utf8
import redis
import sys
import traceback
import time

db = 0
auth = 'ericsdad'
nodes = [
        "127.0.0.1:7010",
        "127.0.0.1:7011",
        "127.0.0.1:7012",
        "127.0.0.1:7013",
        "127.0.0.1:7014",
        "127.0.0.1:7015",
        ]
masters = []
# 每个shard有几个节点跑，不得小于1,
# 1表示无备份，2表示1备份，3表示2备份，以此类推
replicate_group_node_num =  2
num = len(nodes)


# check number and replica
if num%replicate_group_node_num != 0:
    print "total node number cannot be divided by replicate_group_node_num evenly"
    sys.exit(1)

def host(str):
    v = str.split(":")
    return [v[0], int(v[1])]

def host_port_db_auth(str):
    l = host(str)
    l.append(db)
    l.append(auth)
    return l


def meetup():
    '''meet up nodes and collect node ids'''
    r = redis.Redis(*host_port_db_auth(nodes[0]))
    for node in nodes[1:]:
        r.cluster("meet", *host(node))

def replicate():
    pairs = [] # master-slave pairs
     
    m = replicate_group_node_num
    for i in range(0, num/m):
        master = nodes[i*m]
        masters.append(master) # save master

        slaves = nodes[i*m+1:i*m+m]
        for slave in slaves:
            pairs.append((master, slave)) # save master-slave pair

    print "Master Nodes: ", masters
    print "Replication Groups: ", pairs
    # make all slaves replicate to its master
    for pair in pairs:
        master = pair[0]
        slave = pair[1]
        masters.append(master)
        r = redis.Redis(*host_port_db_auth(slave))
        while True:
            try:
                # it is chance that failed to get cluster, need to retry
                masterId = r.cluster("nodes")[master]['node_id']
                r.cluster("replicate", masterId)
                break
            except Exception, e:
                #traceback.print_exc()
                time.sleep(0.3)


def assign_slots_by_range():
    '''assign slots by range to masters'''
    TOTAL_SLOTS = 16384
    num = len(masters)
    per_node = TOTAL_SLOTS/num
    for i in range(0, num):
        start_slot = i*per_node
        end_slot = i*per_node+per_node
        r = redis.Redis(*host_port_db_auth(masters[i]))
        r.cluster("addslots", *range(start_slot, end_slot))

    odd_slots = TOTAL_SLOTS-per_node*num
    if odd_slots>0:
        r = redis.Redis(*host_port_db_auth(masters[num-1]))
        r.cluster("addslots", *range(per_node*num, per_node*num+odd_slots))
    
if __name__=="__main__":
    meetup()
    replicate()
    try:
        assign_slots_by_range()
    except Exception,e:
        traceback.print_exc()
        print "Encouter exception: ", e
        print "seems you already formed a cluster"

