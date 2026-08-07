-- RetailMart | 05 - CASE
-- Business question: segment customers by spend so marketing can target
-- them differently (VIP retention vs. new-customer activation, etc.)

WITH customer_spend AS (
    SELECT
        c.customer_id,
        c.customer_name,
        SUM(o.line_revenue) AS lifetime_spend,
        COUNT(o.order_id)    AS total_orders
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    WHERE o.order_status IN ('Delivered', 'Shipped')
    GROUP BY c.customer_id, c.customer_name
)
SELECT
    customer_id,
    customer_name,
    lifetime_spend,
    total_orders,
    CASE
        WHEN lifetime_spend >= 50000 THEN 'VIP'
        WHEN lifetime_spend >= 15000 THEN 'High Value'
        WHEN lifetime_spend >= 5000  THEN 'Regular'
        ELSE 'Low Value'
    END AS customer_segment
FROM customer_spend
ORDER BY lifetime_spend DESC
LIMIT 20;

-- Segment counts (how many customers fall into each bucket)
WITH customer_spend AS (
    SELECT c.customer_id, SUM(o.line_revenue) AS lifetime_spend
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    WHERE o.order_status IN ('Delivered', 'Shipped')
    GROUP BY c.customer_id
),
segmented AS (
    SELECT
        customer_id,
        CASE
            WHEN lifetime_spend >= 50000 THEN 'VIP'
            WHEN lifetime_spend >= 15000 THEN 'High Value'
            WHEN lifetime_spend >= 5000  THEN 'Regular'
            ELSE 'Low Value'
        END AS customer_segment
    FROM customer_spend
)
SELECT customer_segment, COUNT(*) AS num_customers
FROM segmented
GROUP BY customer_segment
ORDER BY num_customers DESC;

-- Order-level CASE: flag late deliveries
SELECT
    order_id,
    delivery_days,
    CASE
        WHEN delivery_days IS NULL THEN 'Unknown'
        WHEN delivery_days <= 3 THEN 'Fast'
        WHEN delivery_days <= 7 THEN 'Normal'
        ELSE 'Slow'
    END AS delivery_speed
FROM orders
WHERE order_status = 'Delivered'
LIMIT 15;
