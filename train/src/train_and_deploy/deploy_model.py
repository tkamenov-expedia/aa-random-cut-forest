""" Deploy model to SageMaker """

import boto3
import os


class Deployer:

    def __init__(self):
        #self.REGION = boto3.session.Session().region_name
        self.REGION = 'us-west-2'
        self.sagemaker = boto3.client('sagemaker', self.REGION)

    def deploy(self, job_name, parameters):
        model_parameters = parameters['model']
        train_parameters = parameters['train']
        deploy_parameters = parameters['deploy']

        model_name = model_parameters['name']
        container = train_parameters['containers'][self.REGION]
        instance_type = train_parameters['instance_type']
        execution_role = train_parameters['sagemaker_role']
        production_variant_name = deploy_parameters['production_variant_name']

        # Create model in SageMaker
        model_data_url = os.path.join(
            's3://',
            model_parameters['bucket'],
            model_parameters['bucket_prefix'],
            job_name,
            'output',
            'model.tar.gz'
        )

        print('Creating model {} using container {} and model data url {}'.format(model_name, container, model_data_url))
        self.create_model(job_name, container, model_data_url, execution_role)

        # Create endpoint configuration
        print('Creating endpoint configuration "{}"'.format(job_name))
        self.create_endpoint_config(job_name, production_variant_name, instance_type)

        # Create or update endpoint to make predictions
        #endpoint = '{}-{}'.format('aa-rcf', job_name)
        if self.check_endpoint_exists(job_name):
            print('Updating existing endpoint {} ...'.format(job_name))
            self.update_endpoint(job_name, job_name)
        else:
            print('Creating a new endpoint {} ...'.format(job_name))
            self.create_endpoint(job_name, job_name)
            self.wait_until_create_endpoint_finished(job_name)

        print('Model {} deployed to Sagemaker endpoint {}.'.format(job_name, job_name))

    # Create SageMaker model
    def create_model(self, name, container, model_data_url, execution_role):
        try:
            self.sagemaker.create_model(
                ModelName=name,
                PrimaryContainer={
                    'Image': container,
                    'ModelDataUrl': model_data_url
                },
                ExecutionRoleArn=execution_role
            )
        except Exception as e:
            print(e)
            print('Error creating model with name {}. Check if model with that name exists already.'.format(name))
            raise(e)

    # Create SageMaker endpoint configuration.
    def create_endpoint_config(self, name, variant, instance_type):
        try:
            self.sagemaker.create_endpoint_config(
                EndpointConfigName=name,
                ProductionVariants=[
                    {
                        'VariantName': variant,
                        'ModelName': name,
                        'InitialInstanceCount': 1,
                        'InstanceType': instance_type
                    }
                ]
            )
        except Exception as e:
            print(e)
            print('Error creating endpoint configuration.')
            raise(e)

    # Check if SageMaker endpoint already exists for this model.
    def check_endpoint_exists(self, endpoint_name):
        try:
            self.sagemaker.describe_endpoint(
                EndpointName=endpoint_name
            )
            return True
        except Exception as e:
            return False

    # Create SageMaker endpoint with input endpoint configuration.
    def create_endpoint(self, endpoint_name, config_name):
        try:
            response = self.sagemaker.create_endpoint(
                EndpointName=endpoint_name,
                EndpointConfigName=config_name
            )
            print("Initiated creating endpoint {} with ARN {}".format(endpoint_name, response['EndpointArn']))

        except Exception as e:
            print(e)
            print('Error creating endpoint.')
            raise(e)

    # Update SageMaker endpoint to input endpoint configuration
    def update_endpoint(self, endpoint_name, config_name):
        try:
            self.sagemaker.update_endpoint(
                EndpointName=endpoint_name,
                EndpointConfigName=config_name
            )
        except Exception as e:
            print(e)
            print('Unable to update endpoint.')
            raise(e)

    # Wait until endpoint is created
    def wait_until_create_endpoint_finished(self, endpoint_name):
        endpoint_description = self.sagemaker.describe_endpoint(EndpointName=endpoint_name)
        status = endpoint_description['EndpointStatus']
        print('Creating endpoint {}, status: {}'.format(endpoint_name, status))

        try:
            self.sagemaker.get_waiter('endpoint_in_service').wait(EndpointName=endpoint_name)
        finally:
            resp = self.sagemaker.describe_endpoint(EndpointName=endpoint_name)
            status = resp['EndpointStatus']
            print("Arn: " + resp['EndpointArn'])
            print("Create endpoint ended with status: " + status)

            if status != 'InService':
                endpoint_description = self.sagemaker.describe_endpoint(EndpointName=endpoint_name)
                message = endpoint_description['FailureReason']
                print('Training failed with the following error: {}'.format(message))
                raise Exception('Endpoint {} creation failed: {}'.format(endpoint_description, message))