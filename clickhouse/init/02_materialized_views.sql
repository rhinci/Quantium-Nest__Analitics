CREATE MATERIALIZED VIEW IF NOT EXISTS quantium.mv_sales_daily
TO quantium.sales_daily
AS
SELECT
    toDate(created_at)       AS day,
    uniqState(order_id)      AS orders_count,
    sum(quantity)            AS items_sold,
    sum(quantity * unit_price) AS revenue
FROM quantium.orders
GROUP BY day;

CREATE MATERIALIZED VIEW IF NOT EXISTS quantium.mv_sales_by_product
TO quantium.sales_by_product
AS
SELECT
    toDate(created_at)         AS day,
    product_id,
    uniqState(order_id)        AS orders_count,
    sum(quantity)               AS quantity_sold,
    sum(quantity * unit_price)  AS revenue
FROM quantium.orders
GROUP BY day, product_id;

CREATE MATERIALIZED VIEW IF NOT EXISTS quantium.mv_customer_stats
TO quantium.customer_stats
AS
SELECT
    customer_id,
    uniqState(order_id)         AS total_orders,
    sum(quantity)                AS total_items,
    sum(quantity * unit_price)   AS total_revenue,
    min(toDate(created_at))      AS first_order_date,
    max(toDate(created_at))      AS last_order_date
FROM quantium.orders
GROUP BY customer_id;