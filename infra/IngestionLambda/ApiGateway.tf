resource "aws_api_gateway_rest_api" "stocks_ingestion" {
  name        = "${var.proj_name}--${var.env}--gateway"
  description = "API Gateway for the stock ingestion lambda"
}

resource "aws_api_gateway_resource" "stocks_ingestion_proxy" {
  rest_api_id = aws_api_gateway_rest_api.stocks_ingestion.id
  parent_id   = aws_api_gateway_rest_api.stocks_ingestion.root_resource_id
  path_part   = "{proxy+}"
}

resource "aws_api_gateway_method" "stocks_ingestion_proxy" {
  rest_api_id   = aws_api_gateway_rest_api.stocks_ingestion.id
  resource_id   = aws_api_gateway_resource.stocks_ingestion_proxy.id
  http_method   = "ANY"
  authorization = "NONE"
  # authorizer_id = var.cognito_scope_identifier
}

resource "aws_api_gateway_integration" "stocks_ingestion_lambda" {
  rest_api_id             = aws_api_gateway_rest_api.stocks_ingestion.id
  resource_id             = aws_api_gateway_method.stocks_ingestion_proxy.resource_id
  http_method             = aws_api_gateway_method.stocks_ingestion_proxy.http_method
  integration_http_method = "ANY"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.stocks_ingestion_lambda.invoke_arn
}

resource "aws_api_gateway_method" "stocks_ingestion_proxy_root" {
  rest_api_id   = aws_api_gateway_rest_api.stocks_ingestion.id
  resource_id   = aws_api_gateway_rest_api.stocks_ingestion.root_resource_id
  http_method   = "ANY"
  authorization = "NONE"
  # authorizer_id = aws_api_gateway_authorizer.stocks_ingestion_authorizer.id
}

resource "aws_api_gateway_integration" "stocks_ingestion_lambda_root" {
  rest_api_id             = aws_api_gateway_rest_api.stocks_ingestion.id
  resource_id             = aws_api_gateway_method.stocks_ingestion_proxy_root.resource_id
  http_method             = aws_api_gateway_method.stocks_ingestion_proxy_root.http_method
  integration_http_method = "ANY"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.stocks_ingestion_lambda.invoke_arn
}

resource "aws_api_gateway_deployment" "stocks_ingestion" {
  depends_on = [
    aws_api_gateway_integration.stocks_ingestion_lambda,
    aws_api_gateway_integration.stocks_ingestion_lambda_root
  ]
  rest_api_id = aws_api_gateway_rest_api.stocks_ingestion.id
  stage_name  = "entry"
}

resource "aws_api_gateway_stage" "stocks_ingestion" {
    rest_api_id = aws_api_gateway_rest_api.stocks_ingestion.id
    stage_name  = "exec"
    deployment_id = aws_api_gateway_deployment.stocks_ingestion.id
}

resource "aws_api_gateway_usage_plan" "stocks_ingestion" {
    name = "${var.proj_name}--${var.env}--usage-plan"
    api_stages {
        api_id = aws_api_gateway_rest_api.stocks_ingestion.id
        stage  = aws_api_gateway_deployment.stocks_ingestion.stage_name
    }
    throttle_settings {
        burst_limit = 100
        rate_limit  = 100
    }
    quota_settings {
        limit  = 1000
        offset = 0
        period = "MONTH"
    }
}

# resource "aws_api_gateway_authorizer" "stocks_ingestion_authorizer"{
#     name = "${var.proj_name}--${var.env}--authorizer"
#     type = "COGNITO_USER_POOLS"
#     rest_api_id = aws_api_gateway_rest_api.stocks_ingestion.id
#     provider_arns = var.cognito_arns
# }