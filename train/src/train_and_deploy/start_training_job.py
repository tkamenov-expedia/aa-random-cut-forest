import boto3
import os
import datetime


class Trainer:

    def __init__(self):
        #self.REGION = boto3.session.Session().region_name
        self.REGION = 'us-west-2'
        self.sagemaker = boto3.client('sagemaker', 'us-west-2')

    def train(self, parameters):
        time = time = datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S-%f")
        model_name = parameters['model']['name']
        job_name = '{}-{}-{}'.format('aa-rcf', model_name, time)
        print('Starting training job {} ...'.format(job_name))

        self.start_training_job(job_name, parameters)
        self.wait_until_training_completed(job_name)

        return job_name

    def start_training_job(self, job_name, parameters):
        train_parameters = parameters['train']
        model_parameters = parameters['model']

        # initiate create_training_job
        try:
            self.sagemaker.create_training_job(
                TrainingJobName=job_name,
                HyperParameters={
                    'feature_dim': train_parameters['hyperparameters']['feature_dim'],
                    'num_samples_per_tree': train_parameters['hyperparameters']['number_of_samples_per_tree'],
                    'num_trees': train_parameters['hyperparameters']['number_of_trees']
                },
                AlgorithmSpecification={
                    'TrainingImage': train_parameters['containers'][self.REGION],
                    'TrainingInputMode': 'File'
                },
                RoleArn=train_parameters['sagemaker_role'],
                InputDataConfig=[
                    {
                        'ChannelName': 'train',
                        'DataSource': {
                            'S3DataSource': {
                                'S3DataType': 'ManifestFile',
                                'S3Uri': train_parameters['train_manifest_uri']
                            }
                        },
                        'ContentType': train_parameters['content_type'],
                        'CompressionType': 'None'
                    }
                ],
                OutputDataConfig={
                    'S3OutputPath': os.path.join('s3://', model_parameters['bucket'], model_parameters['bucket_prefix'])
                },
                ResourceConfig={
                    'InstanceType': train_parameters['instance_type'],
                    'InstanceCount': 1,
                    'VolumeSizeInGB': 50
                },
                StoppingCondition={
                    'MaxRuntimeInSeconds': 86400
                }
            )
        except Exception as e:
            print(e)
            print('Unable to create training job.')
            raise e

    def wait_until_training_completed(self, job_name):
        status = self.sagemaker.describe_training_job(TrainingJobName=job_name)['TrainingJobStatus']
        print('Training job {} status: {}'.format(job_name, status))

        # wait for create_training_job to finish
        try:
            self.sagemaker.get_waiter('training_job_completed_or_stopped').wait(TrainingJobName=job_name)
        finally:
            status = self.sagemaker.describe_training_job(TrainingJobName=job_name)['TrainingJobStatus']
            print("Training job ended with status: " + status)
            if status == 'Failed':
                message = self.sagemaker.describe_training_job(TrainingJobName=job_name)['FailureReason']
                print('Training failed with the following error: {}'.format(message))
                raise Exception('Training job {} failed'.format(message))






