#!/usr/bin/env python
# coding=utf-8

import re
import sys
import json
config = json.load(open(sys.argv[1]))

from pyspark import SparkContext
sc = SparkContext(appName = '%s-tweet-locations' % config['username'])

sc.addPyFile('../helpers.py')
from helpers import safe_json_loads, safeget, get_center

# --
# Helpers

def extract(x):
    loc = safeget(x, 'geo.coordinates', None)
    if loc:
        loc = {'lat' : loc[0], 'lon' : loc[1], 'mad' : 0}
    else:
        loc = safeget(x, 'location.geo.coordinates', None)
        if loc:
            loc = get_center(loc[0])
    
    return (
        re.sub('id:twitter.com:', '', safeget(x, 'actor.id')),
        re.sub('tag:search.twitter.com,', '', safeget(x, 'id')),
        safeget(x, 'postedTime'),
        loc['lat'] if loc else None,
        loc['lon'] if loc else None,
        loc['mad'] if loc else None,
        [i['id'] for i in safeget(x, 'twitter_entities.user_mentions', [])]
    )

# --
# Run

sc.textFile('/qcr/gnip/run1-1000000.json.gz')\
    .filter(lambda x: x != '')\
    .map(safe_json_loads)\
    .filter(lambda x: x != None)\
    .map(extract)\
    .filter(lambda x: x[2] != '')\
    .sortBy(lambda x: x[2])\
    .map(json.dumps)\
    .saveAsTextFile(path='/user/bjohnson/qcr/ginf/redis/raw/1000000')


'''
sc.textFile(outpath).map(lambda x: x.split('\t')[0]).distinct().count()

gnip : 20,325,489
'''

