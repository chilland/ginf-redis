import sys
import argparse
import ultrajson as json

import ginf

def get_params():
    parser = argparse.ArgumentParser(description='store graph')
    parser.add_argument("--redis-service", type=str, default='localhost:6379')
    return parser.parse_args()


if __name__ == "__main__":
    args = get_params()
    graph_api = ginf.GinfGraph(args.redis_service)
    for i,line in enumerate(sys.stdin):
        
        # Error handling for bad records in GNIP data
        if line.strip() == '':
            continue
        if json.loads(line).keys() == ['info']:
            continue
        
        try:
            obj = ginf.io.gnip(json.loads(line))
            graph_api.update(obj)
        except KeyboardInterrupt:
            raise
        except:
            print >> sys.stderr, 'error @ %s' % line
        
        if not i % 1000:
            print >> sys.stderr, '%d records completed' % i
    
    graph_api.execute(force=True)
