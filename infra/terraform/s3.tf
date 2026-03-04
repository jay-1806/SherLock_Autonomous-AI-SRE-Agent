resource "aws_s3_bucket" "sre_investigations" {
  bucket = "sre-investigations-${var.environment}-${data.aws_caller_identity.current.account_id}"
}

resource "aws_s3_bucket_versioning" "sre_investigations" {
  bucket = aws_s3_bucket.sre_investigations.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket" "sre_telemetry_staging" {
  bucket = "sre-telemetry-staging-${var.environment}-${data.aws_caller_identity.current.account_id}"
}

resource "aws_s3_bucket_versioning" "sre_telemetry_staging" {
  bucket = aws_s3_bucket.sre_telemetry_staging.id

  versioning_configuration {
    status = "Enabled"
  }
}

data "aws_caller_identity" "current" {}
