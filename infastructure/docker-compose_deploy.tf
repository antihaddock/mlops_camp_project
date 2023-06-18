# Create an ECS cluster
resource "aws_ecs_cluster" "example_cluster" {
  name = "mlops cluster"  # Replace with your desired cluster name
}

# Create a task definition for mlflow service
resource "aws_ecs_task_definition" "mlflow_task_definition" {
  family                = "mlflow-task"
  container_definitions = jsonencode([
    {
      "name": "mlflow",
      "image": "ghcr.io/mlflow/mlflow",
      "portMappings": [
        {
          "containerPort": 8000,
          "hostPort": 8000
        }
      ],
      "environment": [
        {
          "name": "AWS_ACCESS_KEY_ID",
          "value": "****"
        },
        {
          "name": "AWS_SECRET_ACCESS_KEY",
          "value": "****"
        },
        {
          "name": "AWS_DEFAULT_REGION",
          "value": "*****"
        }
      ],
      "command": ["mlflow", "server", "--default-artifact-root", "s3://mlopsbucketantihaddock", "--port", "8000"],
      "memory": 512  # Specify the memory limit for the container
    }
  ])
}

# Create a task definition for myapp service
resource "aws_ecs_task_definition" "myapp_task_definition" {
  family                = "myapp-task"
  container_definitions = jsonencode([
    {
      "name": "myapp",
      "image": "python:3.8.12-slim",
      "portMappings": [
        {
          "containerPort": 5000,
          "hostPort": 5000
        },
        {
          "containerPort": 8000,
          "hostPort": 8000
        }
      ],
      "environment": [
        {
          "name": "AWS_ACCESS_KEY_ID",
          "value": "******"
        },
        {
          "name": "AWS_SECRET_ACCESS_KEY",
          "value": "*****"
        },
        {
          "name": "AWS_DEFAULT_REGION",
          "value": "****"
        }
      ],
      "mountPoints": [
        {
          "sourceVolume": "myapp-volume",
          "containerPath": "/application",
          "readOnly": false
        }
      ],
      "entryPoint": [
        "pipenv",
        "run",
        "gunicorn",
        "--bind=0.0.0.0:5000",
        "predict:app"
      ],
      "memory": 512  # Specify the memory limit for the container
    }
  ])

  volume {
    name = "myapp-volume"
  }
}

# Create an ECS service for mlflow task
resource "aws_ecs_service" "mlflow_service" {
  name            = "mlflow-service"
  cluster         = aws_ecs_cluster.example_cluster.id
  task_definition = aws_ecs_task_definition.mlflow_task_definition.arn
  desired_count   = 1
}

# Create an ECS service for myapp task
resource "aws_ecs_service" "myapp_service" {
  name            = "myapp-service"
  cluster         = aws_ecs_cluster.example_cluster.id
  task_definition = aws_ecs_task_definition.myapp_task_definition.arn
  desired_count   = 1
}
