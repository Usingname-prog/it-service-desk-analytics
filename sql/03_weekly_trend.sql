-- Includes both open and resolved tickets
SELECT week_start,COUNT(*) AS tickets FROM tickets GROUP BY week_start ORDER BY week_start;
