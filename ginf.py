import redis

from helpers import spatial_stats

class GinfGraph:
    
    buffer_length = 250
    prefix = "ginf"
    
    def __init__(self, n_decimals=3, pipeline=True):
        self.n_decimals = n_decimals
        self.pipeline = pipeline
        
        r = redis.Redis(host='localhost', port=6379, db=0)
        if pipeline:
            self.con = r.pipeline()
        else:
            self.con = r
    
    def _format_location(self, lat, lon):
        lat = round(float(lat), self.n_decimals)
        lon = round(float(lon), self.n_decimals)
        return '%f|%f' % (lat, lon)
    
    def add_post_location(self, source, lat, lon):
        location = self._format_location(lat, lon)
        self.con.hincrby('%s:post-locations:%d' % (self.prefix, source), location, 1)
         
    def add_mentions(self, source, target):
        if source != target:
            self.con.sadd('%s:did-mention:%d' % (self.prefix, source), target)
            self.con.sadd('%s:was-mentioned:%d' % (self.prefix, target), source)
    
    def add_dirty(self, user, mode):
        self.con.sadd('%s:dirty:%s' %(self.prefix, mode), user)
    
    def update(self, obj):
        if obj['has_geo']:
            self.add_post_location(obj['source'], obj['lat'], obj['lon'])
            self.add_dirty(obj['source'], 'actual')
            
        for target in obj['targets']:
            self.add_mentions(obj['source'], target)
            self.add_dirty(target, 'predicted')
        
        self.execute()
    
    def execute(self):
        if self.pipeline & (len(self.con) > self.buffer_length):
            self.con.execute()
            self.con.reset()


class GinfAPI:
    buffer_length = 250
    prefix = "ginf"
    
    def __init__(self):
        self.con = redis.Redis(host='localhost', port=6379, db=0)
    
    # Helpers
    def _deformat_location(self, k):
        return dict(zip(['lat', 'lon'], map(float, k.split('|'))))
    
    def deformat_locations(self, locs):
        return [(self._deformat_location(k), int(v)) for k,v in locs.iteritems()]
    
    # Working with post locations
    def get_post_locations(self, user):
        return self.con.hgetall('%s:post-locations:%d' % (self.prefix, user))
    
    def compute_user_loc(self, user):
        locs = self.get_post_locations(user)
        locs = self.deformat_locations(locs)
        if locs:
            locs = [loc for loc,n in locs for _ in range(n)] # Hack 
            return spatial_stats(locs)
    
    def predict_user_loc(self, neibs):
        if neibs:
            locs = map(get_user_loc, neibs)
            if locs:
                loc = spatial_stats(locs)
    
    # Working with predicted locations
    def get_neighbors(self, user):
        return self.con.sinter(
            '%s:did-mention:%d' % (self.prefix, user), 
            '%s:was-mentioned:%d' % (self.prefix, user)
        )
        
    def get_user_loc(self, user, always_predict=False):
        # Have location data for user
        if self.con.exists('%s:post-locations:%d' % (self.prefix, user)) and not always_predict:
            mode = 'actual'
            # Is dirty
            if self.con.sismember('%s:dirty:actual' % self.prefix, user):
                print 'computing | actual'
                loc = self.compute_user_loc(user)
            # Is not dirty
            else:
                print 'cached | actual'
                loc = self.con.hgetall('%s:user-locations:actual:%d' % (self.prefix, user))
        # Do not have location data
        else:
            mode = 'predicted'
            # Is dirty
            if self.con.sismember('%s:dirty:predicted' % self.prefix, user):
                print 'computing | prediction'
                neibs = self.get_neighbors(user)
                loc = self.predict_user_loc(neibs)
            # Is not dirty
            else:
                print 'cached | predicted'
                loc = self.con.hgetall('%s:user-locations:predicted:%d' % (self.prefix, user))
        
        if loc:
            self.con.hmset('%s:user-locations:%s:%d' % (self.prefix, mode, user), loc)
            self.con.srem('%s:dirty:%s' % (self.prefix, mode), user)
            return loc
