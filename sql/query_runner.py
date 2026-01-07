from pathlib import Path
import duckdb
import pandas as pd
import re

DB_PATH = Path("data/processed/olist.duckdb")

# Very simple blocklist for safety in a demo app
BLOCKLIST = re.compile(
    r"\b(insert|update|delete|drop|alter|create|attach|detach|copy|export|pragma)\b",
    re.IGNORECASE,
)

def run_sql(sql: str) -> pd.DataFrame:
    if not DB_PATH.exists():
        raise FileNotFoundError(f"DuckDB not found at {DB_PATH}. Run sql/warehouse_build.py first.")

    s = sql.strip()
    if not s:
        raise ValueError("Empty SQL.")

    if BLOCKLIST.search(s):
        raise ValueError("Unsafe SQL detected (non-SELECT operation).")

    if not (s.lower().startswith("select") or s.lower().startswith("with")):
        raise ValueError("Only SELECT/WITH queries are allowed.")

    con = duckdb.connect(str(DB_PATH), read_only=True)
    try:
        con.execute("SET enable_progress_bar=false;")
        df = con.execute(sql).df()
        return df
    finally:
        con.close()
