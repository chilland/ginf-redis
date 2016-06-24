#!/bin/bash

cat data/2014-12-21.json | head -n 100000 | parallel --pipe -N 10000 -P 8 "python runner.py"