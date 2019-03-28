#!/bin/bash
docker rmi redis-cluster
docker build -t redis-cluster .
