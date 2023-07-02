terraform {
  required_providers {
    dotenv = {
      source  = "codemountain/dotenv"
      version = "1.1.0"
    }
    aws = {
      source  = "hashicorp/aws"
      version = "3.63.0"
    }
  }
}

provider "dotenv" {
  path = "../docker/.env"
}

data "dotenv" "env" {}

provider "aws" {
  access_key       = data.dotenv.env.variables.AWS_ACCESS_KEY_ID
  secret_access_key = data.dotenv.env.variables.AWS_SECRET_ACCESS_KEY
  region           = data.dotenv.env.variables.AWS_REGION
}

resource "aws_db_instance" "example" {
  allocated_storage = 10
  engine            = "postgres"
  engine_version    = "13.4"
  instance_class    = "db.t3.micro"
  name              = "mydatabase"
  username          = "myuser"
  password          = "mypassword"
}

resource "aws_s3_bucket" "mlopsbucket" {
  bucket = "mlopsbucketantihaddock"  
}
