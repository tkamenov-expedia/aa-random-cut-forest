# This is the file that implements a flask server to do inferences. It's the file that you will modify to
# implement the scoring for your own algorithm.

from __future__ import print_function

import json

import flask

from threading import Thread

from train_and_deploy.deploy_model import Deployer
from train_and_deploy.start_training_job import Trainer

prefix = '/opt/ml/'

# The flask app for serving predictions
app = flask.Flask(__name__)

trainer = Trainer()
deployer = Deployer()

@app.route('/ping', methods=['GET'])
def ping():
    """Determine if the container is working and healthy. In this sample container, we declare
    it healthy if we can load the model successfully."""
    print('Checking service health...')

    #TODO check if we can load data
    # health = load_data() is not None
    health = True

    status = 200 #if health else 404
    return flask.Response(response='["OK"]', status=status, mimetype='application/json')

@app.route('/train', methods=['POST'])
def train():
    # curl --data '{"model": {"name":"1234-5678-test", "bucket":"aa-models", "bucket_prefix":"rcf-detector/models"}, "train": {"train_manifest_uri" : "s3://aa-datasets/rcf/training_data/0914b255-39e5-40da-925b-131d28b0a928_manifest", "instance_type": "ml.c4.xlarge", "content_type": "application/x-recordio-protobuf","sagemaker_role": "arn:aws:iam::810409578363:role/service-role/AmazonSageMaker-ExecutionRole-20180406T120781", "containers":  { "us-west-2": "174872318107.dkr.ecr.us-west-2.amazonaws.com/randomcutforest:latest", "us-east-1": "382416733822.dkr.ecr.us-east-1.amazonaws.com/randomcutforest:latest", "us-east-2": "404615174143.dkr.ecr.us-east-2.amazonaws.com/randomcutforest:latest", "eu-west-1": "438346466558.dkr.ecr.eu-west-1.amazonaws.com/randomcutforest:latest", "ap-northeast-1": "351501993468.dkr.ecr.ap-northeast-1.amazonaws.com/randomcutforest:latest" }, "hyperparameters": { "feature_dim": "12", "number_of_samples_per_tree": "200", "number_of_trees": "50" } }, "deploy": { "execution_role": "arn:aws:iam::810409578363:role/service-role/AmazonSageMaker-ExecutionRole-20180406T120781", "instance_type": "ml.c4.xlarge", "production_variant_name": "test"}}' -H "Content-Type: application/json" 127.0.0.1:8080/train
    """ Start training job in AWS. """

    print('Training random cut forest model ...')

    query_parameters = {}

    if flask.request.content_type == 'application/json':
        # body = flask.request.get_json()
        body = flask.request.data.decode('utf-8')
        query_parameters = json.loads(body)
    else:
        return flask.Response(response='This preprocess only supports application/json as input data', status=415, mimetype='text/plain')

    thread = Thread(target = train_thread, args = (query_parameters, ))
    thread.start()

    return flask.Response(response='{"status":"TRAINING_STARTED"}', status=200, mimetype='text/csv')

def train_thread(training_parameters):

    job_name = trainer.train(training_parameters)
    # TODO wait for the job to be finished
    print ("Job name: " + job_name)

    deployer.deploy(job_name, training_parameters)