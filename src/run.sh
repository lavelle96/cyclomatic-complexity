#!/bin/bash
number_of_clients=2

python master.py &
for i in {0..$number_of_clients}
do 
    python worker.py &
done





