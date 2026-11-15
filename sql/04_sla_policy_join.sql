-- JOIN tickets to separately stored SLA policies, then group by priority
SELECT p.priority,p.resolution_target_hours,
 COUNT(t.ticket_id) AS resolved_tickets,
 SUM(CASE WHEN t.resolution_hours>p.resolution_target_hours THEN 1 ELSE 0 END) AS breaches,
 ROUND(100.0*SUM(CASE WHEN t.resolution_hours>p.resolution_target_hours THEN 1 ELSE 0 END)/COUNT(t.ticket_id),2) AS breach_rate_pct
FROM sla_policies p JOIN tickets t ON t.priority=p.priority
WHERE t.status='Resolved'
GROUP BY p.priority,p.resolution_target_hours ORDER BY p.priority;
