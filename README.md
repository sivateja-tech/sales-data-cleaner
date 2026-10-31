# Sales Data Cleaner and Report

A small Python project that takes a **messy sales CSV**, cleans it with **pandas**, answers business questions with **SQL**, and draws charts with **matplotlib**.

## What it does

1. **Load** the raw CSV (`data/sales_raw.csv`)
2. **Clean** it: trim spaces, standardise text (`"  laptop "` becomes `Laptop`), remove duplicate rows, drop rows with bad dates, missing or negative values, and add a `total` column
3. **Query** it with SQL (`GROUP BY`, `SUM`, `COUNT`, `ORDER BY`): revenue by product, by month and by city
4. **Chart** it: saves `revenue_by_product.png` and `revenue_by_month.png`
5. **Save** the cleaned data as `output/sales_clean.csv`

The sample data is **synthetic** (generated for this project), with mistakes planted on purpose: 2 duplicate rows, 2 missing prices, 1 negative quantity, 2 invalid dates, and inconsistent spacing and capital letters.

## Run it

```bash
pip install -r requirements.txt
python sales_report.py data/sales_raw.csv --out output
python -m pytest
```

Example output:

```
CLEANING SUMMARY
  rows in:                122
  duplicates removed:     2
  invalid rows removed:   5
  rows out:               115

REVENUE BY PRODUCT
   product  orders   revenue
    Laptop      21 3648000.0
     Phone      24 1373000.0
 ...
```

## Files

```
sales_report.py              the whole program (load, clean, SQL, charts)
data/sales_raw.csv           messy sample data
tests/test_sales_report.py   5 pytest tests
requirements.txt
```

## Tech

Python, pandas, SQL (SQLite), matplotlib, pytest
