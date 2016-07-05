import re
import sys
import argparse
import ultrajson as json

sys.path.append('../../ginf')
from ginf import GinfAPI
from helpers import safeget


def get_params():
    parser = argparse.ArgumentParser(description='predict location')
    parser.add_argument("--always-predict", action='store_true')
    parser.add_argument("--always-dirty", action='store_true')
    parser.add_argument("--redis-host", type=str, default='localhost')
    parser.add_argument("--redis-port", type=int, default=6379)
    parser.add_argument("--redis-db", type=int, default=0)
    return parser.parse_args()


if __name__ == "__main__":
    args = get_params()
    ginf_api = GinfAPI(args.redis_host, args.redis_port, args.redis_db)
    
    for i,line in enumerate(sys.stdin):
        try:
            source = re.sub('id:twitter.com:', '', safeget(json.loads(line), 'actor.id'))
            
            loc, mode = ginf_api.get_user_loc(source, always_predict=args.always_predict, always_dirty=args.always_dirty)
            
            if loc:
                loc.update({"source" : source, "mode" : mode})
                print json.dumps(loc)
        except:
            print >> sys.stderr, 'error: %s' % line
        
        if not i % 1000:
            print >> sys.stderr, '%d records complete' % i
