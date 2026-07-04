/* ============================================================================
   CUSTOMER SALES INSIGHTS MINI-PROJECT
   Superstore Dataset - Advanced SQL (Subqueries, CTEs, Window Functions)
   Engine: SQLite (ANSI-standard syntax; also runs on PostgreSQL / MySQL 8+)
   ============================================================================
   Dataset: Sample Superstore (9,994 order-line rows)
   Source table: superstore_raw  (loaded from CSV via build_db.py / pandas)
   ============================================================================ */


/* ============================================================================
   STEP 1: STAGING TABLE
   ----------------------------------------------------------------------------
   superstore_raw already exists (loaded directly from the CSV using pandas'
   to_sql in build_db.py). Below is the equivalent CREATE TABLE statement
   for reference / for engines where you load via LOAD DATA / COPY instead
   of pandas.
   ============================================================================ */

-- Reference DDL (already satisfied by build_db.py):
-- CREATE TABLE superstore_raw (
--     "Row ID"        INTEGER,
--     "Order ID"      TEXT,
--     "Order Date"    TEXT,
--     "Ship Date"     TEXT,
--     "Ship Mode"     TEXT,
--     "Customer ID"   TEXT,
--     "Customer Name" TEXT,
--     "Segment"       TEXT,
--     "Country"       TEXT,
--     "City"          TEXT,
--     "State"         TEXT,
--     "Postal Code"   REAL,
--     "Region"        TEXT,
--     "Product ID"    TEXT,
--     "Category"      TEXT,
--     "Sub-Category"  TEXT,
--     "Product Name"  TEXT,
--     "Sales"         REAL,
--     "Quantity"      REAL,
--     "Discount"      REAL,
--     "Profit"        REAL
-- );

SELECT COUNT(*) AS staging_row_count FROM superstore_raw;


/* ============================================================================
   STEP 2: NORMALIZED SCHEMA - customers, products, orders
   ============================================================================ */

DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;

-- NOTE ON DESIGN: a Customer ID in this dataset can appear with more than one
-- City/State/Region (the same customer ships orders to different locations
-- over time). Those are properties of the SHIPMENT, not stable attributes of
-- the customer, so city/state/region live on `orders`, while `customers`
-- keeps only attributes that are one-to-one with a customer.

CREATE TABLE customers (
    customer_id    TEXT PRIMARY KEY,
    customer_name  TEXT,
    segment        TEXT,
    country        TEXT
);

CREATE TABLE products (
    product_id     TEXT PRIMARY KEY,
    category       TEXT,
    sub_category   TEXT,
    product_name   TEXT
);

CREATE TABLE orders (
    row_id         INTEGER PRIMARY KEY,
    order_id       TEXT,
    order_date     TEXT,
    ship_date      TEXT,
    ship_mode      TEXT,
    customer_id    TEXT,
    product_id     TEXT,
    city           TEXT,
    state          TEXT,
    region         TEXT,
    sales          REAL,
    quantity       REAL,
    discount       REAL,
    profit         REAL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id)  REFERENCES products(product_id)
);


/* ============================================================================
   STEP 3: POPULATE TABLES USING SELECT DISTINCT
   ============================================================================ */

-- customers: one row per unique customer (stable attributes only --
-- city/state/region are shipment-level, so they live on `orders` instead,
-- since the same customer_id ships to multiple locations in this dataset)
INSERT INTO customers (customer_id, customer_name, segment, country)
SELECT DISTINCT
    "Customer ID",
    "Customer Name",
    "Segment",
    "Country"
FROM superstore_raw;

-- products: one row per unique product.
-- Data-quality note: 32 Product IDs carry two slightly different Product Name
-- spellings in the raw source (a known quirk of this dataset), so a plain
-- SELECT DISTINCT would violate the product_id primary key. MIN(Product Name)
-- deterministically picks one canonical name per product_id.
INSERT INTO products (product_id, category, sub_category, product_name)
SELECT
    "Product ID",
    "Category",
    "Sub-Category",
    MIN("Product Name")
FROM superstore_raw
GROUP BY "Product ID", "Category", "Sub-Category";

-- orders: one row per order line. row_id is already unique per source row,
-- so SELECT DISTINCT here is a no-op safety net (guards against accidental
-- source duplicates) rather than a true dedup step.
INSERT INTO orders (row_id, order_id, order_date, ship_date, ship_mode,
                     customer_id, product_id, city, state, region,
                     sales, quantity, discount, profit)
SELECT DISTINCT
    "Row ID",
    "Order ID",
    "Order Date",
    "Ship Date",
    "Ship Mode",
    "Customer ID",
    "Product ID",
    "City",
    "State",
    "Region",
    "Sales",
    "Quantity",
    "Discount",
    "Profit"
FROM superstore_raw;

SELECT
    (SELECT COUNT(*) FROM customers) AS n_customers,
    (SELECT COUNT(*) FROM products)  AS n_products,
    (SELECT COUNT(*) FROM orders)    AS n_orders;


/* ============================================================================
   STEP 4: SUBQUERIES
   ============================================================================ */

-- 4a. Order lines with sales ABOVE the overall average sale amount
SELECT
    row_id, order_id, customer_id, product_id, sales
FROM orders
WHERE sales > (SELECT AVG(sales) FROM orders)
ORDER BY sales DESC;

-- 4b. Each customer's single HIGHEST-VALUE order (correlated subquery)
--     i.e. for every customer, find the order_id whose total order sales
--     is the max among all their orders.
SELECT
    o.customer_id,
    o.order_id,
    o.order_total
FROM (
    SELECT customer_id, order_id, SUM(sales) AS order_total
    FROM orders
    GROUP BY customer_id, order_id
) o
WHERE o.order_total = (
    SELECT MAX(o2.order_total)
    FROM (
        SELECT customer_id, order_id, SUM(sales) AS order_total
        FROM orders
        GROUP BY customer_id, order_id
    ) o2
    WHERE o2.customer_id = o.customer_id
)
ORDER BY o.order_total DESC;

-- 4c. Customers whose TOTAL lifetime sales exceed the average total sales
--     across all customers (subquery inside a subquery / nested aggregate)
SELECT customer_id, total_sales
FROM (
    SELECT customer_id, SUM(sales) AS total_sales
    FROM orders
    GROUP BY customer_id
) cust_totals
WHERE total_sales > (
    SELECT AVG(total_sales) FROM (
        SELECT customer_id, SUM(sales) AS total_sales
        FROM orders
        GROUP BY customer_id
    )
)
ORDER BY total_sales DESC;


/* ============================================================================
   STEP 5: CTEs - customer-level aggregation
   ============================================================================ */

WITH customer_sales AS (
    SELECT
        customer_id,
        COUNT(DISTINCT order_id) AS num_orders,
        SUM(sales)               AS total_sales,
        SUM(profit)              AS total_profit,
        AVG(sales)               AS avg_line_sales
    FROM orders
    GROUP BY customer_id
)
SELECT *
FROM customer_sales
ORDER BY total_sales DESC
LIMIT 20;


/* ============================================================================
   STEP 6: WINDOW FUNCTIONS - ranking and analysis
   ============================================================================ */

-- 6a. ROW_NUMBER, RANK, DENSE_RANK of customers by total sales
WITH customer_sales AS (
    SELECT customer_id, SUM(sales) AS total_sales
    FROM orders
    GROUP BY customer_id
)
SELECT
    customer_id,
    total_sales,
    ROW_NUMBER() OVER (ORDER BY total_sales DESC) AS row_num,
    RANK()       OVER (ORDER BY total_sales DESC) AS sales_rank,
    DENSE_RANK() OVER (ORDER BY total_sales DESC) AS sales_dense_rank
FROM customer_sales
ORDER BY total_sales DESC;

-- 6b. Rank orders WITHIN each customer by order value (PARTITION BY)
WITH order_totals AS (
    SELECT customer_id, order_id, SUM(sales) AS order_total
    FROM orders
    GROUP BY customer_id, order_id
)
SELECT
    customer_id,
    order_id,
    order_total,
    RANK() OVER (PARTITION BY customer_id ORDER BY order_total DESC) AS rank_within_customer
FROM order_totals
ORDER BY customer_id, rank_within_customer;

-- 6c. Segmenting customers into quartiles by total sales (NTILE)
WITH customer_sales AS (
    SELECT customer_id, SUM(sales) AS total_sales
    FROM orders
    GROUP BY customer_id
)
SELECT
    customer_id,
    total_sales,
    NTILE(4) OVER (ORDER BY total_sales DESC) AS sales_quartile
FROM customer_sales
ORDER BY total_sales DESC;


/* ============================================================================
   STEP 7: JOIN + CTE + WINDOW FUNCTIONS -> FINAL RESULT SET
   (customer, total sales, rank)
   ============================================================================ */

WITH customer_sales AS (
    SELECT
        o.customer_id,
        SUM(o.sales)  AS total_sales,
        SUM(o.profit) AS total_profit,
        COUNT(DISTINCT o.order_id) AS num_orders
    FROM orders o
    GROUP BY o.customer_id
),
ranked_customers AS (
    SELECT
        cs.customer_id,
        c.customer_name,
        c.segment,
        cs.total_sales,
        cs.total_profit,
        cs.num_orders,
        ROW_NUMBER() OVER (ORDER BY cs.total_sales DESC) AS sales_rank
    FROM customer_sales cs
    JOIN customers c ON c.customer_id = cs.customer_id
)
SELECT *
FROM ranked_customers
ORDER BY sales_rank;


/* ============================================================================
   STEP 8: BUSINESS QUERIES
   ============================================================================ */

-- 8a. TOP 10 customers by total sales
WITH customer_sales AS (
    SELECT o.customer_id, SUM(o.sales) AS total_sales
    FROM orders o
    GROUP BY o.customer_id
)
SELECT
    c.customer_name,
    c.segment,
    cs.total_sales,
    RANK() OVER (ORDER BY cs.total_sales DESC) AS rank
FROM customer_sales cs
JOIN customers c ON c.customer_id = cs.customer_id
ORDER BY cs.total_sales DESC
LIMIT 10;

-- 8b. BOTTOM 10 (lowest-spending) customers by total sales
WITH customer_sales AS (
    SELECT o.customer_id, SUM(o.sales) AS total_sales
    FROM orders o
    GROUP BY o.customer_id
)
SELECT
    c.customer_name,
    c.segment,
    cs.total_sales,
    RANK() OVER (ORDER BY cs.total_sales ASC) AS rank_from_bottom
FROM customer_sales cs
JOIN customers c ON c.customer_id = cs.customer_id
ORDER BY cs.total_sales ASC
LIMIT 10;

-- 8c. SINGLE-ORDER customers (customers who placed exactly one order)
WITH customer_orders AS (
    SELECT customer_id, COUNT(DISTINCT order_id) AS num_orders
    FROM orders
    GROUP BY customer_id
)
SELECT
    c.customer_name,
    c.segment,
    co.num_orders
FROM customer_orders co
JOIN customers c ON c.customer_id = co.customer_id
WHERE co.num_orders = 1
ORDER BY c.customer_name;

-- 8d. Customers with ABOVE-AVERAGE total sales (subquery + CTE combined)
WITH customer_sales AS (
    SELECT o.customer_id, SUM(o.sales) AS total_sales
    FROM orders o
    GROUP BY o.customer_id
)
SELECT
    c.customer_name,
    c.segment,
    cs.total_sales,
    ROUND(cs.total_sales - (SELECT AVG(total_sales) FROM customer_sales), 2) AS diff_from_avg
FROM customer_sales cs
JOIN customers c ON c.customer_id = cs.customer_id
WHERE cs.total_sales > (SELECT AVG(total_sales) FROM customer_sales)
ORDER BY cs.total_sales DESC;

-- 8e. Sales distribution across customer segments (RANK per segment)
WITH customer_sales AS (
    SELECT o.customer_id, SUM(o.sales) AS total_sales
    FROM orders o
    GROUP BY o.customer_id
)
SELECT
    c.segment,
    c.customer_name,
    cs.total_sales,
    RANK() OVER (PARTITION BY c.segment ORDER BY cs.total_sales DESC) AS rank_in_segment
FROM customer_sales cs
JOIN customers c ON c.customer_id = cs.customer_id
ORDER BY c.segment, rank_in_segment
LIMIT 30;

/* ============================================================================
   END OF SCRIPT
   ============================================================================ */
