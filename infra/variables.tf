variable "OAUTH_CLIENT_ID" {
  description = "Client Id for google oauth should come from env variable TF_VAR_OAUTH_CLIENT_ID"
  type        = string
}

variable "OAUTH_CLIENT_SECRET" {
  description = "Client Id for google oauth should come from env variable TF_VAR_OAUTH_CLIENT_SECRET"
  type        = string
}

variable "env" {
  description = "Environment used for the deploy. Currently it does not add any kind of account separation."
  type        = string
  default     = "dev"
}

variable "proj_name" {
  description = "Name of the project"
  type        = string
  default     = "stocks-ingestion"
}
