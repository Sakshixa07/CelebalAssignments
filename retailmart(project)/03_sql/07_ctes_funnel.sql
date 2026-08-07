-- RetailMart | 07 - CTEs
-- Business question: order funnel - of everyone who places an order, how
-- many make it through to a successful, paid delivery? Where do we lose people?

WITH funnel AS (
    SELECT
        o.order_id,
        o.order_status,
        pay.payment_status,
        CASE WHEN o.order_status IN ('Processing','Shipped','Delivered') THEN 1 ELSE 0 END AS reached_processing,
        CASE WHEN o.order_status IN ('Shipped','Delivered') THEN 1 ELSE 0 END AS reached_shipped,
        CASE WHEN o.order_status = 'Delivered' THEN 1 ELSE 0 END AS reached_delivered,
        CASE WHEN o.order_status = 'Delivered' AND pay.payment_status = 'Success' THEN 1 ELSE 0 END AS reached_paid_delivery
    FROM orders o
    LEFT JOIN payments pay ON o.order_id = pay.order_id
),
funnel_totals AS (
    SELECT
        COUNT(*)                        AS total_orders,
        SUM(reached_processing)         AS processing,
        SUM(reached_shipped)            AS shipped,
        SUM(reached_delivered)          AS delivered,
        SUM(reached_paid_delivery)      AS paid_delivery
    FROM funnel
)
SELECT
    total_orders,
    processing,
    ROUND(100.0 * processing / total_orders, 1)      AS pct_processing,
    shipped,
    ROUND(100.0 * shipped / total_orders, 1)          AS pct_shipped,
    delivered,
    ROUND(100.0 * delivered / total_orders, 1)        AS pct_delivered,
    paid_delivery,
    ROUND(100.0 * paid_delivery / total_orders, 1)    AS pct_paid_delivery
FROM funnel_totals;

-- Multi-CTE example: monthly funnel trend (new orders -> delivered same status snapshot)
WITH monthly_orders AS (
    SELECT
        strftime('%Y-%m', order_date) AS month,
        order_status,
        COUNT(*) AS num_orders
    FROM orders
    GROUP BY month, order_status
),
monthly_totals AS (
    SELECT month, SUM(num_orders) AS total FROM monthly_orders GROUP BY month
)
SELECT
    mo.month,
    mo.order_status,
    mo.num_orders,
    mt.total AS month_total,
    ROUND(100.0 * mo.num_orders / mt.total, 1) AS pct_of_month
FROM monthly_orders mo
JOIN monthly_totals mt ON mo.month = mt.month
WHERE mo.order_status = 'Delivered'
ORDER BY mo.month;
