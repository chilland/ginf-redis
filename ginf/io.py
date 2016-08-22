import re
from .helpers import get_center

def safeget(x, path, missingVal=''):
    ''' Safely get a nested property '''
    path = path.split('.')
    for p in path[:-1]:
        x = x.get(p, {})

    return x.get(path[-1], missingVal)

def namespace_id(source, user):
    return '%s_%s' % (str(source), str(user))

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
    targets = x['targets'] if x.get('targets') else []
    return {
        'source' : namespace_id(x['source'], x['user']),
        'date' : x['date'],
        'lat' : x['lat'],
        'lon' : x['lon'],
        'targets' : map(lambda t: namespace_id(x['source'], t['id']), targets),
        'has_geo' : (x['lat'] != None) & (x['lon'] != None)
    }
