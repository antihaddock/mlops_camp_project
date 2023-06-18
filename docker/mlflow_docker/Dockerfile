FROM ghcr.io/mlflow/mlflow

RUN pip install boto3

CMD mlflow server --default-artifact-root s3://mlopsbucketantihaddock/1 --host 0.0.0.0 --port 8000

EXPOSE 8000
