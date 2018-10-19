# RCF Data Service

Data service makes queries AWS Athena to get booking data and saves the result to s3 bucket.

## How to run locally

Make sure you ar in the ```/haystack-aa-random-cut-forest/data_service``` directory.

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

```docker build ./src -f docker/Dockerfile -t rcf-data-service```

### Run
Run using

```./build.sh -r```

or, if you want to use a docker command

```docker run -p 8080:8080  -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e AWS_SESSION_TOKEN    --rm rcf-data-service  serve```

## Test
To start training, use a curl command similar to this:
```
curl --data '{"s3":{"train_bucket": "aa-datasets","train_set_prefix":"rcf/training_data"},"database":{"name": "aa_datasets","table": "bookings_test","limit": 100},"tags":{"lob": "hotel","pos":"expedia.com"}}' -H "Content-Type: application/json" 127.0.0.1:8080/preprocess
```

