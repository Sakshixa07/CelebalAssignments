"""
Loads the cleaned CSV files into a SQLite database (ecommerce.db) for SQL analysis.
"""

import sqlite3
import pandas as pd

DB_PATH = "ecommerce.db"
CLEAN_DIR = "cleaned"


def main():
    conn = sqlite3.connect(DB_PATH)

    customers = pd.read_csv(f"{CLEAN_DIR}/customers.csv")
    products = pd.read_csv(f"{CLEAN_DIR}/products.csv")
    orders = pd.read_csv(f"{CLEAN_DIR}/orders.csv", parse_dates=["order_date"])
    order_items = pd.read_csv(f"{CLEAN_DIR}/order_items.csv")

    # customer_id may be nullable Int64 with pd.NA -- convert cleanly for SQLite
    orders["customer_id"] = orders["customer_id"].astype("Int64")

    customers.to_sql("customers", conn, if_exists="replace", index=False)
    products.to_sql("products", conn, if_exists="replace", index=False)
    orders.to_sql("orders", conn, if_exists="replace", index=False)
    order_items.to_sql("order_items", conn, if_exists="replace", index=False)

    cur = conn.cursor()
    cur.execute("CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_items_order ON order_items(order_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_items_product ON order_items(product_id)")
    conn.commit()

    for table in ["customers", "products", "orders", "order_items"]:
        n = cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table}: {n} rows loaded")

    conn.close()
    print(f"Database ready at {DB_PATH}")


if __name__ == "__main__":
    main()
