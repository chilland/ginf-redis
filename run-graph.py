import sys
import ultrajson as json

from ginf import GinfGraph
from helpers import format_gnip

if __name__ == "__main__":
    graph_api = GinfGraph()
    for i,line in enumerate(sys.stdin):
        for obj in format_gnip(line):
            print obj
            # graph_api.update(obj)
        
        # if not i % 1000:
            # print >> sys.stderr, '%d records completed' % i
    
    # graph_api.execute(force=True)