"""Reproducible fictional service desk ticket generator."""
from __future__ import annotations
from datetime import datetime, timedelta
import random
import pandas as pd

SLA_HOURS = {"P1": 4, "P2": 8, "P3": 24, "P4": 72}
TEAMS = ("Workplace IT", "Applications", "Network", "Identity & Access")
CATEGORIES = ("Access request", "Software", "Connectivity", "Device", "Incident")
CHANNELS = ("Portal", "Email", "Phone")

def generate_tickets(count: int = 1500, seed: int = 42) -> pd.DataFrame:
    if count <= 0:
        raise ValueError("count must be greater than zero")
    rng = random.Random(seed)
    start = datetime(2026, 1, 1, 8, 0)
    records = []
    for number in range(1, count + 1):
        priority = rng.choices(["P1", "P2", "P3", "P4"], weights=[6,18,48,28])[0]
        team = rng.choice(TEAMS)
        opened = start + timedelta(hours=rng.randint(0, 24*90))
        resolved = rng.random() >= 0.09
        sla = SLA_HOURS[priority]
        team_factor = {"Workplace IT":0.72,"Applications":1.15,"Network":1.36,"Identity & Access":0.92}[team]
        resolution = round(max(0.1, rng.lognormvariate(0.0,0.65)*sla*0.65*team_factor),2) if resolved else None
        records.append({
            "ticket_id":f"INC-{number:05d}","opened_at":opened.isoformat(timespec="seconds"),
            "week_start":(opened-timedelta(days=opened.weekday())).date().isoformat(),
            "priority":priority,"team":team,"category":rng.choice(CATEGORIES),
            "channel":rng.choice(CHANNELS),"status":"Resolved" if resolved else "Open",
            "resolution_hours":resolution,"allowed_resolution_hours":sla
        })
    result = pd.DataFrame(records)
    validate_tickets(result)
    return result

def validate_tickets(frame: pd.DataFrame) -> None:
    required = {"ticket_id","opened_at","week_start","priority","team","category","channel","status","resolution_hours","allowed_resolution_hours"}
    if not required.issubset(frame.columns):
        raise ValueError("missing required columns")
    if frame.empty or frame.ticket_id.isna().any() or frame.ticket_id.duplicated().any():
        raise ValueError("ticket IDs must be unique")
    if not frame.priority.isin(SLA_HOURS).all() or not frame.status.isin(["Resolved","Open"]).all():
        raise ValueError("invalid priority or status")
    if frame.loc[frame.status.eq("Resolved"),"resolution_hours"].isna().any():
        raise ValueError("resolved tickets require resolution time")
    if frame.loc[frame.status.eq("Open"),"resolution_hours"].notna().any():
        raise ValueError("open tickets must not have resolution time")
    if (frame.loc[frame.status.eq("Resolved"),"resolution_hours"]<0).any():
        raise ValueError("resolution time must be nonnegative")
    if any(int(r.allowed_resolution_hours)!=SLA_HOURS[r.priority] for r in frame.itertuples(index=False)):
        raise ValueError("priority SLA mismatch")
