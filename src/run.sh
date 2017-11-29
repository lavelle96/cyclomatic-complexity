#!/bin/bash
num_iters=$1

for i in $( seq 1 $num_iters ) 
do 
    ./run_n_clients.sh $i 
    wait
done

