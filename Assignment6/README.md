# Spark Data Processing Pipeline — Retail Dataset

**Dataset:** `new_retail_data.csv` (Kaggle — Retail Analysis on Large Dataset)
302,010 rows × 29 columns — customer demographics, transaction details, product info.

## Files
- `retail_pipeline.py` — full PySpark script (read → transform → filter → write)
- `run_output_clean.log` — execution output from running the script
- `output/cleaned_retail_csv/` — pipeline output written as CSV
- `output/cleaned_retail_parquet/` — pipeline output written as Parquet (partitioned by `txn_year`)

## Architecture concepts, applied

**Driver / Cluster Manager / Executors** — In this script, the Driver is the
Python process that builds the logical plan and schedules work. `master("local[*]")`
means the local machine's threads act as both cluster manager and executors
(on a real cluster this would be YARN/Kubernetes handing out Executor JVMs on
worker nodes). `defaultParallelism` in the run shows how many parallel task
slots were available.

**Lazy evaluation & DAG** — Every `select`/`filter`/`withColumn` call only
extends a logical plan; nothing runs until an action (`count`, `show`, `write`).
This is visible in the log: the "LAZY EVALUATION DEMO" section builds a chain
and only the following `.explain()` reveals the actual DAG (Scan → Filter →
Project) — Catalyst had already pushed the filters down into the scan itself.

**Wide transformation & shuffle** — `groupBy("product_category").agg(...)`
required an `Exchange hashpartitioning` step in the physical plan — data for
the same category living on different partitions had to be shuffled together
before aggregating. This is the single most expensive operation type in
Spark and the thing to minimize (fewer wide transformations, smaller
`shuffle.partitions` for small clusters, pre-partitioned storage for repeat
queries).

## Performance results (measured on this run)

| Metric | CSV | Parquet |
|---|---|---|
| Write time (301,021 rows) | 6.73s | 6.69s |
| Output size on disk | 36 MB | **7.4 MB** (~5x smaller) |
| Filtered read (`product_category == 'CLOTHING'`) | 1.20s | 0.98s |
| Column-pruned scan (2 of 19 columns) | — | 0.41s |

**Why Parquet wins:**
- **Columnar storage** — reading only 2 of 19 columns means Spark only pulls
  those column chunks off disk; CSV has to read every column of every row
  regardless of what's selected.
- **Predicate pushdown** — the physical plan for the Parquet filter shows
  `PushedFilters: [IsNotNull(product_category), EqualTo(product_category,CLOTHING)]`.
  Spark uses Parquet's own per-row-group statistics to skip whole chunks of
  data that can't match, instead of reading everything and filtering in memory.
- **Compression** — Parquet's columnar layout compresses far better than
  row-based CSV text, hence the 5x size reduction.
- **Partition pruning** — writing with `partitionBy("txn_year")` means a
  future query filtering by year can skip entire partition folders without
  even opening them.

CSV write/read times were comparable to Parquet at this data size (300K
rows fits comfortably in memory either way); the real cost of CSV shows up
in **storage volume** and **scan cost under repeated filtered/selective
reads** — both of which matter a lot more once the dataset is orders of
magnitude larger, or read many times downstream.

## Data quality handling

- 350 rows had a null `Total_Amount` in the raw CSV — dropped via
  `dropna(subset=[...])` since it's a required business metric.
- Non-critical nulls (ratings, order status, brand) were filled with
  defaults instead of dropped, to avoid losing otherwise-valid rows —
  301,021 of 302,010 rows survived cleaning.
- A small number of rows had a null `product_category`, visible as a
  `NULL` row in the groupBy summary — worth a follow-up data-quality note
  in a real project.

## Best practices followed

- Explicit `StructType` schema on read (no `inferSchema` — avoids an extra
  full file scan just to guess types).
- `show()` / `count()` used throughout instead of `collect()` — with
  300K+ rows, `collect()` would pull everything to the Driver's memory,
  risking an OOM and defeating the purpose of distributed processing.
- Final output written as partitioned Parquet for efficient downstream reads.
- `spark.sql.shuffle.partitions` tuned down from the default 200 to match
  this small local environment.
