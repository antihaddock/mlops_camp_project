Working Repo for the DataTalksClub MLOps Zoomcamp project
Written by Ryan Gallagher


## How To Use This Repo ##

This repo is the final project for the DataTalksClub MLOps Zoomcamp.

## The dataset

The data set used for this project can be found on Kaggle here: https://www.kaggle.com/datasets/nehaprabhavalkar/av-healthcare-analytics-ii


The aim of the dataset is to predict hospital length of stay - which is represented by the ``stay`` column. For the purpose of this repo and the project this target coliumn has been converted into a binary outcome of less then 30 days and greater then 30 days. As such the purpose of this ML model is to predict if a patient admitted to hospital will be admitted for greater then 30 days or not.

The dataset contains a range of variables related to the demographics of the patient and their medical history. A full data dictionary is available at `./data/train_data_dictionary.csv`. 

The data directory contains files used for the model process. `train_data.csv` is used to train the model and is also used for testing the data via a test/train split on this data. The `test_data.csv` is used as a validation dataset can be fed into the deployed model to confirm the model is running.


# Cloud deployment
AWS used for deployment of this repo
- A S3 bucket is utilised for storing ML flow artifacts and metrics
- All elements of the repo are containerized in docker and can be deployed to AWS webservices
- All up there 6 containers to this repo within the `./docker/docker-compose.yml` to run this repo
- Provisioning to deployment on AWS is provided within the makefile in the main directory of the repo

THe flow of the repo and its containers will be summarized below

# Infastructure creation
Terraform is used to create all infastructure for this project. Terraform code can be found in the `infastructure` directory. It is used to create the S3 bucket and AWS ECS services to which the docker containers can deployed. `./infastructure/AWS_infastructure.tf` contains the IAC code for deployment of the infastructure for this repo and is created through the makefile `make infastructure` command.

A visual representation of the infastructure can be seen here: <img src="./MLOps Workflow.png" title="Repo Layout">

# Orchestration
Prefect is used as the orchestration platform for the repo and is programmed to run via `./orchestation/prefect_train.py` . A Prefect server is deployed in `./docker/docker-compose.yml` and configured to run within the code base of this repo. The prefect server is configured to utilised a Postgres database container for its backend storage.

In order for the model to be trained for the first time the docker containers must be running, then `prefect_train.py` can be called to train a variety of models on which the model deployment can run. the prefect server within the docker container must be running for this to work.


# Model deployment
 The main ML model is deployed via a flask app in a docker container. The docker-compose at `./docker/docker-compose.yml` lists the  `flaskapp` container which drives the ML model. This app communicates with a Mlflow container to search for and register the best model available in the mlflow server to make predictions on the data.

 The entire model can be tested by calling `./model/flask_app.py` which is configured to access the ML model, return predictions and log these predictions with Evidently and store in a postgres database (docker container). The flask app searches Mlflow for the most up to date model with each run. The docker compose needs to be running for `flask_app.py` to work. You must have called `./orchestation/prefect_train.py` at least once in order for the model to make predictions otherwise an error will be returned that no model exists.


# Model Monitoring
We utilise evidently for model monitoring. Code related to model monitoring can be found in `./monitoring` directory. `./model/predict.py` and `./model/config_db.py` contain the code base for evidently reports to be generated and logged on a ML model run. The evidently data is stored in the postgres database for access by a Grafana dashboard (which is also deployed as a docker container).

I have had a horrid time trying to get Evidently working on this dataset to no success(really weird data type errors that make no sense). As such all the code is configured to run reports, store reports and dashboard, but in order for the repo to run for anyone, it is commented out in `./model/predict.py`

# Reproducibility
To run and deploy this setup to AWS you need to follow the below steps:
1. In order to have this model deploy to AWS you MUST put a `.env `file into `./docker/` subdirectory. The repo expects this `.env` to be in the format of:
`aws_access_key_id=ID`
`aws_secret_access_key=KEY`
`region=REGION`
The below are only needed for deployment to AWS of the docker containers.
`ami-id=id`
`KEY_PAIR_NAME=name`
`vpc_id=vpc-id`
`subnet_id=subnet-id`
`bucket_name=bucketname`
`ami_id=ami_id`

This `.env` file is used to load these env variables into the docker-compose.yml and also Terraform code in `./infastructure`. from the root directory call `make all` which will deploy the model.

To run this locally:
You will still need have a `.env` with these variables
`aws_access_key_id=ID`
`aws_secret_access_key=KEY`
`region=REGION`

1. You can then call `make local_run` which will run the steps to deploy, train and make predictions locally. Be warned it will take around 30 minutes to train the `XGBoost` and `RandomForestClassifier` models. If you want to speed this up comment out these models in line 224 of `orchestration/prefect_train.py`
2. Alternatively you can interact directly with the docker-compose.yml at `./docker/docker-compose.yml` by calling docker compose build follow by `docker compose up`
This will deploy the containers locally from the command line
3. Utilise `./model/flask_app.py` to interact with the deployed containers and return predictions on the model.

When deployed locally you can access the servers at the following addresses. (If deployed to AWS you will need to locate the  URI's for your deployments)
- Prefect: 127.0.0.1:4200/
- Mlflow: 127.0.0.1:8000/
- Grafana: http://127.0.0.1:3000/login
- Postgres admin: http://0.0.0.0:5050

Versioning of the dependencies is available by the `requirements.txt` in the root directory and the `Pipfile` built of this also in the root of this repo.


# Best Practices
For this repo we have applied the following best practices:
1. Unit tests are stored in `./tests/` subdirectory
2. Integration tests are also stored at `./integration/` and callable via the makefile
3. Makefile for runing the model is located in the root directory
4. Code format checking utilising code linting
5. Code linting and formatting is done via the Makefile and pylint + black and isort
6. Git pre commit hooks used for this repo are found in `pre-commit-config.yml` in `./tests/` subdirectory