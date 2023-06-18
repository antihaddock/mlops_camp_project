Working Repo for the DataTalksClub MLOps Zoomcamp project
Written by Ryan Gallagher


## How To Use This Repo ##

This repo is the final project for the DataTalksClub MLOps Zoomcamp.

## The dataset

The data set used for this project can be found on Kaggle here: https://www.kaggle.com/datasets/nehaprabhavalkar/av-healthcare-analytics-ii


The aim of the dataset is to predict hospital length of stay - which is represented by the ``stay`` column. For the purpose of this repo and the project this target coliumn has been converted into a binary outcome of less then 30 days and greater then 30 days.

The dataset contains a range of variables related to the demographics of the patient and their medical history. A full data dictionaru is available at `./data/train_data_dictionary.csv`. 

The data directory contains files used for the model process. `train_data.csv` is used to train the model and is also used for testing the data via a test/train split on this data. The `test_data.csv` is used as a validation dataset can be fed into the deployed model to confirm the model is running.


## Infastructure

# Cloud deployment
AWS used for deployment of this repo
- A S3 bucket is utilised for storing ML flow artifacts and metrics
- A Mlflow server is deployed via docker to AWS Elastic Beanstalk
- A flask app is also deployed via docker to AWS Elastic Beanstalk to serve the ML model

The flask app searches the Mlflow server to retrieve the model with the highest metric as part of it's workflow. 

# Infastructure creation
Terraform is used to create all infastructure for this project. Terraform code can be found in the `infastructure` directory. It is used to create the S3 bucket and elastic beanstalk instances to which the docker containers are deployed

A visual representation of the infastructure can be seen here !<img src="./MLOps Workflow.png" title="Repo Layout">
# Orchestration
Prefect is used as the orchestration platform for the repo and is programmed to run `./model/train.py` daily to ensure the most up to date model is available for deployment.


# Model deployment
 A docker-compose is available in the main directory of the repo which contains docker images for a Mlflow server and the custom flask app for serving the ML model. The flask app and Mlflow server are networked together. The flask app searches Mlflow for the most up to date model with each run.

# Model Monitoring