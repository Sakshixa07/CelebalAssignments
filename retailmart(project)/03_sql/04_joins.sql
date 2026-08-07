-- RetailMart | 04 - JOINs
-- Business question: build a "Customer 360" unified view - who is this
-- customer, what have they bought, and how much have they paid us?

-- Customer 360: one row per order, enriched with customer + product + payment info
SELECT
    c.customer_id,
    c.customer_name,
    c.city,
    o.order_id,
    o.order_date,
    p.product_name,
    p.category,
    o.quantity,
    o.line_revenue,
    o.order_status,
    pay.payment_method,
    pay.payment_status
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN products  p ON o.product_id  = p.product_id
LEFT JOIN payments pay ON o.order_id = pay.order_id
ORDER BY o.order_date DESC
LIMIT 15;

-- Revenue by category (needs the products join to get category)
SELECT
    p.category,
    COUNT(*)             AS num_orders,
    SUM(o.line_revenue)  AS total_revenue
FROM orders o
JOIN products p ON o.product_id = p.product_id
WHERE o.order_status IN ('Delivered', 'Shipped')
GROUP BY p.category
ORDER BY total_revenue DESC;

-- Per-customer lifetime summary (total orders, total spend, favourite category)
SELECT
    c.customer_id,
    c.customer_name,
    c.city,
    COUNT(o.order_id)         AS total_orders,
    SUM(o.line_revenue)       AS lifetime_spend,
    ROUND(AVG(o.line_revenue), 2) AS avg_order_value
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_status IN ('Delivered', 'Shipped')
GROUP BY c.customer_id, c.customer_name, c.city
ORDER BY lifetime_spend DESC
LIMIT 10;

-- Orders that never received a payment record (LEFT JOIN + IS NULL anti-join pattern)
SELECT o.order_id, o.customer_id, o.order_date, o.order_status
FROM orders o
LEFT JOIN payments pay ON o.order_id = pay.order_id
WHERE pay.payment_id IS NULL;
