"""Comprehensive mock data for the SherLock SRE platform."""
from datetime import datetime, timedelta

# ─── Investigations ───────────────────────────────────────────────────────────

MOCK_INVESTIGATIONS = [
    {
        "id": "inv-001",
        "title": "API Gateway High Latency",
        "description": "Increased response times detected on API Gateway service. P99 latency exceeded 2s threshold. Correlated with traffic spike from marketing campaign launch.",
        "status": "in_progress",
        "severity": "high",
        "service": "api-gateway",
        "created_at": "2026-02-27T10:30:00Z",
        "updated_at": "2026-02-27T11:45:00Z",
        "assigned_to": "oncall-team",
        "confidence": 0.87,
        "rca_summary": "Database connection pool exhaustion caused by sudden traffic spike from marketing campaign.",
        "hypotheses": [
            {"hypothesis": "Database connection pool exhaustion", "confidence": 0.87, "status": "confirmed"},
            {"hypothesis": "CDN cache miss rate increase", "confidence": 0.32, "status": "rejected"},
            {"hypothesis": "Upstream DNS resolution delay", "confidence": 0.15, "status": "rejected"}
        ],
        "evidence": [
            {"type": "metric", "source": "CloudWatch", "description": "DB connection count at 100% capacity since 10:28 UTC"},
            {"type": "log", "source": "ECS", "description": "Connection timeout errors in api-gateway task logs"},
            {"type": "deployment", "source": "GitHub", "description": "No deployments in last 6 hours - ruled out code change"}
        ],
        "blast_radius": ["api-gateway", "user-service", "order-service"],
        "timeline": [
            {"timestamp": "2026-02-27T10:30:00Z", "event": "Alert triggered: High latency detected (P99 > 2s)", "source": "datadog"},
            {"timestamp": "2026-02-27T10:32:00Z", "event": "Investigation created automatically", "source": "sherlock"},
            {"timestamp": "2026-02-27T10:33:00Z", "event": "Hypothesis generated: DB connection pool exhaustion", "source": "sherlock"},
            {"timestamp": "2026-02-27T10:35:00Z", "event": "Evidence collected: CloudWatch DB metrics confirm pool at 100%", "source": "sherlock"},
            {"timestamp": "2026-02-27T10:38:00Z", "event": "Correlated with marketing campaign traffic spike (+340%)", "source": "sherlock"},
            {"timestamp": "2026-02-27T11:00:00Z", "event": "Root cause confirmed: Database connection pool exhaustion", "source": "sherlock"},
            {"timestamp": "2026-02-27T11:15:00Z", "event": "NBA recommended: Scale out ECS desired count (ACT-002)", "source": "sherlock"}
        ],
        "root_cause": "Database connection pool exhausted due to 340% traffic spike from marketing campaign launch",
        "remediation": "Scale up database connections and add connection pooling. Recommended action: ACT-002 (ECS Scale-Out)",
        "nba_action_id": "ACT-002"
    },
    {
        "id": "inv-002",
        "title": "Payment Service 5xx Errors",
        "description": "Spike in 500 errors from payment processing service. Error rate exceeded 5% threshold. Customer-facing impact confirmed.",
        "status": "open",
        "severity": "critical",
        "service": "payment-service",
        "created_at": "2026-02-27T14:00:00Z",
        "updated_at": "2026-02-27T14:15:00Z",
        "assigned_to": None,
        "confidence": 0.45,
        "rca_summary": "Investigation in progress — initial analysis suggests deployment correlation.",
        "hypotheses": [
            {"hypothesis": "Bad deployment rolled out 25 min ago", "confidence": 0.72, "status": "investigating"},
            {"hypothesis": "Downstream payment provider outage", "confidence": 0.45, "status": "investigating"}
        ],
        "evidence": [
            {"type": "deployment", "source": "GitHub", "description": "payment-service v2.14.3 deployed 25 min before alert"},
            {"type": "metric", "source": "Prometheus", "description": "Error rate jumped from 0.2% to 7.8% at 13:35 UTC"}
        ],
        "blast_radius": ["payment-service", "checkout-service", "order-service"],
        "timeline": [
            {"timestamp": "2026-02-27T14:00:00Z", "event": "Alert triggered: 5xx error rate > 5%", "source": "pagerduty"},
            {"timestamp": "2026-02-27T14:02:00Z", "event": "Investigation created automatically", "source": "sherlock"},
            {"timestamp": "2026-02-27T14:05:00Z", "event": "Deployment correlation detected: v2.14.3 deployed 25 min prior", "source": "sherlock"},
            {"timestamp": "2026-02-27T14:10:00Z", "event": "Checking downstream payment provider health", "source": "sherlock"}
        ],
        "root_cause": None,
        "remediation": None,
        "nba_action_id": None
    },
    {
        "id": "inv-003",
        "title": "Cache Service Memory Pressure",
        "description": "Redis cache showing high memory usage warnings. Eviction rate increasing. Risk of cache performance degradation.",
        "status": "resolved",
        "severity": "medium",
        "service": "cache-service",
        "created_at": "2026-02-26T08:00:00Z",
        "updated_at": "2026-02-26T12:30:00Z",
        "assigned_to": "platform-team",
        "confidence": 0.94,
        "rca_summary": "Missing TTL on session cache entries caused unbounded memory growth over 72 hours.",
        "hypotheses": [
            {"hypothesis": "Missing TTL on cache entries", "confidence": 0.94, "status": "confirmed"},
            {"hypothesis": "Memory leak in cache client library", "confidence": 0.12, "status": "rejected"}
        ],
        "evidence": [
            {"type": "metric", "source": "Prometheus", "description": "Memory grew linearly over 72 hours — no TTL eviction observed"},
            {"type": "config", "source": "Redis", "description": "Session keys missing EXPIRE directive in cache writer"},
            {"type": "log", "source": "ElastiCache", "description": "Eviction policy triggered at 80% memory threshold"}
        ],
        "blast_radius": ["cache-service", "user-service"],
        "timeline": [
            {"timestamp": "2026-02-26T08:00:00Z", "event": "Alert triggered: Memory usage > 80%", "source": "prometheus"},
            {"timestamp": "2026-02-26T08:05:00Z", "event": "Investigation created automatically", "source": "sherlock"},
            {"timestamp": "2026-02-26T09:00:00Z", "event": "Hypothesis: Missing TTL causing memory accumulation", "source": "sherlock"},
            {"timestamp": "2026-02-26T10:00:00Z", "event": "Confirmed: Session keys have no EXPIRE directive", "source": "sherlock"},
            {"timestamp": "2026-02-26T12:00:00Z", "event": "TTL policy updated and stale keys flushed", "source": "manual"},
            {"timestamp": "2026-02-26T12:30:00Z", "event": "Memory normalized to 45%. Investigation resolved.", "source": "sherlock"}
        ],
        "root_cause": "Missing TTL on session cache entries caused unbounded memory growth",
        "remediation": "Added 24h TTL to all session cache entries. Flushed 2.1M stale keys.",
        "nba_action_id": "ACT-008"
    },
    {
        "id": "inv-004",
        "title": "Auth Service Timeout",
        "description": "Authentication requests timing out intermittently. 15% of login attempts failing with 504 Gateway Timeout.",
        "status": "closed",
        "severity": "low",
        "service": "auth-service",
        "created_at": "2026-02-25T16:00:00Z",
        "updated_at": "2026-02-25T18:00:00Z",
        "assigned_to": "security-team",
        "confidence": 0.91,
        "rca_summary": "Third-party identity provider (Okta) experienced a partial outage affecting token validation.",
        "hypotheses": [
            {"hypothesis": "Third-party identity provider outage", "confidence": 0.91, "status": "confirmed"},
            {"hypothesis": "Internal certificate expiry", "confidence": 0.08, "status": "rejected"}
        ],
        "evidence": [
            {"type": "external", "source": "Okta Status", "description": "Okta status page confirms partial outage 15:45-17:30 UTC"},
            {"type": "metric", "source": "CloudWatch", "description": "Auth latency P99 spiked to 12s (baseline: 200ms)"},
            {"type": "log", "source": "ECS", "description": "Connection timeout to accounts.okta.com in auth-service logs"}
        ],
        "blast_radius": ["auth-service"],
        "timeline": [
            {"timestamp": "2026-02-25T16:00:00Z", "event": "Alert triggered: Auth timeout rate > 10%", "source": "datadog"},
            {"timestamp": "2026-02-25T16:05:00Z", "event": "Investigation created automatically", "source": "sherlock"},
            {"timestamp": "2026-02-25T16:15:00Z", "event": "External dependency check: Okta status page reports degraded", "source": "sherlock"},
            {"timestamp": "2026-02-25T16:30:00Z", "event": "Root cause confirmed: Okta partial outage", "source": "sherlock"},
            {"timestamp": "2026-02-25T17:30:00Z", "event": "Okta reports issue resolved", "source": "external"},
            {"timestamp": "2026-02-25T18:00:00Z", "event": "Auth latency normalized. Investigation closed.", "source": "sherlock"}
        ],
        "root_cause": "Third-party identity provider (Okta) experienced partial outage",
        "remediation": "No action required — external dependency resolved. Added Okta health to monitoring.",
        "nba_action_id": None
    },
    {
        "id": "inv-005",
        "title": "Order Service CPU Saturation",
        "description": "ECS task CPU utilization sustained above 90% for 8 minutes. Auto-scaling not triggering due to misconfigured target tracking policy.",
        "status": "resolved",
        "severity": "high",
        "service": "order-service",
        "created_at": "2026-02-27T06:15:00Z",
        "updated_at": "2026-02-27T07:30:00Z",
        "assigned_to": "platform-team",
        "confidence": 0.92,
        "rca_summary": "Auto-scaling target tracking policy was set to 95% CPU instead of 70%, preventing scale-out.",
        "hypotheses": [
            {"hypothesis": "Auto-scaling policy misconfiguration", "confidence": 0.92, "status": "confirmed"},
            {"hypothesis": "Runaway background job consuming CPU", "confidence": 0.35, "status": "rejected"}
        ],
        "evidence": [
            {"type": "config", "source": "Terraform", "description": "Target tracking policy threshold set to 95% (should be 70%)"},
            {"type": "metric", "source": "CloudWatch", "description": "CPU at 91% for 8 min, desired count unchanged at 2"}
        ],
        "blast_radius": ["order-service", "payment-service", "notification-service"],
        "timeline": [
            {"timestamp": "2026-02-27T06:15:00Z", "event": "Alert triggered: CPU > 90% for 5+ min", "source": "cloudwatch"},
            {"timestamp": "2026-02-27T06:17:00Z", "event": "Investigation created automatically", "source": "sherlock"},
            {"timestamp": "2026-02-27T06:22:00Z", "event": "Auto-scaling policy inspected: threshold at 95% (misconfigured)", "source": "sherlock"},
            {"timestamp": "2026-02-27T06:30:00Z", "event": "Manual scale-out triggered: desired count 2 → 5", "source": "manual"},
            {"timestamp": "2026-02-27T07:00:00Z", "event": "Terraform PR opened to fix scaling threshold to 70%", "source": "sherlock"},
            {"timestamp": "2026-02-27T07:30:00Z", "event": "CPU normalized. Investigation resolved.", "source": "sherlock"}
        ],
        "root_cause": "Auto-scaling target tracking policy misconfigured at 95% CPU threshold instead of 70%",
        "remediation": "Fixed auto-scaling threshold to 70%. Manually scaled to 5 tasks. Terraform PR merged.",
        "nba_action_id": "ACT-001"
    },
    {
        "id": "inv-006",
        "title": "Lambda Throttling — Image Processor",
        "description": "Image processing Lambda function experiencing sustained throttling. 12% of invocations rejected.",
        "status": "resolved",
        "severity": "medium",
        "service": "image-processor",
        "created_at": "2026-02-26T19:00:00Z",
        "updated_at": "2026-02-26T20:15:00Z",
        "assigned_to": "platform-team",
        "confidence": 0.96,
        "rca_summary": "Concurrent execution limit hit due to batch upload feature launch without capacity planning.",
        "hypotheses": [
            {"hypothesis": "Concurrent execution limit reached", "confidence": 0.96, "status": "confirmed"}
        ],
        "evidence": [
            {"type": "metric", "source": "CloudWatch", "description": "Throttled invocations: 1,247 in last 15 min"},
            {"type": "deployment", "source": "GitHub", "description": "Batch upload feature deployed 2 hours prior"}
        ],
        "blast_radius": ["image-processor", "media-service"],
        "timeline": [
            {"timestamp": "2026-02-26T19:00:00Z", "event": "Alert triggered: Lambda throttle rate > 10%", "source": "cloudwatch"},
            {"timestamp": "2026-02-26T19:03:00Z", "event": "Investigation created automatically", "source": "sherlock"},
            {"timestamp": "2026-02-26T19:10:00Z", "event": "Root cause identified: Concurrency limit at 100, demand peak at 340", "source": "sherlock"},
            {"timestamp": "2026-02-26T19:30:00Z", "event": "Concurrency increased to 500 via ACT-003", "source": "sherlock"},
            {"timestamp": "2026-02-26T20:15:00Z", "event": "Throttling ceased. Investigation resolved.", "source": "sherlock"}
        ],
        "root_cause": "Lambda concurrent execution limit (100) insufficient for batch upload feature demand (peak 340)",
        "remediation": "Increased reserved concurrency to 500. ACT-003 executed automatically.",
        "nba_action_id": "ACT-003"
    }
]


# ─── Services ─────────────────────────────────────────────────────────────────

MOCK_SERVICES = [
    {
        "name": "api-gateway",
        "display_name": "API Gateway",
        "status": "degraded",
        "health_score": 72,
        "team": "platform-team",
        "sla_tier": "P1",
        "last_deployment": "2026-02-27T08:00:00Z",
        "active_incidents": 1,
        "dependencies": ["user-service", "order-service", "auth-service", "cache-service"],
        "region": "us-east-1",
        "environment": "production",
        "incident_history": [
            {"id": "inv-001", "title": "API Gateway High Latency", "date": "2026-02-27", "severity": "high", "root_cause": "DB connection pool exhaustion"},
            {"id": "inv-012", "title": "API Gateway 502 Errors", "date": "2026-02-20", "severity": "medium", "root_cause": "Upstream timeout configuration"},
            {"id": "inv-019", "title": "API Gateway Certificate Expiry Warning", "date": "2026-02-10", "severity": "low", "root_cause": "Auto-renewal failed"}
        ]
    },
    {
        "name": "payment-service",
        "display_name": "Payment Service",
        "status": "critical",
        "health_score": 35,
        "team": "payments-team",
        "sla_tier": "P1",
        "last_deployment": "2026-02-27T13:35:00Z",
        "active_incidents": 1,
        "dependencies": ["auth-service", "order-service"],
        "region": "us-east-1",
        "environment": "production",
        "incident_history": [
            {"id": "inv-002", "title": "Payment Service 5xx Errors", "date": "2026-02-27", "severity": "critical", "root_cause": "Under investigation"},
            {"id": "inv-008", "title": "Payment Timeout Spike", "date": "2026-02-15", "severity": "high", "root_cause": "DB deadlock on transactions table"}
        ]
    },
    {
        "name": "cache-service",
        "display_name": "Cache Service (Redis)",
        "status": "healthy",
        "health_score": 98,
        "team": "platform-team",
        "sla_tier": "P2",
        "last_deployment": "2026-02-26T12:30:00Z",
        "active_incidents": 0,
        "dependencies": [],
        "region": "us-east-1",
        "environment": "production",
        "incident_history": [
            {"id": "inv-003", "title": "Cache Service Memory Pressure", "date": "2026-02-26", "severity": "medium", "root_cause": "Missing TTL on cache entries"}
        ]
    },
    {
        "name": "auth-service",
        "display_name": "Auth Service",
        "status": "healthy",
        "health_score": 99,
        "team": "security-team",
        "sla_tier": "P1",
        "last_deployment": "2026-02-24T14:00:00Z",
        "active_incidents": 0,
        "dependencies": ["cache-service"],
        "region": "us-east-1",
        "environment": "production",
        "incident_history": [
            {"id": "inv-004", "title": "Auth Service Timeout", "date": "2026-02-25", "severity": "low", "root_cause": "Third-party Okta outage"}
        ]
    },
    {
        "name": "order-service",
        "display_name": "Order Service",
        "status": "healthy",
        "health_score": 95,
        "team": "commerce-team",
        "sla_tier": "P1",
        "last_deployment": "2026-02-27T06:00:00Z",
        "active_incidents": 0,
        "dependencies": ["payment-service", "cache-service", "notification-service"],
        "region": "us-east-1",
        "environment": "production",
        "incident_history": [
            {"id": "inv-005", "title": "Order Service CPU Saturation", "date": "2026-02-27", "severity": "high", "root_cause": "Auto-scaling misconfiguration"}
        ]
    },
    {
        "name": "user-service",
        "display_name": "User Service",
        "status": "healthy",
        "health_score": 97,
        "team": "identity-team",
        "sla_tier": "P2",
        "last_deployment": "2026-02-26T10:00:00Z",
        "active_incidents": 0,
        "dependencies": ["auth-service", "cache-service"],
        "region": "us-east-1",
        "environment": "production",
        "incident_history": []
    },
    {
        "name": "notification-service",
        "display_name": "Notification Service",
        "status": "healthy",
        "health_score": 100,
        "team": "platform-team",
        "sla_tier": "P3",
        "last_deployment": "2026-02-25T09:00:00Z",
        "active_incidents": 0,
        "dependencies": [],
        "region": "us-east-1",
        "environment": "production",
        "incident_history": []
    },
    {
        "name": "image-processor",
        "display_name": "Image Processor (Lambda)",
        "status": "healthy",
        "health_score": 96,
        "team": "media-team",
        "sla_tier": "P3",
        "last_deployment": "2026-02-26T17:00:00Z",
        "active_incidents": 0,
        "dependencies": ["media-service"],
        "region": "us-east-1",
        "environment": "production",
        "incident_history": [
            {"id": "inv-006", "title": "Lambda Throttling", "date": "2026-02-26", "severity": "medium", "root_cause": "Concurrency limit hit"}
        ]
    }
]


# ─── Remediation Catalog ──────────────────────────────────────────────────────

MOCK_REMEDIATION_CATALOG = [
    {
        "action_id": "ACT-001",
        "name": "ECS Service Restart",
        "description": "Force restart all tasks in an ECS service to recover from hung processes or memory leaks.",
        "trigger_condition": "Service CPU > 90% for 5 min with no deployment in last 2 hours",
        "risk_level": "low",
        "requires_mfa": False,
        "category": "compute",
        "estimated_duration": "2-3 minutes",
        "rollback_procedure": "Previous task definition revision will be restored automatically if health check fails within 5 minutes.",
        "last_executed": "2026-02-27T07:30:00Z",
        "execution_count": 12,
        "success_rate": 0.92
    },
    {
        "action_id": "ACT-002",
        "name": "ECS Desired Count Scale-Out",
        "description": "Increase the desired task count for an ECS service to handle increased traffic load.",
        "trigger_condition": "Service error rate > 5% with CPU > 70%; agent confidence > 0.85",
        "risk_level": "low",
        "requires_mfa": False,
        "category": "compute",
        "estimated_duration": "3-5 minutes",
        "rollback_procedure": "Reduce desired count back to original value. Tasks drain gracefully.",
        "last_executed": "2026-02-27T11:15:00Z",
        "execution_count": 8,
        "success_rate": 1.0
    },
    {
        "action_id": "ACT-003",
        "name": "Lambda Concurrency Increase",
        "description": "Increase reserved concurrent executions for a Lambda function experiencing throttling.",
        "trigger_condition": "Lambda throttle rate > 10% for 3 consecutive minutes",
        "risk_level": "low",
        "requires_mfa": False,
        "category": "serverless",
        "estimated_duration": "< 1 minute",
        "rollback_procedure": "Reduce reserved concurrency to previous value.",
        "last_executed": "2026-02-26T19:30:00Z",
        "execution_count": 5,
        "success_rate": 1.0
    },
    {
        "action_id": "ACT-004",
        "name": "RDS Read Replica Failover",
        "description": "Promote a read replica to primary if the current primary is under extreme CPU pressure.",
        "trigger_condition": "Primary RDS CPU > 95% for 10 min; read replica healthy",
        "risk_level": "medium",
        "requires_mfa": True,
        "category": "database",
        "estimated_duration": "5-10 minutes",
        "rollback_procedure": "Manual: reconfigure old primary as new replica and switch DNS records.",
        "last_executed": "2026-02-20T03:15:00Z",
        "execution_count": 2,
        "success_rate": 1.0
    },
    {
        "action_id": "ACT-005",
        "name": "Deployment Rollback (Last Known Good)",
        "description": "Roll back to the last known good deployment revision if an error rate spike is detected post-deploy.",
        "trigger_condition": "Error rate spike within 30 min of deployment; agent confidence > 0.90",
        "risk_level": "medium",
        "requires_mfa": True,
        "category": "deployment",
        "estimated_duration": "3-5 minutes",
        "rollback_procedure": "Re-deploy the rolled-back version. Requires new deployment pipeline run.",
        "last_executed": "2026-02-18T22:45:00Z",
        "execution_count": 4,
        "success_rate": 0.75
    },
    {
        "action_id": "ACT-006",
        "name": "ALB Target Group Deregister",
        "description": "Remove a failing EC2 instance from the ALB target group to stop routing traffic to it.",
        "trigger_condition": "Specific EC2 instance failure rate > 50% for 5 min",
        "risk_level": "medium",
        "requires_mfa": True,
        "category": "networking",
        "estimated_duration": "< 1 minute",
        "rollback_procedure": "Re-register instance to target group after health is restored.",
        "last_executed": None,
        "execution_count": 0,
        "success_rate": None
    },
    {
        "action_id": "ACT-007",
        "name": "Circuit Breaker Enable",
        "description": "Enable circuit breaker pattern for a downstream dependency experiencing high error rates.",
        "trigger_condition": "Downstream dependency error rate > 30%; latency > 3x baseline",
        "risk_level": "low",
        "requires_mfa": False,
        "category": "resilience",
        "estimated_duration": "< 1 minute",
        "rollback_procedure": "Disable circuit breaker flag via feature toggle.",
        "last_executed": "2026-02-22T14:30:00Z",
        "execution_count": 6,
        "success_rate": 1.0
    },
    {
        "action_id": "ACT-008",
        "name": "ElastiCache Flush (Selected Keys)",
        "description": "Flush specific key patterns from ElastiCache to resolve cache poisoning or stale data issues.",
        "trigger_condition": "Cache poisoning pattern detected by agent with high confidence",
        "risk_level": "high",
        "requires_mfa": True,
        "category": "cache",
        "estimated_duration": "1-2 minutes",
        "rollback_procedure": "Cache will repopulate on next read. Monitor cache hit rate for 10 minutes post-flush.",
        "last_executed": "2026-02-26T12:00:00Z",
        "execution_count": 3,
        "success_rate": 1.0
    }
]


# ─── Remediation Execution Log ────────────────────────────────────────────────

MOCK_EXECUTION_LOG = [
    {
        "execution_id": "exec-001",
        "action_id": "ACT-002",
        "action_name": "ECS Desired Count Scale-Out",
        "investigation_id": "inv-001",
        "triggered_by": "engineer@company.com",
        "status": "success",
        "executed_at": "2026-02-27T11:20:00Z",
        "duration_seconds": 187,
        "pre_state": {"desired_count": 2, "running_count": 2},
        "post_state": {"desired_count": 5, "running_count": 5},
        "dry_run": False
    },
    {
        "execution_id": "exec-002",
        "action_id": "ACT-003",
        "action_name": "Lambda Concurrency Increase",
        "investigation_id": "inv-006",
        "triggered_by": "auto-remediation",
        "status": "success",
        "executed_at": "2026-02-26T19:30:00Z",
        "duration_seconds": 12,
        "pre_state": {"reserved_concurrency": 100},
        "post_state": {"reserved_concurrency": 500},
        "dry_run": False
    },
    {
        "execution_id": "exec-003",
        "action_id": "ACT-008",
        "action_name": "ElastiCache Flush (Selected Keys)",
        "investigation_id": "inv-003",
        "triggered_by": "platform-lead@company.com",
        "status": "success",
        "executed_at": "2026-02-26T12:00:00Z",
        "duration_seconds": 45,
        "pre_state": {"keys_matched": 2_100_000, "memory_usage_pct": 82},
        "post_state": {"keys_flushed": 2_100_000, "memory_usage_pct": 45},
        "dry_run": False
    }
]


# ─── KPI / Eval Metrics ──────────────────────────────────────────────────────

MOCK_EVAL_SUMMARY = {
    "last_updated": "2026-02-27T12:00:00Z",
    "period": "Last 30 days",
    "kpis": [
        {
            "name": "Mean Time to Root Cause (MTTRC)",
            "value": "4.2 min",
            "target": "≥ 70% reduction vs. baseline",
            "trend": "improving",
            "change": "-18% vs. last month",
            "status": "on_track",
            "history": [8.5, 7.2, 6.1, 5.5, 4.8, 4.2]
        },
        {
            "name": "Investigation Accuracy Rate",
            "value": "87%",
            "target": "≥ 85% (Phase 1)",
            "trend": "improving",
            "change": "+3% vs. last month",
            "status": "on_track",
            "history": [72, 76, 80, 82, 84, 87]
        },
        {
            "name": "Autonomous Coverage",
            "value": "83%",
            "target": "≥ 80% P1/P2 alerts",
            "trend": "stable",
            "change": "+1% vs. last month",
            "status": "on_track",
            "history": [65, 70, 75, 78, 82, 83]
        },
        {
            "name": "Alert-to-Investigation Latency",
            "value": "2.8 min",
            "target": "< 4 min for ≥ 75%",
            "trend": "improving",
            "change": "-22% vs. last month",
            "status": "on_track",
            "history": [6.2, 5.1, 4.3, 3.8, 3.2, 2.8]
        },
        {
            "name": "On-Call Toil Reduction",
            "value": "52%",
            "target": "≥ 50% reduction",
            "trend": "improving",
            "change": "+8% vs. last month",
            "status": "on_track",
            "history": [15, 25, 33, 40, 44, 52]
        },
        {
            "name": "Auto-Remediation Success Rate",
            "value": "94%",
            "target": "≥ 90%",
            "trend": "stable",
            "change": "+1% vs. last month",
            "status": "on_track",
            "history": [82, 85, 88, 91, 93, 94]
        },
        {
            "name": "False Positive Escalation Rate",
            "value": "3.2%",
            "target": "≤ 5%",
            "trend": "improving",
            "change": "-1.5% vs. last month",
            "status": "on_track",
            "history": [12, 9, 7, 5.5, 4.7, 3.2]
        },
        {
            "name": "Engineer NPS",
            "value": "42",
            "target": "≥ 40 within 3 months",
            "trend": "improving",
            "change": "+6 vs. last month",
            "status": "on_track",
            "history": [18, 24, 30, 34, 36, 42]
        }
    ],
    "summary_stats": {
        "total_investigations_30d": 127,
        "auto_triggered": 105,
        "manual_triggered": 22,
        "avg_confidence": 0.84,
        "total_remediations": 34,
        "successful_remediations": 32,
        "top_recurring_causes": [
            {"cause": "Connection pool exhaustion", "count": 8},
            {"cause": "Auto-scaling misconfiguration", "count": 6},
            {"cause": "Deployment-related regression", "count": 5},
            {"cause": "Third-party dependency outage", "count": 4},
            {"cause": "Cache TTL misconfiguration", "count": 3}
        ]
    }
}


# ─── Feedback Data ────────────────────────────────────────────────────────────

MOCK_FEEDBACK = [
    {"investigation_id": "inv-001", "rating": "correct", "comment": "Spot on — connection pool was the issue.", "submitted_by": "sre-lead@company.com", "submitted_at": "2026-02-27T12:00:00Z"},
    {"investigation_id": "inv-003", "rating": "correct", "comment": "Missing TTL was confirmed. Good catch.", "submitted_by": "platform-eng@company.com", "submitted_at": "2026-02-26T13:00:00Z"},
    {"investigation_id": "inv-004", "rating": "correct", "comment": "External dependency correctly identified.", "submitted_by": "security-eng@company.com", "submitted_at": "2026-02-25T19:00:00Z"},
    {"investigation_id": "inv-005", "rating": "partially_correct", "comment": "Scaling config was right, but missed that the node group also needed updating.", "submitted_by": "platform-eng@company.com", "submitted_at": "2026-02-27T08:00:00Z"},
    {"investigation_id": "inv-006", "rating": "correct", "comment": "Lambda concurrency was the bottleneck.", "submitted_by": "media-eng@company.com", "submitted_at": "2026-02-26T21:00:00Z"},
]


# ─── Graph Data (mock nodes/edges for visualization) ─────────────────────────

MOCK_GRAPH_DATA = {
    "nodes": [
        {"id": "api-gateway", "label": "API Gateway", "type": "service", "status": "degraded", "health": 72},
        {"id": "payment-service", "label": "Payment Service", "type": "service", "status": "critical", "health": 35},
        {"id": "cache-service", "label": "Cache Service", "type": "service", "status": "healthy", "health": 98},
        {"id": "auth-service", "label": "Auth Service", "type": "service", "status": "healthy", "health": 99},
        {"id": "order-service", "label": "Order Service", "type": "service", "status": "healthy", "health": 95},
        {"id": "user-service", "label": "User Service", "type": "service", "status": "healthy", "health": 97},
        {"id": "notification-service", "label": "Notification Service", "type": "service", "status": "healthy", "health": 100},
        {"id": "image-processor", "label": "Image Processor", "type": "service", "status": "healthy", "health": 96},
        {"id": "media-service", "label": "Media Service", "type": "service", "status": "healthy", "health": 99},
        {"id": "rds-primary", "label": "RDS Primary", "type": "host", "status": "healthy", "health": 88},
        {"id": "elasticache-cluster", "label": "ElastiCache", "type": "host", "status": "healthy", "health": 98},
        {"id": "deploy-v2.14.3", "label": "Deploy v2.14.3", "type": "deployment", "status": "suspect", "health": None},
        {"id": "inc-002", "label": "INC-002: 5xx Errors", "type": "incident", "status": "active", "health": None}
    ],
    "edges": [
        {"source": "api-gateway", "target": "user-service", "call_volume": 1200, "error_rate": 0.2},
        {"source": "api-gateway", "target": "order-service", "call_volume": 800, "error_rate": 0.5},
        {"source": "api-gateway", "target": "auth-service", "call_volume": 2000, "error_rate": 0.1},
        {"source": "api-gateway", "target": "cache-service", "call_volume": 5000, "error_rate": 0.0},
        {"source": "order-service", "target": "payment-service", "call_volume": 600, "error_rate": 7.8},
        {"source": "order-service", "target": "cache-service", "call_volume": 1500, "error_rate": 0.0},
        {"source": "order-service", "target": "notification-service", "call_volume": 400, "error_rate": 0.0},
        {"source": "user-service", "target": "auth-service", "call_volume": 900, "error_rate": 0.1},
        {"source": "user-service", "target": "cache-service", "call_volume": 3000, "error_rate": 0.0},
        {"source": "payment-service", "target": "auth-service", "call_volume": 500, "error_rate": 0.3},
        {"source": "image-processor", "target": "media-service", "call_volume": 200, "error_rate": 0.0},
        {"source": "payment-service", "target": "rds-primary", "call_volume": 600, "error_rate": 0.5},
        {"source": "order-service", "target": "rds-primary", "call_volume": 800, "error_rate": 0.1},
        {"source": "cache-service", "target": "elasticache-cluster", "call_volume": 10000, "error_rate": 0.0},
        {"source": "deploy-v2.14.3", "target": "payment-service", "call_volume": None, "error_rate": None},
        {"source": "inc-002", "target": "payment-service", "call_volume": None, "error_rate": None}
    ]
}


# ─── Helper Functions ─────────────────────────────────────────────────────────

def get_all_investigations():
    """Return all investigations as summaries."""
    return [
        {
            "id": inv["id"],
            "title": inv["title"],
            "status": inv["status"],
            "severity": inv["severity"],
            "service": inv["service"],
            "created_at": inv["created_at"],
            "confidence": inv.get("confidence"),
            "rca_summary": inv.get("rca_summary"),
        }
        for inv in MOCK_INVESTIGATIONS
    ]


def get_investigation_by_id(investigation_id: str):
    """Return a single investigation by ID."""
    for inv in MOCK_INVESTIGATIONS:
        if inv["id"] == investigation_id:
            return inv
    return None


def get_investigation_graph(investigation_id: str):
    """Return graph data for a specific investigation."""
    inv = get_investigation_by_id(investigation_id)
    if not inv:
        return None
    # Filter graph to nodes relevant to this investigation's blast radius
    blast = set(inv.get("blast_radius", []))
    # Always include all nodes for a richer visualization
    return MOCK_GRAPH_DATA


def get_all_services():
    """Return all services with health status."""
    return [
        {
            "name": svc["name"],
            "display_name": svc["display_name"],
            "status": svc["status"],
            "health_score": svc["health_score"],
            "team": svc["team"],
            "sla_tier": svc["sla_tier"],
            "last_deployment": svc["last_deployment"],
            "active_incidents": svc["active_incidents"],
        }
        for svc in MOCK_SERVICES
    ]


def get_service_by_name(name: str):
    """Return a service with full details by name."""
    for svc in MOCK_SERVICES:
        if svc["name"] == name:
            return svc
    return None


def get_remediation_catalog():
    """Return the full remediation action catalog."""
    return MOCK_REMEDIATION_CATALOG


def get_remediation_action(action_id: str):
    """Return a single remediation action by ID."""
    for action in MOCK_REMEDIATION_CATALOG:
        if action["action_id"] == action_id:
            return action
    return None


def get_execution_log():
    """Return remediation execution history."""
    return MOCK_EXECUTION_LOG


def get_eval_summary():
    """Return eval/KPI summary data."""
    return MOCK_EVAL_SUMMARY


def get_feedback():
    """Return all feedback entries."""
    return MOCK_FEEDBACK


def get_feedback_for_investigation(investigation_id: str):
    """Return feedback for a specific investigation."""
    return [f for f in MOCK_FEEDBACK if f["investigation_id"] == investigation_id]
