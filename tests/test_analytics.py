from pathlib import Path
import sqlite3
import pandas as pd
import pytest
from service_analytics.generate import generate_tickets,validate_tickets
from service_analytics.analytics import calculate_kpis,grouped_performance
from service_analytics.pipeline import build_dashboard

def test_generator_is_reproducible():
    pd.testing.assert_frame_equal(generate_tickets(40,7),generate_tickets(40,7))

def test_unique_ids_and_valid_resolution():
    data=generate_tickets(100,3)
    assert data.ticket_id.is_unique
    validate_tickets(data)
    assert data.loc[data.status.eq("Open"),"resolution_hours"].isna().all()

def test_kpi_excludes_open():
    data=pd.DataFrame([
      {"ticket_id":"T1","team":"X","priority":"P1","status":"Resolved","resolution_hours":5.0,"allowed_resolution_hours":4},
      {"ticket_id":"T2","team":"X","priority":"P1","status":"Resolved","resolution_hours":3.0,"allowed_resolution_hours":4},
      {"ticket_id":"T3","team":"Y","priority":"P2","status":"Open","resolution_hours":None,"allowed_resolution_hours":8}
    ])
    k=calculate_kpis(data)
    assert k["resolved_sla_breach_rate_pct"]==50.0 and k["open_backlog"]==1
    assert grouped_performance(data,"team").iloc[0].breach_rate_pct==50.0

def test_reject_invalid_count():
    with pytest.raises(ValueError):
        generate_tickets(0)

def test_pipeline_creates_report_and_database(tmp_path:Path):
    s=build_dashboard(35,5,tmp_path)
    assert s["tickets_total"]==35
    assert (tmp_path/"reports/dashboard.html").exists()
    with sqlite3.connect(tmp_path/"reports/service_desk.db") as conn:
        assert conn.execute("SELECT COUNT(*) FROM tickets").fetchone()[0]==35
        assert conn.execute("SELECT COUNT(*) FROM sla_policies").fetchone()[0]==4
