from __future__ import annotations

import time
from pathlib import Path
from datetime import datetime, timezone

import pandas as pd
import chromadb

from sql.query_runner import run_sql
from rag.llm_sql import generate_sql

# ----------------------------
# Config
# ----------------------------
CHROMA_DIR = Path("data/processed/chroma_kpi")
LOG_PATH = Path("data/processed/query_log.csv")

MODEL_NAME = "no_key_mode"

# ----------------------------
# Utilities
# ----------------------------
def log_query(query, kpi, grain, sql, rows, status):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).isoformat()

    row = pd.DataFrame([{
        "timestamp_utc": ts,
        "query": query,
        "kpi": kpi,
        "grain": grain,
        "rows": rows,
        "status": status
    }])

    if LOG_PATH.exists():
        row.to_csv(LOG_PATH, mode="a", header=False, index=False)
    else:
        row.to_csv(LOG_PATH, index=False)


def retrieve_top_kpi(query: str):
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    col = client.get_collection("kpi_defs")

    res = col.query(
        query_texts=[query],
        n_results=1,
        include=["documents", "metadatas", "distances"]
    )

    evidence = res["documents"][0][0]
    meta = res["metadatas"][0][0]
    dist = res["distances"][0][0]
    return evidence, meta, dist


def extract_sql_example(evidence: str) -> str:
    marker = "SQL Example:"
    if marker not in evidence:
        return ""

    return evidence.split(marker, 1)[1].strip()


# ----------------------------
# Main API
# ----------------------------
def answer(query: str):
    start = time.time()

    try:
        # 1. Retrieve KPI
        evidence, meta, dist = retrieve_top_kpi(query)

        # 2. Retrieval confidence gate
        RETRIEVAL_MAX_DISTANCE = 1.25
        if dist is None or dist > RETRIEVAL_MAX_DISTANCE:
            log_query(
                query=query,
                kpi=None,
                grain=None,
                sql="",
                rows=0,
                status=f"refused_low_retrieval_confidence(dist={dist})"
            )
            return {
                "question": query,
                "status": "refused",
                "kpi": None,
                "grain": None,
                "sql": None,
                "df": None,
                "rows": 0,
                "retrieval_distance": dist,
            }

        kpi = meta.get("kpi")
        grain = meta.get("grain")

        # 3. Generate SQL (LLM or fallback)
        sql = generate_sql(
            question=query,
            kpi_evidence=evidence,
            model=MODEL_NAME
        )

        if sql == "CANNOT_ANSWER":
            sql = extract_sql_example(evidence)
            status = "fallback_sql_example"
        else:
            status = "llm_generated"

        # 4. Execute SQL
        df = run_sql(sql)
        rows = len(df)

        # 5. Log
        log_query(query, kpi, grain, sql, rows, status)

        return {
            "question": query,
            "status": status,
            "kpi": kpi,
            "grain": grain,
            "sql": sql,
            "df": df,
            "rows": rows,
            "retrieval_distance": dist,
            "evidence": evidence,
        }

    except Exception as e:
        log_query(query, None, None, "", 0, f"error:{e}")
        return {
            "question": query,
            "status": "error",
            "kpi": None,
            "grain": None,
            "sql": None,
            "df": None,
            "rows": 0,
            "error": str(e),
        }
