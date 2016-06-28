# --
# Development dataset 

DATA=data/part-00000

# Compute actual locations
redis-cli flushall
cat $DATA | parallel -u --pipe -N 100000 -P 10 "python run-graph.py"
cat $DATA | python run-predict.py > output/act

# Compute predicted locations
redis-cli flushall
cat $DATA | parallel -u --pipe -N 100000 -P 6 "python run-graph.py"
cat $DATA | python run-predict.py --always-predict > output/pred-n3-mad30-speedinf

python munge-results.py


# --
# On server

mkdir -p output

DATA=data/

# Compute actual locations
redis-cli flushall
cat data/run1-100.gz | gzip -cd | parallel -u --pipe -N 100000 -P 10 "python run-graph.py"
cat data/run1-100.gz | gzip -cd | python run-predict.py > output/act

# Compute predicted locations
redis-cli flushall
cat $DATA | parallel -u --pipe -N 100000 -P 6 "python run-graph.py"
cat $DATA | python run-predict.py --always-predict > output/pred-n3-mad30-speedinf

python munge-results.py