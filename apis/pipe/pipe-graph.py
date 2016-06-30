import sys
import ultrajson as json

sys.path.append('../../ginf')
from ginf import GinfGraph
from helpers import format_gnip


def get_params():
    parser = argparse.ArgumentParser(description='store graph')
    parser.add_argument("--redis-host", type=str, default='localhost')
    parser.add_argument("--redis-port", type=int, default=6379)
    parser.add_argument("--redis-db", type=int, default=0)
    return parser.parse_args()


if __name__ == "__main__":
    args = get_params()
    graph_api = GinfGraph(args.redis_host, args.redis_post, args.redis_db)
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
