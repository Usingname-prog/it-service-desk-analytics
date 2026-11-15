"""Generate fictional IT tickets, load SQLite and produce a static dashboard."""
from __future__ import annotations
import argparse
import html
import json
from pathlib import Path
import sqlite3

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .generate import generate_tickets
from .analytics import calculate_kpis, grouped_performance, weekly_volume

ROOT=Path(__file__).resolve().parents[1]

def build_dashboard(count:int=1500,seed:int=42,root:Path=ROOT)->dict:
    data_dir=root/"data"
    reports=root/"reports"
    data_dir.mkdir(parents=True,exist_ok=True)
    reports.mkdir(parents=True,exist_ok=True)
    tickets=generate_tickets(count,seed)
    tickets.to_csv(data_dir/"tickets.csv",index=False)
    db_path=reports/"service_desk.db"
    with sqlite3.connect(db_path) as conn:
        tickets.to_sql("tickets",conn,if_exists="replace",index=False)
        conn.execute("CREATE TABLE IF NOT EXISTS sla_policies (priority TEXT PRIMARY KEY,resolution_target_hours INTEGER NOT NULL)")
        conn.execute("DELETE FROM sla_policies")
        conn.executemany("INSERT INTO sla_policies VALUES (?,?)",[("P1",4),("P2",8),("P3",24),("P4",72)])
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_ticket_id ON tickets(ticket_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_priority_team ON tickets(priority,team)")
    summary=calculate_kpis(tickets)
    by_priority=grouped_performance(tickets,"priority")
    by_team=grouped_performance(tickets,"team")
    by_week=weekly_volume(tickets)
    (reports/"kpis.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    for name,frame in (("by_priority",by_priority),("by_team",by_team),("by_week",by_week)):
        frame.to_csv(reports/(name+".csv"),index=False)
    fig,ax=plt.subplots(figsize=(7,3.5))
    ax.bar(by_priority.priority,by_priority.breach_rate_pct)
    ax.set_title("Resolved SLA breach rate by priority")
    ax.set_ylabel("Breach rate (%)")
    ax.set_ylim(0,max(30,float(by_priority.breach_rate_pct.max())*1.2))
    fig.tight_layout()
    fig.savefig(reports/"sla_by_priority.png",dpi=140)
    plt.close(fig)
    fig,ax=plt.subplots(figsize=(8,3.5))
    ax.plot(by_week.week_start,by_week.tickets,marker="o",markersize=3)
    ax.set_title("Synthetic ticket volume by week")
    ax.set_ylabel("Ticket count")
    positions=list(range(0,len(by_week),max(1,len(by_week)//6)))
    ax.set_xticks(positions)
    ax.set_xticklabels(by_week.iloc[positions].week_start,rotation=25,ha="right")
    fig.tight_layout()
    fig.savefig(reports/"ticket_volume.png",dpi=140)
    plt.close(fig)
    cards="".join(f'<article class="card"><small>{html.escape(k.replace("_"," ").title())}</small><strong>{v if v is not None else "N/A"}</strong></article>' for k,v in summary.items())
    rows="".join("<tr><td>"+html.escape(str(r.team))+"</td><td>"+str(r.resolved_tickets)+"</td><td>"+str(r.breaches)+"</td><td>"+str(r.breach_rate_pct)+"%</td></tr>" for r in by_team.itertuples(index=False))
    page=f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>IT Service Desk — Synthetic Demo</title>
<style>body{{font:16px/1.5 system-ui,sans-serif;max-width:1100px;margin:32px auto;padding:0 20px;color:#19273c;background:#f5f7fa}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px}}.card,.panel{{background:white;border:1px solid #dce2ea;border-radius:12px;padding:18px}}.card small{{display:block;color:#596579}}.card strong{{display:block;font-size:1.7rem}}.charts{{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:22px 0}}img{{max-width:100%}}td,th{{text-align:left;padding:8px;border-bottom:1px solid #ddd}}@media(max-width:800px){{.charts{{grid-template-columns:1fr}}}}</style></head>
<body><h1>IT Service Desk Analytics</h1><p>Fictional tickets — illustrative SLA targets, not real company performance.</p><section class="cards">{cards}</section><div class="charts"><div class="panel"><img alt="Breach rates" src="sla_by_priority.png"></div><div class="panel"><img alt="Weekly volume" src="ticket_volume.png"></div></div><h2>Resolved tickets by team</h2><div class="panel"><table><thead><tr><th>Team</th><th>Resolved</th><th>Breaches</th><th>Rate</th></tr></thead><tbody>{rows}</tbody></table></div><p>Open tickets are excluded from the SLA breach denominator. Synthetic data only.</p></body></html>"""
    (reports/"dashboard.html").write_text(page,encoding="utf-8")
    return summary

def main()->None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--tickets",type=int,default=1500)
    parser.add_argument("--seed",type=int,default=42)
    args=parser.parse_args()
    result=build_dashboard(args.tickets,args.seed)
    print(json.dumps(result,indent=2))
    print("Dashboard created at reports/dashboard.html")

if __name__=="__main__":
    main()
