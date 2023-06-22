LOCAL_IMAGE_NAME:= mlopscamp_project

test:
	pytest tests/

setup:
	pipenv install --dev
	pre-commit install

infrastructure:
    terraform init
    terraform apply -auto-approve
    terraform output -json > output.json

quality_checks:
	isort .
	black .
	pylint --recursive=y .

build: quality_checks test
	docker compose build -t ${LOCAL_IMAGE_NAME} --no-cache .
	
up: build infrastructure
	docker compose up 

integration_test: build
	LOCAL_IMAGE_NAME=${LOCAL_IMAGE_NAME} bash tests/run.sh

publish: build integration_test
	LOCAL_IMAGE_NAME=${LOCAL_IMAGE_NAME} bash //run.sh

docker_push: up
	docker push <repository-uri>/<image-name>:<tag>
