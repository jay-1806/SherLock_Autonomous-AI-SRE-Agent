# SherLock — Terraform Infrastructure
# Part 1 (agent, graph, ingestion) + Part 2 (audit trail, remediation)

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Remote state — S3 backend
  # backend "s3" {
  #   bucket         = "sherlock-terraform-state"
  #   key            = "platform/terraform.tfstate"
  #   region         = "us-east-1"
  #   dynamodb_table = "terraform-locks"
  #   encrypt        = true
  # }
}

provider "aws" {
  region = var.region
}

# ─── S3 Buckets (Part 2) ────────────────────────────────────────────────

resource "aws_s3_bucket" "audit_trail" {
  bucket = "${var.project_name}-audit-trail-${var.environment}"

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Component   = "part2-audit"
  }
}

resource "aws_s3_bucket_versioning" "audit_trail" {
  bucket = aws_s3_bucket.audit_trail.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "audit_trail" {
  bucket = aws_s3_bucket.audit_trail.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "aws:kms"
    }
  }
}

# ─── IAM Roles (Part 2) ─────────────────────────────────────────────────

resource "aws_iam_role" "remediation_executor" {
  name = "${var.project_name}-remediation-executor-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
        Condition = {
          NumericLessThan = {
            "aws:MaxSessionDuration" = "900"
          }
        }
      }
    ]
  })

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Component   = "auto-remediation"
  }
}
