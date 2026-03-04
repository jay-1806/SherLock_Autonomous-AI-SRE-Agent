output "cluster_endpoint" {
  description = "EKS cluster API endpoint"
  value       = module.eks.cluster_endpoint
}

output "cluster_name" {
  description = "EKS cluster name"
  value       = module.eks.cluster_name
}

output "sre_investigations_bucket" {
  description = "SRE investigations S3 bucket name"
  value       = aws_s3_bucket.sre_investigations.id
}

output "sre_telemetry_staging_bucket" {
  description = "SRE telemetry staging S3 bucket name"
  value       = aws_s3_bucket.sre_telemetry_staging.id
}

# Part 2 outputs
output "audit_bucket_name" {
  value       = aws_s3_bucket.audit_trail.bucket
  description = "S3 bucket for remediation audit trail"
}

output "remediation_role_arn" {
  value       = aws_iam_role.remediation_executor.arn
  description = "IAM role ARN for remediation executor"
}
