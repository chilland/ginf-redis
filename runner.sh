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
PCOM="parallel -u --pipe -N 100000 -P 10"

# Compute actual locations
redis-cli flushall
time cat data/run1-100.gz | gzip -cd | parallel -u --pipe -N 100000 -P 10 "python run-graph.py"
time cat data/run1-100.gz | gzip -cd | python run-predict.py > output/act

# Compute predicted locations
redis-cli flushall

time cat data/run1-100.gz | gzip -cd | $PCOM "python run-graph.py"

# real    7m10.003s
# user    66m19.108s
# sys     2m53.220s

time cat data/run1-100.gz | gzip -cd | python run-predict.py --always-predict > output/pred

python munge-results.py