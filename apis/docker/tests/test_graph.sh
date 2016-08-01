#!/bin/bash

ENDPOINT=http://localhost:5000/api/score

control_c() {
   exit
}

post () {
    cat test-data.json | curl -H "Content-Type: application/json" -XPOST -d @- $ENDPOINT
}

for i in $(seq 200); do
    trap control_c SIGINT;
    post > /dev/null;
done
post