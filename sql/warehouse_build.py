import duckdb
from pathlib import Path

RAW_DIR = Path("data/raw")
DB_PATH = Path("data/processed/olist.duckdb")

REQUIRED = [
    "olist_orders_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_customers_dataset.csv",
    "olist_products_dataset.csv",
    "olist_order_payments_dataset.csv",
]

def main():
    missing = [f for f in REQUIRED if not (RAW_DIR / f).exists()]
    if missing:
        raise FileNotFoundError(
            "Missing files in data/raw:\n" + "\n".join(missing) +
            "\n\nPut the Olist CSVs into analytics-copilot\\data\\raw\\"
        )

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DB_PATH))

    con.execute(f"""
        CREATE OR REPLACE TABLE orders AS
        SELECT * FROM read_csv_auto('{(RAW_DIR / "olist_orders_dataset.csv").as_posix()}');
    """)

    con.execute(f"""
        CREATE OR REPLACE TABLE order_items AS
        SELECT * FROM read_csv_auto('{(RAW_DIR / "olist_order_items_dataset.csv").as_posix()}');
    """)

    con.execute(f"""
        CREATE OR REPLACE TABLE customers AS
        SELECT * FROM read_csv_auto('{(RAW_DIR / "olist_customers_dataset.csv").as_posix()}');
    """)

    con.execute(f"""
        CREATE OR REPLACE TABLE products AS
        SELECT * FROM read_csv_auto('{(RAW_DIR / "olist_products_dataset.csv").as_posix()}');
    """)

    con.execute(f"""
        CREATE OR REPLACE TABLE order_payments AS
        SELECT * FROM read_csv_auto('{(RAW_DIR / "olist_order_payments_dataset.csv").as_posix()}');
    """)

    print(f"✅ Built DuckDB at: {DB_PATH}")
    for t in ["orders", "order_items", "customers", "products", "order_payments"]:
        n = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f" - {t}: {n:,} rows")

    con.close()

if __name__ == "__main__":
    main()
