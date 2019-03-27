for i in 0 1 2 3 4 5
do
  docker kill redis-node${i}
  docker rm redis-node${i}
done
