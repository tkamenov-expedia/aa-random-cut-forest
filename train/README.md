# RCF Trainer

## How to run locally

Make sure you ar in the ```/haystack-aa-random-cut-forest/train``` directory.

### Prerequisites
Get your keys from AWS. You could use

```aws_key_gen login```

Locate your ```.aws``` directory and get your credentials from ```credentials``` file.

Now set the environment variables
```
export AWS_ACCESS_KEY_ID=ASIA111111111111111
export AWS_SECRET_ACCESS_KEY=A222222222222222222222222222222222222222
export AWS_SESSION_TOKEN=ABCD/2834987439872349
```

### Build
Build first using

```./build.sh -b```

or, if you want to use a docker command

```docker build ./src -f docker/Dockerfile -t rcf-train```

### Run
Run using

```./build.sh -r```

or, if you want to use a docker command

```docker run -p 8080:8080  -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e AWS_SESSION_TOKEN    --rm rcf-train  serve```

## Test
To start training, use a curl command similar to this:
```
curl --data '{"model": {"name":"rcf-bookings", "bucket":"aa-models", "bucket_prefix":"rcf/models"}, "train": {"train_manifest_uri" : "s3://aa-datasets/rcf/training_data/manifest", "instance_type": "ml.c4.xlarge", "content_type": "application/x-recordio-protobuf","sagemaker_role": "arn:aws:iam::810409578363:role/service-role/AmazonSageMaker-ExecutionRole-20180406T120781", "containers":  { "us-west-2": "174872318107.dkr.ecr.us-west-2.amazonaws.com/randomcutforest:latest", "us-east-1": "382416733822.dkr.ecr.us-east-1.amazonaws.com/randomcutforest:latest", "us-east-2": "404615174143.dkr.ecr.us-east-2.amazonaws.com/randomcutforest:latest", "eu-west-1": "438346466558.dkr.ecr.eu-west-1.amazonaws.com/randomcutforest:latest", "ap-northeast-1": "351501993468.dkr.ecr.ap-northeast-1.amazonaws.com/randomcutforest:latest" }, "hyperparameters": { "feature_dim": "12", "number_of_samples_per_tree": "200", "number_of_trees": "50" } }, "deploy": { "execution_role": "arn:aws:iam::810409578363:role/service-role/AmazonSageMaker-ExecutionRole-20180406T120781", "instance_type": "ml.c4.xlarge", "production_variant_name": "test"}}
' -H "Content-Type: application/json" 127.0.0.1:8080/train
```

