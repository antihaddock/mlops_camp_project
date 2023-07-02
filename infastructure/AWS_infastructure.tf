# Load environment variables from .env file
locals {
  aws_access_key     = file("./docker/.env")["AWS_ACCESS_KEY"]
  aws_secret_key     = file("./docker/.env")["AWS_SECRET_KEY"]
  aws_region         = file("./docker/.env")["AWS_REGION"]
  ami_id             = file("./docker/.env")["AMI_ID"]
  key_pair_name      = file("./docker/.env")["KEY_PAIR_NAME"]
  subnet_id          = file("./docker/.env")["SUBNET_ID"]
  bucket_name        = file("./docker/.env")["BUCKET_NAME"]
}

# Configure AWS provider
provider "aws" {
  access_key = local.aws_access_key
  secret_key = local.aws_secret_key
  region     = local.aws_region
}

# Create ECS cluster
resource "aws_ecs_cluster" "ecs_cluster" {
  name = "my-ecs-cluster"
}

# Create EC2 instance profile for ECS
resource "aws_iam_instance_profile" "ecs_instance_profile" {
  name = "ecs-instance-profile"
  role = aws_iam_role.ecs_instance_role.name
}

# Create IAM role for ECS instance
resource "aws_iam_role" "ecs_instance_role" {
  name = "ecs-instance-role"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

# Attach policy to ECS instance role
resource "aws_iam_role_policy_attachment" "ecs_instance_role_policy" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"
  role       = aws_iam_role.ecs_instance_role.name
}

# Create ECS instance security group
resource "aws_security_group" "ecs_instance_sg" {
  name        = "ecs-instance-sg"
  description = "ECS instance security group"

  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Create launch configuration for ECS instances
resource "aws_launch_configuration" "ecs_launch_configuration" {
  name          = "ecs-launch-configuration"
  image_id      = local.ami_id
  instance_type = "t2.micro"
  iam_instance_profile = aws_iam_instance_profile.ecs_instance_profile.name
  security_groups      = [aws_security_group.ecs_instance_sg.id]
  key_name             = local.key_pair_name
}

# Create auto scaling group for ECS instances
resource "aws_autoscaling_group" "ecs_autoscaling_group" {
  name                 = "ecs-autoscaling-group"
  desired_capacity     = 2
  min_size             = 1
  max_size             = 4
  launch_configuration = aws_launch_configuration.ecs_launch_configuration.name
  vpc_zone_identifier  = [local.subnet_id]
}

# Create S3 bucket
resource "aws_s3_bucket" "mlopsbucket" {
  bucket = local.bucket_name
  # Additional bucket configuration options
}


# Output ECS cluster name
output "ecs_cluster_name" {
  value = aws_ecs_cluster.ecs_cluster.name
}
