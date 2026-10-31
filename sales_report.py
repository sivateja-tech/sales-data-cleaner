"""Clean a messy sales CSV, answer questions with SQL, and draw charts.

Run:  python sales_report.py data/sales_raw.csv --out output
"""

import argparse
import sqlite3
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # draw charts to files, no window needed
import matplotlib.pyplot as plt
import pandas as pd


# ---------------------------------------------------------------- step 1: load
def load_data(path):
    """Read the CSV file into a pandas table (DataFrame)."""
    return pd.read_csv(path)


# --------------------------------------------------------------- step 2: clean
def clean_data(df):
    """Fix the common problems in the data.

    Returns the cleaned table and a dictionary that counts what was fixed.
    """
    fixed = {"rows_in": len(df)}

    # 1. Remove extra spaces and make text look the same ("  laptop " -> "Laptop")
    for col in ["customer", "product", "city"]:
        df[col] = df[col].astype(str).str.strip().str.title()

    # 2. Remove rows that are exact copies of another row
    before = len(df)
    df = df.drop_duplicates()
    fixed["duplicates_removed"] = before - len(df)

    # 3. Turn dates into real dates; anything invalid becomes NaT ("not a time")
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")

    # 4. Turn quantity and price into numbers; anything invalid becomes NaN (missing)
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["price"] = pd.to_numeric(df["price"], errors="coerce")

    # 5. Drop rows with a missing date, missing number, or a quantity/price <= 0
    before = len(df)
    df = df.dropna(subset=["order_date", "quantity", "price"])
    df = df[(df["quantity"] > 0) & (df["price"] > 0)]
    fixed["invalid_rows_removed"] = before - len(df)

    # 6. Add a new column: total = quantity x price
    df = df.assign(total=df["quantity"] * df["price"])

    fixed["rows_out"] = len(df)
    return df.reset_index(drop=True), fixed


# ------------------------------------------------------------------ step 3: SQL
def run_sql_reports(df):
    """Put the clean data in a temporary SQL table and ask it questions."""
    conn = sqlite3.connect(":memory:")
    df.assign(order_date=df["order_date"].dt.strftime("%Y-%m-%d")).to_sql(
        "sales", conn, index=False
    )

    queries = {
        # Which product earns the most?
        "revenue_by_product": """
            SELECT product, COUNT(*) AS orders, SUM(total) AS revenue
            FROM sales
            GROUP BY product
            ORDER BY revenue DESC
        """,
        # How do sales change month by month?
        "revenue_by_month": """
            SELECT strftime('%Y-%m', order_date) AS month, SUM(total) AS revenue
            FROM sales
            GROUP BY month
            ORDER BY month
        """,
        # Which cities are best?
        "revenue_by_city": """
            SELECT city, SUM(total) AS revenue
            FROM sales
            GROUP BY city
            ORDER BY revenue DESC
        """,
    }
    reports = {name: pd.read_sql_query(sql, conn) for name, sql in queries.items()}
    conn.close()
    return reports


# --------------------------------------------------------------- step 4: charts
def make_charts(reports, out_dir):
    """Save two charts as PNG pictures."""
    by_product = reports["revenue_by_product"]
    plt.figure(figsize=(7, 4))
    plt.bar(by_product["product"], by_product["revenue"])
    plt.title("Revenue by product")
    plt.ylabel("Revenue (INR)")
    plt.tight_layout()
    plt.savefig(out_dir / "revenue_by_product.png")
    plt.close()

    by_month = reports["revenue_by_month"]
    plt.figure(figsize=(7, 4))
    plt.plot(by_month["month"], by_month["revenue"], marker="o")
    plt.title("Revenue by month")
    plt.ylabel("Revenue (INR)")
    plt.tight_layout()
    plt.savefig(out_dir / "revenue_by_month.png")
    plt.close()


# ------------------------------------------------------------------ run it all
def main():
    parser = argparse.ArgumentParser(description="Clean sales data and make a report.")
    parser.add_argument("input", help="path to the raw CSV file")
    parser.add_argument("--out", default="output", help="folder for the results")
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(exist_ok=True)

    raw = load_data(args.input)
    clean, fixed = clean_data(raw)
    reports = run_sql_reports(clean)

    clean.to_csv(out_dir / "sales_clean.csv", index=False)
    make_charts(reports, out_dir)

    print("CLEANING SUMMARY")
    print(f"  rows in:                {fixed['rows_in']}")
    print(f"  duplicates removed:     {fixed['duplicates_removed']}")
    print(f"  invalid rows removed:   {fixed['invalid_rows_removed']}")
    print(f"  rows out:               {fixed['rows_out']}")
    print("\nREVENUE BY PRODUCT")
    print(reports["revenue_by_product"].to_string(index=False))
    print(f"\nSaved cleaned data and charts in: {out_dir}/")


if __name__ == "__main__":
    main()
