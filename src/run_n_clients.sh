#!/bin/bash
#First argument passed in is number of clients
number_of_clients=$1

python master.py &

for i in $( seq 2 $number_of_clients ); do python worker.py & done
python worker.py



