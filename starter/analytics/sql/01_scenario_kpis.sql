-- One line per scenario and seed: the KPIs a manager reads first.
-- Compare scenarios with analytics/multiseed.py, which pairs them by seed; a single run is one draw.
SELECT scenario,
       seed,
       COUNT(*)                       AS days,
       ROUND(AVG(orders), 1)          AS orders_per_day,
       ROUND(100 * AVG(on_time), 2)   AS on_time_pct,
       ROUND(100 * AVG(fill_rate), 2) AS fill_rate_pct,
       ROUND(AVG(wages), 0)           AS wages_per_day,
       ROUND(AVG(penalties), 0)       AS penalties_per_day,
       ROUND(AVG(profit), 0)          AS profit_per_day
FROM fact_daily_kpi
GROUP BY scenario, seed
ORDER BY scenario, seed;
