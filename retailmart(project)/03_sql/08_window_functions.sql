-- RetailMart | 08 - Window Functions
-- Business question: which products are trending within their own category?
-- (rank products by revenue, but reset the ranking per category)

WITH product_revenue AS (
    SELECT
        p.product_id,
        p.product_name,
        p.category,
        SUM(o.line_revenue) AS total_revenue,
        SUM(o.quantity)     AS units_sold
    FROM products p
    JOIN orders o ON p.product_id = o.product_id
    WHERE o.order_status IN ('Delivered', 'Shipped')
    GROUP BY p.product_id, p.product_name, p.category
),
ranked AS (
    SELECT
        category,
        product_name,
        total_revenue,
        units_sold,
        RANK() OVER (PARTITION BY category ORDER BY total_revenue DESC) AS rank_in_category,
        ROUND(100.0 * total_revenue / SUM(total_revenue) OVER (PARTITION BY category), 1) AS pct_of_category_revenue
    FROM product_revenue
)
-- SQLite has no QUALIFY clause, so filter the ranked CTE with a plain WHERE instead
SELECT *
FROM ranked
WHERE rank_in_category <= 3
ORDER BY category, rank_in_category;

-- Running total of monthly revenue (cumulative revenue over time)
WITH monthly_revenue AS (
    SELECT
        strftime('%Y-%m', order_date) AS month,
        SUM(line_revenue) AS revenue
    FROM orders
    WHERE order_status IN ('Delivered', 'Shipped')
    GROUP BY month
)
SELECT
    month,
    revenue,
    SUM(revenue) OVER (ORDER BY month) AS cumulative_revenue,
    ROUND(AVG(revenue) OVER (ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 2) AS rolling_3mo_avg
FROM monthly_revenue
ORDER BY month;

-- Customer order sequencing: label each customer's 1st, 2nd, 3rd... order (ROW_NUMBER)
SELECT
    customer_id,
    order_id,
    order_date,
    ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date) AS order_sequence,
    LAG(order_date) OVER (PARTITION BY customer_id ORDER BY order_date) AS previous_order_date
FROM orders
ORDER BY customer_id, order_sequence
LIMIT 20;
