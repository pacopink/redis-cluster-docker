# DO Health check on Redis Cluster
##  RETURN CODE:
```
      0 - Normal,
      1 - Failed,
          Conditions for RETURN CODE 1:
              a. connect to Redis instance failed or timeout
              b. connected to Redis instance, 'cluster info' shows cluster_status not 'ok'
      2 - Warning, Still can serve but abnormal
          Conditions for RETURN CODE 2:
              a. detect any unconnected instance in the cluster
              b. detect any master of slots partions, without connected slave instance to backup it
              c. detect any master and slave are allocated in the same host
              d. detect master instances distribution, that more than 'quorum can lost' number of master instances
                 are allocated on the same host, in this case, if the host is down, the remaining masters will failed to form quorum
```
Besides the script return code, there are some useful message printed to STDOUT
