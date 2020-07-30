#!/bin/env python2
#coding:utf8
import redis
import sys
import time
import os

db = os.getenv('REDIS_DB')
db = 0 if db is None else db
auth = os.getenv('REDIS_AUTH')
node = os.getenv('REDIS_HOST_PORT')

def host(str):
    v = str.split(":")
    return [v[0], int(v[1])]


def host2(str):
    v = str.split(":")
    return [v[0], v[1]]


def host_port_db_auth(str):
    l = host(str)
    l.append(db)
    l.append(auth)
    return l
    

if __name__=="__main__":
    return_code = 0
    r = redis.Redis(*host_port_db_auth(node))
    info = None
    nodes = None
    try:
        info = r.cluster("info")
        nodes = r.cluster("nodes")
    except Exception as e:
        print e
        sys.exit(1)


    print "--- cluster info ---"
    for k,v in info.items():
        print k,v

    cluster_state = info['cluster_state'] 
    if cluster_state != 'ok':
        print "ERROR: cluster_state is not ok [%s]"%cluster_state
        sys.exit(1)

    cluster_size = int(info['cluster_size'])
    total_instances_count = len(nodes)

    # 记录master节点在主机上的分布 host->[node_id1, ..., node_idX]
    master_instances_distribution = dict()
    # 记录实例的node_id->host:port
    instances = dict()
    # key slots的分片，master_node_id->[slave_node_id1, ..., slave_node_idX]
    partitions = dict()
    # 记录unconnected的节点，与nodes同构
    unconnected = dict()
    # 记录实例是否connected状态 node_id->(True|False)
    instance_connnect_status = dict()
    # 记录实例分布在那个主机上 node_id->hostname
    instance_distribution = dict()

    for k,v in nodes.items():
        node_id = v['node_id']
        master_id = v['master_id']
        connected = v['connected']

        instance_connnect_status[node_id] = connected

        h, p = host2(k)
        instances[node_id] = k
        instance_distribution[node_id] = h

        if not connected: 
            unconnected[k] = v
        if 'master' in v['flags']:
            if 'fail' not in v['flags'] and connected:
                if h not in master_instances_distribution:
                    master_instances_distribution[h]  = list()
                master_instances_distribution[h].append(node_id)
                if node_id not in partitions:
                    partitions[node_id] = list()
        else:
            if master_id not in partitions:
                partitions[master_id] = list()
            partitions[master_id].append(node_id)

    print "--- counts ---"
    print "cluster_size: %d, total_instances_count: %d, unconnected_instances_count: %d"%(cluster_size, total_instances_count, len(unconnected))
    print "--- partitions ---"
    print partitions
    print "--- master_instances_distribution ---"
    print master_instances_distribution
    print "--- instances ---"
    print instances
    print "--- checking ---"


    if len(unconnected)>0:
        print "WARNING: there is some unconnected instances: %s"%unconnected
        return_code = 2

    for k in partitions:
        if len(partitions[k])<1:
            print "WARNING: there is an instance [%s] node_id=[%s] without 'slave' to backup"%(instances[k], k)
            return_code = 2

        any_connected_slave = reduce(lambda x,y: x or y, map(lambda x: instance_connnect_status[x], partitions[k]), False)
        if not any_connected_slave:
            print "WARNING: there is an instance [%s] node_id=[%s] without connected 'slave' to backup"%(instances[k], k)
            return_code = 2

        master_host = instance_distribution[k]
        for slave in partitions[k]:
            slave_host = instance_distribution[slave]
            if master_host == slave_host:
                print "WARNING: master_instance[%s] and its slave[%s] is in the same host[%s]"%(instances[k], instances[slave], master_host)
                return_code = 2


    # 从partition，计算最大的能失去的大小
    partition_count = len(partitions)
    min_quorum = int(partition_count/2) + 1
    max_can_lost = partition_count - min_quorum
    for k,v in master_instances_distribution.items():
        if len(v)>max_can_lost:
            print "WARNING: too many master instances(%d)>max_can_lost(%d) is running on host:[%s], if the host is out, your cluster will failed to quorum, reallocate some of them "%(len(v), max_can_lost, k)
            return_code = 2

    if return_code == 0:
        print "INFO: Cluster OK"
    else:
        sys.exit(return_code)
