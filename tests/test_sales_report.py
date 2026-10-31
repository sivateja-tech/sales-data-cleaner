import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from sales_report import clean_data, run_sql_reports  # noqa: E402


def make_df(rows):
    cols = ["order_id", "order_date", "customer", "product", "city", "quantity", "price"]
    return pd.DataFrame(rows, columns=cols)


def test_text_is_trimmed_and_standardised():
    df = make_df([[1, "2025-01-05", " ravi kumar ", "  laptop ", "HYDERABAD", 1, 100]])
    clean, _ = clean_data(df)
    assert clean.loc[0, "product"] == "Laptop"
    assert clean.loc[0, "city"] == "Hyderabad"
    assert clean.loc[0, "customer"] == "Ravi Kumar"


def test_duplicate_rows_are_removed():
    row = [1, "2025-01-05", "Ravi", "Phone", "Delhi", 1, 100]
    clean, fixed = clean_data(make_df([row, row]))
    assert len(clean) == 1
    assert fixed["duplicates_removed"] == 1


def test_invalid_rows_are_removed():
    df = make_df([
        [1, "2025-01-05", "A", "Phone", "Delhi", 1, 100],     # good
        [2, "not a date", "B", "Phone", "Delhi", 1, 100],     # bad date
        [3, "2025-01-06", "C", "Phone", "Delhi", -2, 100],    # negative quantity
        [4, "2025-01-07", "D", "Phone", "Delhi", 1, None],    # missing price
    ])
    clean, fixed = clean_data(df)
    assert list(clean["order_id"]) == [1]
    assert fixed["invalid_rows_removed"] == 3


def test_total_is_quantity_times_price():
    clean, _ = clean_data(make_df([[1, "2025-01-05", "A", "Phone", "Delhi", 3, 100]]))
    assert clean.loc[0, "total"] == 300


def test_sql_report_sums_revenue_per_product():
    clean, _ = clean_data(make_df([
        [1, "2025-01-05", "A", "Phone", "Delhi", 1, 100],
        [2, "2025-01-20", "B", "Phone", "Delhi", 2, 100],
        [3, "2025-02-02", "C", "Laptop", "Delhi", 1, 500],
    ]))
    reports = run_sql_reports(clean)
    by_product = reports["revenue_by_product"].set_index("product")["revenue"]
    assert by_product["Phone"] == 300
    assert by_product["Laptop"] == 500
    assert list(reports["revenue_by_month"]["month"]) == ["2025-01", "2025-02"]
