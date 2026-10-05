CREATE TABLE IF NOT EXISTS quantium.brands
(
    brand_id           UInt32,
    brand_name         String,
    country_of_origin  String
)
ENGINE = MergeTree
ORDER BY brand_id;

CREATE TABLE IF NOT EXISTS quantium.categories
(
    category_id         UInt32,
    category_name       String,
    parent_category_id  Nullable(UInt32)
)
ENGINE = MergeTree
ORDER BY category_id;

CREATE TABLE IF NOT EXISTS quantium.products
(
    product_id    UInt32,
    product_name  String,
    price         Decimal(10, 2),
    category_id   UInt32,
    brand_id      UInt32
)
ENGINE = MergeTree
ORDER BY product_id;

CREATE TABLE IF NOT EXISTS quantium.customers
(
    customer_id  UInt64,
    full_name    String,
    email        String,
    city_id         UInt32
)
ENGINE = MergeTree
ORDER BY customer_id;


CREATE TABLE IF NOT EXISTS quantium.cities
(
    city_id    UInt32,
    city_name  String
)
ENGINE = MergeTree
ORDER BY city_id;

CREATE TABLE IF NOT EXISTS quantium.orders
(
    order_id         UInt64,
    order_item_id    UInt64,
    created_at       DateTime,
    customer_id      UInt64,
    device_type      LowCardinality(String),
    payment_method   LowCardinality(String),
    delivery_method  LowCardinality(String),
    promo_code       Bool,
    product_id       UInt32,
    quantity         UInt16,
    unit_price       Decimal(10, 2)
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(created_at)
ORDER BY (created_at, order_id);




CREATE TABLE IF NOT EXISTS quantium.sales_daily
(
    day           Date,
    orders_count  AggregateFunction(uniq, UInt64),
    items_sold    SimpleAggregateFunction(sum, UInt64),
    revenue       SimpleAggregateFunction(sum, Decimal(38, 2))
)
ENGINE = AggregatingMergeTree
PARTITION BY toYYYYMM(day)
ORDER BY day;

CREATE TABLE IF NOT EXISTS quantium.sales_by_product
(
    day            Date,
    product_id     UInt32,
    orders_count   AggregateFunction(uniq, UInt64),
    quantity_sold  SimpleAggregateFunction(sum, UInt64),
    revenue        SimpleAggregateFunction(sum, Decimal(38, 2))
)
ENGINE = AggregatingMergeTree
PARTITION BY toYYYYMM(day)
ORDER BY (product_id, day);

CREATE TABLE IF NOT EXISTS quantium.customer_stats
(
    customer_id       UInt64,
    total_orders      AggregateFunction(uniq, UInt64),
    total_items       SimpleAggregateFunction(sum, UInt64),
    total_revenue     SimpleAggregateFunction(sum, Decimal(38, 2)),
    first_order_date  SimpleAggregateFunction(min, Date),
    last_order_date   SimpleAggregateFunction(max, Date)
)
ENGINE = AggregatingMergeTree
ORDER BY customer_id;