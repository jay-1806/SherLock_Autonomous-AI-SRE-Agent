-- Staging model for CloudWatch metrics normalization
WITH raw AS (
    SELECT * FROM {{ source('cloudwatch', 'metrics') }}
)
SELECT
    id AS signal_id,
    'metric' AS signal_type,
    service_name,
    host_id,
    namespace,
    timestamp_utc,
    value,
    NULL::TEXT AS body,
    severity,
    tags,
    trace_id,
    span_id,
    parent_span_id,
    'aws-cloudwatch' AS source_connector,
    '1.0' AS schema_version
FROM raw
