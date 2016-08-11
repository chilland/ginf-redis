from __future__ import division
import sys
import argparse
import logging
from flask import Flask, make_response, jsonify, request
from flask.ext.restful import Api, Resource, reqparse
from flask.ext.restful.representations.json import output_json
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from sklearn.externals import joblib
from generic_model import *

output_json.func_globals['settings'] = {
    'ensure_ascii' : False,
    'encoding' : 'utf8'
}

app = Flask(__name__)
api = Api(app)

logging.basicConfig(format='%(levelname)s %(asctime)s %(filename)s %(lineno)d: %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def parse_arguments():
    parser = argparse.ArgumentParser(description="ginf-predict")
    parser._optionals.title = "Options"
    parser.add_argument("-p", "--port", help="Specify port for API to listen on.",  type=str, required=False, default=5000)
    parser.add_argument("--redis-service", type=str, default="localhost:6379")
    parser.add_argument("--always-predict", action="store_true")
    parser.add_argument("--always-dirty", action="store_true")
    return parser.parse_args()


class ClassifierAPI(Resource):
    def __init__(self, **kwargs):
        super(ClassifierAPI, self).__init__()

    def post(self):
        json_data = request.get_json()
        try:
            res = model.predict_api(json_data)
            return make_response(jsonify(res), 200)
        except Exception as e:
            logger.info(e)
            return {}


class HealthCheck(Resource):
    def get(self):
        return make_response(jsonify({"status": "ok"}), 200)


@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)
    

if __name__ == '__main__':
    logger.info('Starting service.')
    start_args = parse_arguments()
    port = start_args.port
    
    logger.info('Loading model.')
    model = apiModel(**{
        'always_predict' : start_args.always_predict,
        'always_dirty' : start_args.always_dirty,
        'redis_service' : start_args.redis_service,
    })
    logger.info('Done loading model.')
    
    api.add_resource(ClassifierAPI, '/api/score')
    api.add_resource(HealthCheck, '/api/health')
    
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(port)
    IOLoop.instance().start()
