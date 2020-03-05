#!/bin/python

import redis
import json
import sys
import os

r = redis.Redis(os.getenv("REDIS_HOST"), os.getenv("REDIS_PORT"), password=os.getenv("REDIS_PWD"))
nodes = r.cluster("nodes")

cluster_ok = True

node_list = list()
for k,v in nodes.items():
	(host, port) = k.split(":")
	nodeId = v["node_id"]
        masterId = v["master_id"]
	master = True if v["flags"].find("master")>=0 else False
	fail = True if v["flags"].find("fail")>=0 else False
	not_connected = not v["connected"]
	if fail or not_connected:
		print "node failed or not_connected"
		print json.dumps(nodes, indent=2)
		sys.exit(1)	
	node_list.append((nodeId, k, host, masterId, master))

nodeMapByNodeId = dict()
nodeMapByHostPort = dict()
nodeMapByHost = dict()
slaveMapByMasterId = dict()
for n in node_list:
	nid = n[0]
	hostPort = n[1]
	host = n[2]
	nodeMapByNodeId[nid] = n
	nodeMapByHostPort[hostPort] = n
	if host not in nodeMapByHost:
		nodeMapByHost[host] = list()
	nodeMapByHost[host].append(n)
	if not n[4]:
		masterId = n[3]
		slaveMapByMasterId[masterId] = n

minQuorum = int((len(slaveMapByMasterId)*1.0/2)+0.5)
print "minQuorum={mq}".format(mq=minQuorum)

def countMaster(l):
	c = 0
	for i in l:
		if i[4]:
			c+=1
	return c

for k,v in nodeMapByHost.items():
	print "Host: {host} - master# {master}".format(host=k, master=countMaster(v))	
	if countMaster(v) >= minQuorum:
		cluster_ok = False
		print "detect more than mininual quorum ({minQuorum}) master in one host, single point failure risk!!!".format(minQuorum=minQuorum)
		#slaves = map(lambda x:nodeMapByHost[x[2]], map(lambda x:slaveMapByMasterId[x[0]], filter(lambda x:x[4]==True, v)))
		#print slaves
		failover_candidates = list()
		for m in v:
		        hostPort = m[1]	
			nid = m[0]
			slave = slaveMapByMasterId[nid]
			slaveHost = slave[2]
			failover_candidates.append((countMaster(nodeMapByHost[slaveHost]), hostPort, slave[1]))
			#if countMaster(nodeMapByHost[slaveHost])==0:
			#	print "suggest to failover "+ hostPort+ " to", slave[1]
		#print failover_candidates
		failover_candidates.sort()
		print "suggest to failover "+ failover_candidates[0][1] + " to", failover_candidates[0][2]

if cluster_ok:
	print "cluster ok"
	sys.exit(0)
else:
	print "cluster have some problems"
	sys.exit(1)
