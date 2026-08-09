-- ============================================================
-- Part 3: SQL Analysis
-- Run against ecommerce.db (SQLite). Load with load_db.py first.
-- Revenue formula used throughout: quantity * unit_price * (1 - discount_percent/100.0)
-- Note: quantity can be negative (returns), so revenue naturally nets out returns.
-- ============================================================


-- ============================================================
-- BASIC QUERIES
-- ============================================================

-- 1. Total revenue per category
SELECT
    p.category,
    ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) AS total_revenue
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
GROUP BY p.category
ORDER BY total_revenue DESC;


-- 2. Top 10 customers by total order value
SELECT
    o.customer_id,
    c.customer_name,
    ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 2) AS total_order_value
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
JOIN customers c ON c.customer_id = o.customer_id
WHERE o.customer_id IS NOT NULL
GROUP BY o.customer_id, c.customer_name
ORDER BY total_order_value DESC
LIMIT 10;


-- 3. Month-wise order count for the last 12 months
SELECT
    strftime('%Y-%m', order_date) AS year_month,
    COUNT(*) AS order_count
FROM orders
WHERE order_date >= date((SELECT MAX(order_date) FROM orders), '-12 months')
GROUP BY year_month
ORDER BY year_month;


-- ============================================================
-- INTERMEDIATE QUERIES
-- ============================================================

-- 4. Customers who placed orders but never had any item delivered
SELECT DISTINCT o.customer_id, c.customer_name
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
WHERE o.customer_id IS NOT NULL
  AND o.customer_id NOT IN (
        SELECT customer_id FROM orders WHERE status = 'DELIVERED' AND customer_id IS NOT NULL
  );


-- 5. Products that were ordered but had more returns than purchases
-- (a "return" is a negative-quantity row; a "purchase" is a positive-quantity row)
SELECT
    p.product_id,
    p.product_name,
    SUM(CASE WHEN oi.quantity > 0 THEN oi.quantity ELSE 0 END) AS total_purchased,
    SUM(CASE WHEN oi.quantity < 0 THEN -oi.quantity ELSE 0 END) AS total_returned
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
GROUP BY p.product_id, p.product_name
HAVING total_returned > total_purchased;


-- 6. Return rate (returned items / total items) per category
SELECT
    p.category,
    SUM(CASE WHEN oi.quantity < 0 THEN -oi.quantity ELSE 0 END) AS returned_items,
    SUM(ABS(oi.quantity)) AS total_items,
    ROUND(
        1.0 * SUM(CASE WHEN oi.quantity < 0 THEN -oi.quantity ELSE 0 END)
        / NULLIF(SUM(ABS(oi.quantity)), 0), 4
    ) AS return_rate
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
GROUP BY p.category
ORDER BY return_rate DESC;


-- ============================================================
-- ADVANCED QUERIES (Window Functions, CTEs, Subqueries)
-- ============================================================

-- 7. Running total of revenue per region, ordered by date
WITH daily_region_revenue AS (
    SELECT
        o.region_code,
        date(o.order_date) AS order_date,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS daily_revenue
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    GROUP BY o.region_code, date(o.order_date)
)
SELECT
    region_code,
    order_date,
    ROUND(daily_revenue, 2) AS daily_revenue,
    ROUND(SUM(daily_revenue) OVER (
        PARTITION BY region_code ORDER BY order_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ), 2) AS running_total
FROM daily_region_revenue
ORDER BY region_code, order_date;


-- 8. For each category, rank products by total revenue (DENSE_RANK, ties share rank)
WITH product_revenue AS (
    SELECT
        p.category,
        p.product_name,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS total_revenue
    FROM order_items oi
    JOIN products p ON p.product_id = oi.product_id
    GROUP BY p.category, p.product_name
)
SELECT
    category,
    product_name,
    ROUND(total_revenue, 2) AS total_revenue,
    DENSE_RANK() OVER (PARTITION BY category ORDER BY total_revenue DESC) AS rank_in_category
FROM product_revenue
ORDER BY category, rank_in_category;


-- 9. Days between consecutive orders per customer (LAG), flag "At Risk" if avg gap > 30 days
WITH customer_orders AS (
    SELECT
        customer_id,
        date(order_date) AS order_date,
        LAG(date(order_date)) OVER (PARTITION BY customer_id ORDER BY order_date) AS previous_order_date
    FROM orders
    WHERE customer_id IS NOT NULL
),
gaps AS (
    SELECT
        customer_id,
        order_date,
        previous_order_date,
        CASE WHEN previous_order_date IS NOT NULL
             THEN julianday(order_date) - julianday(previous_order_date)
        END AS days_gap
    FROM customer_orders
),
avg_gaps AS (
    SELECT customer_id, AVG(days_gap) AS avg_gap
    FROM gaps
    WHERE days_gap IS NOT NULL
    GROUP BY customer_id
)
SELECT
    g.customer_id,
    g.order_date,
    g.previous_order_date,
    g.days_gap,
    CASE WHEN a.avg_gap > 30 THEN 'At Risk' ELSE 'Normal' END AS risk_flag
FROM gaps g
JOIN avg_gaps a ON a.customer_id = g.customer_id
ORDER BY g.customer_id, g.order_date;


-- 10. CTE with multiple levels: monthly revenue per customer -> tier -> count per month
WITH monthly_customer_revenue AS (
    SELECT
        o.customer_id,
        strftime('%Y-%m', o.order_date) AS year_month,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS monthly_revenue
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.customer_id IS NOT NULL
    GROUP BY o.customer_id, year_month
),
tiered AS (
    SELECT
        customer_id,
        year_month,
        monthly_revenue,
        CASE
            WHEN monthly_revenue > 10000 THEN 'High'
            WHEN monthly_revenue >= 5000 THEN 'Medium'
            ELSE 'Low'
        END AS tier
    FROM monthly_customer_revenue
)
SELECT
    year_month,
    tier,
    COUNT(DISTINCT customer_id) AS customer_count
FROM tiered
GROUP BY year_month, tier
ORDER BY year_month, tier;


-- 11. NTILE: divide customers into 4 quartiles by total lifetime value
WITH customer_ltv AS (
    SELECT
        o.customer_id,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS total_value
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.customer_id IS NOT NULL
    GROUP BY o.customer_id
)
SELECT
    customer_id,
    ROUND(total_value, 2) AS total_value,
    NTILE(4) OVER (ORDER BY total_value DESC) AS quartile,
    CASE NTILE(4) OVER (ORDER BY total_value DESC)
        WHEN 1 THEN 'Platinum'
        WHEN 2 THEN 'Gold'
        WHEN 3 THEN 'Silver'
        WHEN 4 THEN 'Bronze'
    END AS quartile_label
FROM customer_ltv
ORDER BY quartile, total_value DESC;


-- 12. Year-over-year comparison: each month's revenue vs same month previous year
WITH monthly_revenue AS (
    SELECT
        CAST(strftime('%Y', o.order_date) AS INTEGER) AS year,
        CAST(strftime('%m', o.order_date) AS INTEGER) AS month,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS revenue
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    GROUP BY year, month
)
SELECT
    m.year,
    m.month,
    ROUND(m.revenue, 2) AS revenue,
    ROUND(p.revenue, 2) AS prev_year_revenue,
    CASE
        WHEN p.revenue IS NULL OR p.revenue = 0 THEN NULL
        ELSE ROUND((m.revenue - p.revenue) / p.revenue * 100, 2)
    END AS yoy_growth_percent
FROM monthly_revenue m
LEFT JOIN monthly_revenue p
    ON p.year = m.year - 1 AND p.month = m.month
ORDER BY m.year, m.month;


-- 13. First/last purchased category per customer, flag category_shift
WITH customer_category_orders AS (
    SELECT
        o.customer_id,
        p.category,
        o.order_date,
        FIRST_VALUE(p.category) OVER (
            PARTITION BY o.customer_id ORDER BY o.order_date
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) AS first_category,
        LAST_VALUE(p.category) OVER (
            PARTITION BY o.customer_id ORDER BY o.order_date
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) AS last_category
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    JOIN products p ON p.product_id = oi.product_id
    WHERE o.customer_id IS NOT NULL
)
SELECT DISTINCT
    customer_id,
    first_category,
    last_category,
    CASE WHEN first_category != last_category THEN 'Yes' ELSE 'No' END AS category_shift
FROM customer_category_orders
ORDER BY customer_id;


-- 14. Cumulative distribution: % of total revenue from top N% of customers
WITH customer_revenue AS (
    SELECT
        o.customer_id,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS revenue
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.customer_id IS NOT NULL
    GROUP BY o.customer_id
),
ranked AS (
    SELECT
        customer_id,
        revenue,
        SUM(revenue) OVER (ORDER BY revenue DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_revenue,
        SUM(revenue) OVER () AS grand_total
    FROM customer_revenue
)
SELECT
    customer_id,
    ROUND(revenue, 2) AS revenue,
    ROUND(cumulative_revenue, 2) AS cumulative_revenue,
    ROUND(100.0 * cumulative_revenue / grand_total, 2) AS cumulative_percent
FROM ranked
ORDER BY revenue DESC;


-- 15. Complex CTE: cohort analysis by registration month, retention months 0-3
WITH cohorts AS (
    SELECT
        customer_id,
        strftime('%Y-%m', registration_date) AS cohort_month
    FROM customers
),
customer_order_months AS (
    SELECT DISTINCT
        customer_id,
        strftime('%Y-%m', order_date) AS order_month
    FROM orders
    WHERE customer_id IS NOT NULL
),
cohort_activity AS (
    SELECT
        c.customer_id,
        c.cohort_month,
        com.order_month,
        CAST(
            (strftime('%Y', com.order_month || '-01') - strftime('%Y', c.cohort_month || '-01')) * 12 +
            (strftime('%m', com.order_month || '-01') - strftime('%m', c.cohort_month || '-01'))
            AS INTEGER
        ) AS month_offset
    FROM cohorts c
    JOIN customer_order_months com ON com.customer_id = c.customer_id
),
cohort_sizes AS (
    SELECT cohort_month, COUNT(*) AS cohort_size
    FROM cohorts
    GROUP BY cohort_month
)
SELECT
    ca.cohort_month,
    cs.cohort_size,
    SUM(CASE WHEN ca.month_offset = 0 THEN 1 ELSE 0 END) AS month_0_active,
    SUM(CASE WHEN ca.month_offset = 1 THEN 1 ELSE 0 END) AS month_1_active,
    SUM(CASE WHEN ca.month_offset = 2 THEN 1 ELSE 0 END) AS month_2_active,
    SUM(CASE WHEN ca.month_offset = 3 THEN 1 ELSE 0 END) AS month_3_active,
    ROUND(100.0 * SUM(CASE WHEN ca.month_offset = 1 THEN 1 ELSE 0 END) / cs.cohort_size, 2) AS retention_month_1_pct,
    ROUND(100.0 * SUM(CASE WHEN ca.month_offset = 2 THEN 1 ELSE 0 END) / cs.cohort_size, 2) AS retention_month_2_pct,
    ROUND(100.0 * SUM(CASE WHEN ca.month_offset = 3 THEN 1 ELSE 0 END) / cs.cohort_size, 2) AS retention_month_3_pct
FROM cohort_activity ca
JOIN cohort_sizes cs ON cs.cohort_month = ca.cohort_month
WHERE ca.month_offset >= 0
GROUP BY ca.cohort_month, cs.cohort_size
ORDER BY ca.cohort_month;


-- 16. Products frequently bought together (self-join on order_id, dedupe pairs)
WITH pairs AS (
    SELECT
        a.order_id,
        MIN(pa.product_name, pb.product_name) AS product_a,
        MAX(pa.product_name, pb.product_name) AS product_b
    FROM order_items a
    JOIN order_items b
        ON a.order_id = b.order_id AND a.product_id < b.product_id
    JOIN products pa ON pa.product_id = a.product_id
    JOIN products pb ON pb.product_id = b.product_id
)
SELECT
    product_a,
    product_b,
    COUNT(*) AS times_bought_together
FROM pairs
GROUP BY product_a, product_b
ORDER BY times_bought_together DESC
LIMIT 50;
