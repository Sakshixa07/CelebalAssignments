"""
Loads the cleaned Superstore CSV into a SQLite database as `superstore_raw`.
This mirrors the "load into staging table" step of the assignment.
SQLite is used as the SQL engine so the .sql script is portable and runs
without a server -- all syntax used (CTEs, window functions, subqueries)
is standard ANSI SQL that also runs unchanged on PostgreSQL / MySQL 8+.
"""
import sqlite3
import pandas as pd

df = pd.read_csv("superstore.csv")

conn = sqlite3.connect("superstore.db")
df.to_sql("superstore_raw", conn, if_exists="replace", index=False)
conn.commit()
conn.close()
print("Loaded", len(df), "rows into superstore_raw")
