-- RetailMart | 01 - SELECT basics & keys
-- Business question: what does our core data actually look like?

-- Peek at each table (primary key columns are the *_id columns)
SELECT customer_id, customer_name, city, signup_date
FROM customers
LIMIT 10;

SELECT product_id, product_name, category, price
FROM products
LIMIT 10;

SELECT order_id, customer_id, product_id, quantity, order_status
FROM orders
LIMIT 10;

-- Distinct values are a fast way to sanity check a column's domain
SELECT DISTINCT order_status
FROM orders;

SELECT DISTINCT category
FROM products
ORDER BY category;

-- Every order should reference a real customer_id (foreign key relationship).
-- Zero rows returned here means referential integrity holds.
SELECT o.order_id, o.customer_id
FROM orders o
LEFT JOIN customers c ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL;
