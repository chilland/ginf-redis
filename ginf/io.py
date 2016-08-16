import re
from .helpers import get_center

def safeget(x, path, missingVal=''):
    ''' Safely get a nested property '''
    path = path.split('.')
    for p in path[:-1]:
        x = x.get(p, {})
    
    return x.get(path[-1], missingVal)


def gnip(x):
    loc = safeget(x, 'geo.coordinates', None)
    if loc:
        loc = {'lat' : loc[0], 'lon' : loc[1], 'mad' : 0}
    else:
        loc = safeget(x, 'location.geo.coordinates', None)
        if loc:
            loc = get_center(loc[0])
    
    return {
        'source' : re.sub('id:twitter.com:', '', safeget(x, 'actor.id')),
        'date' : safeget(x, 'postedTime'),
        'lat' : float(loc['lat']) if loc else None,
        'lon' : float(loc['lon']) if loc else None,
        'targets' : [str(i['id']) for i in safeget(x, 'twitter_entities.user_mentions', [])],
        'has_geo' : loc != None
    }


def kafka(x):
    return {
        'source' : '%s_%s' % (str(x['source']), str(x['user'])),
        'date' : x['date'],
        'lat' : x['lat'],
        'lon' : x['lon'],
        'targets' : [
            '%s_%s' % (str(x['source']), str(target['id'])) for target in x['targets']
        ],
        'has_geo' : (x['lat'] != None) & (x['lon'] != None)
    }