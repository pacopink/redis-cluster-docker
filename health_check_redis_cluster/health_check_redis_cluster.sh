#!/usr/bin/env bash
# 2020-7-30 Paco Li
# DO Health check on Redis Cluster
# RETURN CODE: 
#       0 - Normal, 
#       1 - Failed, 
#           Conditions for RETURN CODE 1:
#               a. connect to Redis instance failed or timeout
#               b. connected to Redis instance, 'cluster info' shows cluster_status not 'ok'
#       2 - Warning, Still can serve but abnormal
#           Conditions for RETURN CODE 2:
#               a. detect any unconnected instance in the cluster
#               b. detect any master of slots partions, without connected slave instance to backup it
#               c. detect master instances distribution, that more than 'quorum can lost' number of master instances 
#                  are allocated on the same host, in this case, if the host is down, the remaining masters will failed to form quorum
# Besides the script return code, there are some useful message printed to STDOUT


# Set your redis cluster AUTH 
export REDIS_AUTH="******"
# Set your redis instance to conenct
export REDIS_HOST_PORT="192.168.232.181:7015"
# The real python script to do the check
python ./check_redis_cluster.py
