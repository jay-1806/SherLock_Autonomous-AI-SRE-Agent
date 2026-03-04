"""
SherLock SRE Platform — Streamlit Dashboard
A Python-based dashboard for the SherLock autonomous SRE platform.
"""
import sys
import os
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

# ─── Data Layer ───────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from api.src.app.services.mock_data import (
        get_all_investigations,
        get_investigation_by_id,
        get_all_services,
        get_service_by_name,
        get_remediation_catalog,
        get_execution_log,
        get_eval_summary,
        get_feedback,
    )
    DATA_LOADED = True
except ImportError as e:
    DATA_LOADED = False
    IMPORT_ERROR = str(e)

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SherLock | SRE Platform",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

if not DATA_LOADED:
    st.error(f"Could not import mock data: {IMPORT_ERROR}")
    st.info("Make sure you are running from the SherLock/ directory: streamlit run streamlit_app.py")
    st.stop()

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
.status-badge{display:inline-block;padding:2px 10px;border-radius:12px;font-size:12px;font-weight:600;}
.status-open{background:rgba(245,158,11,.15);color:#f59e0b;border:1px solid rgba(245,158,11,.3);}
.status-in_progress{background:rgba(59,130,246,.15);color:#3b82f6;border:1px solid rgba(59,130,246,.3);}
.status-resolved{background:rgba(16,185,129,.15);color:#10b981;border:1px solid rgba(16,185,129,.3);}
.status-closed{background:rgba(107,114,128,.15);color:#6b7280;border:1px solid rgba(107,114,128,.3);}
.sev-low{background:rgba(107,114,128,.15);color:#9ca3af;}
.sev-medium{background:rgba(234,179,8,.15);color:#eab308;}
.sev-high{background:rgba(249,115,22,.15);color:#f97316;}
.sev-critical{background:rgba(239,68,68,.15);color:#ef4444;}
</style>
""", unsafe_allow_html=True)

# ─── Helpers ──────────────────────────────────────────────────────────────────

def status_badge(status):
    label = status.replace("_", " ").title()
    return f'<span class="status-badge status-{status}">{label}</span>'

def sev_badge(sev):
    icons = {"low": "○", "medium": "◑", "high": "◉", "critical": "●"}
    icon = icons.get(sev, "•")
    return f'<span class="status-badge sev-{sev}">{icon} {sev.upper()}</span>'

def fmt_dt(dt_str):
    if not dt_str:
        return "—"
    try:
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        return dt.strftime("%b %d, %H:%M UTC")
    except Exception:
        return dt_str

def confidence_bar(conf):
    if conf is None:
        return "—"
    pct = int(conf * 100)
    color = "#10b981" if pct >= 85 else "#f59e0b" if pct >= 70 else "#ef4444"
    return (
        '<div style="display:flex;align-items:center;gap:8px;">'
        '<div style="width:80px;height:6px;background:#374151;border-radius:3px;overflow:hidden;">'
        f'<div style="width:{pct}%;height:100%;background:{color};border-radius:3px;"></div></div>'
        f'<span style="font-size:12px;color:#9ca3af;">{pct}%</span></div>'
    )

def sparkline(data, color="#3b82f6"):
    bar_colors = [color if i == len(data) - 1 else color + "80" for i in range(len(data))]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=list(range(len(data))), y=data, marker_color=bar_colors))
    fig.update_layout(
        height=50, margin=dict(l=0, r=0, t=0, b=0), showlegend=False,
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig

# ─── Sidebar Navigation ───────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🔍 SherLock")
    st.markdown("*Autonomous SRE Platform*")
    st.divider()
    page = st.radio(
        "Navigation",
        ["Incident Feed", "Services Health", "KPI Dashboard", "Remediation Catalog", "Feedback"],
        index=0,
        label_visibility="collapsed",
    )
    st.divider()
    st.caption("SherLock v0.1.0 — Part 2")

# ─── Page: Incident Feed ──────────────────────────────────────────────────────

if page == "Incident Feed":
    st.title("Incident Feed")
    st.caption("Active and recent investigations")

    investigations = get_all_investigations()
    active = [i for i in investigations if i["status"] in ("open", "in_progress")]
    critical_inv = [i for i in investigations if i["severity"] == "critical"]
    resolved = [i for i in investigations if i["status"] in ("resolved", "closed")]
    avg_conf = (
        sum(i.get("confidence") or 0 for i in investigations) / len(investigations)
        if investigations else 0
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Active", len(active))
    c2.metric("Critical", len(critical_inv))
    c3.metric("Resolved / Closed", len(resolved))
    c4.metric("Avg Confidence", f"{int(avg_conf * 100)}%")
    st.divider()

    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        filter_status = st.selectbox("Status", ["All", "open", "in_progress", "resolved", "closed"])
    with col_f2:
        filter_sev = st.selectbox("Severity", ["All", "critical", "high", "medium", "low"])
    with col_f3:
        svcs = sorted({i["service"] for i in investigations})
        filter_svc = st.selectbox("Service", ["All"] + svcs)

    filtered = investigations
    if filter_status != "All":
        filtered = [i for i in filtered if i["status"] == filter_status]
    if filter_sev != "All":
        filtered = [i for i in filtered if i["severity"] == filter_sev]
    if filter_svc != "All":
        filtered = [i for i in filtered if i["service"] == filter_svc]

    st.caption(f"Showing {len(filtered)} investigations")

    sev_icon_map = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "⚪"}
    for inv in filtered:
        is_active = inv["status"] in ("open", "in_progress")
        icon = sev_icon_map.get(inv["severity"], "•")
        with st.expander(
            f"{icon} [{inv['id'].upper()}] {inv['title']}",
            expanded=is_active,
        ):
            col_a, col_b = st.columns([2, 1])
            with col_a:
                st.markdown(
                    f"{status_badge(inv['status'])} &nbsp; {sev_badge(inv['severity'])}",
                    unsafe_allow_html=True,
                )
                if inv.get("rca_summary"):
                    st.markdown(f"> {inv['rca_summary']}")
                st.caption(f"Service: `{inv['service']}` | Created: {fmt_dt(inv.get('created_at'))}")
            with col_b:
                if inv.get("confidence") is not None:
                    st.markdown(
                        f"**Confidence**<br>{confidence_bar(inv['confidence'])}",
                        unsafe_allow_html=True,
                    )

            full = get_investigation_by_id(inv["id"])
            if full:
                tab1, tab2, tab3 = st.tabs(["Hypotheses", "Evidence", "Timeline"])
                with tab1:
                    for h in (full.get("hypotheses") or []):
                        h_pct = int((h.get("confidence") or 0) * 100)
                        if h["status"] == "confirmed":
                            st.markdown(f":green[✓] **{h['hypothesis']}** — {h_pct}% confidence")
                        elif h["status"] == "rejected":
                            st.markdown(f":red[✗] **{h['hypothesis']}** — {h_pct}% confidence")
                        else:
                            st.markdown(f":blue[?] **{h['hypothesis']}** — {h_pct}% confidence")
                with tab2:
                    for e in (full.get("evidence") or []):
                        st.markdown(f"- **[{e['type'].upper()}]** `{e['source']}` — {e['description']}")
                with tab3:
                    for t in (full.get("timeline") or []):
                        st.markdown(f"- `{fmt_dt(t['timestamp'])}` **{t['source'].upper()}** — {t['event']}")

# ─── Page: Services Health ────────────────────────────────────────────────────

elif page == "Services Health":
    st.title("Services Health")
    st.caption("Production service status and health scores")

    services = get_all_services()
    healthy_svcs = [s for s in services if s["status"] == "healthy"]
    degraded_svcs = [s for s in services if s["status"] == "degraded"]
    critical_svcs = [s for s in services if s["status"] == "critical"]

    c1, c2, c3 = st.columns(3)
    c1.metric("Healthy", len(healthy_svcs))
    c2.metric("Degraded", len(degraded_svcs))
    c3.metric("Critical", len(critical_svcs))
    st.divider()

    names = [s["display_name"] for s in services]
    scores = [s["health_score"] for s in services]
    bar_colors = [
        "#ef4444" if s <= 50 else "#f59e0b" if s <= 80 else "#10b981"
        for s in scores
    ]
    fig = go.Figure(go.Bar(
        x=names, y=scores, marker_color=bar_colors, text=scores, textposition="outside",
    ))
    fig.add_hline(y=80, line_dash="dot", line_color="#f59e0b", annotation_text="Degraded threshold")
    fig.add_hline(y=50, line_dash="dot", line_color="#ef4444", annotation_text="Critical threshold")
    fig.update_layout(
        title="Service Health Scores",
        yaxis=dict(range=[0, 115], title="Health Score"),
        height=350,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#9ca3af"),
        yaxis_gridcolor="#2d2d3d",
    )
    st.plotly_chart(fig, use_container_width=True)
    st.divider()

    svc_icon_map = {"healthy": "🟢", "degraded": "🟠", "critical": "🔴"}
    for svc in services:
        icon = svc_icon_map.get(svc["status"], "⚪")
        with st.expander(f"{icon} {svc['display_name']} — Health: {svc['health_score']}/100"):
            col1, col2, col3 = st.columns(3)
            col1.write(f"**Status:** {svc['status'].upper()}")
            col1.write(f"**Team:** {svc['team']}")
            col2.write(f"**SLA Tier:** {svc['sla_tier']}")
            col2.write(f"**Active Incidents:** {svc['active_incidents']}")
            col3.write(f"**Last Deploy:** {fmt_dt(svc.get('last_deployment'))}")

            full = get_service_by_name(svc["name"])
            if full and full.get("dependencies"):
                st.write(f"**Dependencies:** {', '.join(f'`{d}`' for d in full['dependencies'])}")
            if full and full.get("incident_history"):
                st.write("**Recent Incidents:**")
                for ih in full["incident_history"]:
                    sev_i = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "⚪"}.get(ih["severity"], "•")
                    st.caption(f"{sev_i} `{ih['date']}` **{ih['title']}** — {ih['root_cause']}")

# ─── Page: KPI Dashboard ──────────────────────────────────────────────────────

elif page == "KPI Dashboard":
    st.title("KPI Dashboard")
    data = get_eval_summary()
    st.caption(f"Platform performance metrics • {data['period']} • Updated {fmt_dt(data['last_updated'])}")
    st.divider()

    spark_colors = {
        "Mean Time to Root Cause (MTTRC)": "#3b82f6",
        "Investigation Accuracy Rate": "#10b981",
        "Autonomous Coverage": "#a855f7",
        "Alert-to-Investigation Latency": "#06b6d4",
        "On-Call Toil Reduction": "#f59e0b",
        "Auto-Remediation Success Rate": "#10b981",
        "False Positive Escalation Rate": "#ef4444",
        "Engineer NPS": "#ec4899",
    }

    kpis = data["kpis"]
    for row_start in range(0, len(kpis), 4):
        cols = st.columns(4)
        for col, kpi in zip(cols, kpis[row_start:row_start + 4]):
            with col:
                st.metric(label=kpi["name"], value=kpi["value"], delta=kpi["change"].strip())
                hist = kpi.get("history", [])
                if hist:
                    color = spark_colors.get(kpi["name"], "#3b82f6")
                    st.plotly_chart(
                        sparkline(hist, color),
                        use_container_width=True,
                        config={"displayModeBar": False},
                    )
                st.caption(f"Target: {kpi['target']}")
                ok = kpi["status"] == "on_track"
                st.caption(f":{'green' if ok else 'red'}[{'✓ On Track' if ok else kpi['status']}]")

    st.divider()
    st.subheader("Summary Statistics (30 days)")
    stats = data["summary_stats"]
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Investigations", stats["total_investigations_30d"])
    auto_pct = int(stats["auto_triggered"] / stats["total_investigations_30d"] * 100)
    c2.metric("Auto-Triggered", f"{stats['auto_triggered']} ({auto_pct}%)")
    c3.metric("Manual Triggered", stats["manual_triggered"])
    c4.metric("Avg Confidence", f"{int(stats['avg_confidence'] * 100)}%")
    c5.metric("Remediations (S/T)", f"{stats['successful_remediations']}/{stats['total_remediations']}")

    st.divider()
    st.subheader("Top Recurring Root Causes")
    causes = stats["top_recurring_causes"]
    fig = go.Figure(go.Bar(
        x=[c["count"] for c in causes],
        y=[c["cause"] for c in causes],
        orientation="h",
        marker_color="#3b82f6",
        text=[c["count"] for c in causes],
        textposition="outside",
    ))
    fig.update_layout(
        height=250,
        margin=dict(l=0, r=40, t=0, b=0),
        xaxis=dict(title="Occurrences"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#9ca3af"),
        xaxis_gridcolor="#2d2d3d",
    )
    st.plotly_chart(fig, use_container_width=True)

# ─── Page: Remediation Catalog ────────────────────────────────────────────────

elif page == "Remediation Catalog":
    st.title("Remediation Catalog")
    st.caption("Autonomous remediation actions and execution history")

    catalog = get_remediation_catalog()
    exec_log = get_execution_log()

    categories = sorted({a["category"] for a in catalog})
    filter_cat = st.selectbox("Filter by Category", ["All"] + categories)
    if filter_cat != "All":
        catalog = [a for a in catalog if a["category"] == filter_cat]

    st.caption(f"{len(catalog)} actions")
    st.divider()

    risk_color = {"low": "green", "medium": "orange", "high": "red"}
    for action in catalog:
        rc = risk_color.get(action["risk_level"], "gray")
        mfa = " 🔐" if action["requires_mfa"] else ""
        sr = (
            f"{int((action['success_rate'] or 0) * 100)}%"
            if action.get("success_rate") is not None
            else "—"
        )
        with st.expander(
            f"[{action['action_id']}] {action['name']} — :{rc}[{action['risk_level'].upper()} RISK]{mfa}"
        ):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(action["description"])
                st.caption(f"**Trigger:** {action['trigger_condition']}")
                st.caption(f"**Rollback:** {action['rollback_procedure']}")
            with col2:
                st.metric("Executions", action["execution_count"])
                st.metric("Success Rate", sr)
                st.caption(f"Duration: {action['estimated_duration']}")
                if action.get("last_executed"):
                    st.caption(f"Last run: {fmt_dt(action['last_executed'])}")

    st.divider()
    st.subheader("Execution Log")
    if exec_log:
        for entry in exec_log:
            icon = "✅" if entry["status"] == "success" else "❌"
            with st.expander(
                f"{icon} [{entry['execution_id']}] {entry['action_name']} — {fmt_dt(entry['executed_at'])}"
            ):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Investigation:** `{entry['investigation_id']}`")
                    st.write(f"**Triggered by:** {entry['triggered_by']}")
                    st.write(f"**Duration:** {entry['duration_seconds']}s")
                with col2:
                    st.write(f"**Pre-state:** {entry['pre_state']}")
                    st.write(f"**Post-state:** {entry['post_state']}")
    else:
        st.info("No executions recorded.")

# ─── Page: Feedback ───────────────────────────────────────────────────────────

elif page == "Feedback":
    st.title("Engineer Feedback")
    st.caption("SRE team ratings on investigation accuracy")

    feedback = get_feedback()
    counts = {"correct": 0, "partially_correct": 0, "incorrect": 0}
    for f in feedback:
        counts[f["rating"]] = counts.get(f["rating"], 0) + 1

    c1, c2, c3 = st.columns(3)
    c1.metric("Correct", counts["correct"])
    c2.metric("Partially Correct", counts["partially_correct"])
    c3.metric("Incorrect", counts.get("incorrect", 0))

    if feedback:
        fig = go.Figure(go.Pie(
            labels=["Correct", "Partially Correct", "Incorrect"],
            values=[counts["correct"], counts["partially_correct"], counts.get("incorrect", 0)],
            hole=0.45,
            marker_colors=["#10b981", "#f59e0b", "#ef4444"],
        ))
        fig.update_layout(
            height=260,
            margin=dict(l=0, r=0, t=20, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#9ca3af"),
            legend=dict(orientation="h", yanchor="bottom", y=-0.2),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.divider()
    st.subheader("Feedback Entries")
    icons = {"correct": "✅", "partially_correct": "⚠️", "incorrect": "❌"}
    for fb in feedback:
        icon = icons.get(fb["rating"], "•")
        st.markdown(
            f"{icon} **Investigation `{fb['investigation_id']}`** — *\"{fb.get('comment', '')}\"*"
        )
        st.caption(f"  By: {fb['submitted_by']} | {fmt_dt(fb['submitted_at'])}")
