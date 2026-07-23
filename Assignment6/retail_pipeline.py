"""
Spark Architecture & Data Processing Pipeline
Dataset: new_retail_data.csv (Kaggle - Retail Analysis on Large Dataset)
Author: Hemant | Celebal Technologies Internship

Covers:
  1. Spark architecture (Driver / Cluster Manager / Executors) - see notes below
  2. Lazy evaluation + DAG / lineage
  3. Schema handling on read (CSV + Parquet)
  4. Filtering, column selection
  5. Renaming, casting, derived columns
  6. Transformations vs actions
  7. Wide transformation / shuffle + predicate pushdown
  8. CSV vs Parquet performance
  9. Null handling
  10. Full read -> transform -> filter -> write pipeline
  11. Best practices (no collect() on big data, use show()/limit())
"""

import time
from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType, DoubleType, LongType
)
from pyspark.sql.functions import (
    col, when, round as spark_round, to_date, year as sp_year,
    month as sp_month, trim, upper, count, sum as spark_sum, avg
)

# ---------------------------------------------------------------------------
# 1. SPARK ARCHITECTURE
# ---------------------------------------------------------------------------
# Driver: this Python process. It builds the logical plan (DAG), negotiates
#         resources with the Cluster Manager, and schedules tasks.
# Cluster Manager: here we use "local[*]" so the Driver itself acts as the
#         cluster manager, allocating threads on this one machine. On a real
#         cluster this would be YARN / Kubernetes / Spark Standalone, which
#         hands out Executors across worker nodes.
# Executors: JVM processes that actually run tasks (one task per partition)
#         and hold cached data in memory. In local mode, executors are
#         threads within this same JVM.
spark = (
    SparkSession.builder
    .appName("RetailDataPipeline")
    .master("local[*]")
    .config("spark.sql.shuffle.partitions", "8")  # small cluster -> fewer shuffle partitions
    .getOrCreate()
)
spark.sparkContext.setLogLevel("ERROR")

print("=" * 80)
print("SPARK ARCHITECTURE INFO")
print("=" * 80)
print(f"Spark version      : {spark.version}")
print(f"Master             : {spark.sparkContext.master}")
print(f"Default parallelism: {spark.sparkContext.defaultParallelism}  (this many executor cores/threads)")
print(f"App name / ID       : {spark.sparkContext.appName} / {spark.sparkContext.applicationId}")

# ---------------------------------------------------------------------------
# 2. SCHEMA HANDLING (explicit schema instead of inferSchema=True)
# ---------------------------------------------------------------------------
# Explicit schema avoids a full extra pass over the file (inferSchema scans
# the whole dataset once just to guess types) and guarantees correct types.
retail_schema = StructType([
    StructField("Transaction_ID",    DoubleType(), True),
    StructField("Customer_ID",       DoubleType(), True),
    StructField("Name",              StringType(), True),
    StructField("Email",             StringType(), True),
    StructField("Phone",             DoubleType(), True),
    StructField("Address",           StringType(), True),
    StructField("City",              StringType(), True),
    StructField("State",             StringType(), True),
    StructField("Zipcode",           DoubleType(), True),
    StructField("Country",           StringType(), True),
    StructField("Age",               DoubleType(), True),
    StructField("Gender",            StringType(), True),
    StructField("Income",            StringType(), True),
    StructField("Customer_Segment",  StringType(), True),
    StructField("Date",              StringType(), True),
    StructField("Year",              DoubleType(), True),
    StructField("Month",             StringType(), True),
    StructField("Time",              StringType(), True),
    StructField("Total_Purchases",   DoubleType(), True),
    StructField("Amount",            DoubleType(), True),
    StructField("Total_Amount",      DoubleType(), True),
    StructField("Product_Category",  StringType(), True),
    StructField("Product_Brand",     StringType(), True),
    StructField("Product_Type",      StringType(), True),
    StructField("Feedback",          StringType(), True),
    StructField("Shipping_Method",   StringType(), True),
    StructField("Payment_Method",    StringType(), True),
    StructField("Order_Status",      StringType(), True),
    StructField("Ratings",           DoubleType(), True),
    StructField("products",          StringType(), True),
])

CSV_PATH = "data/new_retail_data.csv"

print("\n" + "=" * 80)
print("READING CSV WITH EXPLICIT SCHEMA")
print("=" * 80)

t0 = time.time()
df_csv = (
    spark.read
    .option("header", "true")
    .schema(retail_schema)   # explicit schema -> no inference scan
    .csv(CSV_PATH)
)
# NOTE: this line above is still "lazy" - no data has been read yet.
# Spark only builds a logical plan. The line below (count) is an ACTION
# and is what actually triggers the job / file scan.
csv_row_count = df_csv.count()
csv_read_time = time.time() - t0
print(f"CSV row count       : {csv_row_count}")
print(f"CSV read+count time : {csv_read_time:.2f}s")

df_csv.printSchema()

# ---------------------------------------------------------------------------
# 3. LAZY EVALUATION + DAG / LINEAGE
# ---------------------------------------------------------------------------
# Everything from here (select, filter, withColumn...) is a TRANSFORMATION:
# Spark just extends the logical plan (DAG). Nothing executes until an
# ACTION (count, show, collect, write) is called. This lets Catalyst
# optimize the whole chain together (predicate/column pruning etc.)
# before any data actually moves.
print("\n" + "=" * 80)
print("LAZY EVALUATION DEMO - building a transformation chain (no execution yet)")
print("=" * 80)

lazy_chain = (
    df_csv
    .select("Transaction_ID", "Customer_ID", "Country", "Product_Category",
             "Total_Amount", "Date", "Order_Status", "Ratings")
    .filter(col("Total_Amount").isNotNull())
    .filter(col("Country") == "USA")
)
print("Chain built (nothing has run yet). Logical + physical plan:")
lazy_chain.explain(mode="formatted")   # shows DAG stages: Scan -> Filter -> Project

# ---------------------------------------------------------------------------
# 4. SELECT + FILTER + 5. RENAME / CAST / DERIVE + 9. NULL HANDLING
# ---------------------------------------------------------------------------
print("\n" + "=" * 80)
print("TRANSFORM: select, filter, rename, cast, derive columns, handle nulls")
print("=" * 80)

df_clean = (
    df_csv
    .select(
        col("Transaction_ID").cast(LongType()).alias("transaction_id"),
        col("Customer_ID").cast(LongType()).alias("customer_id"),
        trim(col("Country")).alias("country"),
        trim(col("State")).alias("state"),
        col("Age").cast(IntegerType()).alias("age"),
        trim(col("Gender")).alias("gender"),
        trim(col("Customer_Segment")).alias("customer_segment"),
        to_date(col("Date"), "M/d/yyyy").alias("txn_date"),
        col("Total_Purchases").cast(IntegerType()).alias("total_purchases"),
        spark_round(col("Amount"), 2).alias("unit_amount"),
        spark_round(col("Total_Amount"), 2).alias("total_amount"),
        upper(trim(col("Product_Category"))).alias("product_category"),
        trim(col("Product_Brand")).alias("product_brand"),
        trim(col("Payment_Method")).alias("payment_method"),
        trim(col("Order_Status")).alias("order_status"),
        col("Ratings").cast(IntegerType()).alias("ratings"),
    )
    # Handle nulls efficiently: drop rows missing critical business keys,
    # fill non-critical columns with sensible defaults instead of dropping.
    .dropna(subset=["transaction_id", "customer_id", "total_amount"])
    .fillna({"ratings": 0, "order_status": "Unknown", "product_brand": "Unknown"})
    # Derived column (a new business feature): high-value order flag
    .withColumn(
        "order_value_tier",
        when(col("total_amount") >= 500, "High")
        .when(col("total_amount") >= 150, "Medium")
        .otherwise("Low")
    )
    # Derived column from existing date column
    .withColumn("txn_year", sp_year(col("txn_date")))
    .withColumn("txn_month", sp_month(col("txn_date")))
)

df_clean.printSchema()
print("Sample of cleaned data:")
df_clean.show(5, truncate=False)   # show(), NOT collect() - best practice for large data

null_before = df_csv.filter(col("Total_Amount").isNull()).count()
null_after = df_clean.filter(col("total_amount").isNull()).count()
print(f"Rows with null Total_Amount before cleaning: {null_before}")
print(f"Rows with null total_amount after cleaning : {null_after}")
print(f"Rows after cleaning pipeline                : {df_clean.count()}")

# ---------------------------------------------------------------------------
# 6/7. TRANSFORMATIONS vs ACTIONS + WIDE TRANSFORMATION (shuffle)
# ---------------------------------------------------------------------------
# groupBy + agg is a WIDE transformation: rows for the same key can live on
# different partitions, so Spark must SHUFFLE data across the network/disk
# to bring matching keys together before aggregating. This is the most
# expensive operation type in Spark and the main thing to minimize.
print("\n" + "=" * 80)
print("WIDE TRANSFORMATION DEMO: groupBy + agg (triggers a shuffle)")
print("=" * 80)

category_summary = (
    df_clean.groupBy("product_category")
    .agg(
        count("*").alias("num_orders"),
        spark_sum("total_amount").alias("total_revenue"),
        avg("total_amount").alias("avg_order_value"),
    )
    .orderBy(col("total_revenue").desc())
)
print("Physical plan showing the Exchange (shuffle) step:")
category_summary.explain(mode="simple")
category_summary.show(20, truncate=False)   # action -> triggers the shuffle job

# ---------------------------------------------------------------------------
# 8. CSV vs PARQUET - WRITE
# ---------------------------------------------------------------------------
print("\n" + "=" * 80)
print("WRITE COMPARISON: CSV vs Parquet")
print("=" * 80)

t0 = time.time()
(df_clean.write.mode("overwrite").option("header", "true")
 .csv("output/cleaned_retail_csv"))
csv_write_time = time.time() - t0

t0 = time.time()
(df_clean.write.mode("overwrite")
 .partitionBy("txn_year")   # partitioning helps future predicate pushdown by year
 .parquet("output/cleaned_retail_parquet"))
parquet_write_time = time.time() - t0

print(f"CSV write time     : {csv_write_time:.2f}s")
print(f"Parquet write time : {parquet_write_time:.2f}s")

import subprocess
csv_size = subprocess.run(
    "du -sh output/cleaned_retail_csv | cut -f1", shell=True,
    capture_output=True, text=True
).stdout.strip()
parquet_size = subprocess.run(
    "du -sh output/cleaned_retail_parquet | cut -f1", shell=True,
    capture_output=True, text=True
).stdout.strip()
print(f"CSV output size on disk     : {csv_size}")
print(f"Parquet output size on disk : {parquet_size}")

# ---------------------------------------------------------------------------
# 8b. CSV vs PARQUET - READ + PREDICATE PUSHDOWN
# ---------------------------------------------------------------------------
print("\n" + "=" * 80)
print("READ COMPARISON + PREDICATE PUSHDOWN")
print("=" * 80)

t0 = time.time()
csv_readback = spark.read.option("header", "true").schema(df_clean.schema.remove(
    df_clean.schema.fieldNames().index("txn_year")
) if False else df_clean.schema).csv("output/cleaned_retail_csv")
csv_filtered_count = csv_readback.filter(col("product_category") == "CLOTHING").count()
csv_reread_time = time.time() - t0

t0 = time.time()
parquet_readback = spark.read.parquet("output/cleaned_retail_parquet")
parquet_filtered_count = parquet_readback.filter(col("product_category") == "CLOTHING").count()
parquet_reread_time = time.time() - t0

print(f"CSV     : filter(product_category == 'Clothing') -> {csv_filtered_count} rows in {csv_reread_time:.2f}s")
print(f"Parquet : filter(product_category == 'Clothing') -> {parquet_filtered_count} rows in {parquet_reread_time:.2f}s")

print("\nParquet physical plan (look for 'PushedFilters' - this is predicate pushdown,")
print("Spark skips reading row groups that can't match the filter, using Parquet's")
print("own column statistics, instead of reading everything and filtering in memory):")
parquet_readback.filter(col("product_category") == "CLOTHING").explain(mode="simple")

print("\nAlso note column pruning: Parquet is columnar, so selecting only 2-3 columns")
print("reads only those column chunks from disk. CSV is row-based and must read every")
print("column of every row regardless of what you select.")
t0 = time.time()
parquet_readback.select("product_category", "total_amount").filter(col("total_amount") > 500).count()
pruned_time = time.time() - t0
print(f"Parquet column-pruned scan (2 cols only) time: {pruned_time:.2f}s")

# ---------------------------------------------------------------------------
# 10. FULL PIPELINE SUMMARY (read -> transform -> filter -> write) already done above
# 11. BEST PRACTICES REMINDER
# ---------------------------------------------------------------------------
print("\n" + "=" * 80)
print("BEST PRACTICES APPLIED IN THIS SCRIPT")
print("=" * 80)
print("""
- Explicit schema on read instead of inferSchema (avoids an extra full scan)
- show()/count() used for inspection instead of collect() (never pulled full
  data to the driver - with 300K+ rows collect() risks driver OOM and is
  unnecessary since we only need to see samples or aggregates)
- Parquet used for the final storage layer -> columnar, compressed, supports
  predicate pushdown and column pruning, and is splittable for parallel reads
- partitionBy("txn_year") on Parquet write -> future queries filtering by
  year can skip whole partitions entirely (partition pruning)
- Reduced spark.sql.shuffle.partitions to 8 to match this small local
  environment (default 200 would create excessive tiny tasks here)
""")

spark.stop()
print("Spark session stopped.")
