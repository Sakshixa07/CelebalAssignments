# Customer Sales Insights — Superstore Dataset
### Mini-Project: Subqueries, CTEs & Window Functions in SQL

**Dataset:** Sample Superstore (9,994 order-line rows → 793 customers, 1,862 products)
**Total sales:** $2,297,200.86 | **Total profit:** $286,397.02

---

## 1. Approach

1. Loaded the raw CSV into a staging table `superstore_raw`.
2. Split it into a normalized schema — `customers`, `products`, `orders` — populated with `SELECT DISTINCT`.
3. Used **subqueries** to find above-average sales and each customer's highest-value order.
4. Used **CTEs** to compute per-customer aggregates (total sales, profit, order count).
5. Used **window functions** (`ROW_NUMBER`, `RANK`, `DENSE_RANK`, `NTILE`) to rank and segment customers.
6. Combined **JOIN + CTE + window functions** into one final ranked report.
7. Answered the assignment's business questions directly from the model.

A data-quality note worth documenting: 780 of 793 customer IDs appear with **more than one** shipping city/state/region across their orders, and 32 product IDs carry two slightly different spellings of the same product name. Both are known quirks of this dataset. They were resolved by keeping city/state/region on the `orders` table (a shipment-level attribute, not a customer-level one) and by picking one canonical product name with `MIN()`.

---

## 2. Business Query Results

### Top 10 customers by total sales
| Rank | Customer | Segment | Total Sales |
|---|---|---|---|
| 1 | Sean Miller | Home Office | $25,043.05 |
| 2 | Tamara Chand | Corporate | $19,052.22 |
| 3 | Raymond Buch | Consumer | $15,117.34 |
| 4 | Tom Ashbrook | Home Office | $14,595.62 |
| 5 | Adrian Barton | Consumer | $14,473.57 |
| 6 | Ken Lonsdale | Consumer | $14,175.23 |
| 7 | Sanjit Chand | Consumer | $14,142.33 |
| 8 | Hunter Lopez | Consumer | $12,873.30 |
| 9 | Sanjit Engle | Consumer | $12,209.44 |
| 10 | Christopher Conant | Consumer | $12,129.07 |

### Bottom 10 (lowest-spending) customers
| Rank | Customer | Segment | Total Sales |
|---|---|---|---|
| 1 | Thais Sissman | Consumer | $4.83 |
| 2 | Lela Donovan | Corporate | $5.30 |
| 3 | Carl Jackson | Corporate | $16.52 |
| 4 | Mitch Gastineau | Corporate | $16.74 |
| 5 | Roy Skaria | Home Office | $22.33 |
| 6 | Susan Gilcrest | Corporate | $47.95 |
| 7 | Ricardo Emerson | Consumer | $48.36 |
| 8 | Larry Blacks | Consumer | $50.19 |
| 9 | Adrian Shami | Home Office | $58.82 |
| 10 | Jasper Cacioppo | Consumer | $71.26 |

### Single-order customers (12 of 793, 1.5%)
Anemone Ratner, Anthony O'Donnell, Carl Jackson, Jenna Caffey, Jocasta Rupert, Lela Donovan, Mitch Gastineau, Patricia Hirasaki, Ricardo Emerson, Roland Murray, Susan MacKendrick, Theresa Coyne.

### Above-average customers
Average lifetime sales per customer: **$2,896.85**.
**294 of 793 customers (37%)** spend above this average — the rest cluster below it, indicating a right-skewed distribution typical of retail spend.

### Sales by segment
| Segment | Total Sales |
|---|---|
| Consumer | $1,161,401 |
| Corporate | $706,146 |
| Home Office | $429,653 |

### Sales by region
| Region | Total Sales | Orders |
|---|---|---|
| West | $725,458 | 1,611 |
| East | $678,781 | 1,401 |
| Central | $501,240 | 1,175 |
| South | $391,722 | 822 |

---

## 3. Key Insights

1. **Revenue is concentrated at the top.** The top 10 customers (1.3% of the base) each spent well above the $2,896.85 average — led by Sean Miller at $25,043 across just 5 orders.
2. **37% of customers (294/793) are above-average spenders**, confirming a long right tail: a minority of accounts drive a disproportionate share of the $2.3M total.
3. **High sales ≠ high profit.** Sean Miller, the #1 customer by sales, is actually **unprofitable overall (-$1,980 profit)** — likely from heavy discounting. Several other high-revenue customers (e.g., Becky Martin) show the same pattern. Sales rank should not be used alone to prioritize accounts; profit-adjusted ranking is needed for retention/growth decisions.
4. **Only 12 customers (1.5%) are single-order buyers** — the large majority of the base is repeat business, a healthy retention signal.
5. **Consumer is the largest segment by revenue** (~$1.16M) — about 1.6x Corporate and 2.7x Home Office — so broad promotions reach the most value when aimed at Consumer.
6. **West leads all regions** in both sales (~$725K) and order volume (1,611 orders), ahead of East, Central, and South, useful for prioritizing regional inventory and logistics investment.

---

## 4. Deliverables
- `superstore_analysis.sql` — full annotated SQL script (staging → schema → subqueries → CTEs → window functions → business queries)
- `Customer_Sales_Insights.ipynb` — executed Jupyter notebook with live outputs
- `build_db.py` — loads the CSV into SQLite as `superstore_raw`
- `superstore.csv` — cleaned source data (9,994 rows)
- This report (`insights_report.md`)
