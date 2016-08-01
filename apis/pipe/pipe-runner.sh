# --
# On server

mkdir -p output

PCOM="parallel -u --pipe -N 100000 -P 10"

# Compute actual locations
redis-cli flushall
time cat data/run1-100.gz | gzip -cd | $PCOM "python pipe-graph.py"
time cat data/run1-100.gz | gzip -cd | python pipe-predict.py > output/act

# Compute predicted locations
redis-cli flushall
time cat data/run1-100.gz | gzip -cd | $PCOM "python pipe-graph.py"
time cat data/run1-100.gz | gzip -cd | python pipe-predict.py --always-predict > output/pred