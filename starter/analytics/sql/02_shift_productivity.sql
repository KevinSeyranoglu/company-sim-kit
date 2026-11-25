-- Hours, output and cost per shift (baseline runs). A shift with many hours and little output is
-- the first place to look for a staffing finding.
SELECT shift,
       ROUND(SUM(hours), 0)                                AS hours,
       SUM(units_done)                                     AS units,
       ROUND(SUM(units_done) / NULLIF(SUM(hours), 0), 1)   AS units_per_hour,
       ROUND(100.0 * SUM(units_done) / SUM(SUM(units_done)) OVER (), 1) AS share_of_units_pct,
       ROUND(SUM(wage_cost), 0)                            AS wage_cost
FROM fact_labor
WHERE scenario = 'baseline' AND absent = 0
GROUP BY shift
ORDER BY hours DESC;
