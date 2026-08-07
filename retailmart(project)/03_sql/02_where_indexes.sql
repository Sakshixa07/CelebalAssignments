-- RetailMart | 02 - WHERE + Indexes
-- Business question: filter orders by status, date range, and value -
-- these are the exact filters the indexes created in 00_build_database.py
-- (idx_orders_status, idx_orders_date) are designed to speed up.

-- Filter by status (uses idx_orders_status)
SELECT order_id, customer_id, order_date, order_status
FROM orders
WHERE order_status = 'Cancelled'
LIMIT 10;

-- Filter by date range (uses idx_orders_date)
SELECT order_id, order_date, order_status, line_revenue
FROM orders
WHERE order_date BETWEEN '2026-06-01' AND '2026-06-30'
LIMIT 10;

-- Combine filters: high-value delivered orders in the last quarter
SELECT order_id, customer_id, order_date, line_revenue
FROM orders
WHERE order_status = 'Delivered'
  AND line_revenue > 5000
  AND order_date >= '2026-05-01'
ORDER BY line_revenue DESC
LIMIT 10;

-- Confirm the query planner is actually using the index (EXPLAIN QUERY PLAN)
EXPLAIN QUERY PLAN
SELECT * FROM orders WHERE order_status = 'Delivered';
