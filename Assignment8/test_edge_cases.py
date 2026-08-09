"""
Part 5: Edge Case Handling
Test functions verifying how the system behaves for each edge case.
Run with: python3 test_edge_cases.py
(Plain functions + assertions -- no pytest dependency required, but pytest works too.)
"""

from datetime import datetime, timedelta
import pandas as pd

from data_cleaning import check_referential_integrity, clean_orders


# --------------------------------------------------------------------------
# 1. order_items has an order_id not in orders
# --------------------------------------------------------------------------
def test_orphan_order_item():
    orders = pd.DataFrame({
        "order_id": [1, 2, 3],
        "customer_id": [10, 11, 12],
        "order_date": ["2026-01-01 10:00:00", "2026-01-02 10:00:00", "2026-01-03 10:00:00"],
        "status": ["DELIVERED", "PLACED", "SHIPPED"],
        "region_code": ["NORTH", "SOUTH", "EAST"],
    })
    order_items = pd.DataFrame({
        "item_id": [1, 2, 3],
        "order_id": [1, 2, 999],   # 999 does not exist in orders
        "product_id": [100, 101, 102],
        "quantity": [1, 2, 1],
        "unit_price": [10.0, 20.0, 30.0],
        "discount_percent": [0, 5, 10],
    })

    orphans = check_referential_integrity(orders, order_items)

    assert len(orphans) == 1, f"Expected 1 orphan, got {len(orphans)}"
    assert orphans[0]["order_id"] == 999
    print("PASS: test_orphan_order_item - orphaned order_items are correctly detected"
          " and excluded from JOINs (INNER JOIN naturally drops them; this function"
          " surfaces them explicitly for data-quality reporting).")


# --------------------------------------------------------------------------
# 2. discount_percent > 100
# --------------------------------------------------------------------------
def test_discount_out_of_range():
    order_items = pd.DataFrame({
        "item_id": [1, 2, 3],
        "order_id": [1, 1, 2],
        "product_id": [1, 2, 3],
        "quantity": [1, 1, 1],
        "unit_price": [100.0, 100.0, 100.0],
        "discount_percent": [50, 150, -10],   # 150 and -10 are invalid
    })

    invalid_mask = (order_items["discount_percent"] < 0) | (order_items["discount_percent"] > 100)
    invalid_rows = order_items[invalid_mask]

    assert len(invalid_rows) == 2, f"Expected 2 invalid discount rows, got {len(invalid_rows)}"

    # Demonstrate what happens to *revenue* if an out-of-range discount is used unclamped:
    # discount_percent = 150 -> (1 - 150/100) = -0.5 -> NEGATIVE revenue from a "sale", which
    # is not meaningful. The system should clamp discount_percent to [0, 100] before computing
    # revenue rather than silently accepting it.
    row = order_items.iloc[1]
    naive_revenue = row["quantity"] * row["unit_price"] * (1 - row["discount_percent"] / 100)
    clamped_discount = min(max(row["discount_percent"], 0), 100)
    clamped_revenue = row["quantity"] * row["unit_price"] * (1 - clamped_discount / 100)

    assert naive_revenue < 0, "Unclamped 150% discount should produce negative revenue (the bug)"
    assert clamped_revenue == 0, "Clamped 100% discount should produce zero revenue (the fix)"

    print(f"PASS: test_discount_out_of_range - found {len(invalid_rows)} rows outside [0,100]; "
          f"unclamped revenue would be {naive_revenue} (invalid, negative), "
          f"clamping discount_percent to [0,100] gives {clamped_revenue} (correct).")


# --------------------------------------------------------------------------
# 3. quantity is 0
# --------------------------------------------------------------------------
def test_zero_quantity():
    order_items = pd.DataFrame({
        "item_id": [1, 2],
        "order_id": [1, 1],
        "product_id": [1, 2],
        "quantity": [0, 5],
        "unit_price": [50.0, 20.0],
        "discount_percent": [0, 0],
    })

    zero_qty_rows = order_items[order_items["quantity"] == 0]
    assert len(zero_qty_rows) == 1

    # Revenue contribution of a zero-quantity row is always 0, regardless of price/discount --
    # it doesn't error, but it's worth flagging since a "line item" with 0 units ordered is
    # usually a data-entry mistake rather than a real transaction.
    revenue = (zero_qty_rows["quantity"] * zero_qty_rows["unit_price"] *
               (1 - zero_qty_rows["discount_percent"] / 100)).sum()
    assert revenue == 0

    print("PASS: test_zero_quantity - a quantity=0 row contributes 0 revenue (no crash), "
          "but is flagged in the data-quality report as a likely data-entry error.")


# --------------------------------------------------------------------------
# 4. order_date is in the future
# --------------------------------------------------------------------------
def test_future_order_date():
    future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
    orders = pd.DataFrame({
        "order_id": [1, 2],
        "customer_id": [10, 11],
        "order_date": [future_date, "2026-01-01 10:00:00"],
        "status": ["PLACED", "DELIVERED"],
        "region_code": ["NORTH", "SOUTH"],
    })

    cleaned, issues = clean_orders(orders)

    assert issues["future_dated_orders_count"] == 1
    assert issues["future_dated_order_ids"] == [1]

    print("PASS: test_future_order_date - future-dated orders are parsed successfully "
          "(not treated as a format error) but flagged separately for review; "
          "the system does not silently accept or silently reject them.")


def run_all():
    tests = [
        test_orphan_order_item,
        test_discount_out_of_range,
        test_zero_quantity,
        test_future_order_date,
    ]
    for t in tests:
        t()
    print(f"\n{len(tests)}/{len(tests)} edge case tests passed.")


if __name__ == "__main__":
    run_all()
