import re
import sys
import argparse
import ultrajson as json

from ginf import GinfAPI
from helpers import safeget

def get_params():
    parser = argparse.ArgumentParser(description='ingest_otc_halts')
    parser.add_argument("--always-predict", action='store_true')
    parser.add_argument("--always-dirty", action='store_true')
    return parser.parse_args()

if __name__ == "__main__":
    args = get_params()
    ginf_api = GinfAPI()
    
    for i,line in enumerate(sys.stdin):
        try:
            obj = json.loads(line)
            source = re.sub('id:twitter.com:', '', safeget(obj, 'actor.id'))
            
            loc, mode = ginf_api.get_user_loc(source, always_predict=args.always_predict, always_dirty=args.always_dirty)
            
            if loc:
                loc.update({"source" : source, "mode" : mode})
                print json.dumps(loc)
        except:
            print >> sys.stderr, 'error: %s' % line
        
        if not i % 1000:
            print >> sys.stderr, '%d records complete' % i
