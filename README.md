Working Repo for the DataTalksClub MLOps Zoomcamp project
Written by Ryan Gallagher


## How To Use This Repo ##

This repo is the final project for the DataTalksClub MLOps Zoomcamp.

## The dataset

The data set used for this project can be found on Kaggle here: https://www.kaggle.com/datasets/nehaprabhavalkar/av-healthcare-analytics-ii


The aim of the dataset is to predict hospital length of stay - which is represented by the ``stay`` column. For the purpose of this repo and the project this target coliumn has been converted into a binary outcome of less then 30 days and greater then 30 days.

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
Terraform is used to create all infastructure for this project. Terraform code can be found in the `infastructure` directory. It is used to create the S3 bucket and AWS instances to which the docker containers can deployed. `./infastructure/AWS_infastructure.tf` contains the IAC code for deployment of the infastructure for this repo.

A visual representation of the infastructure can be seen here: <img src="./MLOps Workflow.png" title="Repo Layout">

# Orchestration
Prefect is used as the orchestration platform for the repo and is programmed to run `./orchestation/prefect_train.py` . A Prefect server is deployed in `./docker/docker-compose.yml` and configured to run within the code base of this repo. The prefect server is configured to utilised a Postgres database container for its backend storage.


# Model deployment
 The main ML model is deployed via a flask app in a docker container. The docker-compose at `./docker/docker-compose.yml` lists the  `flaskapp` container which drives the ML model. This app communicates with a Mlflow container to search for and register the best model available in the mlflow to make predictions on the data.

 The entire model can be tested by calling `./model/flask_app.py` which is configured to access the ML model, return predictions and log these predictions with Evidently and store in a postgres database (docker container). The flask app searches Mlflow for the most up to date model with each run.


# Model Monitoring
We utilise evidently for model monitoring. Code related to model monitoring can be found in `./monitoring` directory. `./model/predict.py` and `./model/config_db.py` contain the code base for evidently reports to be generated and logged on a ML model run. The evidently data is stored in the postgres database for access by a Grafana dashboard (which is also deployed as a docker container).

I have had a horrid time trying to get Evidently working on this dataset to no success(really weird data type errors that make no sense). As such all the code is configured to run reports, store reports and dashboard, but in order for the repo to run for anyone, it is commented out in `./model/predict.py`

# Reproducibility
In order to run this repo you have the follow these steps:
1. In order to have this model deploy to AWS you MUST put a `.env `file into `./docker/` subdirectory. The repo expects this `.env` to be in the format of:
`aws_access_key_id=ID`
`aws_secret_access_key=KEY`
`region=REGION`
This `.env` file is used to load these env variables into the docker-compose.yml and also Terraform code.

Once you have done this to run the repo you can either:
1. Utilise the make file to complete all the steps to run the repo
2. interact directly with the docker-compose.yml at `./docker/docker-compose.yml` by calling docker compose build follow by `docker compose up`
This will deploy the containers locally
3. Utilise `./model/flask_app.py` to interact with the deployed containers and return predictions on the model.

When deployed locally you can access the servers at the following addresses. (If deployed to AWS you will need to locate the  URI's for your deployments)
- Prefect:
- Mlflow:
- Grafana: 
- Postgres admin :

Versioning of the dependencies is available by the `requirements.txt` in the root directory and the `Pipfile` built of this also in the root of this repo.


# Best Practices
For this repo we have applied the following best practices:
1. Unit tests are stored in `./tests/` subdirectory
2. Integration tests are also stored at `./tests/` and callable via the makefile
3. Makefile for runing the model is located in the root directory
4. Code format checking utilising code linting
5. Code linting and formatting is done via the Makefile and pylint + black and isort


