"""
RetailMart | 05 - Delta Lake + Medallion Architecture
--------------------------------------------------------
Builds the full Bronze -> Silver -> Gold pipeline on Delta Lake tables:

  BRONZE  - raw data, ingested as-is (append-only, full history preserved)
  SILVER  - cleaned, deduped, typed, conformed to a business model
  GOLD    - aggregated, business-ready tables that power dashboards

Also implements SCD Type 2 for the product catalogue: when a product's
price changes, the old row is closed out (is_current = false, end_date set)
and a new row is inserted, so we can always answer "what did this product
cost on the day of that historical order?"

Run: python3 05_medallion_pipeline.py
"""
import os
import shutil

from delta import configure_spark_with_delta_pip
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from delta.tables import DeltaTable

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
LAKE_DIR = os.path.join(os.path.dirname(__file__), "lakehouse")

BRONZE = os.path.join(LAKE_DIR, "bronze")
SILVER = os.path.join(LAKE_DIR, "silver")
GOLD = os.path.join(LAKE_DIR, "gold")


def get_spark():
    builder = (
        SparkSession.builder
        .appName("RetailMart-Medallion")
        .master("local[*]")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        .config("spark.sql.shuffle.partitions", "8")
    )
    return configure_spark_with_delta_pip(builder).getOrCreate()


# ---------------------------------------------------------------------------
# BRONZE: raw ingestion, no transformation, just land the data as Delta
# ---------------------------------------------------------------------------
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
        df.write.format("delta").mode("overwrite").save(path)
        print(f"  bronze.{name:<10} : {df.count():>6,} rows -> {path}")


# ---------------------------------------------------------------------------
# SILVER: cleaned, deduped, typed
# ---------------------------------------------------------------------------
def build_silver(spark):
    print("\n" + "=" * 60)
    print("SILVER LAYER — cleaned & conformed")
    print("=" * 60)

    # customers: dedupe on customer_id, standardize city casing
    customers = spark.read.format("delta").load(os.path.join(BRONZE, "customers"))
    customers_silver = (
        customers
        .withColumn("city", F.initcap(F.trim("city")))
        .dropDuplicates(["customer_id"])
        .select("customer_id", "customer_name", "email", "city", "signup_date")
    )
    customers_silver.write.format("delta").mode("overwrite").save(os.path.join(SILVER, "customers"))
    print(f"  silver.customers : {customers_silver.count():>6,} rows (deduped)")

    # orders: dedupe, fix quantities, compute delivery_days + line_revenue
    orders = spark.read.format("delta").load(os.path.join(BRONZE, "orders"))
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
    orders_silver.write.format("delta").mode("overwrite").save(os.path.join(SILVER, "orders"))
    print(f"  silver.orders    : {orders_silver.count():>6,} rows (deduped + cleaned)")

    # payments: pass-through with type cleanup
    payments = spark.read.format("delta").load(os.path.join(BRONZE, "payments"))
    payments_silver = payments.dropDuplicates(["payment_id"]).select(
        "payment_id", "order_id", "payment_method", "amount", "payment_status", "payment_date"
    )
    payments_silver.write.format("delta").mode("overwrite").save(os.path.join(SILVER, "payments"))
    print(f"  silver.payments  : {payments_silver.count():>6,} rows")


# ---------------------------------------------------------------------------
# SILVER: Product catalogue as SCD Type 2
# ---------------------------------------------------------------------------
def init_product_scd2(spark):
    """First load: every product becomes an open (is_current=true) record."""
    products = spark.read.format("delta").load(os.path.join(BRONZE, "products"))
    scd2_init = (
        products
        .withColumn("effective_date", F.current_date())
        .withColumn("end_date", F.lit(None).cast("date"))
        .withColumn("is_current", F.lit(True))
        .select("product_id", "product_name", "category", "price", "cost",
                "effective_date", "end_date", "is_current")
    )
    path = os.path.join(SILVER, "products_scd2")
    scd2_init.write.format("delta").mode("overwrite").save(path)
    return DeltaTable.forPath(spark, path), scd2_init


def apply_price_change_scd2(spark, product_dt, price_updates_df):
    """
    price_updates_df: product_id, new_price columns for products whose
    price changed. Implements SCD2 with a two-step MERGE:
      1. close out the current row for any product being updated
      2. insert a brand-new current row with the new price
    """
    path = os.path.join(SILVER, "products_scd2")

    # Step 1: close out existing current rows for changed products
    updates_to_close = price_updates_df.select("product_id").distinct()
    (
        product_dt.alias("t")
        .merge(
            updates_to_close.alias("s"),
            "t.product_id = s.product_id AND t.is_current = true"
        )
        .whenMatchedUpdate(set={
            "end_date": F.current_date(),
            "is_current": F.lit(False),
        })
        .execute()
    )

    # Step 2: insert new current rows carrying the new price (attrs from bronze, price from update)
    bronze_products = spark.read.format("delta").load(os.path.join(BRONZE, "products"))
    new_rows = (
        bronze_products
        .join(price_updates_df, "product_id")
        .withColumn("price", F.col("new_price"))
        .withColumn("effective_date", F.current_date())
        .withColumn("end_date", F.lit(None).cast("date"))
        .withColumn("is_current", F.lit(True))
        .select("product_id", "product_name", "category", "price", "cost",
                "effective_date", "end_date", "is_current")
    )
    new_rows.write.format("delta").mode("append").save(path)
    return DeltaTable.forPath(spark, path)


def build_products_scd2(spark):
    print("\n" + "=" * 60)
    print("SILVER LAYER — product catalogue SCD Type 2")
    print("=" * 60)

    product_dt, initial_df = init_product_scd2(spark)
    print(f"  Initial load: {initial_df.count():,} products, all is_current = true")

    # simulate a price change event for 5 products (e.g. a quarterly repricing)
    bronze_products = spark.read.format("delta").load(os.path.join(BRONZE, "products"))
    sample = bronze_products.select("product_id", "price").limit(5)
    price_updates = sample.withColumn("new_price", F.round(F.col("price") * 1.10, 2)) \
        .select("product_id", "new_price")

    print("\n  Simulating a price increase for 5 products...")
    apply_price_change_scd2(spark, product_dt, price_updates)

    final = spark.read.format("delta").load(os.path.join(SILVER, "products_scd2"))
    print(f"\n  products_scd2 total rows now: {final.count():,} "
          f"(5 products now have 2 rows: 1 closed + 1 current)")

    print("\n  History for one repriced product:")
    example_id = price_updates.first()["product_id"]
    final.filter(F.col("product_id") == example_id) \
        .select("product_id", "price", "effective_date", "end_date", "is_current") \
        .orderBy("effective_date") \
        .show(truncate=False)

    print("  Time-travel query — Delta Lake versioning lets us also read the")
    print("  table AS OF an earlier version, independent of the SCD2 columns:")
    history = DeltaTable.forPath(spark, os.path.join(SILVER, "products_scd2")).history()
    history.select("version", "timestamp", "operation").show(truncate=False)


# ---------------------------------------------------------------------------
# GOLD: business-ready aggregates
# ---------------------------------------------------------------------------
def build_gold(spark):
    print("\n" + "=" * 60)
    print("GOLD LAYER — business-ready aggregates")
    print("=" * 60)

    orders = spark.read.format("delta").load(os.path.join(SILVER, "orders"))
    customers = spark.read.format("delta").load(os.path.join(SILVER, "customers"))
    products = spark.read.format("delta").load(os.path.join(SILVER, "products_scd2")) \
        .filter("is_current = true")

    fulfilled = orders.filter(F.col("order_status").isin("Delivered", "Shipped"))

    # Gold 1: monthly revenue
    monthly_revenue = (
        fulfilled
        .withColumn("month", F.date_format("order_date", "yyyy-MM"))
        .groupBy("month")
        .agg(
            F.count("*").alias("num_orders"),
            F.round(F.sum("line_revenue"), 2).alias("total_revenue"),
        )
        .orderBy("month")
    )
    monthly_revenue.write.format("delta").mode("overwrite").save(os.path.join(GOLD, "monthly_revenue"))
    print(f"  gold.monthly_revenue : {monthly_revenue.count()} months")

    # Gold 2: customer 360
    customer_360 = (
        fulfilled
        .join(customers, "customer_id")
        .groupBy("customer_id", "customer_name", "city")
        .agg(
            F.count("order_id").alias("total_orders"),
            F.round(F.sum("line_revenue"), 2).alias("lifetime_spend"),
            F.max("order_date").alias("last_order_date"),
        )
        .withColumn(
            "customer_segment",
            F.when(F.col("lifetime_spend") >= 50000, "VIP")
             .when(F.col("lifetime_spend") >= 15000, "High Value")
             .when(F.col("lifetime_spend") >= 5000, "Regular")
             .otherwise("Low Value")
        )
    )
    customer_360.write.format("delta").mode("overwrite").save(os.path.join(GOLD, "customer_360"))
    print(f"  gold.customer_360    : {customer_360.count():,} customers")

    # Gold 3: product performance (using current SCD2 price)
    product_perf = (
        fulfilled
        .join(products, "product_id")
        .groupBy("product_id", "product_name", "category")
        .agg(
            F.sum("quantity").alias("units_sold"),
            F.round(F.sum("line_revenue"), 2).alias("total_revenue"),
        )
        .orderBy(F.desc("total_revenue"))
    )
    product_perf.write.format("delta").mode("overwrite").save(os.path.join(GOLD, "product_performance"))
    print(f"  gold.product_performance : {product_perf.count()} products")

    print("\n  Sample: top 5 customers by lifetime spend")
    customer_360.orderBy(F.desc("lifetime_spend")).show(5, truncate=False)


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
    print("MEDALLION PIPELINE COMPLETE")
    print("=" * 60)
    print(f"Lakehouse written to: {LAKE_DIR}")
    print("  bronze/  - raw ingested tables")
    print("  silver/  - cleaned tables + products_scd2 (full history)")
    print("  gold/    - monthly_revenue, customer_360, product_performance")

    spark.stop()


if __name__ == "__main__":
    main()
