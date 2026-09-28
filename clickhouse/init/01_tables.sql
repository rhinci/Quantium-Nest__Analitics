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
    city         LowCardinality(String)
)
ENGINE = MergeTree
ORDER BY customer_id;




CREATE TABLE IF NOT EXISTS quantium.orders
(
    order_id         UInt64,
    customer_id      UInt64,
    created_at       DateTime,
    device_type      LowCardinality(String),
    payment_method   LowCardinality(String),
    delivery_method  LowCardinality(String),
    promo_code       Bool,
    total_price      Decimal(12, 2)
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(created_at)
ORDER BY (created_at, order_id);

CREATE TABLE IF NOT EXISTS quantium.order_items
(
    order_item_id  UInt64,
    order_id       UInt64,
    product_id     UInt32,
    quantity       UInt16,
    unit_price     Decimal(10, 2)
)
ENGINE = MergeTree
ORDER BY (order_id, order_item_id);

CREATE TABLE IF NOT EXISTS quantium.order_status_events
(
    order_id      UInt64,
    event_time    DateTime,
    order_status  LowCardinality(String)
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(event_time)
ORDER BY (event_time, order_id);




CREATE TABLE IF NOT EXISTS quantium.orders_per_minute
(
    minute          DateTime,
    payment_method  LowCardinality(String),
    orders_count    UInt64,
    revenue         Decimal(18, 2)
)
ENGINE = SummingMergeTree
PARTITION BY toYYYYMM(minute)
ORDER BY (minute, payment_method);
