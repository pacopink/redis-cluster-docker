###ATTENTON: In this branch, add password 'ericsdad' to all redis instances, so you need to add '-a ericsdad' in redis-cli

Use docker to build a redis cluster with 6 instances for testing 
The 6 instances are divided into 3 shards, 1 master- 1 slave per shard,
so that HA can be achived.
```
.
├── Dockerfile
├── build.sh      # used to build customized  docker image named: 'redis-cluster'
├── docker-run-nodes.sh   # run 6 docker containers from image 'redis-clsuter', redis-node[0-5], listens to localhost:701[0-5]
├── form-cluster.py  # python script to assign slots and roles to redis-node[0-6]
├── redis.conf   # this is the template redis.conf to build into 'redis-cluster' image, 'run.sh' will replace ports with -e values from docker run.
├── run.sh       # this is the script is the entrypoint of  'redis-cluster' image, which will replace redis.conf with user specified port before run redis-server
├── docker-clean-nodes.sh # run this to docker stop and docker rm redis-node[0-5]
├── README.md    # this file as you can see
└── start-cluster.sh # run this if you want to start all nodes
```

## Step 1: Build a customized redis docker image

run build.sh to build a customized docker image named : redis-cluster

## Step 2: run 6 docker containers from image 'redis-clsuter'

run 'docker-run-nodes.sh', then you will get 6 independent docker containers of redis instance, 
named redis-node[0-5] which listens to localhost:701[0-5]

## Step 3: assign master-slave role , and assign slots to each shard of redis-node[0-5]

here we use a python script to do this, 3 nodes will be master of 3 shards, and the rest will be slave for each.
```
% python ./form-cluster.py 
Master Nodes:  ['127.0.0.1:7010', '127.0.0.1:7012', '127.0.0.1:7014']
Replication Groups:  [('127.0.0.1:7010', '127.0.0.1:7011'), ('127.0.0.1:7012', '127.0.0.1:7013'), ('127.0.0.1:7014', '127.0.0.1:7015')]
```
## Step 4: test it 

### redis-cli test, you can see slot calulation and redirection between shards
an extra -c argument shall be added to let redis-cli aware that it is connecting to a redis cluster, so that it can accept redirection
you can connect to any instance at first, even a slave can do.
```
% redis-cli -c -p 7011
127.0.0.1:7011> get a
-> Redirected to slot [15495] located at 127.0.0.1:7014
(nil)
127.0.0.1:7014> get b
-> Redirected to slot [3300] located at 127.0.0.1:7012
(nil)
127.0.0.1:7012> get aa
-> Redirected to slot [1180] located at 127.0.0.1:7010
(nil)
127.0.0.1:7010> get dd
-> Redirected to slot [11212] located at 127.0.0.1:7012
(nil)
```
### try to docker stop a master node redis-node0, that is 127.0.0.1:7010
```
% docker stop redis-node0
redis-node0
```
### then set a key which are in the shard, you can see the former slave takes over master to serve
```
127.0.0.1:7012> set aa value
-> Redirected to slot [1180] located at 127.0.0.1:7011
OK
127.0.0.1:7011> get aa
"value"
```
### docker start redis-node0
```
% docker start redis-node0
redis-node0
```
### after it start up, it takes the slave role, use cluster failover to regain master role
```
127.0.0.1:7010> ROLE
1) "slave"
2) "127.0.0.1"
3) (integer) 7011
4) "connected"
5) (integer) 183
127.0.0.1:7010> CLUSTER FAILOVER
OK
127.0.0.1:7010> ROLE
1) "master"
2) (integer) 310
3) 1) 1) "127.0.0.1"
      2) "7011"
      3) "310"
127.0.0.1:7010> 

127.0.0.1:7011> role
1) "slave"
2) "127.0.0.1"
3) (integer) 7010
4) "connected"
5) (integer) 422
```
### the key-value we set before is not lost, the that is how the HA works, enjoy it.
```
127.0.0.1:7011> get aa
-> Redirected to slot [1180] located at 127.0.0.1:7010
"value"
127.0.0.1:7010> get aa
"value"
```
