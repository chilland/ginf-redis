#!/bin/bash

ENDPOINT=http://192.168.99.100:6000/api/score
# ENDPOINT=http://localhost:6000/api/score

cat test-data.json | curl -H "Content-Type: application/json" -XPOST -d @- $ENDPOINT
