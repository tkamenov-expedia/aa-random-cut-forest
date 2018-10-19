""" RCF predictor - invokes RCF endpoint in Sagemaker to get the anomaly score. """

import boto3
import json
from .detector_repository import DetectorRepository

class Predictor:

    def __init__(self):
        self.runtime = boto3.client('runtime.sagemaker', 'us-west-2')
        self.repository = DetectorRepository()

    def detect(self, value, uuid):
        detector = self.repository.get(uuid)
        detector.new_metrics(value)
        print('Detecting anomaly for value {} and model {} (endpoint  {}).'.format(value, uuid, detector.get_metadata()['endpoint']))

        body = detector.get_shingle().to_csv()
        print('Sending to endpoint: {}'.format(body))
        response = self.runtime.invoke_endpoint(EndpointName=detector.get_metadata()['endpoint'],
                                           ContentType='text/csv',
                                           Body=body.encode('utf-8'))

        results = json.loads(response['Body'].read().decode())
        print("Anomaly score is " + str(results))
        return results

