#!/bin/bash

ENDPOINT=http://localhost:6000/api/score

cat test-data.json | curl -H "Content-Type: application/json" -XPOST -d @- $ENDPOINT
