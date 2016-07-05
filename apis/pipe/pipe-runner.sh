# --
# On server

mkdir -p output

PCOM="parallel -u --pipe -N 100000 -P 10"

# Compute actual locations
redis-cli flushall
time cat data/run1-100.gz | gzip -cd | parallel -u --pipe -N 100000 -P 10 "python pipe-graph.py"
time cat data/run1-100.gz | gzip -cd | python pipe-predict.py > output/act

# Compute predicted locations
redis-cli flushall
time cat data/run1-100.gz | gzip -cd | $PCOM "python pipe-graph.py"

# real    7m10.003s
# user    66m19.108s
# sys     2m53.220s

time cat data/run1-100.gz | gzip -cd | python pipe-predict.py --always-predict > output/pred

# Predictions in parallel
rm output/pred.par
time cat ../../data/run1-100.gz | gzip -cd | $PCOM "python run-graph.py"
time cat ../../data/run1-100.gz | gzip -cd | $PCOM "python run-predict.py --always-predict" >> output/pred.par
