"""
RetailMart - Raw Data Generator
--------------------------------
Generates realistic (and realistically MESSY) raw CSV files that simulate
what a fast-growing e-commerce company's scattered systems would produce:

    customers.csv   - customer master data (with dupes / inconsistent casing)
    products.csv     - product catalogue (with price changes over time removed -
                        SCD2 history is built later in the Delta Lake layer)
    orders.csv        - order transactions (missing values, bad dates, dupes)
    payments.csv      - payment transactions linked to orders

Run:  python3 generate_data.py
"""
import random
import uuid
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)
np.random.seed(42)

N_CUSTOMERS = 800
N_PRODUCTS = 150
N_ORDERS = 6000
START_DATE = datetime(2025, 1, 1)
END_DATE = datetime(2026, 7, 31)

CATEGORIES = {
    "Electronics": (1500, 60000),
    "Fashion": (299, 4999),
    "Home & Kitchen": (199, 15000),
    "Beauty": (99, 2999),
    "Sports": (399, 12000),
    "Books": (99, 1499),
    "Grocery": (49, 999),
}

CITIES = ["Delhi", "Mumbai", "Bengaluru", "Pune", "Hyderabad", "Chennai",
          "Kolkata", "Ahmedabad", "Jaipur", "Lucknow"]

ORDER_STATUSES = ["Delivered", "Delivered", "Delivered", "Delivered",
                   "Shipped", "Processing", "Cancelled", "Returned"]

PAYMENT_METHODS = ["Credit Card", "Debit Card", "UPI", "Net Banking", "COD", "Wallet"]
PAYMENT_STATUSES = ["Success", "Success", "Success", "Success", "Failed", "Refunded"]


def random_date(start, end):
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days),
                              seconds=random.randint(0, 86400))


# ---------------------------------------------------------------------------
# 1. CUSTOMERS  (with intentional duplicates + inconsistent casing/spacing)
# ---------------------------------------------------------------------------
def generate_customers():
    rows = []
    for i in range(1, N_CUSTOMERS + 1):
        cust_id = f"CUST{i:05d}"
        name = fake.name()
        email = fake.email()
        city = random.choice(CITIES)
        signup_date = random_date(START_DATE - timedelta(days=200), END_DATE)
        rows.append({
            "customer_id": cust_id,
            "customer_name": name,
            "email": email,
            "city": city,
            "signup_date": signup_date.strftime("%Y-%m-%d"),
        })

    df = pd.DataFrame(rows)

    # inject messiness: duplicate ~3% of customers with inconsistent city casing
    dupes = df.sample(frac=0.03, random_state=1).copy()
    dupes["city"] = dupes["city"].str.upper()
    df = pd.concat([df, dupes], ignore_index=True)

    # inject a few missing emails
    missing_idx = df.sample(frac=0.02, random_state=2).index
    df.loc[missing_idx, "email"] = np.nan

    return df.sample(frac=1, random_state=3).reset_index(drop=True)


# ---------------------------------------------------------------------------
# 2. PRODUCTS
# ---------------------------------------------------------------------------
def generate_products():
    rows = []
    for i in range(1, N_PRODUCTS + 1):
        category = random.choice(list(CATEGORIES.keys()))
        lo, hi = CATEGORIES[category]
        price = round(random.uniform(lo, hi), 2)
        rows.append({
            "product_id": f"PROD{i:04d}",
            "product_name": f"{fake.word().capitalize()} {category.split()[0]} {random.choice(['Pro','Lite','Max','Plus',''])}".strip(),
            "category": category,
            "price": price,
            "cost": round(price * random.uniform(0.55, 0.8), 2),
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 3. ORDERS (with missing delivery dates, bad status values, some dupes)
# ---------------------------------------------------------------------------
def generate_orders(customers_df, products_df):
    cust_ids = customers_df["customer_id"].unique().tolist()
    prod_ids = products_df["product_id"].tolist()
    prod_price_map = dict(zip(products_df["product_id"], products_df["price"]))

    rows = []
    for i in range(1, N_ORDERS + 1):
        order_id = f"ORD{i:06d}"
        cust_id = random.choice(cust_ids)
        prod_id = random.choice(prod_ids)
        qty = random.randint(1, 5)
        order_date = random_date(START_DATE, END_DATE)
        status = random.choice(ORDER_STATUSES)

        # delivery date: only present if delivered; some missing even when delivered (data quality issue)
        delivery_date = ""
        if status == "Delivered":
            days_to_deliver = random.randint(1, 12)
            if random.random() > 0.05:  # 5% missing on purpose
                delivery_date = (order_date + timedelta(days=days_to_deliver)).strftime("%Y-%m-%d")

        unit_price = prod_price_map[prod_id]

        rows.append({
            "order_id": order_id,
            "customer_id": cust_id,
            "product_id": prod_id,
            "quantity": qty,
            "unit_price": unit_price,
            "order_date": order_date.strftime("%Y-%m-%d"),
            "delivery_date": delivery_date,
            "order_status": status,
        })

    df = pd.DataFrame(rows)

    # inject exact duplicate order rows (system re-sent same record)
    dupes = df.sample(frac=0.015, random_state=4)
    df = pd.concat([df, dupes], ignore_index=True)

    # inject a few negative/zero quantities (bad data)
    bad_idx = df.sample(frac=0.005, random_state=5).index
    df.loc[bad_idx, "quantity"] = 0

    return df.sample(frac=1, random_state=6).reset_index(drop=True)


# ---------------------------------------------------------------------------
# 4. PAYMENTS
# ---------------------------------------------------------------------------
def generate_payments(orders_df):
    rows = []
    for _, order in orders_df.drop_duplicates("order_id").iterrows():
        amount = round(order["quantity"] * order["unit_price"], 2)
        status = random.choice(PAYMENT_STATUSES)
        if order["order_status"] == "Cancelled":
            status = "Refunded"
        rows.append({
            "payment_id": f"PAY{uuid.uuid4().hex[:8].upper()}",
            "order_id": order["order_id"],
            "payment_method": random.choice(PAYMENT_METHODS),
            "amount": amount,
            "payment_status": status,
            "payment_date": order["order_date"],
        })
    return pd.DataFrame(rows)


def main():
    print("Generating customers...")
    customers = generate_customers()
    print("Generating products...")
    products = generate_products()
    print("Generating orders...")
    orders = generate_orders(customers, products)
    print("Generating payments...")
    payments = generate_payments(orders)

    customers.to_csv("customers.csv", index=False)
    products.to_csv("products.csv", index=False)
    orders.to_csv("orders.csv", index=False)
    payments.to_csv("payments.csv", index=False)

    print(f"\ncustomers.csv : {len(customers):,} rows")
    print(f"products.csv  : {len(products):,} rows")
    print(f"orders.csv    : {len(orders):,} rows")
    print(f"payments.csv  : {len(payments):,} rows")
    print("\nDone. Files written to current directory.")


if __name__ == "__main__":
    main()
