

resource "aws_lambda_function" "stocks_ingestion_lambda" {
  function_name = "${var.proj_name}-${var.env}"
  description   = "This is the lambda function for stock ingestion."
  s3_bucket     = aws_s3_bucket.stocks_ingestion_lambda_zip_s3.bucket
  s3_key        = var.ingestion_lambda_zip_key
  handler       = var.stocks_ingestion_lambda_handler
  runtime       = var.stocks_ingestion_lambda_runtime


  role = aws_iam_role.iam_role_stocks_ingestion.arn
  environment {
    variables = {
      ENV = var.env
    }
  }
  depends_on = [aws_s3_bucket.stocks_ingestion_lambda_zip_s3, aws_s3_bucket.stocks_ingestion_data_s3, aws_s3_object.stocks_ingestion_lambda_zip]

}

resource "aws_lambda_permission" "stocks_ingestion_apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.stocks_ingestion_lambda.function_name
  principal     = "apigateway.amazonaws.com"

  # The /*/* portion grants access from any method on any resource
  # within the API Gateway "REST API".
  source_arn = "${aws_api_gateway_rest_api.stocks_ingestion.execution_arn}/*/*"
}




resource "aws_iam_role" "iam_role_stocks_ingestion" {
  name               = var.iam_role_name_stocks_ingestion
  assume_role_policy = data.aws_iam_policy_document.lambda_base_policy.json
}


resource "aws_iam_role_policy" "iam_policy_stocks_ingestion" {
  name   = var.iam_role_policy_name_stocks_ingestion
  role   = aws_iam_role.iam_role_stocks_ingestion.id
  policy = data.aws_iam_policy_document.stocks_ingestion.json
}

data "aws_iam_policy_document" "stocks_ingestion" {

  statement {
    effect = "Allow"

    actions = [
      "lambda-object:*",
      "lambda:*",
      "logs:*",
      "s3:*",
    ]

    resources = ["*"]

  }

}







