#!/bin/bash

DATA=data/part-00000

# Compute actual locations
redis-cli flushall
cat $DATA | parallel -u --pipe -N 100000 -P 6 "python run-graph.py"
cat $DATA | python run-predict.py > act

# Compute predicted locations
redis-cli flushall
cat $DATA | parallel -u --pipe -N 100000 -P 6 "python run-graph.py"
cat $DATA | python run-predict.py --always-predict > pred

python munge-results.py