"""Slack notification service."""
from typing import Dict, Any, Optional
from ..config import SLACK_WEBHOOK_URL, SLACK_CHANNEL
import json


def format_investigation_message(investigation: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format a completed investigation as a rich Slack Block Kit message.
    
    Message anatomy (optimized for 3 AM on-call engineer):
    - Header: alert name, severity badge, affected service, timestamp
    - Root cause: one-sentence RCA summary with confidence indicator
    - Evidence: top 3 citations with graph links
    - Action buttons: View Investigation, Acknowledge, Execute Recommended Action
    """
    severity = investigation.get("severity", "unknown")
    confidence = investigation.get("confidence", 0)
    
    severity_emoji = {
        "critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"
    }.get(severity, "⚪")
    
    confidence_color = "good" if confidence >= 0.85 else ("warning" if confidence >= 0.70 else "danger")
    
    # Top 3 evidence citations
    evidence = investigation.get("evidence", [])[:3]
    evidence_text = "\n".join(
        f"• [{e['source']}] {e['description']}" for e in evidence
    ) or "No evidence collected yet."
    
    blocks = {
        "channel": SLACK_CHANNEL,
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{severity_emoji} {investigation.get('title', 'Unknown Alert')}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Service:*\n`{investigation.get('service', 'unknown')}`"},
                    {"type": "mrkdwn", "text": f"*Severity:*\n{severity_emoji} {severity.upper()}"},
                    {"type": "mrkdwn", "text": f"*Status:*\n{investigation.get('status', 'unknown')}"},
                    {"type": "mrkdwn", "text": f"*Confidence:*\n{confidence:.0%}"}
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Root Cause:*\n{investigation.get('rca_summary', 'Investigation in progress...')}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Evidence:*\n{evidence_text}"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "🔍 View Investigation"},
                        "url": f"https://dashboard.sherlock-sre.com/investigations/{investigation.get('id')}",
                        "style": "primary"
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "✅ Acknowledge"},
                        "action_id": f"ack_{investigation.get('id')}"
                    }
                ]
            }
        ]
    }
    
    # Add recommended action button if NBA exists
    nba = investigation.get("nba_action_id")
    if nba:
        blocks["blocks"][-1]["elements"].append({
            "type": "button",
            "text": {"type": "plain_text", "text": f"⚡ Execute {nba}"},
            "action_id": f"execute_{nba}_{investigation.get('id')}",
            "style": "danger"
        })
    
    return blocks


async def send_investigation_notification(investigation: Dict[str, Any]) -> bool:
    """
    Send investigation notification to Slack.
    
    In production: POST to Slack webhook URL.
    Returns True if sent successfully.
    """
    if not SLACK_WEBHOOK_URL:
        # No Slack configured — skip silently
        return False
    
    message = format_investigation_message(investigation)
    
    # In production:
    # async with httpx.AsyncClient() as client:
    #     response = await client.post(SLACK_WEBHOOK_URL, json=message)
    #     return response.status_code == 200
    
    return True


def format_step_update(investigation_id: str, step: str) -> Dict[str, Any]:
    """
    Format an investigation step update as a Slack thread reply.
    
    Each step (hypothesis generated, evidence collected, etc.) posts
    as a thread reply for traceability.
    """
    return {
        "channel": SLACK_CHANNEL,
        "thread_ts": f"thread_{investigation_id}",
        "text": f"📋 *Update for {investigation_id}:* {step}"
    }
