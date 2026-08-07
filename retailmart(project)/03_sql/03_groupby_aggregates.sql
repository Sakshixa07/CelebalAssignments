-- RetailMart | 03 - GROUP BY / Aggregates
-- Business question: "What was last month's revenue?" and how has it trended?

-- Monthly revenue (delivered + shipped orders only, excludes cancelled/returned)
SELECT
    strftime('%Y-%m', order_date) AS month,
    COUNT(*)                       AS num_orders,
    SUM(line_revenue)              AS total_revenue,
    ROUND(AVG(line_revenue), 2)    AS avg_order_value
FROM orders
WHERE order_status IN ('Delivered', 'Shipped')
GROUP BY month
ORDER BY month;

-- Revenue by product category (requires join, previewed here with product_id
-- grouping only; full category breakdown lives in 04_joins.sql)
SELECT
    product_id,
    COUNT(*)          AS num_orders,
    SUM(quantity)      AS units_sold,
    SUM(line_revenue)  AS total_revenue
FROM orders
WHERE order_status IN ('Delivered', 'Shipped')
GROUP BY product_id
ORDER BY total_revenue DESC
LIMIT 10;

-- Order status mix as a percentage of all orders
SELECT
    order_status,
    COUNT(*) AS num_orders,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM orders), 1) AS pct_of_total
FROM orders
GROUP BY order_status
ORDER BY num_orders DESC;

-- HAVING: cities with more than 50 signed-up customers
SELECT city, COUNT(*) AS num_customers
FROM customers
GROUP BY city
HAVING COUNT(*) > 50
ORDER BY num_customers DESC;
