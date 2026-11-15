"""Business KPI calculations for fictional ticket records."""
from __future__ import annotations
import pandas as pd

def calculate_kpis(tickets: pd.DataFrame) -> dict:
    resolved = tickets.loc[tickets.status.eq("Resolved")].copy()
    count = len(resolved)
    breaches = int((resolved.resolution_hours > resolved.allowed_resolution_hours).sum())
    return {
      "tickets_total":len(tickets),
      "tickets_resolved":count,
      "open_backlog":len(tickets)-count,
      "resolved_sla_breaches":breaches,
      "resolved_sla_breach_rate_pct":round(100*breaches/count,2) if count else None,
      "avg_resolution_hours":round(float(resolved.resolution_hours.mean()),2) if count else None,
    }

def grouped_performance(tickets: pd.DataFrame, group: str) -> pd.DataFrame:
    if group not in ("priority","team"):
        raise ValueError("group must be priority or team")
    data=tickets.loc[tickets.status.eq("Resolved")].copy()
    data["breached"]=(data.resolution_hours>data.allowed_resolution_hours).astype(int)
    grouped=data.groupby(group,as_index=False).agg(
        resolved_tickets=("ticket_id","count"),
        breaches=("breached","sum"),
        avg_resolution_hours=("resolution_hours","mean"),
    )
    grouped["breach_rate_pct"]=(100*grouped.breaches/grouped.resolved_tickets).round(2)
    grouped["avg_resolution_hours"]=grouped.avg_resolution_hours.round(2)
    return grouped.sort_values(group).reset_index(drop=True)

def weekly_volume(tickets: pd.DataFrame) -> pd.DataFrame:
    return tickets.groupby("week_start",as_index=False).agg(tickets=("ticket_id","count")).sort_values("week_start")
