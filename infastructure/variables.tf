locals {
  data_lake_bucket = "data_engineering_project_data_lake"
}

variable "project" {
  description = "datazoomcap2023"
  default = "datazoomcap2023"
}

variable "region" {
  description = "Region for GCP resources. Choose as per your location: https://cloud.google.com/about/locations"
  default = "australia-southeast1"
  type = string
}

variable "storage_class" {
  description = "Our data lake bucket Prefect will store data in"
  default = "STANDARD"
}

variable "BQ_DATASET_1" {
  description = "BigQuery Dataset that raw data (from GCS) will be written to"
  type = string
  default = "healthcare_payments_raw"
}

variable "BQ_DATASET_2" {
  description = "BigQuery Dataset that will be the transformed layer of the data warehouse. Will ingest from the raw layer"
  type = string
  default = "healthcare_payments_transformed"
}
