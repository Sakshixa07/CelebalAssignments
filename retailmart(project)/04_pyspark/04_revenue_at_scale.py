"""
RetailMart | 04 - PySpark
---------------------------
Same "monthly revenue / top products / customer 360" questions as the SQL
layer, but expressed with the Spark DataFrame API and Spark SQL, the way
they'd actually run once RetailMart's order volume outgrows what a single
machine (and SQLite) can comfortably handle.

Demonstrates: schema definition, DataFrame transformations, Spark SQL,
window functions at scale, and writing partitioned Parquet output.
"""
import os

from pyspark.sql import SparkSession, Window
from pyspark.sql import functions as F
from pyspark.sql.types import (StructType, StructField, StringType,
                                DoubleType, IntegerType, DateType)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output_parquet")


def get_spark():
    return (
        SparkSession.builder
        .appName("RetailMart-RevenueAtScale")
        .master("local[*]")
        .config("spark.sql.shuffle.partitions", "8")  # small for local/demo runs
        .getOrCreate()
    )


ORDERS_SCHEMA = StructType([
    StructField("order_id", StringType(), False),
    StructField("customer_id", StringType(), True),
    StructField("product_id", StringType(), True),
    StructField("quantity", IntegerType(), True),
    StructField("unit_price", DoubleType(), True),
    StructField("order_date", DateType(), True),
    StructField("delivery_date", DateType(), True),
    StructField("delivery_days", DoubleType(), True),
    StructField("line_revenue", DoubleType(), True),
    StructField("order_status", StringType(), True),
])


def main():
    spark = get_spark()
    spark.sparkContext.setLogLevel("ERROR")

    # orders_clean.csv has an extra is_valid_quantity column beyond our schema;
    # read with permissive mode + explicit column selection so Spark ignores it
    orders_raw = (
        spark.read
        .option("header", True)
        .option("inferSchema", True)
        .csv(os.path.join(DATA_DIR, "orders_clean.csv"))
    )
    orders = orders_raw.select(
        "order_id", "customer_id", "product_id",
        F.col("quantity").cast(IntegerType()),
        F.col("unit_price").cast(DoubleType()),
        F.to_date("order_date").alias("order_date"),
        F.to_date("delivery_date").alias("delivery_date"),
        F.col("delivery_days").cast(DoubleType()),
        F.col("line_revenue").cast(DoubleType()),
        "order_status",
    )

    products = spark.read.option("header", True).option("inferSchema", True) \
        .csv(os.path.join(DATA_DIR, "products.csv"))
    customers = spark.read.option("header", True).option("inferSchema", True) \
        .csv(os.path.join(DATA_DIR, "customers.csv")).dropDuplicates(["customer_id"])

    orders.cache()

    print("=" * 55)
    print("SCHEMA")
    print("=" * 55)
    orders.printSchema()

    fulfilled = orders.filter(F.col("order_status").isin("Delivered", "Shipped"))

    # --- Monthly revenue (DataFrame API) ---
    print("=" * 55)
    print("MONTHLY REVENUE")
    print("=" * 55)
    monthly_revenue = (
        fulfilled
        .withColumn("month", F.date_format("order_date", "yyyy-MM"))
        .groupBy("month")
        .agg(
            F.count("*").alias("num_orders"),
            F.round(F.sum("line_revenue"), 2).alias("total_revenue"),
            F.round(F.avg("line_revenue"), 2).alias("avg_order_value"),
        )
        .orderBy("month")
    )
    monthly_revenue.show(20, truncate=False)

    # --- Top products per category using a Window function (Spark SQL) ---
    print("=" * 55)
    print("TOP 3 PRODUCTS PER CATEGORY (Window function)")
    print("=" * 55)
    fulfilled.createOrReplaceTempView("orders_v")
    products.createOrReplaceTempView("products_v")

    top_products = spark.sql("""
        WITH product_revenue AS (
            SELECT
                p.category,
                p.product_name,
                ROUND(SUM(o.line_revenue), 2) AS total_revenue
            FROM orders_v o
            JOIN products_v p ON o.product_id = p.product_id
            GROUP BY p.category, p.product_name
        ),
        ranked AS (
            SELECT *,
                   RANK() OVER (PARTITION BY category ORDER BY total_revenue DESC) AS rnk
            FROM product_revenue
        )
        SELECT category, product_name, total_revenue, rnk
        FROM ranked
        WHERE rnk <= 3
        ORDER BY category, rnk
    """)
    top_products.show(30, truncate=False)

    # --- Customer 360 at scale (broadcast join since customers/products are small) ---
    print("=" * 55)
    print("CUSTOMER 360 (broadcast join demo)")
    print("=" * 55)
    customer_360 = (
        fulfilled
        .join(F.broadcast(customers), "customer_id")
        .groupBy("customer_id", "customer_name", "city")
        .agg(
            F.count("order_id").alias("total_orders"),
            F.round(F.sum("line_revenue"), 2).alias("lifetime_spend"),
        )
        .orderBy(F.desc("lifetime_spend"))
    )
    customer_360.show(10, truncate=False)

    # --- Write partitioned Parquet (Bronze-style output partitioned by status) ---
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    orders.write.mode("overwrite").partitionBy("order_status") \
        .parquet(os.path.join(OUTPUT_DIR, "orders_by_status"))
    print(f"\nPartitioned Parquet written to: {OUTPUT_DIR}/orders_by_status")

    print("\nRow count check:", orders.count(), "orders processed")

    spark.stop()


if __name__ == "__main__":
    main()
