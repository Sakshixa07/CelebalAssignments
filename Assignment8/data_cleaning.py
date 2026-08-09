"""
Part 2: Data Cleaning (pandas)

Provides:
    clean_orders(df)                -> (cleaned_df, issues_dict)
    clean_products(df)              -> (cleaned_df, issues_dict)
    validate_emails(df)             -> list of customer_ids with invalid emails
    check_referential_integrity(orders_df, order_items_df) -> list of orphan order_ids

Also runs an end-to-end pipeline: reads data/*.csv, cleans everything, writes
cleaned/*.csv, and writes reports/data_quality_report.txt summarizing every
issue that was found and fixed.
"""

import re
import pandas as pd

DATA_DIR = "data"
CLEAN_DIR = "cleaned"
REPORT_PATH = "reports/data_quality_report.txt"

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


# --------------------------------------------------------------------------
# clean_orders
# --------------------------------------------------------------------------
def clean_orders(df: pd.DataFrame):
    """
    Fixes:
      - order_date in wrong format (DD-MM-YYYY) -> normalized to YYYY-MM-DD HH:MM:SS
      - NULL / empty customer_id -> filled with placeholder -1 and flagged
    Returns (cleaned_df, issues) where issues is a dict of counts/details.
    """
    df = df.copy()
    issues = {}

    # --- Fix customer_id ---
    df["customer_id"] = df["customer_id"].replace(r"^\s*$", pd.NA, regex=True)
    missing_mask = df["customer_id"].isna()
    issues["missing_customer_id_count"] = int(missing_mask.sum())
    issues["missing_customer_id_order_ids"] = df.loc[missing_mask, "order_id"].tolist()

    df["customer_id_missing_flag"] = missing_mask
    # Use nullable Int64 so we can keep NA for missing rather than inventing a fake id
    df["customer_id"] = pd.to_numeric(df["customer_id"], errors="coerce").astype("Int64")

    # --- Fix order_date ---
    def parse_date(value):
        value = str(value).strip()
        # Correct format already
        try:
            return pd.to_datetime(value, format="%Y-%m-%d %H:%M:%S")
        except ValueError:
            pass
        # Wrong format: DD-MM-YYYY (no time)
        try:
            return pd.to_datetime(value, format="%d-%m-%Y")
        except ValueError:
            pass
        # Fallback: let pandas guess; NaT if it fails
        return pd.to_datetime(value, errors="coerce")

    parsed_dates = df["order_date"].apply(parse_date)
    bad_format_mask = ~df["order_date"].astype(str).str.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")
    issues["reformatted_date_count"] = int(bad_format_mask.sum())
    issues["unparseable_date_order_ids"] = df.loc[parsed_dates.isna(), "order_id"].tolist()

    df["order_date"] = parsed_dates

    # --- Flag future dates (edge case awareness, not silently dropped) ---
    now = pd.Timestamp.now()
    future_mask = df["order_date"] > now
    issues["future_dated_orders_count"] = int(future_mask.sum())
    issues["future_dated_order_ids"] = df.loc[future_mask, "order_id"].tolist()

    return df, issues


# --------------------------------------------------------------------------
# clean_products
# --------------------------------------------------------------------------
def clean_products(df: pd.DataFrame):
    """
    Normalizes product_name: trims whitespace, converts to Title Case.
    Returns (cleaned_df, issues).
    """
    df = df.copy()
    issues = {}

    original = df["product_name"]
    trimmed = original.str.strip()
    normalized = trimmed.str.title()

    changed_mask = original != normalized
    issues["normalized_name_count"] = int(changed_mask.sum())
    issues["examples"] = list(zip(
        original[changed_mask].head(5), normalized[changed_mask].head(5)
    ))

    df["product_name"] = normalized

    # Flag duplicate product names that only differed by casing/whitespace pre-clean
    dup_mask = df.duplicated(subset=["product_name"], keep=False)
    issues["duplicate_product_name_count"] = int(dup_mask.sum())

    return df, issues


# --------------------------------------------------------------------------
# validate_emails
# --------------------------------------------------------------------------
def validate_emails(df: pd.DataFrame):
    """
    Returns a list of customer_ids whose email is invalid
    (missing '@' or missing a domain).
    """
    invalid_mask = ~df["email"].astype(str).str.match(EMAIL_RE)
    return df.loc[invalid_mask, "customer_id"].tolist()


# --------------------------------------------------------------------------
# check_referential_integrity
# --------------------------------------------------------------------------
def check_referential_integrity(orders_df: pd.DataFrame, order_items_df: pd.DataFrame):
    """
    Returns a list of order_items rows (as dicts) whose order_id does not exist
    in the orders table -- i.e. orphaned order_items.
    """
    valid_order_ids = set(orders_df["order_id"])
    orphan_mask = ~order_items_df["order_id"].isin(valid_order_ids)
    orphans = order_items_df.loc[orphan_mask]
    return orphans.to_dict(orient="records")


# --------------------------------------------------------------------------
# Pipeline
# --------------------------------------------------------------------------
def run_pipeline():
    import os
    os.makedirs(CLEAN_DIR, exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    orders = pd.read_csv(f"{DATA_DIR}/orders.csv", dtype={"customer_id": "string"})
    products = pd.read_csv(f"{DATA_DIR}/products.csv")
    customers = pd.read_csv(f"{DATA_DIR}/customers.csv")
    order_items = pd.read_csv(f"{DATA_DIR}/order_items.csv")

    orders_clean, order_issues = clean_orders(orders)
    products_clean, product_issues = clean_products(products)
    invalid_email_ids = validate_emails(customers)
    orphan_items = check_referential_integrity(orders_clean, order_items)

    # order_items has its own quality checks worth surfacing too
    negative_qty_count = int((order_items["quantity"] < 0).sum())
    zero_qty_count = int((order_items["quantity"] == 0).sum())
    bad_discount_count = int(
        ((order_items["discount_percent"] < 0) | (order_items["discount_percent"] > 100)).sum()
    )

    # Write cleaned CSVs
    orders_clean.to_csv(f"{CLEAN_DIR}/orders.csv", index=False)
    products_clean.to_csv(f"{CLEAN_DIR}/products.csv", index=False)
    customers.to_csv(f"{CLEAN_DIR}/customers.csv", index=False)  # email left as-is; invalid ones are reported, not deleted
    order_items.to_csv(f"{CLEAN_DIR}/order_items.csv", index=False)

    # Write report
    with open(REPORT_PATH, "w") as f:
        f.write("DATA QUALITY REPORT\n")
        f.write("=" * 60 + "\n\n")

        f.write("[orders.csv]\n")
        f.write(f"  Missing customer_id rows fixed/flagged : {order_issues['missing_customer_id_count']}\n")
        f.write(f"  Dates reformatted to YYYY-MM-DD HH:MM:SS: {order_issues['reformatted_date_count']}\n")
        f.write(f"  Unparseable dates (set to NaT)          : {len(order_issues['unparseable_date_order_ids'])}\n")
        f.write(f"  Future-dated orders (flagged, not fixed): {order_issues['future_dated_orders_count']}\n\n")

        f.write("[products.csv]\n")
        f.write(f"  Product names normalized (trim + title case): {product_issues['normalized_name_count']}\n")
        f.write(f"  Duplicate names after normalization          : {product_issues['duplicate_product_name_count']}\n")
        if product_issues["examples"]:
            f.write("  Examples (before -> after):\n")
            for before, after in product_issues["examples"]:
                f.write(f"    '{before}' -> '{after}'\n")
        f.write("\n")

        f.write("[customers.csv]\n")
        f.write(f"  Invalid emails found: {len(invalid_email_ids)}\n")
        f.write(f"  Affected customer_ids (first 10): {invalid_email_ids[:10]}\n\n")

        f.write("[order_items.csv]\n")
        f.write(f"  Orphaned order_items (order_id not in orders): {len(orphan_items)}\n")
        f.write(f"  Negative-quantity rows (returns)              : {negative_qty_count}\n")
        f.write(f"  Zero-quantity rows                            : {zero_qty_count}\n")
        f.write(f"  discount_percent out of [0,100] range         : {bad_discount_count}\n")

    print("Cleaning complete.")
    print(f"  Cleaned CSVs written to: {CLEAN_DIR}/")
    print(f"  Report written to      : {REPORT_PATH}")


if __name__ == "__main__":
    run_pipeline()
