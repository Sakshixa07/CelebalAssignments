-- RetailMart | 06 - Subqueries
-- Business question: which customers spend more than the average customer?
-- (a classic "compare each row to an aggregate of the whole set" pattern)

-- Scalar subquery in WHERE: customers above the average lifetime spend
SELECT
    c.customer_id,
    c.customer_name,
    SUM(o.line_revenue) AS lifetime_spend
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_status IN ('Delivered', 'Shipped')
GROUP BY c.customer_id, c.customer_name
HAVING SUM(o.line_revenue) > (
    -- average lifetime spend across ALL customers
    SELECT AVG(cust_total)
    FROM (
        SELECT SUM(line_revenue) AS cust_total
        FROM orders
        WHERE order_status IN ('Delivered', 'Shipped')
        GROUP BY customer_id
    )
)
ORDER BY lifetime_spend DESC
LIMIT 15;

-- Correlated subquery: each product's revenue vs. its own category average
SELECT
    p.product_id,
    p.product_name,
    p.category,
    (SELECT SUM(o.line_revenue) FROM orders o WHERE o.product_id = p.product_id) AS product_revenue
FROM products p
WHERE (SELECT SUM(o.line_revenue) FROM orders o WHERE o.product_id = p.product_id) >
      (SELECT AVG(cat_rev) FROM (
          SELECT p2.category, SUM(o2.line_revenue) AS cat_rev
          FROM products p2
          JOIN orders o2 ON p2.product_id = o2.product_id
          WHERE p2.category = p.category
          GROUP BY p2.category
      ))
ORDER BY product_revenue DESC
LIMIT 10;

-- IN subquery: customers who have at least one cancelled order
SELECT customer_id, customer_name, city
FROM customers
WHERE customer_id IN (
    SELECT customer_id FROM orders WHERE order_status = 'Cancelled'
)
LIMIT 15;
