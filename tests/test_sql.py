from pathlib import Path
import sqlite3
import pandas as pd
from service_analytics.analytics import calculate_kpis,grouped_performance
from service_analytics.generate import generate_tickets,SLA_HOURS

def test_sql_matches_python_for_reports():
    tickets=generate_tickets(200,17)
    paths=Path(__file__).resolve().parents[1]/"sql"
    with sqlite3.connect(":memory:") as conn:
        tickets.to_sql("tickets",conn,index=False)
        conn.execute("CREATE TABLE sla_policies (priority TEXT PRIMARY KEY,resolution_target_hours INTEGER)")
        conn.executemany("INSERT INTO sla_policies VALUES (?,?)",SLA_HOURS.items())
        result={p.name:pd.read_sql_query(p.read_text(),conn) for p in sorted(paths.glob("*.sql"))}
    priority=result["01_priority_performance.sql"].rename(columns={"breached":"breaches"})
    expected=grouped_performance(tickets,"priority")
    pd.testing.assert_frame_equal(priority[expected.columns],expected,check_dtype=False)
    joined=result["04_sla_policy_join.sql"]
    assert joined.resolved_tickets.sum()==calculate_kpis(tickets)["tickets_resolved"]
    assert joined.breaches.sum()==calculate_kpis(tickets)["resolved_sla_breaches"]
    team=result["02_team_performance.sql"].rename(columns={"breached":"breaches"}).sort_values("team").reset_index(drop=True)
    expected_team=grouped_performance(tickets,"team")
    pd.testing.assert_frame_equal(team,expected_team[team.columns],check_dtype=False)
    assert result["03_weekly_trend.sql"].tickets.sum()==len(tickets)

def test_no_resolved_tickets():
    tickets=generate_tickets(10,5)
    tickets["status"]="Open"
    tickets["resolution_hours"]=None
    k=calculate_kpis(tickets)
    assert k["resolved_sla_breach_rate_pct"] is None and k["avg_resolution_hours"] is None
    assert k["open_backlog"]==10

def test_at_target_not_breached():
    tickets=generate_tickets(4,3)
    tickets["status"]="Resolved"
    tickets["resolution_hours"]=tickets["allowed_resolution_hours"]
    assert calculate_kpis(tickets)["resolved_sla_breaches"]==0
