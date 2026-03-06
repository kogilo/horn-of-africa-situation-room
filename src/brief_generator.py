from __future__ import annotations
import pandas as pd

def generate_weekly_brief(
    week_end: pd.Timestamp,
    risk_table: pd.DataFrame,
    incidents: pd.DataFrame,
    forecast: pd.DataFrame,
) -> str:
    top = risk_table.head(10).copy()
    total_incidents = len(incidents)
    recent_7d = incidents[incidents["event_date"] >= (week_end - pd.Timedelta(days=7))]
    recent_30d = incidents[incidents["event_date"] >= (week_end - pd.Timedelta(days=30))]

    brief = []
    brief.append(f"# Weekly Situation Brief — Horn of Africa")
    brief.append(f"**Week ending:** {week_end.date()}")
    brief.append("")
    brief.append("## Executive Summary")
    brief.append(f"- Total incidents in dataset: **{total_incidents}**")
    brief.append(f"- Incidents last 7 days: **{len(recent_7d)}**")
    brief.append(f"- Incidents last 30 days: **{len(recent_30d)}**")
    brief.append("")
    brief.append("## Top Risk Areas (Region-level)")
    brief.append("")
    brief.append("| Rank | Country | Region | Risk Level | Score (0–100) | Incidents | Avg Severity | Last Event |")
    brief.append("|---:|---|---|---|---:|---:|---:|---|")
    for i, row in enumerate(top.itertuples(index=False), start=1):
        brief.append(
            f"| {i} | {row.country} | {row.region} | {row.risk_level} | {row.risk_score_0_100:.1f} | "
            f"{int(row.incident_count)} | {row.avg_severity:.2f} | {pd.to_datetime(row.last_event).date()} |"
        )
    brief.append("")
    brief.append("## Displacement Outlook (Baseline Forecast)")
    if forecast is None or forecast.empty:
        brief.append("- Forecast not available (insufficient data).")
    else:
        fsum = forecast.groupby("month")["net_flow_forecast"].sum().reset_index()
        next3 = fsum.head(3)
        brief.append("- Projected net displacement (next 3 months, total across regions):")
        for r in next3.itertuples(index=False):
            brief.append(f"  - {pd.to_datetime(r.month).strftime('%Y-%m')}: **{int(r.net_flow_forecast):,}**")
    brief.append("")
    brief.append("## Analyst Notes (Fill-in)")
    brief.append("- Key drivers (security, politics, economy, climate):")
    brief.append("- Diplomatic engagement opportunities / risks:")
    brief.append("- Recommended actions (7–14 days):")
    brief.append("")
    return "\n".join(brief)