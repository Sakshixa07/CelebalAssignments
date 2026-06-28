-- =====================================================================
-- SECTION D: JOINS & RELATIONSHIPS
-- =====================================================================
-- These questions test your ability to combine data from multiple 
-- tables using different types of JOINs.
-- =====================================================================

-- ===================================================================
-- Q19. INNER JOIN - Orders with customer names
-- ===================================================================
-- Solution:
SELECT 
    o.order_id,
    o.order_date,
    c.first_name,
    c.last_name,
    o.total_amount
FROM orders o
INNER JOIN customers c ON o.customer_id = c.customer_id
ORDER BY o.order_date DESC;

-- Explanation:
-- - INNER JOIN matches rows from both tables on the join condition
-- - Only rows with matching customer_id in both tables are included
-- - Expected result: 10 rows (all orders have valid customers)
-- - Key concept: If a customer had no orders, they wouldn't appear

-- Equivalent syntax (older style):
SELECT 
    o.order_id,
    o.order_date,
    c.first_name,
    c.last_name,
    o.total_amount
FROM orders o, customers c
WHERE o.customer_id = c.customer_id
ORDER BY o.order_date DESC;

-- ===================================================================
-- Q20. LEFT JOIN - All customers and their orders (if any)
-- ===================================================================
-- Solution:
SELECT 
    c.customer_id,
    c.first_name,
    c.last_name,
    c.city,
    o.order_id,
    o.order_date,
    o.status,
    o.total_amount
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
ORDER BY c.customer_id, o.order_date;

-- Explanation:
-- - LEFT JOIN includes ALL rows from the left table (customers)
-- - Matches rows from right table (orders) where possible
-- - If a customer has no orders, order columns show NULL
-- - In this dataset, all customers have at least one order
-- - Useful for finding customers with no orders:
--   WHERE o.order_id IS NULL

-- Find customers with NO orders:
SELECT 
    c.customer_id,
    c.first_name,
    c.last_name,
    c.city,
    COUNT(o.order_id) AS order_count
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.first_name, c.last_name, c.city
HAVING COUNT(o.order_id) = 0;

-- Expected result: Empty (all customers have orders in sample data)

-- ===================================================================
-- Q21. Three-table JOIN - Orders with products and order items
-- ===================================================================
-- Solution:
SELECT 
    oi.item_id,
    o.order_id,
    o.order_date,
    p.product_name,
    p.category,
    oi.quantity,
    oi.unit_price,
    oi.discount_pct,
    ROUND(oi.quantity * oi.unit_price, 2) AS subtotal_before_discount,
    ROUND(oi.quantity * oi.unit_price * (1 - oi.discount_pct/100), 2) AS subtotal_after_discount
FROM orders o
INNER JOIN order_items oi ON o.order_id = oi.order_id
INNER JOIN products p ON oi.product_id = p.product_id
ORDER BY o.order_id, oi.item_id;

-- Explanation:
-- - Chains multiple JOINs together
-- - First JOIN: orders with order_items via order_id
-- - Second JOIN: order_items with products via product_id
-- - Shows complete order details including product information
-- - Calculates line item totals with discount applied

-- More detailed version with customer and all info:
SELECT 
    c.first_name,
    c.last_name,
    o.order_id,
    o.order_date,
    p.product_name,
    p.category,
    oi.quantity,
    oi.unit_price,
    oi.discount_pct,
    ROUND(oi.quantity * oi.unit_price * (1 - oi.discount_pct/100), 2) AS line_total,
    o.status
FROM customers c
INNER JOIN orders o ON c.customer_id = o.customer_id
INNER JOIN order_items oi ON o.order_id = oi.order_id
INNER JOIN products p ON oi.product_id = p.product_id
WHERE o.status = 'Delivered'
ORDER BY c.first_name, o.order_id;

-- ===================================================================
-- Q22. LEFT JOIN vs RIGHT JOIN vs FULL OUTER JOIN
-- ===================================================================

-- LEFT JOIN Example:
-- Returns ALL from left table, matching rows from right table
SELECT 
    c.customer_id,
    c.first_name,
    COUNT(o.order_id) AS order_count
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.first_name;
-- Result: All 8 customers, even those with no orders

-- RIGHT JOIN Example (opposite of LEFT):
-- Returns ALL from right table, matching rows from left table
SELECT 
    c.customer_id,
    c.first_name,
    o.order_id,
    o.order_date
FROM customers c
RIGHT JOIN orders o ON c.customer_id = o.customer_id;
-- Result: All orders, even if customer info is missing

-- FULL OUTER JOIN Example:
-- Returns ALL rows from both tables, matching where possible
-- (Note: Not supported in MySQL, use UNION in MySQL)
SELECT 
    c.customer_id,
    c.first_name,
    o.order_id,
    o.order_date
FROM customers c
FULL OUTER JOIN orders o ON c.customer_id = o.customer_id;

-- MySQL equivalent using UNION:
SELECT 
    c.customer_id,
    c.first_name,
    o.order_id,
    o.order_date
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
UNION
SELECT 
    c.customer_id,
    c.first_name,
    o.order_id,
    o.order_date
FROM customers c
RIGHT JOIN orders o ON c.customer_id = o.customer_id;

-- Comparison Table:
-- JOIN Type     | Rows from Left | Rows from Right | Use Case
-- ============================================================
-- INNER JOIN    | Matched only   | Matched only    | Only records in both tables
-- LEFT JOIN     | ALL            | Matched only    | All from left, details from right
-- RIGHT JOIN    | Matched only   | ALL             | All from right, details from left
-- FULL OUTER    | ALL            | ALL             | All records from both tables
--
-- When to use FULL OUTER JOIN:
-- - Finding records that exist in EITHER table
-- - Identifying unmatched records in both tables
-- - Audit trails and reconciliation
-- Example: Find customers with no orders AND orders with invalid customers

-- ===================================================================
-- Q23. Foreign Key Relationships and Constraints
-- ===================================================================

-- Answer: Foreign Key Relationships in the schema
-- ================================================================
-- Table        | Column        | References        | Constraint
-- ================================================================
-- orders       | customer_id   | customers.id      | Referential Integrity
-- order_items  | order_id      | orders.id         | Referential Integrity  
-- order_items  | product_id    | products.id       | Referential Integrity
--
-- What happens if you try to insert order with customer_id = 999:
-- ERROR: Foreign key constraint fails
-- The database will REJECT the insert with error like:
-- "Cannot add or update a child row: a foreign key constraint fails"
--
-- Why this protection is important:
-- - Prevents orphaned records (orders without customers)
-- - Maintains referential integrity
-- - Ensures data consistency across tables
-- - Prevents invalid relationships

-- Demonstration query (this will fail):
-- INSERT INTO orders VALUES
-- (1011, 999, '2024-08-30', 'Pending', 1000.00);
-- ERROR: Foreign key constraint 'orders_ibfk_1' fails

-- Correct approach:
-- 1. First verify customer exists
SELECT * FROM customers WHERE customer_id = 102;

-- 2. Then insert order only if customer exists
INSERT INTO orders VALUES
(1011, 102, '2024-08-30', 'Pending', 1000.00);

-- 3. Verify insert
SELECT * FROM orders WHERE order_id = 1011;

-- Clean up:
DELETE FROM orders WHERE order_id = 1011;

-- ===================================================================
-- ADDITIONAL JOIN EXAMPLES
-- ===================================================================

-- Self Join - Compare two rows in same table (e.g., customers in same city)
SELECT 
    c1.customer_id AS customer_1_id,
    c1.first_name AS customer_1,
    c2.customer_id AS customer_2_id,
    c2.first_name AS customer_2,
    c1.city
FROM customers c1
INNER JOIN customers c2 
    ON c1.city = c2.city 
    AND c1.customer_id < c2.customer_id
ORDER BY c1.city, c1.customer_id;

-- Cross Join (Cartesian product) - All combinations
SELECT 
    c.customer_id,
    c.first_name,
    p.product_id,
    p.product_name
FROM customers c
CROSS JOIN products p
LIMIT 5;  -- Limit to prevent too many rows

-- Left Join with aggregation
SELECT 
    p.product_id,
    p.product_name,
    COUNT(oi.item_id) AS times_purchased,
    SUM(oi.quantity) AS total_quantity
FROM products p
LEFT JOIN order_items oi ON p.product_id = oi.product_id
GROUP BY p.product_id, p.product_name
ORDER BY times_purchased DESC;

-- ===================================================================
-- END OF SECTION D
-- ===================================================================
