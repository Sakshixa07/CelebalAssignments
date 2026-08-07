"""
RetailMart | 05b - Medallion pipeline, Parquet-based sandbox demo
--------------------------------------------------------------------
IMPORTANT CONTEXT FOR THIS FILE
================================
05_medallion_pipeline.py (the file next to this one) is the REAL, intended
solution: it uses actual Delta Lake tables and Delta's DeltaTable.merge()
API to implement SCD2. That is what you should show/submit as the
Delta Lake deliverable — it's correct Delta Lake code.

This file exists only because the sandbox this was built in has no network
access to Maven Central, so the Delta Lake JAR can't be downloaded here to
actually execute 05_medallion_pipeline.py. To prove the Bronze/Silver/Gold
+ SCD2 logic genuinely works (not just "looks right"), this version
reimplements the same pipeline using plain Parquet + manual merge logic
(union old-unaffected-rows + newly-closed-rows + newly-inserted-rows,
then overwrite) instead of DeltaTable.merge().

On your machine / Databricks / anywhere with normal internet access,
05_medallion_pipeline.py will run directly and is the better answer,
since it also gives you Delta's transaction log, time travel (see the
`history()` call in that file), and ACID guarantees that plain Parquet
doesn't have.

Run: python3 05b_medallion_pipeline_parquet_demo.py
"""
import os
import shutil

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
LAKE_DIR = os.path.join(os.path.dirname(__file__), "lakehouse_parquet_demo")

BRONZE = os.path.join(LAKE_DIR, "bronze")
SILVER = os.path.join(LAKE_DIR, "silver")
GOLD = os.path.join(LAKE_DIR, "gold")


def get_spark():
    return (
        SparkSession.builder
        .appName("RetailMart-Medallion-ParquetDemo")
        .master("local[*]")
        .config("spark.sql.shuffle.partitions", "8")
        .getOrCreate()
    )


def build_bronze(spark):
    print("\n" + "=" * 60)
    print("BRONZE LAYER — raw ingestion")
    print("=" * 60)
    for name in ["customers", "products", "orders", "payments"]:
        df = (
            spark.read.option("header", True).option("inferSchema", True)
            .csv(os.path.join(DATA_DIR, f"{name}.csv"))
            .withColumn("_ingested_at", F.current_timestamp())
            .withColumn("_source_file", F.lit(f"{name}.csv"))
        )
        path = os.path.join(BRONZE, name)
        df.write.mode("overwrite").parquet(path)
        print(f"  bronze.{name:<10} : {df.count():>6,} rows -> {path}")


def build_silver(spark):
    print("\n" + "=" * 60)
    print("SILVER LAYER — cleaned & conformed")
    print("=" * 60)

    customers = spark.read.parquet(os.path.join(BRONZE, "customers"))
    customers_silver = (
        customers
        .withColumn("city", F.initcap(F.trim("city")))
        .dropDuplicates(["customer_id"])
        .select("customer_id", "customer_name", "email", "city", "signup_date")
    )
    customers_silver.write.mode("overwrite").parquet(os.path.join(SILVER, "customers"))
    print(f"  silver.customers : {customers_silver.count():>6,} rows (deduped)")

    orders = spark.read.parquet(os.path.join(BRONZE, "orders"))
    orders_silver = (
        orders
        .dropDuplicates(["order_id"])
        .withColumn("order_date", F.to_date("order_date"))
        .withColumn("delivery_date", F.to_date("delivery_date"))
        .withColumn("is_valid_quantity", F.col("quantity") > 0)
        .withColumn("delivery_days",
                    F.when(F.col("delivery_date").isNotNull(),
                           F.datediff("delivery_date", "order_date")))
        .withColumn("line_revenue", F.col("quantity") * F.col("unit_price"))
        .withColumn("order_status", F.initcap(F.trim("order_status")))
        .select("order_id", "customer_id", "product_id", "quantity", "unit_price",
                "order_date", "delivery_date", "delivery_days", "line_revenue",
                "order_status", "is_valid_quantity")
    )
    orders_silver.write.mode("overwrite").parquet(os.path.join(SILVER, "orders"))
    print(f"  silver.orders    : {orders_silver.count():>6,} rows (deduped + cleaned)")

    payments = spark.read.parquet(os.path.join(BRONZE, "payments"))
    payments_silver = payments.dropDuplicates(["payment_id"]).select(
        "payment_id", "order_id", "payment_method", "amount", "payment_status", "payment_date"
    )
    payments_silver.write.mode("overwrite").parquet(os.path.join(SILVER, "payments"))
    print(f"  silver.payments  : {payments_silver.count():>6,} rows")


def build_products_scd2(spark):
    """
    Same SCD2 semantics as the real Delta version, implemented with a
    manual merge: read current table, split into (rows to close) and
    (rows untouched), union with newly-inserted current rows, overwrite.
    A real Delta table would do this in place with DeltaTable.merge()
    and get a transaction log + time travel for free (see 05_medallion_pipeline.py).
    """
    print("\n" + "=" * 60)
    print("SILVER LAYER — product catalogue SCD Type 2 (manual merge)")
    print("=" * 60)

    products = spark.read.parquet(os.path.join(BRONZE, "products"))
    path = os.path.join(SILVER, "products_scd2")

    scd2_init = (
        products
        .withColumn("effective_date", F.current_date())
        .withColumn("end_date", F.lit(None).cast("date"))
        .withColumn("is_current", F.lit(True))
        .select("product_id", "product_name", "category", "price", "cost",
                "effective_date", "end_date", "is_current")
    )
    scd2_init.write.mode("overwrite").parquet(path)
    print(f"  Initial load: {scd2_init.count():,} products, all is_current = true")

    # simulate a price change for 5 products
    sample = products.select("product_id", "price").limit(5)
    price_updates = sample.withColumn("new_price", F.round(F.col("price") * 1.10, 2)) \
        .select("product_id", "new_price")
    changed_ids = [r["product_id"] for r in price_updates.collect()]

    current = spark.read.parquet(path)

    # rows NOT affected by this update, unchanged
    untouched = current.filter(~F.col("product_id").isin(changed_ids))

    # rows being closed out (was current, now historical)
    closed = (
        current.filter(F.col("product_id").isin(changed_ids))
        .withColumn("end_date", F.current_date())
        .withColumn("is_current", F.lit(False))
    )

    # brand-new current rows with the updated price
    new_current = (
        products.join(price_updates, "product_id")
        .withColumn("price", F.col("new_price"))
        .withColumn("effective_date", F.current_date())
        .withColumn("end_date", F.lit(None).cast("date"))
        .withColumn("is_current", F.lit(True))
        .select("product_id", "product_name", "category", "price", "cost",
                "effective_date", "end_date", "is_current")
    )

    print("\n  Simulating a price increase for 5 products...")
    merged = untouched.unionByName(closed).unionByName(new_current)

    # write to a temp path first, then swap it in -- writing straight back
    # to `path` while lazily reading from it (via `current`) causes Spark
    # to look for source files that get deleted mid-job
    tmp_path = path + "_tmp"
    merged.write.mode("overwrite").parquet(tmp_path)
    shutil.rmtree(path)
    os.rename(tmp_path, path)

    final = spark.read.parquet(path)
    print(f"\n  products_scd2 total rows now: {final.count():,} "
          f"(5 products now have 2 rows: 1 closed + 1 current)")

    example_id = changed_ids[0]
    print("\n  History for one repriced product:")
    final.filter(F.col("product_id") == example_id) \
        .select("product_id", "price", "effective_date", "end_date", "is_current") \
        .orderBy("effective_date").show(truncate=False)


def build_gold(spark):
    print("\n" + "=" * 60)
    print("GOLD LAYER — business-ready aggregates")
    print("=" * 60)

    orders = spark.read.parquet(os.path.join(SILVER, "orders"))
    customers = spark.read.parquet(os.path.join(SILVER, "customers"))
    products = spark.read.parquet(os.path.join(SILVER, "products_scd2")).filter("is_current = true")

    fulfilled = orders.filter(F.col("order_status").isin("Delivered", "Shipped"))

    monthly_revenue = (
        fulfilled
        .withColumn("month", F.date_format("order_date", "yyyy-MM"))
        .groupBy("month")
        .agg(F.count("*").alias("num_orders"),
             F.round(F.sum("line_revenue"), 2).alias("total_revenue"))
        .orderBy("month")
    )
    monthly_revenue.write.mode("overwrite").parquet(os.path.join(GOLD, "monthly_revenue"))
    print(f"  gold.monthly_revenue : {monthly_revenue.count()} months")

    customer_360 = (
        fulfilled
        .join(customers, "customer_id")
        .groupBy("customer_id", "customer_name", "city")
        .agg(F.count("order_id").alias("total_orders"),
             F.round(F.sum("line_revenue"), 2).alias("lifetime_spend"),
             F.max("order_date").alias("last_order_date"))
        .withColumn(
            "customer_segment",
            F.when(F.col("lifetime_spend") >= 50000, "VIP")
             .when(F.col("lifetime_spend") >= 15000, "High Value")
             .when(F.col("lifetime_spend") >= 5000, "Regular")
             .otherwise("Low Value")
        )
    )
    customer_360.write.mode("overwrite").parquet(os.path.join(GOLD, "customer_360"))
    print(f"  gold.customer_360    : {customer_360.count():,} customers")

    product_perf = (
        fulfilled
        .join(products, "product_id")
        .groupBy("product_id", "product_name", "category")
        .agg(F.sum("quantity").alias("units_sold"),
             F.round(F.sum("line_revenue"), 2).alias("total_revenue"))
        .orderBy(F.desc("total_revenue"))
    )
    product_perf.write.mode("overwrite").parquet(os.path.join(GOLD, "product_performance"))
    print(f"  gold.product_performance : {product_perf.count()} products")

    print("\n  Sample: top 5 customers by lifetime spend")
    customer_360.orderBy(F.desc("lifetime_spend")).show(5, truncate=False)

    print("  Sample: monthly revenue")
    monthly_revenue.show(5, truncate=False)


def main():
    if os.path.exists(LAKE_DIR):
        shutil.rmtree(LAKE_DIR)

    spark = get_spark()
    spark.sparkContext.setLogLevel("ERROR")

    build_bronze(spark)
    build_silver(spark)
    build_products_scd2(spark)
    build_gold(spark)

    print("\n" + "=" * 60)
    print("MEDALLION PIPELINE COMPLETE (Parquet demo)")
    print("=" * 60)
    print(f"Lakehouse written to: {LAKE_DIR}")
    print("Note: this run used Parquet, not Delta Lake, due to a sandboxed")
    print("environment with no access to Maven Central. See the top of this")
    print("file and 05_medallion_pipeline.py for the real Delta Lake version.")

    spark.stop()


if __name__ == "__main__":
    main()
