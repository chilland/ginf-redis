import sys
import ultrajson as json

from ginf import GinfGraph
from helpers import format_gnip

if __name__ == "__main__":
    graph_api = GinfGraph()
    for i,line in enumerate(sys.stdin):
        # Error handling for bad records in GNIP data
        if line.strip() == '':
            continue
        if json.loads(line).keys() == ['info']:
            continue
        
        try:
            obj = format_gnip(json.loads(line))
            graph_api.update(obj)
        except KeyboardInterrupt:
            raise
        except:
            print >> sys.stderr, 'error @ %s' % line
        
        if not i % 1000:
            print >> sys.stderr, '%d records completed' % i
    
    graph_api.execute(force=True)
