"""
Part 1: Data Generation
Generates 4 realistic-but-messy CSV files for the E-Commerce Order Analytics System:
    - customers.csv
    - products.csv
    - orders.csv
    - order_items.csv

Intentional data-quality issues (as required by the assignment):
    - 5% of orders have NULL customer_id
    - 3% of order_items have negative quantity (returns)
    - Some order_date values are in the wrong format (DD-MM-YYYY instead of YYYY-MM-DD HH:MM:SS)
    - Some product names have extra whitespace / inconsistent casing
    - 2% of emails are invalid (missing '@' or missing domain)

Referential integrity is guaranteed by construction: every order_items.order_id is
drawn from the pool of order_ids that were actually generated in orders.csv, and every
order_items.product_id is drawn from the pool of generated product_ids. We do NOT
inject "orphan" order_items here -- that scenario is exercised separately and
deterministically inside test_edge_cases.py so it can be tested in isolation rather
than randomly buried in the main dataset.
"""

import csv
import random
from datetime import datetime, timedelta

random.seed(42)  # reproducible runs

N_CUSTOMERS = 600
N_PRODUCTS = 150
N_ORDERS = 3000
# order_items will naturally exceed 500 rows since each order has 1-5 items

OUTPUT_DIR = "data"

FIRST_NAMES = ["Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Krishna",
               "Ishaan", "Rohan", "Priya", "Ananya", "Diya", "Isha", "Kavya", "Meera",
               "Neha", "Riya", "Saanvi", "Tara", "John", "Jane", "Michael", "Emily",
               "David", "Sarah", "Chris", "Laura", "James", "Anna"]
LAST_NAMES = ["Sharma", "Verma", "Gupta", "Kumar", "Singh", "Patel", "Reddy", "Nair",
              "Iyer", "Rao", "Smith", "Johnson", "Brown", "Taylor", "Wilson", "Clark",
              "Lewis", "Walker", "Hall", "Young"]

CATEGORIES = {
    "Electronics": ["Smartphones", "Laptops", "Headphones", "Cameras", "Accessories"],
    "Clothing": ["Men", "Women", "Kids", "Footwear", "Winterwear"],
    "Home": ["Kitchen", "Furniture", "Decor", "Lighting", "Bedding"],
    "Books": ["Fiction", "Non-Fiction", "Comics", "Academic", "Children"],
}

PRODUCT_ADJ = ["Premium", "Classic", "Deluxe", "Compact", "Pro", "Essential", "Ultra",
               "Smart", "Portable", "Elite"]
PRODUCT_NOUN = {
    "Smartphones": ["Phone X", "Phone Mini", "Phone Max"],
    "Laptops": ["Notebook 14", "Notebook Air", "Gaming Laptop"],
    "Headphones": ["Earbuds", "Over-Ear Headset", "Wireless Buds"],
    "Cameras": ["DSLR Camera", "Action Cam", "Instant Camera"],
    "Accessories": ["Charger", "Power Bank", "Phone Case"],
    "Men": ["T-Shirt", "Jeans", "Jacket"],
    "Women": ["Dress", "Top", "Skirt"],
    "Kids": ["T-Shirt", "Shorts", "Onesie"],
    "Footwear": ["Sneakers", "Sandals", "Boots"],
    "Winterwear": ["Sweater", "Hoodie", "Coat"],
    "Kitchen": ["Blender", "Cookware Set", "Knife Set"],
    "Furniture": ["Chair", "Table", "Bookshelf"],
    "Decor": ["Wall Clock", "Vase", "Photo Frame"],
    "Lighting": ["Table Lamp", "LED Strip", "Ceiling Light"],
    "Bedding": ["Bedsheet Set", "Pillow", "Comforter"],
    "Fiction": ["Novel", "Short Story Collection", "Mystery Book"],
    "Non-Fiction": ["Biography", "Self-Help Book", "History Book"],
    "Comics": ["Graphic Novel", "Comic Bundle", "Manga Volume"],
    "Academic": ["Textbook", "Reference Guide", "Workbook"],
    "Children": ["Picture Book", "Activity Book", "Story Set"],
}

STATUSES = ["PLACED", "SHIPPED", "DELIVERED", "CANCELLED", "RETURNED"]
STATUS_WEIGHTS = [0.15, 0.15, 0.50, 0.10, 0.10]
CUSTOMER_TYPES = ["REGULAR", "PREMIUM", "VIP"]
CUSTOMER_TYPE_WEIGHTS = [0.65, 0.25, 0.10]
REGIONS = ["NORTH", "SOUTH", "EAST", "WEST", "CENTRAL"]


def random_date(start, end):
    delta = end - start
    return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))


def messy_email(name, idx, make_invalid):
    base = name.lower().replace(" ", ".")
    domain = random.choice(["gmail.com", "yahoo.com", "outlook.com", "example.com"])
    if make_invalid:
        variant = random.choice(["no_at", "no_domain"])
        if variant == "no_at":
            return f"{base}{idx}{domain}"          # missing '@'
        else:
            return f"{base}{idx}@"                  # missing domain
    return f"{base}{idx}@{domain}"


def gen_customers():
    rows = []
    reg_start = datetime(2023, 1, 1)
    reg_end = datetime(2026, 7, 1)
    for cid in range(1, N_CUSTOMERS + 1):
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        invalid_email = random.random() < 0.02  # 2% invalid emails
        email = messy_email(name, cid, invalid_email)
        reg_date = random_date(reg_start, reg_end)
        ctype = random.choices(CUSTOMER_TYPES, weights=CUSTOMER_TYPE_WEIGHTS)[0]
        rows.append({
            "customer_id": cid,
            "customer_name": name,
            "email": email,
            "registration_date": reg_date.strftime("%Y-%m-%d %H:%M:%S"),
            "customer_type": ctype,
        })
    with open(f"{OUTPUT_DIR}/customers.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["customer_id", "customer_name", "email",
                                           "registration_date", "customer_type"])
        w.writeheader()
        w.writerows(rows)
    return rows


def messy_product_name(name):
    """Randomly inject extra whitespace / mixed case to simulate dirty data."""
    r = random.random()
    if r < 0.15:
        return f"  {name}  "            # extra spaces
    elif r < 0.30:
        return name.upper()             # all caps
    elif r < 0.40:
        return name.lower()             # all lowercase
    return name


def gen_products():
    rows = []
    pid = 1
    for category, subcats in CATEGORIES.items():
        for subcat in subcats:
            nouns = PRODUCT_NOUN[subcat]
            for adj in PRODUCT_ADJ:
                if pid > N_PRODUCTS:
                    break
                noun = random.choice(nouns)
                clean_name = f"{adj} {noun}"
                cost_price = round(random.uniform(5, 500), 2)
                rows.append({
                    "product_id": pid,
                    "product_name": messy_product_name(clean_name),
                    "category": category,
                    "subcategory": subcat,
                    "cost_price": cost_price,
                })
                pid += 1
            if pid > N_PRODUCTS:
                break
        if pid > N_PRODUCTS:
            break
    with open(f"{OUTPUT_DIR}/products.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["product_id", "product_name", "category",
                                           "subcategory", "cost_price"])
        w.writeheader()
        w.writerows(rows)
    return rows


def gen_orders(customers):
    rows = []
    order_start = datetime(2024, 8, 1)
    order_end = datetime(2026, 8, 1)
    customer_ids = [c["customer_id"] for c in customers]

    for oid in range(1, N_ORDERS + 1):
        missing_customer = random.random() < 0.05  # 5% NULL customer_id
        cust_id = "" if missing_customer else random.choice(customer_ids)
        odate = random_date(order_start, order_end)

        # Some order_dates in wrong format DD-MM-YYYY (no time component)
        if random.random() < 0.08:
            odate_str = odate.strftime("%d-%m-%Y")
        else:
            odate_str = odate.strftime("%Y-%m-%d %H:%M:%S")

        status = random.choices(STATUSES, weights=STATUS_WEIGHTS)[0]
        region = random.choice(REGIONS)

        rows.append({
            "order_id": oid,
            "customer_id": cust_id,
            "order_date": odate_str,
            "status": status,
            "region_code": region,
        })
    with open(f"{OUTPUT_DIR}/orders.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["order_id", "customer_id", "order_date",
                                           "status", "region_code"])
        w.writeheader()
        w.writerows(rows)
    return rows


def gen_order_items(orders, products):
    rows = []
    item_id = 1
    product_ids = [p["product_id"] for p in products]
    product_price = {p["product_id"]: p["cost_price"] for p in products}

    for order in orders:
        n_items = random.randint(1, 5)
        chosen_products = random.sample(product_ids, k=min(n_items, len(product_ids)))
        for pid in chosen_products:
            is_return = random.random() < 0.03  # 3% negative quantity (returns)
            qty = random.randint(1, 5)
            if is_return:
                qty = -qty
            # unit_price roughly cost_price marked up 1.3x-2.5x, with a little noise
            unit_price = round(product_price[pid] * random.uniform(1.3, 2.5), 2)
            discount = round(random.uniform(0, 100) if random.random() < 0.3 else random.uniform(0, 20), 2)

            rows.append({
                "item_id": item_id,
                "order_id": order["order_id"],
                "product_id": pid,
                "quantity": qty,
                "unit_price": unit_price,
                "discount_percent": discount,
            })
            item_id += 1

    with open(f"{OUTPUT_DIR}/order_items.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["item_id", "order_id", "product_id",
                                           "quantity", "unit_price", "discount_percent"])
        w.writeheader()
        w.writerows(rows)
    return rows


def main():
    import os
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    customers = gen_customers()
    products = gen_products()
    orders = gen_orders(customers)
    order_items = gen_order_items(orders, products)

    print(f"Generated {len(customers)} customers -> {OUTPUT_DIR}/customers.csv")
    print(f"Generated {len(products)} products   -> {OUTPUT_DIR}/products.csv")
    print(f"Generated {len(orders)} orders       -> {OUTPUT_DIR}/orders.csv")
    print(f"Generated {len(order_items)} order_items -> {OUTPUT_DIR}/order_items.csv")


if __name__ == "__main__":
    main()
