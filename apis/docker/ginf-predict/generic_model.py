import re
from ginf import GinfAPI
from ginf.helpers import safeget

class apiModel:
    model_name = "ginf-predict-01"
    
    def __init__(self, always_predict, always_dirty, **kwargs):
        self.ginf_api = GinfAPI(**kwargs)
        self.always_predict = always_predict
        self.always_dirty = always_dirty
    
    def predict_api(self, obj):
        source = re.sub('id:twitter.com:', '', safeget(obj, 'actor.id'))
        loc, mode = self.ginf_api.get_user_loc(source, always_predict=self.always_predict, always_dirty=self.always_dirty)
        
        if loc:
            del loc['iter']
        
        return {
            "model" : self.model_name,
            "value" : loc,
            "mode" : mode
        }
