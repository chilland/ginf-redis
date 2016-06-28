import sys
import ultrajson as json

from ginf import GinfGraph

def load_obj(obj):
    '''
        Wrapper for reading data
    '''
    source, _1, date, lat, lon, _2, targets = json.loads(obj)#[1]
    try:
        return {
            "source"  : int(source),
            "date"    : date,
            "lat"     : float(lat) if lat != None else None,
            "lon"     : float(lon) if lon != None else None,
            "targets" : map(int, targets),
            "has_geo" : lat != None
        }
    except:
        print 'error @ %s' % obj

if __name__ == "__main__":
    graph_api = GinfGraph()
    for i,obj in enumerate(sys.stdin):
        graph_api.update(load_obj(obj))
        
        if not i % 1000:
            print >> sys.stderr, '%d records completed' % i
    
    graph_api.execute(force=True)