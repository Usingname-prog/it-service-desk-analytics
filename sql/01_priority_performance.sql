-- SLA breach rate among resolved tickets only
WITH resolved AS (
 SELECT priority,resolution_hours,allowed_resolution_hours FROM tickets WHERE status='Resolved'
)
SELECT priority,COUNT(*) AS resolved_tickets,
 SUM(CASE WHEN resolution_hours>allowed_resolution_hours THEN 1 ELSE 0 END) AS breached,
 ROUND(100.0*SUM(CASE WHEN resolution_hours>allowed_resolution_hours THEN 1 ELSE 0 END)/COUNT(*),2) AS breach_rate_pct,
 ROUND(AVG(resolution_hours),2) AS avg_resolution_hours
FROM resolved GROUP BY priority ORDER BY priority;
