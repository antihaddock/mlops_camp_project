# Load environment variables from .env file
include docker/.env
export

.PHONY: setup_s3 build push

LOCAL_IMAGE_NAME := mlopscamp_project
INTEGRATION_IMAGE_NAME := integration_test
IMAGE_TAG := mlops

all: infrastructure

setup:
	pipenv install --dev
	pipenv run pre-commit install	

test: 
	pytest tests/

quality_checks: tests
	isort .
	black .
	pylint --recursive=y .

build: quality_checkes
	cd docker && \
    docker compose build --no-cache

up: 
	cd docker && docker compose up

integration_test: build
	LOCAL_IMAGE_NAME=${INTEGRATION_IMAGE_NAME} bash integrations/run.sh

docker_push: build
	@aws ecr get-login-password --region $(AWS_REGION) | docker login --username AWS --password-stdin $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com

    # Push the Docker Compose images to ECR
	@docker-compose push

    # Tag and push the specified image to ECR
	@docker tag $(LOCAL_IMAGE_NAME):$(IMAGE_TAG) $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(REPOSITORY_NAME):$(IMAGE_TAG)
	@docker push $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(REPOSITORY_NAME):$(IMAGE_TAG)

deploy: docker_push
	cd infastructure && \
		terraform init && \
		terraform apply -auto-approve -target=aws_launch_configuration.ecs_launch_configuration -target=aws_autoscaling_group.ecs_autoscaling_group

infrastructure: deploy
	cd infastructure && \
		terraform init && \
		terraform apply -auto-approve

train: deploy
	python orchestration/prefect_train.py
	
predict: train
	python ./model/flask_app.py



