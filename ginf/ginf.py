import sys
from redis import StrictRedis
from rediscluster import StrictRedisCluster

from helpers import spatial_stats

# --
# Helpers

def strdict2floatdict(x):
    return dict([(k, float(v)) for k,v in x.iteritems()])


def get_host_port(connect, default_port=80):
    hostport = connect.split(':')
    if len(hostport) == 2:
        port = int(hostport[1])
    else:
        port = default_port
    
    return hostport[0], port


def get_redis_connection(redis_service, default_port):
    nodes = redis_service.split(',')
    if len(nodes) == 1:
        r_host, r_port = get_host_port(redis_service, default_port=default_port)
        r = StrictRedis(r_host, r_port, db=0)
        print "Single-node Redis connection established."
    else:
        startup_nodes = []
        for node in nodes:
            r_host, r_port = node.split(':')
            startup_nodes.append({'host' : r_host, 'port' : r_port})
        
        r = StrictRedisCluster(startup_nodes=startup_nodes, decode_responses=True)
        print "Multi-node Redis connection established."
    
    return r

# --

class GinfGraph:
    
    buffer_length = 250
    prefix = "ginf"
    
    def __init__(self, redis_service, default_port=6379, n_decimals=3, pipeline=True):
        self.n_decimals = n_decimals
        self.pipeline = pipeline
        
        r = get_redis_connection(redis_service, default_port=default_port)
        self.con = r.pipeline() if pipeline else r
    
    def _format_location(self, lat, lon):
        lat = round(float(lat), self.n_decimals)
        lon = round(float(lon), self.n_decimals)
        return '%f|%f' % (lat, lon)
    
    def add_post_location(self, source, lat, lon):
        location = self._format_location(lat, lon)
        self.con.hincrby('%s:post-locations:%s' % (self.prefix, source), location, 1)
         
    def add_mentions(self, source, target):
        if source != target:
            self.con.sadd('%s:did-mention:%s' % (self.prefix, source), target)
            self.con.sadd('%s:was-mentioned:%s' % (self.prefix, target), source)
    
    def add_dirty(self, user, mode):
        self.con.sadd('%s:dirty:%s' %(self.prefix, mode), user)
    
    def update(self, obj):
        if obj['has_geo']:
            self.add_post_location(obj['source'], obj['lat'], obj['lon'])
            self.add_dirty(obj['source'], 'actual')
            
        for target in obj['targets']:
            if target != obj['source']:
                self.add_mentions(obj['source'], target)
                self.add_dirty(target, 'predicted')
            
        self.execute()
        return {
            "post-locations" : '%s:post-locations:%s' % (self.prefix, obj['source']),
            "did-mention" : '%s:did-mention:%s' % (self.prefix, obj['source']),
            "was-mentioned" : [
                '%s:was-mentioned:%s' % (self.prefix, t) for t in obj['targets'] if t != obj['source']
            ]
        }
    
    def execute(self, force=False):
        if force:
            self.con.execute()
            self.con.reset()            
        elif self.pipeline & (len(self.con) > self.buffer_length):
            self.con.execute()
            self.con.reset()


class GinfAPI:
    buffer_length = 250
    prefix = "ginf"
    
    def __init__(self, redis_service, default_port=6379):
        self.con = get_redis_connection(redis_service, default_port=default_port)
    
    # Helpers
    def _deformat_location(self, k):
        return dict(zip(['lat', 'lon'], map(float, k.split('|'))))
    
    def deformat_locations(self, locs):
        return [(self._deformat_location(k), int(v)) for k,v in locs.iteritems()]
    
    # Working with post locations
    def get_post_locations(self, user):
        return self.con.hgetall('%s:post-locations:%s' % (self.prefix, user))
    
    def compute_user_loc(self, user):
        locs = self.get_post_locations(user)
        locs = self.deformat_locations(locs)
        if locs:
            locs = [loc for loc,n in locs for _ in range(n)] # Hack -- spatial stats should accept weighted arguments
            return spatial_stats(locs)
    
    # Working with predicted locations
    def get_neighbors(self, user):
        return self.con.sinter(
            '%s:did-mention:%s' % (self.prefix, user), 
            '%s:was-mentioned:%s' % (self.prefix, user)
        )
    
    def filter_neib_locs(self, neib_locs, min_count=3, max_mad=30, max_speed=1000):
        tmp = []
        for neib_loc in filter(None, neib_locs):
            high_posts = neib_loc['n'] >= min_count # User has more than N posts (or N neighbors)
            low_mad = neib_loc['mad'] <= max_mad # MAD of neighbors is less than M
            # low_speed = neib_loc['max_speed'] < max_speed
            if high_posts and low_mad:
                tmp.append(neib_loc)
    
        return tmp
    
    def predict_user_loc(self, user):
        neibs = self.get_neighbors(user)
        if neibs:
            neib_locs = map(lambda n: self.get_user_loc(n, can_compute_pred=False)[0], neibs) # Could use pipeline
            neib_locs = self.filter_neib_locs(neib_locs)
            if neib_locs:
                return spatial_stats(neib_locs)
    
    def get_user_loc(self, user, can_compute_pred=True, always_predict=False, always_dirty=False):
        '''
            Given a user, return location
            
            If the user ever geotags tweets, return spatial median of geotags
            If not, return spatial median of neighbors' spatial medians
            
            Will return cached values when possible
        '''
        
        # Have location data for user
        if self.con.exists('%s:post-locations:%s' % (self.prefix, user)) and not always_predict:
            mode = 'actual'
            if self.con.sismember('%s:dirty:actual' % self.prefix, user) or always_dirty:
                loc = self.compute_user_loc(user)
            else:
                loc = self.con.hgetall('%s:user-locations:actual:%s' % (self.prefix, user))
        
        # Do not have location data
        else:
            mode = 'predicted'
            if can_compute_pred and self.con.sismember('%s:dirty:predicted' % self.prefix, user) or always_dirty:
                loc = self.predict_user_loc(user)
            else:
                loc = self.con.hgetall('%s:user-locations:predicted:%s' % (self.prefix, user))
            
        if loc:
            loc = strdict2floatdict(loc)
            self.con.hmset('%s:user-locations:%s:%s' % (self.prefix, mode, user), loc)
            self.con.srem('%s:dirty:%s' % (self.prefix, mode), user)
            
            # Error estimates are only for predictions
            if mode != 'predicted':
                loc['error_estimate_km'] = None
            
            return loc, mode
        else:
            return None, None

