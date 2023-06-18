# provider "aws" {
#   region = "ap-southeast-2"  # Replace with your desired AWS region
# }

# resource "aws_s3_bucket" "mlopsbucket" {
#   bucket = "mlopsbucketantihaddock"  # Replace with your desired bucket name
# }

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
