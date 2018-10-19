import datetime
import boto3
import json
import os
import pandas
import numpy

from dateutil.tz import tzutc
from sagemaker.amazon.common import numpy_to_record_serializer

s3 = boto3.client('s3', 'us-west-2')
ssm = boto3.client('ssm', 'us-west-2')

class Transformer:

    def __init__(self):
        self.input_file_type = 'csv'
        self.output_file_type = 'pbr'
        self.shingle_size = 12

    #####################################################################################
    #  Main transformer methods
    #####################################################################################

    # Read .csv file from s3 bucket, shingle, convert to protobuf .pbr format and save back to s3
    def transform_from_file(self, params):
        train_bucket = params['train_bucket']
        train_set_prefix = params['train_set_prefix']

        latest_training_file = self.find_latest_training_file(train_bucket, train_set_prefix, self.input_file_type)
        print("Latest training file is " + latest_training_file)

        input_data = None
        if latest_training_file:
            input_data = self.read_training_data(train_bucket, latest_training_file)

        self.transform_raw_data(params, input_data)

    # Use input data in form of an in-memory matrix, shingle, convert to protobuf .pbr format and save back to s3
    def transform_raw_data(self, params, input_data):
        print('Preparing data for training.')

        train_bucket = params['train_bucket']
        train_set_prefix = params['train_set_prefix']
        model_id = params['model_id']

        train_set_file_name = '{}.{}'.format(model_id, self.output_file_type)

        if input_data is None:
            print('No new data uploaded.')
            print('Skipping until next scheduled data preprocessing run.')
            result = {
                'no_new_data': True
            }
        else:
            print('Converting input data from .csv file to protobuf...')
            self.transform_and_upload_training_data(input_data, self.shingle_size, train_bucket, train_set_prefix, train_set_file_name)
            print('Data transformed and uploaded')

            print('Creating manifest file...')
            train_manifest_key = os.path.join(train_set_prefix, model_id + '_manifest')
            self.create_and_save_manifest(train_bucket, train_set_prefix, train_set_file_name, train_manifest_key)
            print('Manifest file created and uploaded to s3 as {}'.format(train_manifest_key))

            # Return result
            time = datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S-%f")
            train_manifest_uri = os.path.join('s3://', train_bucket, train_manifest_key)

            result = {
                'time': time,
                'train_set_bucket': train_bucket,
                'train_set_prefix': train_set_prefix,
                'train_manifest_uri': train_manifest_uri,
                'endpoint': model_id,
                'no_new_data': False
            }

        print('Data ready for training. The result is:\n {}'.format(result))
        return result

    #####################################################################################
    ### Manifest related methods - manifest is used later by Sagemaker for training
    #####################################################################################

    def make_manifest(self, keys, train_set_path):
        payload = list()
        prefix = {'prefix': train_set_path}
        payload.append(prefix)
        for key in keys:
            payload.append(key)

        return json.dumps(payload).encode()

    def put_manifest(self, body, train_bucket, train_manifest_key):
        try:
            s3.put_object(
                Body=body,
                Bucket=train_bucket,
                ContentType='text/plain',
                Key=train_manifest_key
            )
        except Exception as e:
            print(e)
            print('Unable to put manifest to s3.')
            raise(e)

    # Create and save manifest
    def create_and_save_manifest(self, bucket, prefix, file_name, manifest_key):
        print('Uploading manifest to S3...')

        train_set_path = os.path.join('s3://', bucket, prefix, '')
        body = self.make_manifest([file_name], train_set_path)
        self.put_manifest(body, bucket, manifest_key)

    #####################################################################################
    #  Methods related to S3, shingling and converting data to protobuf format
    #####################################################################################

    # Find the training file which is uploaded latest (by it's upload date)
    def find_latest_training_file(self, bucket, folder, type):
        print('Finding latest training file...')

        last_training_file = None
        last_training_date = datetime.datetime(2000, 1, 1, 0, 0, tzinfo=tzutc())
        files = s3.list_objects(Bucket = bucket, Prefix = folder)

        for file in files['Contents']:
            file_timedate = file['LastModified']
            if file['Key'].endswith(type) and last_training_date < file_timedate:
                last_training_file = file['Key']
                last_training_date = file_timedate

        return last_training_file

    # Load training data from .csv file
    def read_training_data(self, bucket, file):

        print('Loading data from s3...')
        data_location = 's3://{}/{}'.format(bucket, file)
        input_data = pandas.read_csv(data_location)

        return input_data

    # Shingle input data
    def shingle(self, data, shingle_size):
        print('Shingling input data...')

        num_data = len(data)
        shingled_data = numpy.zeros((num_data - shingle_size, shingle_size))

        for n in range(shingle_size, num_data - 1):
            shingled_data[n - shingle_size] = data[(n-shingle_size) : n]

        return shingled_data

    # Convert numpy array to Protobuf RecordIO format and save to s3
    def convert_to_protobuf_and_upload(self, ndarray, bucket, prefix, filename):
        print('Converting numpy array to Protobuf RecordIO format and saving it to s3...')

        # Convert...
        serializer = numpy_to_record_serializer()
        buffer = serializer(ndarray)

        # ... and save
        s3_object = os.path.join(prefix, filename)
        try:
            boto3.Session().resource('s3').Bucket(bucket).Object(s3_object).upload_fileobj(buffer)
            s3_path = 's3://{}/{}'.format(bucket, s3_object)
            return s3_path
        except Exception as e:
            print(e)
            print('Unable to upload data in protobuf format to s3.')
            raise(e)

    # Shingle training data, convert to protobuf format and upload to s3
    def transform_and_upload_training_data(self, input_data, shingle_size, bucket, prefix, training_file_name):
        input_data_shingled = self.shingle(input_data.values[:,1], shingle_size)
        s3_train_data_shingled = self.convert_to_protobuf_and_upload(
            input_data_shingled,
            bucket,
            prefix,
            training_file_name)

        print('Uploaded data to {}'.format(s3_train_data_shingled))




