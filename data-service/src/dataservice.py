# This is the file that implements a flask server to do inferences. It's the file that you will modify to
# implement the scoring for your own algorithm.

from __future__ import print_function

import os
import pandas
import json
import io

import flask

from threading import Thread
from time import sleep

from data_service.transformer import Transformer
from data_service.fetcher import Fetcher

prefix = '/opt/ml/'

# The flask app for serving predictions
app = flask.Flask(__name__)

@app.route('/ping', methods=['GET'])
def ping():
    """Determine if the container is working and healthy. In this sample container, we declare
    it healthy if we can load the model successfully."""
    print('Checking service health...')

    #TODO check if we can reach s3
    # health = s3() is not None
    health = True

    status = 200 if health else 404
    return flask.Response(response='\n["OK"]', status=status, mimetype='application/json')

@app.route('/preprocess', methods=['POST'])
def preprocess():
    # curl --data '{"s3":{"train_bucket": "aa-datasets","train_set_prefix":"rcf/training_data"},"database":{"name": "aa_datasets","table": "bookings_test","limit": 105120},"tags":{"lob": "hotel","pos":"expedia.com"},"model":{"id": "here-goes-model-id"}}' -H "Content-Type: application/json" 127.0.0.1:8080/preprocess 
    # curl --data '{"s3":{"train_bucket": "aa-datasets","train_set_prefix":"rcf/training_data"},"database":{"name": "aa_datasets","table": "bookings_test","limit": 105120},"tags":{"lob": "hotel","pos":"expedia.com"}}' -H "Content-Type: application/json" 127.0.0.1:8080/preprocess
    """ Start data preprocessing. Spawn a thread and let it do it as it may take a while """

    data = None

    print('Fetching data for training from Athena...')

    query_parameters = {}

    # Convert from CSV to pandas
    if flask.request.content_type == 'application/json':
        # body = flask.request.get_json()
        body = flask.request.data.decode('utf-8')
        query_parameters = json.loads(body)
    else:
        return flask.Response(response='This preprocess only supports application/json as input data', status=415, mimetype='text/plain')

    thread = Thread(target = fetcher_thread, args = (query_parameters, ))
    thread.start()

    return flask.Response(response='{"status":"PREPARE_TRAINING_DATA_STARTED"}', status=200, mimetype='text/csv')

def fetcher_thread(query_parameters):

    fetcher = Fetcher()
    query_id, input_data = fetcher.query_and_fetch(query_parameters)

    transformer = Transformer()
    result = transformer.transform_raw_data(
        {
            'train_bucket': query_parameters['s3']['train_bucket'],
            'train_set_prefix': query_parameters['s3']['train_set_prefix'],
            'model_id' : query_id
        },
        pandas.DataFrame(input_data)
    )
