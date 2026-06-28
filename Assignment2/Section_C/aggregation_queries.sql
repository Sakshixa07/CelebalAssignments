-- =====================================================================
-- SECTION C: AGGREGATION (GROUP BY, SUM, COUNT, AVG, MIN, MAX)
-- =====================================================================
-- These questions test your ability to summarize and aggregate data.
-- =====================================================================

-- ===================================================================
-- Q13. Count the total number of orders in the orders table
-- ===================================================================
-- Solution:
SELECT COUNT(*) AS total_orders FROM orders;

-- Explanation: COUNT(*) counts all rows in the table.
-- Expected result: 10 orders

-- Alternative using COUNT(column):
SELECT COUNT(order_id) AS total_orders FROM orders;

-- Note: COUNT(*) and COUNT(order_id) give same result since order_id
-- is PRIMARY KEY (NOT NULL). For columns with NULLs, COUNT(column)
-- ignores NULLs while COUNT(*) counts them.

-- ===================================================================
-- Q14. Total revenue from all 'Delivered' orders
-- ===================================================================
-- Solution:
SELECT SUM(total_amount) AS total_delivered_revenue
FROM orders
WHERE status = 'Delivered';

-- Explanation: 
-- - SUM() adds up all values in the column
-- - WHERE filters to only Delivered orders
-- - Expected result: ₹16,193 (4498 + 799 + 3499 + 5898 + 899 + 1598)

-- To see breakdown:
SELECT 
    status,
    COUNT(*) AS order_count,
    SUM(total_amount) AS total_revenue,
    AVG(total_amount) AS avg_revenue
FROM orders
GROUP BY status;

-- ===================================================================
-- Q15. Average unit_price of products in each category
-- ===================================================================
-- Solution:
SELECT 
    category,
    COUNT(*) AS product_count,
    AVG(unit_price) AS avg_price,
    ROUND(AVG(unit_price), 2) AS avg_price_rounded
FROM products
GROUP BY category
ORDER BY avg_price DESC;

-- Explanation:
-- - GROUP BY category groups products by category
-- - AVG() calculates mean price within each group
-- - ROUND() formats the result to 2 decimal places
-- - Expected results:
--   Electronics: ₹2224 average
--   Clothing: ₹2699 average
--   Home: ₹949 average

-- ===================================================================
-- Q16. For each order status, find count of orders and total revenue
--      Sort by total revenue in descending order
-- ===================================================================
-- Solution:
SELECT 
    status,
    COUNT(*) AS order_count,
    SUM(total_amount) AS total_revenue,
    ROUND(AVG(total_amount), 2) AS avg_revenue_per_order
FROM orders
GROUP BY status
ORDER BY total_revenue DESC;

-- Explanation:
-- - GROUP BY groups orders by status
-- - Aggregate functions calculate metrics for each group
-- - ORDER BY sorts groups by revenue (highest first)
-- - Expected order: Delivered > Shipped > Cancelled > Pending

-- ===================================================================
-- Q17. Most expensive (MAX) and cheapest (MIN) product in each category
-- ===================================================================
-- Solution:
SELECT 
    category,
    MAX(unit_price) AS max_price,
    MIN(unit_price) AS min_price,
    (MAX(unit_price) - MIN(unit_price)) AS price_range
FROM products
GROUP BY category
ORDER BY price_range DESC;

-- Explanation:
-- - MAX() finds highest price in each category
-- - MIN() finds lowest price in each category
-- - Shows price range and variation

-- With product names (requires subquery or joins):
SELECT 
    p1.category,
    p1.product_name AS cheapest_product,
    p1.unit_price AS min_price,
    p2.product_name AS most_expensive_product,
    p2.unit_price AS max_price
FROM products p1
JOIN products p2 
    ON p1.category = p2.category 
    AND p1.unit_price = (SELECT MIN(unit_price) FROM products WHERE category = p1.category)
    AND p2.unit_price = (SELECT MAX(unit_price) FROM products WHERE category = p2.category)
GROUP BY p1.category
ORDER BY p1.category;

-- ===================================================================
-- Q18. Product categories where average unit_price > ₹2000
-- ===================================================================
-- Solution:
SELECT 
    category,
    COUNT(*) AS product_count,
    ROUND(AVG(unit_price), 2) AS avg_price,
    MIN(unit_price) AS min_price,
    MAX(unit_price) AS max_price
FROM products
GROUP BY category
HAVING AVG(unit_price) > 2000
ORDER BY avg_price DESC;

-- Explanation:
-- - GROUP BY groups products by category
-- - HAVING filters groups based on aggregate condition
-- - HAVING is used for conditions on aggregated values (unlike WHERE)
-- - Expected result: Only Electronics category (₹2224 average)
--
-- Key Difference:
-- WHERE filters rows BEFORE grouping
-- HAVING filters groups AFTER aggregation

-- Complete example with both WHERE and HAVING:
SELECT 
    category,
    COUNT(*) AS product_count,
    ROUND(AVG(unit_price), 2) AS avg_price
FROM products
WHERE stock_qty > 150  -- WHERE: filter rows before grouping
GROUP BY category
HAVING AVG(unit_price) > 1000  -- HAVING: filter groups after aggregation
ORDER BY avg_price DESC;

-- ===================================================================
-- ADDITIONAL AGGREGATION EXAMPLES
-- ===================================================================

-- Find customers with multiple orders
SELECT 
    c.customer_id,
    c.first_name,
    c.last_name,
    COUNT(o.order_id) AS order_count,
    SUM(o.total_amount) AS total_spent,
    ROUND(AVG(o.total_amount), 2) AS avg_order_value
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.first_name, c.last_name
HAVING COUNT(o.order_id) > 1
ORDER BY total_spent DESC;

-- Revenue by category (via order_items)
SELECT 
    p.category,
    COUNT(DISTINCT oi.order_id) AS num_orders,
    COUNT(oi.item_id) AS total_items_sold,
    SUM(oi.quantity) AS total_quantity,
    ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_pct/100)), 2) AS revenue_after_discount
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.category
ORDER BY revenue_after_discount DESC;

-- Monthly order statistics
SELECT 
    DATE_FORMAT(order_date, '%Y-%m') AS month,
    COUNT(*) AS orders,
    SUM(total_amount) AS revenue,
    ROUND(AVG(total_amount), 2) AS avg_order_value,
    MAX(total_amount) AS largest_order,
    MIN(total_amount) AS smallest_order
FROM orders
GROUP BY DATE_FORMAT(order_date, '%Y-%m')
ORDER BY month ASC;

-- Top 3 products by quantity sold
SELECT 
    p.product_id,
    p.product_name,
    p.category,
    SUM(oi.quantity) AS total_quantity,
    COUNT(DISTINCT oi.order_id) AS num_orders,
    ROUND(SUM(oi.quantity * oi.unit_price), 2) AS total_revenue
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
GROUP BY p.product_id, p.product_name, p.category
ORDER BY total_quantity DESC
LIMIT 3;

-- ===================================================================
-- AGGREGATE FUNCTION SUMMARY
-- ===================================================================
-- COUNT(*) - Counts all rows (including NULLs)
-- COUNT(column) - Counts non-NULL values in column
-- SUM(column) - Adds up numeric values (ignores NULLs)
-- AVG(column) - Calculates average (ignores NULLs)
-- MIN(column) - Finds minimum value
-- MAX(column) - Finds maximum value
-- STDDEV(column) - Standard deviation
-- VARIANCE(column) - Variance

-- ===================================================================
-- END OF SECTION C
-- ===================================================================
