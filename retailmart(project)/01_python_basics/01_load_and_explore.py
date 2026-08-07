"""
RetailMart | 01 - Python Basics
--------------------------------
Load the raw CSVs with plain Python (csv module, no pandas yet) and answer
the most basic business question: "how much data do we even have, and does
it look sane?"

This mirrors the very first thing a data engineer does on a new project:
open the files, count rows, and spot obvious problems before touching any
analysis logic.
"""
import csv
import os
from collections import Counter

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def load_csv(filename):
    path = os.path.join(DATA_DIR, filename)
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def main():
    customers = load_csv("customers.csv")
    products = load_csv("products.csv")
    orders = load_csv("orders.csv")
    payments = load_csv("payments.csv")

    print("=" * 50)
    print("RAW FILE ROW COUNTS")
    print("=" * 50)
    print(f"customers.csv : {len(customers):,} rows")
    print(f"products.csv  : {len(products):,} rows")
    print(f"orders.csv    : {len(orders):,} rows")
    print(f"payments.csv  : {len(payments):,} rows")

    # --- count orders by status (pure python, dict-based counting) ---
    status_counts = Counter(o["order_status"] for o in orders)
    print("\n" + "=" * 50)
    print("ORDER COUNT BY STATUS")
    print("=" * 50)
    for status, count in status_counts.most_common():
        print(f"{status:<12} {count:>6,}")

    # --- basic data quality checks ---
    print("\n" + "=" * 50)
    print("QUICK DATA QUALITY SCAN")
    print("=" * 50)
    missing_delivery = sum(1 for o in orders if o["order_status"] == "Delivered" and not o["delivery_date"])
    zero_qty = sum(1 for o in orders if int(o["quantity"]) == 0)
    missing_email = sum(1 for c in customers if not c["email"])
    unique_order_ids = len({o["order_id"] for o in orders})
    duplicate_orders = len(orders) - unique_order_ids

    print(f"Delivered orders missing a delivery_date : {missing_delivery:,}")
    print(f"Orders with quantity = 0                 : {zero_qty:,}")
    print(f"Customers missing an email                : {missing_email:,}")
    print(f"Duplicate order_id rows                   : {duplicate_orders:,}")

    print("\nConclusion: raw data is unreliable for direct analysis -> needs")
    print("cleaning (see 02_pandas_cleaning) before it can answer business")
    print("questions like 'what was last month's revenue?'.")


if __name__ == "__main__":
    main()
