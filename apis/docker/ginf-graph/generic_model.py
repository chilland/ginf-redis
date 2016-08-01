from ginf import GinfGraph
from ginf.helpers import format_gnip

class apiModel:
    model_name = "ginf-graph-01"
    
    def __init__(self, **kwargs):
        self.graph_api = GinfGraph(**kwargs)
    
    def predict_api(self, obj):
        obj = format_gnip(obj)
        return self.graph_api.update(obj)