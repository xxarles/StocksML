resource "aws_cognito_user_pool" "stocks_ingestion_user_pool" {
  name = var.proj_name

  password_policy {
    minimum_length                   = var.password_minimum_length
    require_lowercase                = var.password_require_lowercase
    require_numbers                  = var.password_require_numbers
    require_symbols                  = var.password_require_symbols
    require_uppercase                = var.password_require_uppercase
    temporary_password_validity_days = var.temporary_password_validity_days
  }

  verification_message_template {
    email_message         = var.email_message
    default_email_option  = var.default_email_option
    email_subject         = var.email_subject
    email_message_by_link = var.email_message_by_link
    email_subject_by_link = var.email_subject_by_link
  }

  schema {
    attribute_data_type      = var.schema_attribute_data_type
    developer_only_attribute = var.schema_developer_only_attribute
    mutable                  = var.schema_mutable
    name                     = var.schema_name
    required                 = var.schema_required

    string_attribute_constraints {
      min_length = var.schema_min_length
      max_length = var.schema_max_length
    }
  }
}

resource "aws_cognito_user_pool_client" "client" {
  name = "${var.proj_name}--${var.env}--pool"

  user_pool_id                          = aws_cognito_user_pool.stocks_ingestion_user_pool.id
  generate_secret                       = var.client_generate_secret
  refresh_token_validity                = var.client_refresh_token_validity
  prevent_user_existence_errors         = var.client_prevent_user_existence_errors
  explicit_auth_flows                   = var.client_explicit_auth_flows 

  callback_urls                         = var.callback_urls
  logout_urls                           = var.logout_urls
  allowed_oauth_flows                   = var.allowed_oauth_flows
  allowed_oauth_flows_user_pool_client  = var.allowed_oauth_flows_user_pool_client
  allowed_oauth_scopes                  = aws_cognito_resource_server.resource_server.scope_identifiers

  supported_identity_providers  = [aws_cognito_identity_provider.cognito_google_provider.provider_name]
  
}


resource "aws_cognito_identity_provider" "cognito_google_provider" {
  user_pool_id  = aws_cognito_user_pool.stocks_ingestion_user_pool.id
  provider_name = "Google"
  provider_type = "Google"

  provider_details = {
    authorize_scopes = "email"
    client_id        = var.oauth_client_id
    client_secret    = var.oauth_client_secret
    authorize_scopes = "profile email openid"
    attributes_url_add_attributes = true
    attributes_url                = "https://people.googleapis.com/v1/people/me?personFields="
    authorize_url                 = "https://accounts.google.com/o/oauth2/v2/auth"
    oidc_issuer                   = "https://accounts.google.com"
    token_url                     = "https://www.googleapis.com/oauth2/v4/token"
    token_request_method          = "POST"
  }

  attribute_mapping = {
    email       = "email"
    family_name = "family_name"
    given_name  = "given_name"
    name        = "name"
    picture     = "picture"
    username    = "sub"
  }

}



resource "aws_cognito_user_pool_domain" "stocks_ingestion_domain" {
  domain       = var.proj_name
  user_pool_id = aws_cognito_user_pool.stocks_ingestion_user_pool.id
}

resource "aws_cognito_resource_server" "resource_server" {
  name         = "${var.proj_name}--${var.env}--cognito-server"
  identifier   = "https://api.${var.proj_name}_${var.env}"
  user_pool_id = "${aws_cognito_user_pool.stocks_ingestion_user_pool.id}"

  scope {
    scope_name        = "all"
    scope_description = "Get access to all API Gateway endpoints."
  }
}
