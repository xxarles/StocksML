
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.69"
    }
  }
}

provider "aws" {
  access_key = "test"
  secret_key = "test"
  region     = "us-east-1"
  s3_use_path_style           = false
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true

  endpoints {
    apigateway     = "http://localhost:4566"
    apigatewayv2   = "http://localhost:4566"
    cloudformation = "http://localhost:4566"
    cloudwatch     = "http://localhost:4566"
    dynamodb       = "http://localhost:4566"
    ec2            = "http://localhost:4566"
    es             = "http://localhost:4566"
    elasticache    = "http://localhost:4566"
    firehose       = "http://localhost:4566"
    iam            = "http://localhost:4566"
    kinesis        = "http://localhost:4566"
    lambda         = "http://localhost:4566"
    rds            = "http://localhost:4566"
    redshift       = "http://localhost:4566"
    route53        = "http://localhost:4566"
    s3             = "http://s3.localhost.localstack.cloud:4566"
    secretsmanager = "http://localhost:4566"
    ses            = "http://localhost:4566"
    sns            = "http://localhost:4566"
    sqs            = "http://localhost:4566"
    ssm            = "http://localhost:4566"
    stepfunctions  = "http://localhost:4566"
    sts            = "http://localhost:4566"
  }
}

data "aws_region" "current" {}

data "aws_caller_identity" "current" {}


# module "SharedResources" {
#   source              = "./SharedResources"
#   account_id          = data.aws_caller_identity.current.account_id
#   region              = data.aws_region.current.name
#   oauth_client_id     = var.OAUTH_CLIENT_ID
#   oauth_client_secret = var.OAUTH_CLIENT_SECRET
#   env                 = var.env
#   proj_name = var.proj_name
# }

module "IngestionLambda" {
  source                   = "./IngestionLambda"
  account_id               = data.aws_caller_identity.current.account_id
  region                   = data.aws_region.current.name
  # cognito_arns             = ["${module.SharedResources.cognito_arn}"]
  # cognito_scope_identifier = module.SharedResources.cognito_scope_identifier
  env                      = var.env
  proj_name = var.proj_name
}
