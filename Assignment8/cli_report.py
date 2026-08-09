"""
Part 4: Python + SQL Integration
A command-line tool that generates a summary report for a given period.

Usage (interactive):
    python3 cli_report.py

Usage (non-interactive, for scripting/testing):
    python3 cli_report.py --report-type monthly --start 2026-01-01 --end 2026-01-31

No external libraries besides sqlite3 (and argparse/datetime from the stdlib).
"""

import sqlite3
import argparse
from datetime import datetime, timedelta

DB_PATH = "ecommerce.db"


def get_period_dates(report_type, ref_date=None):
    """Given a report type, return (start, end) as date strings for the CURRENT period,
    anchored on ref_date (defaults to today)."""
    if ref_date is None:
        ref_date = datetime.now()

    if report_type == "daily":
        start = end = ref_date.date()
    elif report_type == "weekly":
        start = (ref_date - timedelta(days=ref_date.weekday())).date()
        end = start + timedelta(days=6)
    elif report_type == "monthly":
        start = ref_date.replace(day=1).date()
        next_month = (start.replace(day=28) + timedelta(days=4)).replace(day=1)
        end = next_month - timedelta(days=1)
    else:
        raise ValueError(f"Unknown report_type: {report_type}")

    return str(start), str(end)


def previous_period(report_type, start_str, end_str):
    """Compute the immediately preceding period of equal length, for % comparison."""
    start = datetime.strptime(start_str, "%Y-%m-%d").date()
    end = datetime.strptime(end_str, "%Y-%m-%d").date()
    length = (end - start).days + 1
    prev_end = start - timedelta(days=1)
    prev_start = prev_end - timedelta(days=length - 1)
    return str(prev_start), str(prev_end)


def summarize_period(conn, start, end):
    cur = conn.cursor()

    cur.execute("""
        SELECT COUNT(DISTINCT o.order_id), COUNT(DISTINCT o.customer_id)
        FROM orders o
        WHERE date(o.order_date) BETWEEN ? AND ?
    """, (start, end))
    total_orders, unique_customers = cur.fetchone()
    total_orders = total_orders or 0
    unique_customers = unique_customers or 0

    cur.execute("""
        SELECT COALESCE(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 0)
        FROM orders o
        JOIN order_items oi ON oi.order_id = o.order_id
        WHERE date(o.order_date) BETWEEN ? AND ?
    """, (start, end))
    revenue = cur.fetchone()[0] or 0

    cur.execute("""
        SELECT p.product_name,
               SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS rev
        FROM orders o
        JOIN order_items oi ON oi.order_id = o.order_id
        JOIN products p ON p.product_id = oi.product_id
        WHERE date(o.order_date) BETWEEN ? AND ?
        GROUP BY p.product_name
        ORDER BY rev DESC
        LIMIT 3
    """, (start, end))
    top_products = cur.fetchall()

    return {
        "total_orders": total_orders,
        "revenue": round(revenue, 2),
        "unique_customers": unique_customers,
        "top_products": top_products,
    }


def pct_change(old, new):
    if old == 0:
        return None
    return round((new - old) / old * 100, 2)


def generate_report(report_type, start, end):
    conn = sqlite3.connect(DB_PATH)

    current = summarize_period(conn, start, end)
    prev_start, prev_end = previous_period(report_type, start, end)
    previous = summarize_period(conn, prev_start, prev_end)

    conn.close()

    print("=" * 55)
    print(f" {report_type.upper()} REPORT: {start} to {end}")
    print("=" * 55)
    print(f"Total Orders     : {current['total_orders']}")
    print(f"Total Revenue    : {current['revenue']}")
    print(f"Unique Customers : {current['unique_customers']}")
    print()
    print("Top 3 Products:")
    if current["top_products"]:
        for name, rev in current["top_products"]:
            print(f"  - {name}: {round(rev, 2)}")
    else:
        print("  (no sales in this period)")
    print()
    print(f"Comparison with previous period ({prev_start} to {prev_end}):")
    print(f"  Orders change    : {pct_change(previous['total_orders'], current['total_orders'])}%")
    print(f"  Revenue change   : {pct_change(previous['revenue'], current['revenue'])}%")
    print(f"  Customers change : {pct_change(previous['unique_customers'], current['unique_customers'])}%")
    print("=" * 55)


def main():
    parser = argparse.ArgumentParser(description="E-Commerce Summary Report Tool")
    parser.add_argument("--report-type", choices=["daily", "weekly", "monthly"])
    parser.add_argument("--start", help="Start date YYYY-MM-DD")
    parser.add_argument("--end", help="End date YYYY-MM-DD")
    args = parser.parse_args()

    if args.report_type and args.start and args.end:
        generate_report(args.report_type, args.start, args.end)
        return

    # Interactive mode
    report_type = input("Report type (daily/weekly/monthly): ").strip().lower()
    while report_type not in ("daily", "weekly", "monthly"):
        report_type = input("Please enter daily, weekly, or monthly: ").strip().lower()

    start = input("Start date (YYYY-MM-DD): ").strip()
    end = input("End date (YYYY-MM-DD): ").strip()

    generate_report(report_type, start, end)


if __name__ == "__main__":
    main()
