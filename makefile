# Load environment variables from .env file
include docker/.env
export

.PHONY: setup_s3 build push

LOCAL_IMAGE_NAME := mlopscamp_project
INTEGRATION_IMAGE_NAME := integration_test
IMAGE_TAG := mlops

# To run the whole pipeline and all call
all: infrastructure

# setups up the virtual environment
setup:
	pipenv install --dev
	pipenv run pre-commit install	

# Run unit tests on the repo from the tests subdirectory
test: 
	pytest tests/

# complete quality checks on the code 
quality_checks: tests
	isort .
	black .
	pylint --recursive=y .

# build our docker containers from the docker subdirectory
build: quality_checks
	cd docker && \
    docker compose build --no-cache

# for local deployment go to the docker subdirectory, build the containers and load them
local: 
	cd docker && docker compose build && docker compose up

# run integration tests after the build
integration_test: build
	LOCAL_IMAGE_NAME=${INTEGRATION_IMAGE_NAME} bash integrations/run.sh

# Push the docker compose containers to ECR on AWS
docker_push: build
	@aws ecr get-login-password --region $(AWS_REGION) | docker login --username AWS --password-stdin $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com

    # Push the Docker Compose images to ECR
	@docker-compose push

    # Tag and push the specified image to ECR
	@docker tag $(LOCAL_IMAGE_NAME):$(IMAGE_TAG) $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(REPOSITORY_NAME):$(IMAGE_TAG)
	@docker push $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(REPOSITORY_NAME):$(IMAGE_TAG)

# deploy the infastructure needed for the containers to run on AWS - ECS and S3 bucket
infrastructure: docker_push
	cd infastructure && \
		terraform init && \
		terraform apply -auto-approve

# Trigger training via the prefect server of the ML models
train: infastructure
	python orchestration/prefect_train.py

# make predictions from the trained models
predict: train
	python ./model/flask_app.py
