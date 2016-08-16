import ginf

class apiModel:
    model_name = "ginf-graph-01"
    
    def __init__(self, **kwargs):
        self.graph_api = ginf.GinfGraph(**kwargs)
    
    def predict_api(self, obj):
        obj = ginf.io.kafka(obj)
        return self.graph_api.update(obj)