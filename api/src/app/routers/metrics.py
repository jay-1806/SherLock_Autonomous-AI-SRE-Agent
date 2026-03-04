"""Prometheus-format metrics endpoint."""
from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

router = APIRouter(tags=["metrics"])


@router.get("/metrics", response_class=PlainTextResponse)
async def get_metrics():
    """
    Prometheus-format metrics for external scraping.
    
    Exposes platform KPIs in Prometheus text exposition format.
    Secured by API key in production.
    """
    from ..services.mock_data import get_eval_summary, get_all_investigations, get_execution_log

    evals = get_eval_summary()
    investigations = get_all_investigations()
    executions = get_execution_log()

    total_inv = len(investigations)
    active_inv = sum(1 for i in investigations if i["status"] in ("open", "in_progress"))
    resolved_inv = sum(1 for i in investigations if i["status"] == "resolved")

    lines = [
        "# HELP sherlock_investigations_total Total number of investigations",
        "# TYPE sherlock_investigations_total gauge",
        f"sherlock_investigations_total {total_inv}",
        "",
        "# HELP sherlock_investigations_active Currently active investigations",
        "# TYPE sherlock_investigations_active gauge",
        f"sherlock_investigations_active {active_inv}",
        "",
        "# HELP sherlock_investigations_resolved Resolved investigations",
        "# TYPE sherlock_investigations_resolved gauge",
        f"sherlock_investigations_resolved {resolved_inv}",
        "",
        "# HELP sherlock_mttrc_minutes Mean Time to Root Cause in minutes",
        "# TYPE sherlock_mttrc_minutes gauge",
        "sherlock_mttrc_minutes 4.2",
        "",
        "# HELP sherlock_investigation_accuracy Investigation accuracy rate (0-1)",
        "# TYPE sherlock_investigation_accuracy gauge",
        "sherlock_investigation_accuracy 0.87",
        "",
        "# HELP sherlock_autonomous_coverage Percentage of alerts auto-investigated (0-1)",
        "# TYPE sherlock_autonomous_coverage gauge",
        "sherlock_autonomous_coverage 0.83",
        "",
        "# HELP sherlock_alert_to_investigation_latency_minutes Alert-to-investigation latency",
        "# TYPE sherlock_alert_to_investigation_latency_minutes gauge",
        "sherlock_alert_to_investigation_latency_minutes 2.8",
        "",
        "# HELP sherlock_auto_remediation_success Auto remediation success rate (0-1)",
        "# TYPE sherlock_auto_remediation_success gauge",
        "sherlock_auto_remediation_success 0.94",
        "",
        "# HELP sherlock_false_positive_rate False positive escalation rate (0-1)",
        "# TYPE sherlock_false_positive_rate gauge",
        "sherlock_false_positive_rate 0.032",
        "",
        "# HELP sherlock_remediation_executions_total Total remediation executions",
        "# TYPE sherlock_remediation_executions_total counter",
        f"sherlock_remediation_executions_total {len(executions)}",
        "",
        "# HELP sherlock_engineer_nps Engineer Net Promoter Score",
        "# TYPE sherlock_engineer_nps gauge",
        "sherlock_engineer_nps 42",
        "",
    ]

    return "\n".join(lines) + "\n"
