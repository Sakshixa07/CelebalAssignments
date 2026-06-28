-- =====================================================================
-- SECTION B: FILTERING & OPTIMIZATION (WHERE, Indexes)
-- =====================================================================
-- These questions test your ability to filter data effectively and 
-- understand how indexes improve query performance.
-- =====================================================================

-- ===================================================================
-- Q7. Retrieve all orders with status = 'Delivered'
-- ===================================================================
-- Solution:
SELECT * FROM orders WHERE status = 'Delivered';

-- Explanation: The WHERE clause filters rows based on a condition.
-- This query uses the idx_orders_status index for fast retrieval.
-- Expected result: 6 orders with Delivered status

-- ===================================================================
-- Q8. Find products in 'Electronics' category with unit_price > ₹2000
-- ===================================================================
-- Solution:
SELECT * FROM products 
WHERE category = 'Electronics' AND unit_price > 2000
ORDER BY unit_price DESC;

-- Explanation: Uses compound WHERE condition with AND operator.
-- This leverages idx_products_category index and checks price condition.
-- Expected result: Smart Watch (₹2999) and Bluetooth Speaker (₹3499)

-- ===================================================================
-- Q9. List customers who joined in 2024 and belong to 'Maharashtra'
-- ===================================================================
-- Solution (Index-friendly version):
SELECT customer_id, first_name, last_name, city, state, join_date
FROM customers 
WHERE state = 'Maharashtra' AND join_date >= '2024-01-01' AND join_date < '2025-01-01'
ORDER BY join_date ASC;

-- Alternative (Less efficient - avoids function calls):
-- SELECT * FROM customers 
-- WHERE YEAR(join_date) = 2024 AND state = 'Maharashtra';
-- Note: The YEAR() function prevents index usage, so avoid it!

-- Explanation: Uses idx_customers_state index and date range filtering.
-- Expected result: Aarav Sharma (Mumbai) and Karan Mehta (Pune)

-- ===================================================================
-- Q10. Orders placed between '2024-08-10' and '2024-08-25' (inclusive)
--      that are NOT cancelled
-- ===================================================================
-- Solution:
SELECT * FROM orders 
WHERE order_date >= '2024-08-10' 
  AND order_date <= '2024-08-25'
  AND status != 'Cancelled'
ORDER BY order_date ASC;

-- Explanation: 
-- - Date range filtering uses idx_orders_date index
-- - NOT condition (!=) filters out cancelled orders
-- - Expected result: 4 orders (Delivered, Shipped, Pending)

-- ===================================================================
-- Q11. Explain what idx_orders_date does and its benefits
-- ===================================================================
-- Answer:
-- idx_orders_date is a B-tree index on the order_date column.
--
-- What it does:
-- - Stores sorted references to rows based on order_date value
-- - Enables fast binary search instead of full table scan
-- - Significantly speeds up range queries and sorting
--
-- Performance benefit:
-- - Without index: Database must scan ALL rows (~10 in sample)
-- - With index: Database can directly locate date range (~1-2 seeks)
-- - Especially beneficial when table has millions of rows
--
-- Query that benefits from this index:
SELECT * FROM orders 
WHERE order_date BETWEEN '2024-08-01' AND '2024-08-31'
ORDER BY order_date DESC
LIMIT 10;

-- Explanation: This query directly uses idx_orders_date to:
-- 1. Quickly find orders in the date range
-- 2. Efficiently sort by order_date (index is already sorted)
-- 3. Return results without full table scan

-- ===================================================================
-- Q12. Index usage and SARGABILITY
-- ===================================================================
-- Problem Query (NOT Index-friendly):
-- SELECT * FROM customers WHERE YEAR(join_date) = 2024;
--
-- Why this is inefficient:
-- - YEAR() is a function applied to the column
-- - Database cannot use idx_customers on join_date because the 
--   index stores actual dates, not extracted years
-- - Requires computing YEAR(join_date) for EVERY row (full scan)
--
-- Solution (Index-friendly / SARGABLE):
SELECT * FROM customers 
WHERE join_date >= '2024-01-01' AND join_date < '2025-01-01'
ORDER BY join_date;

-- Explanation:
-- - Avoids function call on the indexed column
-- - Database can use binary search on index to find matching dates
-- - Much faster on large tables
--
-- Additional Index-friendly examples:
-- BAD:  WHERE UPPER(first_name) = 'AARAV'  (function on column)
-- GOOD: WHERE first_name = 'Aarav'         (direct comparison)
--
-- BAD:  WHERE customer_id + 5 = 106       (calculation on column)
-- GOOD: WHERE customer_id = 101            (direct comparison)

-- ===================================================================
-- Additional Filtering Examples
-- ===================================================================

-- IN operator (multiple values)
SELECT * FROM products WHERE category IN ('Electronics', 'Clothing');

-- LIKE operator (pattern matching)
SELECT * FROM customers WHERE first_name LIKE 'A%';  -- Starts with 'A'

-- NULL checks
SELECT * FROM orders WHERE status IS NULL;  -- Would return empty in our data

-- Multiple conditions with OR
SELECT * FROM customers 
WHERE city = 'Mumbai' OR city = 'Pune'
ORDER BY city;

-- ===================================================================
-- PERFORMANCE TIPS FOR FILTERING
-- ===================================================================
-- 1. Always use SARGABLE queries (conditions the index can support)
-- 2. Avoid functions on indexed columns (e.g., YEAR, UPPER, etc.)
-- 3. Use specific column names instead of SELECT *
-- 4. Use BETWEEN for date ranges instead of multiple OR conditions
-- 5. Use IN for multiple specific values
-- 6. Index columns used frequently in WHERE clauses
-- 7. Put most restrictive conditions first in AND queries

-- ===================================================================
-- END OF SECTION B
-- ===================================================================
