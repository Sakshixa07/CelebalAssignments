"""
Small helper to execute a .sql file against retailmart.db and pretty-print
each statement's results. Used since the sandbox doesn't have the sqlite3
CLI installed, only the python sqlite3 module.

Usage: python3 run_sql.py 04_joins.sql
"""
import sqlite3
import sys
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "retailmart.db")


def split_statements(sql_text):
    # strip -- comments line by line first (a semicolon inside a comment
    # would otherwise confuse a naive split), then split what's left on ';'
    code_only_lines = []
    for line in sql_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("--"):
            continue
        code_only_lines.append(line)
    code_only = "\n".join(code_only_lines)
    parts = [p.strip() for p in code_only.split(";")]
    return [p for p in parts if p]


def main():
    if len(sys.argv) != 2:
        print("usage: python3 run_sql.py <file.sql>")
        sys.exit(1)

    filepath = sys.argv[1]
    with open(filepath) as f:
        sql_text = f.read()

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    statements = split_statements(sql_text)
    for i, stmt in enumerate(statements, 1):
        # grab the comment line right above as a label if present
        try:
            cur.execute(stmt)
        except sqlite3.Error as e:
            print(f"\n--- Statement {i} ERROR ---\n{stmt[:200]}\n{e}")
            continue

        if cur.description:
            cols = [d[0] for d in cur.description]
            rows = cur.fetchall()
            print(f"\n--- Query {i} ({len(rows)} rows) ---")
            print(" | ".join(cols))
            print("-" * 60)
            for row in rows[:15]:
                print(" | ".join(str(v) for v in row))
            if len(rows) > 15:
                print(f"... ({len(rows) - 15} more rows)")

    conn.close()


if __name__ == "__main__":
    main()
