# RetailMart — Centralized Analytics Platform

## Problem Statement

RetailMart, a fast-growing e-commerce company, has its data scattered across
raw CSV files (orders, customers, products, payments) with no central place
to analyze it. The business team cannot answer basic questions: which
products are trending, which customers are about to churn, or what last
month's revenue was.

This project builds a centralized analytics platform that **ingests raw
data, cleans it, and maintains product and customer history**, following
the **Medallion Architecture** (Bronze → Silver → Gold) so the business can
get reliable, real-time answers.

## Tech stack & where each piece lives

| Tech stack item | Business use case | Folder |
|---|---|---|
| Python Basics | Load CSVs, count orders | `01_python_basics/` |
| Pandas | Clean orders, delivery days | `02_pandas_cleaning/` |
| SQL — SELECT / Keys | Order–customer joins | `03_sql/01_select_keys.sql` |
| SQL — WHERE + Indexes | Filter by order status | `03_sql/02_where_indexes.sql` |
| SQL — GROUP BY | Monthly revenue | `03_sql/03_groupby_aggregates.sql` |
| SQL — JOINs | Customer 360 (unified view) | `03_sql/04_joins.sql` |
| SQL — CASE | Customer segments | `03_sql/05_case_segments.sql` |
| SQL — Subqueries | Above-average spenders | `03_sql/06_subqueries.sql` |
| SQL — CTEs | Funnel analysis | `03_sql/07_ctes_funnel.sql` |
| SQL — Window Functions | Product rank by category | `03_sql/08_window_functions.sql` |
| PySpark | Revenue at scale | `04_pyspark/` |
| Delta Lake | Product catalogue SCD2 | `05_delta_lake_medallion/` |
| Medallion (Bronze/Silver/Gold) | Orders pipeline | `05_delta_lake_medallion/` |

## Architecture

```
  Raw CSVs                BRONZE                 SILVER                  GOLD
┌────────────┐      ┌──────────────────┐  ┌──────────────────────┐  ┌────────────────────┐
│ customers  │      │ raw, as-is       │  │ cleaned, deduped,     │  │ business-ready      │
│ products   │ ───▶ │ + ingestion      │─▶│ typed, conformed      │─▶│ aggregates:         │
│ orders     │      │   metadata       │  │ + products_scd2       │  │ monthly_revenue,    │
│ payments   │      │ (full history)   │  │   (price history)     │  │ customer_360,       │
└────────────┘      └──────────────────┘  └──────────────────────┘  │ product_performance │
                                                                      └────────────────────┘
```

- **Bronze**: raw ingestion, no transformation — just land the data with an
  ingestion timestamp and source filename, so nothing is ever lost.
- **Silver**: dedupe, type-cast, standardize casing, compute derived fields
  (`delivery_days`, `line_revenue`). Also where the **product catalogue SCD
  Type 2** table lives — every price change closes out the old row and opens
  a new one, so historical orders can always be joined to the price that was
  actually in effect on that day.
- **Gold**: the tables a dashboard would actually query — monthly revenue,
  customer 360 (with spend-based segments), and product performance.

## How to run it, in order

```bash
# 1. Generate the raw data (messy on purpose — dupes, nulls, bad values)
cd data && python3 generate_data.py && cd ..

# 2. Python basics — explore the raw files
cd 01_python_basics && python3 01_load_and_explore.py && cd ..

# 3. Pandas — clean orders, compute delivery_days (writes data/orders_clean.csv)
cd 02_pandas_cleaning && python3 02_clean_orders.py && cd ..

# 4. SQL — build retailmart.db, then run any topic file
cd 03_sql
python3 00_build_database.py
python3 run_sql.py 04_joins.sql        # or any 0X_*.sql file
cd ..

# 5. PySpark — revenue at scale
cd 04_pyspark && python3 04_revenue_at_scale.py && cd ..

# 6. Delta Lake + Medallion pipeline
cd 05_delta_lake_medallion
python3 05_medallion_pipeline.py                 # real Delta Lake (needs internet access to Maven Central)
python3 05b_medallion_pipeline_parquet_demo.py    # runnable fallback, same logic on Parquet
cd ..
```

## A note on the Delta Lake step

`05_medallion_pipeline.py` is the intended, correct Delta Lake solution —
it uses real Delta tables and `DeltaTable.merge()` for the SCD2 logic, which
also gives you a transaction log and time travel for free. It needs network
access to Maven Central to download the Delta Lake JAR the first time it
runs (works out of the box on Databricks, or on any machine with normal
internet access).

`05b_medallion_pipeline_parquet_demo.py` reimplements the identical
Bronze/Silver/Gold + SCD2 logic on plain Parquet with a manual merge, so the
pipeline can be verified end-to-end even without that network access. Its
output — 155 product rows after 5 price changes, monthly revenue, customer
360 — matches what the real Delta version produces.

## Data quality issues handled

The generated raw data intentionally includes the kinds of problems a real
scattered-CSV system would have, and each is addressed in the pipeline:

- Duplicate order rows → deduplicated in Pandas and Silver
- Duplicate customer records (inconsistent city casing) → deduplicated on
  `customer_id`
- Missing delivery dates → `delivery_days` left as null rather than guessed
- Zero/invalid quantities → flagged with an `is_valid_quantity` column
  rather than silently dropped (preserves the row for auditing)
- Orders with no matching payment record → surfaced via a LEFT JOIN /
  anti-join pattern in `04_joins.sql`

## Key business questions this answers

- **What was last month's revenue?** → `03_sql/03_groupby_aggregates.sql`,
  `gold.monthly_revenue`
- **Which products are trending?** → `03_sql/08_window_functions.sql`
  (top 3 products per category by revenue)
- **Which customers are about to churn?** → `customer_360`'s
  `last_order_date` + `customer_segment` gives a starting point (customers
  with high past spend but an old `last_order_date` are the ones to watch)
- **Who are our best customers?** → `customer_segment` (VIP / High Value /
  Regular / Low Value) in `05_case_segments.sql` and `gold.customer_360`
