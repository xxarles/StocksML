#######################################################
################### Base Defs #########################
#######################################################

variable "proj_name" {
  description = "value of the project name"
  type        = string
}

variable "account_id" {
  description = "AWS account Id used to terraform"
  type        = string
}

variable "region" {
  description = "AWS region used to terraform"
  type        = string
}

variable "env" {
  description = "Environment used for the deploy. Currently it does not add any kind of account separation."
  type        = string
}


#########################################################
#################### Lambda #############################
#########################################################

variable "ingestion_lambda_zip_key" {
  description = "The key of the zip file to be uploaded to the lambda"
  type        = string
  default     = "latest/ingestion/ingestion.zip"
}

variable "iam_role_name_stocks_ingestion" {
  description = "Name of the role for stocks ingestion"
  type        = string
  default     = "stocks-ingestion-lamba-role"
}

variable "iam_role_policy_name_stocks_ingestion" {
  description = "Name of the policy for the ingestion lambda"
  type        = string
  default     = "stocks-ingestion-lamba-policy"
}



#########################################################
####################### S3 ##############################
#########################################################

variable "easy_terraform_destroy" {
  description = "Allow for s3 deletion even when not empty"
  type        = bool
  default     = false
}

variable "bucket_name" {
  description = "The name of the bucket"
  type        = string
  default     = "stock-ingetion"
}

variable "log_bucket_prefix" {
  description = "The prefix for the logs"
  type        = string
  default     = "logger"
}

variable "ingestion_lambda_zip_path" {
  description = "The key of the zip file to be uploaded to the lambda"
  type        = string
  default     = "../packaged_lambda/stocks_ingestion.zip"

}
data "aws_iam_policy_document" "lambda_base_policy" {
  statement {
    sid    = ""
    effect = "Allow"

    principals {
      identifiers = ["lambda.amazonaws.com"]
      type        = "Service"
    }

    actions = ["sts:AssumeRole"]
  }
}

variable "stocks_ingestion_lambda_handler" {
  description = "The handler for the lambda"
  type        = string
  default     = "lambda_function.lambda_handler"

}

variable "stocks_ingestion_lambda_runtime" {
  description = "The runtime for the lambda"
  type        = string
  default     = "python3.12"
}
#########################################################
################# API Gateway ###########################
#########################################################

variable "cognito_scope_identifier" {
  description = "Scope identifier for API Gateway"
  type        = string
  default = ""
}


variable "cognito_arns" {
  description = "Cognito arn used for authetication"
  type        = list(string)
  default = [  ]

}
