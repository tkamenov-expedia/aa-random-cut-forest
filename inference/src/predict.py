# This is the file that implements a flask server to do inferences. It's the file that you will modify to
# implement the scoring for your own algorithm.

from __future__ import print_function

import json

import flask

from detect.predictor import Predictor


prefix = '/opt/ml/'

# The flask app for serving predictions
app = flask.Flask(__name__)

predictor = Predictor()

@app.route('/ping', methods=['GET'])
def ping():
    """Determine if the container is working and healthy. In this sample container, we declare
    it healthy if we can load the model successfully."""
    print('Checking service health...')

    #TODO check if we can load model
    # health = load_model() is not None
    health = True

    status = 200 #if health else 404
    return flask.Response(response='["OK"]', status=status, mimetype='application/json')

@app.route('/detect', methods=['POST'])
def detect():
    # curl --data '{"uuid": "1234", "value": 100}' -H "Content-Type: application/json" 127.0.0.1:8080/detect

    query_parameters = {}

    if flask.request.content_type == 'application/json':
        # body = flask.request.get_json()
        body = flask.request.data.decode('utf-8')
        query_parameters = json.loads(body)
    else:
        return flask.Response(response='This preprocess only supports application/json as input data', status=415, mimetype='text/plain')

    result = predictor.detect(query_parameters['value'], query_parameters['uuid'])

    return flask.Response(response='{}'.format(result), status=200, mimetype='text/csv')
