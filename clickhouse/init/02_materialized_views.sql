CREATE MATERIALIZED VIEW IF NOT EXISTS quantium.orders_per_minute_mv
TO quantium.orders_per_minute
AS
SELECT
    toStartOfMinute(created_at) AS minute,
    payment_method,
    count()                     AS orders_count,
    sum(total_price)            AS revenue
FROM quantium.orders
GROUP BY minute, payment_method;