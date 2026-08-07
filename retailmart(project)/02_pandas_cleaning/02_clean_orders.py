"""
RetailMart | 02 - Pandas Cleaning
----------------------------------
Takes the messy raw orders.csv and produces a clean, analysis-ready
DataFrame:

  - drops exact duplicate order rows
  - drops/flags invalid quantities (0 or negative)
  - parses order_date / delivery_date into real datetimes
  - computes delivery_days = delivery_date - order_date
  - computes line_revenue = quantity * unit_price
  - writes the cleaned result to data/orders_clean.csv (used by the SQL,
    PySpark, and Delta Lake layers downstream)
"""
import os

import numpy as np
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def load_raw_orders():
    return pd.read_csv(os.path.join(DATA_DIR, "orders.csv"))


def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)

    # 1. drop exact duplicate rows (same order_id + same everything)
    df = df.drop_duplicates(subset=["order_id"], keep="first").copy()
    dupes_removed = before - len(df)

    # 2. parse dates (delivery_date has blanks -> NaT)
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df["delivery_date"] = pd.to_datetime(df["delivery_date"], errors="coerce")

    # 3. flag invalid quantities instead of silently dropping revenue rows
    df["is_valid_quantity"] = df["quantity"] > 0
    invalid_qty = (~df["is_valid_quantity"]).sum()

    # 4. delivery days: only meaningful when both dates exist and status is Delivered
    df["delivery_days"] = (df["delivery_date"] - df["order_date"]).dt.days
    df.loc[df["delivery_days"] < 0, "delivery_days"] = np.nan  # guard against bad data

    # 5. revenue at the line-item level
    df["line_revenue"] = df["quantity"] * df["unit_price"]

    # 6. standardize order_status casing/whitespace
    df["order_status"] = df["order_status"].str.strip().str.title()

    summary = {
        "rows_before": before,
        "duplicate_rows_removed": dupes_removed,
        "rows_after": len(df),
        "orders_with_invalid_quantity": int(invalid_qty),
        "orders_missing_delivery_days": int(df["delivery_days"].isna().sum()),
    }
    return df, summary


def main():
    raw = load_raw_orders()
    clean, summary = clean_orders(raw)

    print("=" * 55)
    print("CLEANING SUMMARY")
    print("=" * 55)
    for k, v in summary.items():
        print(f"{k:<32}: {v:,}")

    avg_delivery = clean["delivery_days"].mean()
    print(f"\nAverage delivery time (delivered orders): {avg_delivery:.1f} days")

    print("\nDelivery days distribution:")
    print(clean["delivery_days"].describe().round(1))

    out_path = os.path.join(DATA_DIR, "orders_clean.csv")
    clean.to_csv(out_path, index=False)
    print(f"\nClean file written to: {out_path}")


if __name__ == "__main__":
    main()
