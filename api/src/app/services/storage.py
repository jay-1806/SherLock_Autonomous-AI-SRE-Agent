"""S3 storage service for audit trails and investigation archives."""
from typing import Dict, Any
from ..config import AWS_S3_AUDIT_BUCKET
import json
from datetime import datetime, timezone


async def write_audit_log(
    event_type: str,
    data: Dict[str, Any],
    actor: str = "system"
) -> str:
    """
    Write an immutable audit trail entry to S3.
    
    Used for remediation execution logs, investigation archives,
    and feedback submissions; all queryable for compliance.
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    key = f"audit/{event_type}/{timestamp}_{data.get('id', 'unknown')}.json"
    
    record = {
        "event_type": event_type,
        "actor": actor,
        "timestamp": timestamp,
        "data": data,
    }
    
    # In production:
    # import boto3
    # s3 = boto3.client("s3")
    # s3.put_object(
    #     Bucket=AWS_S3_AUDIT_BUCKET,
    #     Key=key,
    #     Body=json.dumps(record),
    #     ContentType="application/json",
    #     ServerSideEncryption="aws:kms"
    # )
    
    return f"s3://{AWS_S3_AUDIT_BUCKET}/{key}"


async def archive_investigation(investigation: Dict[str, Any]) -> str:
    """Archive a completed investigation to S3 for the eval dataset."""
    return await write_audit_log("investigation_archive", investigation)


async def log_remediation_execution(execution: Dict[str, Any], actor: str) -> str:
    """Log a remediation execution attempt to the immutable audit trail."""
    return await write_audit_log("remediation_execution", execution, actor)
