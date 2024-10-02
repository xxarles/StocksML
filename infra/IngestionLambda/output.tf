output "stocks_ingestion_lambda_url"{
    value = aws_api_gateway_deployment.stocks_ingestion.invoke_url
}