for i in 0 1 2 3 4 5
do
  docker restart redis-node${i}
done
