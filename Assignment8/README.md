# E-Commerce Order Analytics System

An end-to-end data analytics pipeline: messy data generation → cleaning/validation →
SQLite loading → SQL analysis (16 queries) → CLI reporting tool → edge case tests.

## Project Structure

```
ecommerce_analytics/
├── generate_data.py       # Part 1: generates 4 messy CSVs into data/
├── data_cleaning.py       # Part 2: cleans data, writes cleaned/ + reports/data_quality_report.txt
├── load_db.py              # loads cleaned/*.csv into ecommerce.db (SQLite)
├── analysis_queries.sql   # Part 3: all 16 basic/intermediate/advanced SQL queries
├── cli_report.py           # Part 4: command-line summary report tool
├── test_edge_cases.py       # Part 5: edge case tests
├── data/                   # raw generated CSVs (with intentional issues)
├── cleaned/                # cleaned CSVs (output of data_cleaning.py)
├── reports/
│   └── data_quality_report.txt
└── ecommerce.db             # SQLite database (output of load_db.py)
```

## How to Run (in order)

```bash
pip install pandas   # only external dependency, needed for Parts 1-2

python3 generate_data.py     # -> data/*.csv (4 files, 500+ rows each)
python3 data_cleaning.py     # -> cleaned/*.csv + reports/data_quality_report.txt
python3 load_db.py           # -> ecommerce.db
sqlite3 ecommerce.db < analysis_queries.sql   # or run queries individually

python3 cli_report.py --report-type monthly --start 2026-01-01 --end 2026-01-31
# or run with no arguments for interactive prompts

python3 test_edge_cases.py   # -> runs the 4 required edge case tests
```

## Design Decisions

**Referential integrity (orders <-> order_items).** `generate_data.py` builds
`order_items` only from `order_id`s that were actually generated in `orders.csv`, so the
main dataset never contains orphaned rows by construction. The orphan scenario itself is
exercised deterministically in `test_edge_cases.py::test_orphan_order_item` rather than
being randomly (and untestably) buried in the generated data. `check_referential_integrity()`
in `data_cleaning.py` is the reusable function that would catch such orphans in any dataset
handed to it, including data that arrives from an external/less-trusted source.

**Missing `customer_id`.** Rather than inventing a fake customer, `clean_orders()` keeps
missing IDs as `NULL` (pandas `pd.NA` / SQLite `NULL`) and adds a `customer_id_missing_flag`
column, since fabricating an ID would corrupt customer-level aggregations (e.g. "top 10
customers by order value") without anyone noticing.

**Wrong-format dates.** `clean_orders()` tries the correct format first
(`YYYY-MM-DD HH:MM:SS`), then falls back to `DD-MM-YYYY`, then a general pandas parse as a
last resort, and any date it still can't parse becomes `NaT` and is reported — dates are
never silently dropped or guessed without a record of it.

**Negative quantity / returns.** Treated as legitimate data (returns), not an error. Revenue
formula (`quantity × unit_price × (1 - discount_percent/100)`) naturally nets returns against
purchases. Query 5 and 6 specifically analyze return behavior.

**Revenue with a bad `discount_percent`.** The generated dataset always produces
`discount_percent` in `[0, 100]`, but `test_edge_cases.py` proves *why* that constraint
matters: an unclamped 150% discount produces negative revenue from a sale, which is
nonsensical. Any pipeline that accepts external data should clamp discount to `[0, 100]`
before computing revenue.

## Data Quality Issues Injected (and where they're handled)

| Issue | Injected in | Detected/fixed by |
|---|---|---|
| 5% NULL `customer_id` | `generate_data.py` | `clean_orders()` |
| 3% negative quantity | `generate_data.py` | intentional (returns), analyzed in queries 5-6 |
| Wrong date format (DD-MM-YYYY) | `generate_data.py` | `clean_orders()` |
| Messy product names (spacing/case) | `generate_data.py` | `clean_products()` |
| 2% invalid emails | `generate_data.py` | `validate_emails()` |
| Orphaned `order_items` | `test_edge_cases.py` (synthetic) | `check_referential_integrity()` |
| `discount_percent` out of range | `test_edge_cases.py` (synthetic) | clamping logic (demonstrated in test) |
| `quantity = 0` | `test_edge_cases.py` (synthetic) | flagged, contributes 0 revenue, no crash |
| Future-dated orders | `test_edge_cases.py` (synthetic) | flagged separately, not rejected or silently accepted |

## SQL Queries (analysis_queries.sql)

**Basic:** total revenue per category · top 10 customers · month-wise order count (last 12 months)

**Intermediate:** customers never delivered · products with more returns than purchases ·
return rate per category

**Advanced:** running total per region (window function) · DENSE_RANK product ranking ·
LAG-based days-between-orders + "At Risk" flag · multi-level CTE customer tiering ·
NTILE quartile segmentation · year-over-year comparison · FIRST_VALUE/LAST_VALUE category
shift · cumulative revenue distribution · cohort retention analysis · self-join
"frequently bought together"
