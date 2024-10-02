resource "aws_s3_bucket" "stocks_ingestion_lambda_zip_s3_log" {
  bucket        = "${var.proj_name}--${var.bucket_name}--${var.env}--log"
  force_destroy = var.easy_terraform_destroy
}

resource "aws_s3_bucket" "stocks_ingestion_lambda_zip_s3" {
  bucket = "${var.proj_name}--${var.bucket_name}--${var.env}--zip"
  tags = {
    Name        = "Stock ingestion lambda zip s3 bucket. Where the .zip used to deploy the lambdas are to be stored."
    environment = var.env
  }
  force_destroy = var.easy_terraform_destroy
}

resource "aws_s3_bucket" "stocks_ingestion_data_s3" {
  bucket = "${var.proj_name}--${var.bucket_name}--${var.env}--data"
  tags = {
    Name        = "Stock ingestion data s3 bucket. Where the data is stored."
    environment = var.env
  }
  force_destroy = var.easy_terraform_destroy
}

resource "aws_s3_bucket_logging" "stocks_ingestion_data_s3_logging" {
    bucket = aws_s3_bucket.stocks_ingestion_data_s3.bucket
    target_bucket = aws_s3_bucket.stocks_ingestion_lambda_zip_s3_log.bucket
    target_prefix = var.log_bucket_prefix
  
}

resource "aws_s3_bucket_logging" "stocks_ingestion_lambda_zip_s3_logging" {
  bucket = aws_s3_bucket.stocks_ingestion_lambda_zip_s3.bucket
  target_bucket = aws_s3_bucket.stocks_ingestion_lambda_zip_s3_log.bucket
  target_prefix = var.log_bucket_prefix
}

resource "aws_s3_bucket_ownership_controls" "stocks_ingestion_lambda_zip_s3_ownership" {
  bucket = aws_s3_bucket.stocks_ingestion_lambda_zip_s3_log.bucket
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_public_access_block" "ingestion_s3_block" {
  bucket = aws_s3_bucket.stocks_ingestion_lambda_zip_s3.bucket

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

# resource "aws_s3_bucket_acl" "ingestion_s3_acl" {
#   bucket = aws_s3_bucket.stocks_ingestion_lambda_zip_s3.bucket
#   acl = "private"
# }

resource "aws_s3_object" "stocks_ingestion_lambda_zip" {
  bucket = aws_s3_bucket.stocks_ingestion_lambda_zip_s3.bucket
  key    = var.ingestion_lambda_zip_key
  source = var.ingestion_lambda_zip_path
  acl    = "private"
  depends_on = [aws_s3_bucket.stocks_ingestion_lambda_zip_s3]
}