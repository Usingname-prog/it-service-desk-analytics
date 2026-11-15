-- Fictional support team SLA performance
SELECT team, COUNT(*) AS resolved_tickets,
 SUM(CASE WHEN resolution_hours>allowed_resolution_hours THEN 1 ELSE 0 END) AS breached,
 ROUND(100.0*SUM(CASE WHEN resolution_hours>allowed_resolution_hours THEN 1 ELSE 0 END)/COUNT(*),2) AS breach_rate_pct
FROM tickets WHERE status='Resolved' GROUP BY team ORDER BY breach_rate_pct DESC;
