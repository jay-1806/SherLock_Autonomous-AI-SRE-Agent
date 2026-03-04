"""Agent configuration — secrets, timeouts, thresholds."""

import json
import os
from functools import lru_cache


@lru_cache(maxsize=1)
def get_secrets() -> dict:
    """
    Fetch all Part 1 secrets from AWS Secrets Manager at startup.
    In local dev, falls back to environment variables.
    """
    if os.environ.get("ENV") == "local":
        return {}

    try:
        import boto3

        client = boto3.client("secretsmanager", region_name=os.environ["AWS_REGION"])
        response = client.get_secret_value(
            SecretId=os.environ["AWS_SECRETS_MANAGER_SECRET_NAME"]
        )
        return json.loads(response["SecretString"])
    except Exception:
        return {}


def get_secret(key: str) -> str:
    secrets = get_secrets()
    value = secrets.get(key) or os.environ.get(key)
    if not value:
        raise ValueError(
            f"Required secret '{key}' not found in Secrets Manager or environment"
        )
    return value
