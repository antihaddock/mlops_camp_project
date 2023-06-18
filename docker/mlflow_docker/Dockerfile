FROM ghcr.io/mlflow/mlflow

RUN pip install boto3

ENV MLFLOW_S3_ENDPOINT_URL=https://s3.ap-southeast-2.amazonaws.com
ENV MLFLOW_S3_IGNORE_TLS=true
ENV MLFLOW_DEFAULT_ARTIFACT_ROOT=s3://mlopsbucketantihaddock/1

CMD mlflow server --default-artifact-root s3://mlopsbucketantihaddock/1 --host 0.0.0.0 --port 8000

EXPOSE 8000
