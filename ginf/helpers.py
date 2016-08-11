import re
import json
import numpy as np
from collections import OrderedDict
from datetime import datetime
from math import radians, degrees, cos, sin, asin, sqrt, atan2

def safeget(x, path, missingVal=''):
    ''' Safely get a nested property '''
    path = path.split('.')
    for p in path[:-1]:
        x = x.get(p, {})
    
    return x.get(path[-1], missingVal)


def round_(x, n=5):
    ''' Round w/ default place value '''
    return round(x, n)


def midpoint(p1, p2):
    ''' Midpoint of two points '''
    lat1, lon1 = map(radians, p1)
    lat2, lon2 = map(radians, p2)
    
    bx = cos(lat2) * cos(lon2 - lon1)
    by = cos(lat2) * sin(lon2 - lon1)
    
    lat3 = atan2(sin(lat1) + sin(lat2), \
           sqrt((cos(lat1) + bx) * (cos(lat1) \
           + bx) + by**2))
    lon3 = lon1 + atan2(by, cos(lat1) + bx)
    
    return map(degrees, [lat3, lon3])


def haversine(p1, p2):
    ''' Appox geographic distance between lat/lon '''
    lat1, lon1 = map(radians, p1)
    lat2, lon2 = map(radians, p2)
    
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a    = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c    = 2 * asin(sqrt(a)) 
    km   = 6371 * c
    return float(km)


def landspeed(p1, p2, time1, time2, eps = 60):
    return abs(3600 * haversine(p1, p2) / (time2 - time1 + eps))


def mad2confidence(mad):
    conf = 1. / (1 + np.log10(1 + mad))
    return round_(conf)


# def filter_landspeed(x, max_speed=1000):
#     ''' Filter users that move more than max_speek km per hour '''
#     posts = sorted(list(x[1]), key = lambda x: x['date'])
#     i = 1
#     while i < len(posts):
#         p1 = (posts[i-1]['lat'], posts[i-1]['lon'])
#         p2 = (posts[i]['lat'], posts[i]['lon'])
#         if landspeed(p1, p2, posts[i-1]['date'], posts[i]['date']) > max_speed:
#             return False
        
#         i += 1
    
#     return True


def _spatial_stats(X, f, eps=1e-3, max_iter=1000):
    '''
        Copied from SO
        ** Does not support weighted points ** 
    '''
    iter_ = 0
    y = np.mean(X, 0)
    while True:
        iter_ += 1
        
        D         = np.array(map(lambda x: f(x, y), X))[:,np.newaxis]
        nonzeros  = (D != 0)[:, 0]
        Dinv      = 1 / D[nonzeros]
        Dinvs     = np.sum(Dinv)
        W         = Dinv / Dinvs
        T         = np.sum(W * X[nonzeros], 0)
        num_zeros = len(X) - np.sum(nonzeros)
        
        if num_zeros == 0:
            y1 = T
        elif num_zeros == len(X):
            out = y
            break
        else:
            R    = (T - y) * Dinvs
            r    = np.linalg.norm(R)
            rinv = 0 if r == 0 else num_zeros/r
            y1   = max(0, 1-rinv)*T + min(1, rinv)*y
        
        if (np.linalg.norm(y - y1) < eps) or (iter_ > max_iter):
            out = y1
            break
                
        y = y1
    
    mad = np.median(D)
    return OrderedDict([
        ("mad"        , round_(mad)),
        ("confidence" , mad2confidence(mad)),
        ("lat"        , round_(out[0])),
        ("lon"        , round_(out[1])),
        ("n"          , len(X)),
        ("iter"       , iter_),
    ])


def get_center(box):
    # *** This is reversed compared to geopoint ***
    lat = sum([float(b[1]) for b in box]) / len(box)
    lon = sum([float(b[0]) for b in box]) / len(box)
    mad = haversine([lat, lon], box[0])
    return {
        "mad" : round_(mad),
        "lat" : round_(lat),
        "lon" : round_(lon),
    }


def spatial_stats(x):
    if len(x) == 1:
        x = list(x)
        mad = 0.0
        return OrderedDict([
            ("mad"        , mad),
            ("confidence" , mad2confidence(mad)),
            ("lat"        , round_(x[0]["lat"])),
            ("lon"        , round_(x[0]["lon"])),
            ("n"          , 1),
            ("iter"       , 0),
        ])
    elif len(x) == 2:
        mp = midpoint(*[[y['lat'], y['lon']] for y in x])
        mad = haversine(mp, [y['lat'], y['lon']])
        return OrderedDict([
            ("mad"        , round_(mad)),
            ("confidence" , mad2confidence(mad)),
            ("lat"        , round_(mp[0])),
            ("lon"        , round_(mp[1])),
            ("n"          , 2),
            ("iter"       , 0),
        ])
    else:
        geo = np.array([[y['lat'], y['lon']] for y in x])
        return _spatial_stats(geo, haversine)


def format_gnip(x):
    loc = safeget(x, 'geo.coordinates', None)
    if loc:
        loc = {'lat' : loc[0], 'lon' : loc[1], 'mad' : 0}
    else:
        loc = safeget(x, 'location.geo.coordinates', None)
        if loc:
            loc = get_center(loc[0])
    
    return {
        "source" : re.sub('id:twitter.com:', '', safeget(x, 'actor.id')),
        "date" : safeget(x, 'postedTime'),
        "lat" : float(loc['lat']) if loc else None,
        "lon" : float(loc['lon']) if loc else None,
        "targets" : [str(i['id']) for i in safeget(x, 'twitter_entities.user_mentions', [])],
        "has_geo" : loc != None
    }
