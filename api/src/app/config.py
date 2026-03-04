"""Application configuration using environment variables."""
import os

# API Configuration
API_PORT = int(os.getenv("API_PORT", "8000"))
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

# CORS — comma-separated list of allowed origins, defaults to wildcard for local dev
_origins_env = os.getenv("ALLOWED_ORIGINS", "*")
ALLOWED_ORIGINS: list[str] = (
    ["*"] if _origins_env.strip() == "*"
    else [o.strip() for o in _origins_env.split(",") if o.strip()]
)

# Authentication
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN", "")
AUTH0_AUDIENCE = os.getenv("AUTH0_AUDIENCE", "")

# Webhook HMAC Secrets
PAGERDUTY_WEBHOOK_SECRET = os.getenv("PAGERDUTY_WEBHOOK_SECRET", "dev-pagerduty-secret")
CLOUDWATCH_WEBHOOK_SECRET = os.getenv("CLOUDWATCH_WEBHOOK_SECRET", "dev-cloudwatch-secret")
OPSGENIE_WEBHOOK_SECRET = os.getenv("OPSGENIE_WEBHOOK_SECRET", "dev-opsgenie-secret")

# Integrations
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL", "#sre-platform-alerts")
PAGERDUTY_API_KEY = os.getenv("PAGERDUTY_API_KEY", "")

# AWS
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_S3_AUDIT_BUCKET = os.getenv("AWS_S3_AUDIT_BUCKET", "sherlock-audit-trail")
AWS_SQS_QUEUE_URL = os.getenv("AWS_SQS_QUEUE_URL", "")

# Rate Limits
ALERT_DEDUP_WINDOW_SECONDS = int(os.getenv("ALERT_DEDUP_WINDOW_SECONDS", "300"))
ALERT_RATE_LIMIT_PER_SERVICE = int(os.getenv("ALERT_RATE_LIMIT_PER_SERVICE", "10"))
WEBSOCKET_MAX_CLIENTS = int(os.getenv("WEBSOCKET_MAX_CLIENTS", "50"))
