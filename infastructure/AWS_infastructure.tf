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

output "database_endpoint" {
  value = aws_db_instance.example.endpoint
}

output "database_port" {
  value = aws_db_instance.example.port
}

output "database_name" {
  value = aws_db_instance.example.name
}

output "database_username" {
  value = aws_db_instance.example.username
}


# resource "aws_elastic_beanstalk_application" "example_app" {
#   name        = "predictionapp"  # Replace with your desired application name
#   description = "MLOPs project app"
# }

# resource "aws_elastic_beanstalk_environment" "example_env" {
#   name                = "example-env"  # Replace with your desired environment name
#   application         = aws_elastic_beanstalk_application.example_app.name
#   solution_stack_name = "64bit Amazon Linux 2 v3.4.5 running Docker"  # Change to Docker stack

#   setting {
#     namespace = "aws:autoscaling:launchconfiguration"
#     name      = "InstanceType"
#     value     = "t3.micro"  # Replace with your desired EC2 instance type
#   }

#   setting {
#     namespace = "aws:elasticbeanstalk:environment"
#     name      = "EnvironmentType"
#     value     = "SingleInstance"
#   }

#   setting {
#     namespace = "aws:elasticbeanstalk:environment"
#     name      = "ServiceRole"
#     value     = "aws-elasticbeanstalk-service-role"
#   }

#   setting {
#     namespace = "aws:elasticbeanstalk:application:environment"
#     name      = "AWS_CONTAINER_LOGGING_ENABLED"
#     value     = "false"  # Set to "true" if you want AWS to collect logs from the container
#   }

#   setting {
#     namespace = "aws:elasticbeanstalk:application:environment"
#     name      = "DOCKER_IMAGE"
#     value     = "<your_docker_image>"  # Replace with the URL of your Docker image
#   }
# }
