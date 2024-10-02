output "cognito_arn"{
    value = aws_cognito_user_pool.stocks_ingestion_user_pool.arn
}

output "cognito_scope_identifier" {
    value = aws_cognito_user_pool.stocks_ingestion_user_pool.id
  
}