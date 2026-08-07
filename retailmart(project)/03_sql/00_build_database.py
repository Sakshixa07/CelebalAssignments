"""
RetailMart | 03 - SQL Layer setup
----------------------------------
Loads the cleaned CSVs into a SQLite database (retailmart.db) so the SQL
topic files in this folder can be run directly against real data.

Run this once before executing any of the 0X_*.sql files:
    python3 00_build_database.py
    sqlite3 retailmart.db < 01_select_keys.sql
"""
import os
import sqlite3

import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
DB_PATH = os.path.join(os.path.dirname(__file__), "retailmart.db")

SCHEMA_SQL = """
DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    customer_id   TEXT PRIMARY KEY,
    customer_name TEXT NOT NULL,
    email         TEXT,
    city          TEXT,
    signup_date   TEXT
);

CREATE TABLE products (
    product_id   TEXT PRIMARY KEY,
    product_name TEXT NOT NULL,
    category     TEXT,
    price        REAL,
    cost         REAL
);

CREATE TABLE orders (
    order_id      TEXT PRIMARY KEY,
    customer_id   TEXT REFERENCES customers(customer_id),
    product_id    TEXT REFERENCES products(product_id),
    quantity      INTEGER,
    unit_price    REAL,
    order_date    TEXT,
    delivery_date TEXT,
    delivery_days REAL,
    line_revenue  REAL,
    order_status  TEXT
);

CREATE TABLE payments (
    payment_id     TEXT PRIMARY KEY,
    order_id       TEXT REFERENCES orders(order_id),
    payment_method TEXT,
    amount         REAL,
    payment_status TEXT,
    payment_date   TEXT
);

-- indexes to support WHERE-clause filtering and JOINs (see 02_where_indexes.sql)
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_product_id ON orders(product_id);
CREATE INDEX idx_orders_status ON orders(order_status);
CREATE INDEX idx_orders_date ON orders(order_date);
CREATE INDEX idx_payments_order_id ON payments(order_id);
"""


def main():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA_SQL)

    customers = pd.read_csv(os.path.join(DATA_DIR, "customers.csv"))
    products = pd.read_csv(os.path.join(DATA_DIR, "products.csv"))
    orders = pd.read_csv(os.path.join(DATA_DIR, "orders_clean.csv"))
    payments = pd.read_csv(os.path.join(DATA_DIR, "payments.csv"))

    # customers.csv intentionally contains duplicate customer_id rows (inconsistent
    # city casing) to simulate a real "same customer, two system records" problem.
    # We keep the first occurrence for the relational model; the duplicates
    # themselves are a good source-data-quality talking point for the report.
    dup_count = customers.duplicated(subset=["customer_id"]).sum()
    print(f"Note: {dup_count} duplicate customer_id rows found in raw customers.csv "
          f"(kept first occurrence, dropped rest)")
    customers = customers.drop_duplicates(subset=["customer_id"], keep="first")

    # orders_clean.csv has an extra is_valid_quantity column we don't need in SQL
    orders_cols = ["order_id", "customer_id", "product_id", "quantity", "unit_price",
                   "order_date", "delivery_date", "delivery_days", "line_revenue", "order_status"]
    orders = orders[orders_cols]

    customers.to_sql("customers", conn, if_exists="append", index=False)
    products.to_sql("products", conn, if_exists="append", index=False)
    orders.to_sql("orders", conn, if_exists="append", index=False)
    payments.to_sql("payments", conn, if_exists="append", index=False)

    conn.commit()

    print("Database built:", DB_PATH)
    for table in ["customers", "products", "orders", "payments"]:
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table:<12}: {count:,} rows")

    conn.close()


if __name__ == "__main__":
    main()
