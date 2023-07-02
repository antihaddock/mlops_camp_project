# Load environment variables from .env file
include docker/.env
export

.PHONY: setup_s3 build push

LOCAL_IMAGE_NAME:= mlopscamp_project
INTEGRATION_IMAGE_NAME:= integration_test
IMAGE_TAG:= mlops

test:
	pytest tests/

setup:
	pipenv install --dev
	pre-commit install

infrastructure:
    cd infastructure 
	terraform init
	terraform apply -auto-approve -target=aws_s3_bucket.example

quality_checks:
	isort .
	black .
	pylint --recursive=y .

build: quality_checks test
	docker compose build -t ${LOCAL_IMAGE_NAME} --no-cache 
	
up: build infrastructure
	docker compose up 

integration_test: build
	LOCAL_IMAGE_NAME=${INTEGRATION_IMAGE_NAME} bash tests/run.sh

publish: build integration_test
	LOCAL_IMAGE_NAME=${LOCAL_IMAGE_NAME} bash //run.sh

docker_push: up
	@$(shell aws ecr get-login-password --region $(AWS_REGION) | docker login --username AWS --password-stdin $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com)
    docker-compose push
    docker tag $(LOCAL_IMAGE_NAME):$(IMAGE_TAG) $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(REPOSITORY_NAME):$(IMAGE_TAG)
    docker push $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(REPOSITORY_NAME):$(IMAGE_TAG)

deploy: docker_push
    cd infastructure
	terraform init
	terraform apply -auto-approve -target=aws_launch_configuration.ecs_launch_configuration -target=aws_autoscaling_group.ecs_autoscaling_group

