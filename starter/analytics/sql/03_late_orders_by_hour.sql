-- When do late orders come from? Share of late orders by the hour the order was created.
SELECT EXTRACT(hour FROM CAST(created_ts AS TIMESTAMP)) AS created_hour,
       COUNT(*)                                          AS orders,
       ROUND(100 * (1 - AVG(on_time)), 2)                AS late_pct,
       ROUND(AVG(late_min) FILTER (WHERE on_time = 0), 0) AS avg_late_min
FROM fact_orders
WHERE scenario = 'baseline'
GROUP BY created_hour
ORDER BY created_hour;
