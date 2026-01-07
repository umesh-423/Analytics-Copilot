import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

from rag.answer_pipeline import answer

LOG_PATH = Path("data/processed/query_log.csv")

st.set_page_config(page_title="Analytics Copilot (RAG → SQL → Insight)", layout="wide")
st.title("📊 Analytics Copilot ")

# ----------------------------
# Sidebar
# ----------------------------
with st.sidebar:
    st.markdown("### Try these questions")
    st.markdown("- Show revenue by month")
    st.markdown("- What is average order value?")
    st.markdown("- Number of orders")
    st.markdown("- Average order value by customer")
    st.markdown("- Top products by revenue")
    st.markdown("- What is net promoter score? (should refuse)")

    st.markdown("---")
    st.markdown("### Logs")
    if LOG_PATH.exists():
        if st.button("View last 20 runs"):
            df_log = pd.read_csv(LOG_PATH).tail(20)
            st.dataframe(df_log, use_container_width=True)
    else:
        st.caption("No logs yet. Run a few questions first.")

# ----------------------------
# Main input
# ----------------------------
query = st.text_input("Ask a business question:", "Show revenue by month")
run = st.button("Run")

def guess_chart(df: pd.DataFrame):
    """
    Lightweight heuristics:
    - If first column looks like a date/time -> line chart against second numeric column
    - Else if first column is categorical -> bar chart of first column vs second numeric column
    """
    if df is None or df.empty or df.shape[1] < 2:
        return None

    xcol = df.columns[0]
    ycol = df.columns[1]

    # Try convert x to datetime
    x = df[xcol].copy()
    x_dt = pd.to_datetime(x, errors="coerce")

    # Choose numeric y
    y = pd.to_numeric(df[ycol], errors="coerce")

    # If mostly datetime -> line chart
    if x_dt.notna().mean() > 0.8 and y.notna().mean() > 0.8:
        return ("line", x_dt, y, xcol, ycol)

    # If x is text-like and y numeric -> bar
    if y.notna().mean() > 0.8:
        return ("bar", df[xcol].astype(str), y, xcol, ycol)

    return None

def render_kpi_cards(df: pd.DataFrame):
    """
    Shows a few simple KPI cards from the result:
    - rows
    - if second column numeric: sum/avg
    """
    cols = st.columns(4)
    cols[0].metric("Rows returned", f"{len(df):,}")

    if df is None or df.empty:
        cols[1].metric("Sum (col2)", "—")
        cols[2].metric("Avg (col2)", "—")
        cols[3].metric("Unique (col1)", "—")
        return

    # 2nd column numeric?
    if df.shape[1] >= 2:
        y = pd.to_numeric(df[df.columns[1]], errors="coerce")
        if y.notna().any():
            cols[1].metric(f"Sum ({df.columns[1]})", f"{y.sum():,.2f}")
            cols[2].metric(f"Avg ({df.columns[1]})", f"{y.mean():,.2f}")
        else:
            cols[1].metric("Sum (col2)", "—")
            cols[2].metric("Avg (col2)", "—")

    # Unique count for first col
    cols[3].metric(f"Unique ({df.columns[0]})", f"{df[df.columns[0]].nunique():,}")

def render_chart(df: pd.DataFrame):
    spec = guess_chart(df)
    if not spec:
        st.caption("No chart generated (result not chart-friendly).")
        return

    chart_type, x, y, xlab, ylab = spec

    fig = plt.figure()
    if chart_type == "line":
        plt.plot(x, y)
        plt.xlabel(xlab)
        plt.ylabel(ylab)
        plt.xticks(rotation=45)
    else:
        # bar
        # If too many categories, show top 20 by y
        tmp = pd.DataFrame({xlab: x, ylab: y}).dropna()
        if len(tmp) > 20:
            tmp = tmp.sort_values(ylab, ascending=False).head(20)
        plt.bar(tmp[xlab], tmp[ylab])
        plt.xlabel(xlab)
        plt.ylabel(ylab)
        plt.xticks(rotation=75)

    plt.tight_layout()
    st.pyplot(fig)

if run:
    out = answer(query)

    # Handle refusal cleanly
    if out.get("status") == "refused":
        st.error("❌ Refused: No relevant KPI found for this question.")
        st.caption(f"Retrieval distance: {out.get('retrieval_distance')}")
        st.stop()

    if out.get("status") == "error":
        st.error("⚠️ Error")
        st.code(out.get("error", "Unknown error"))
        st.stop()

    # Success header
    st.success(
        f"Matched KPI: `{out.get('kpi')}` | grain: `{out.get('grain')}` | mode: `{out.get('status')}`"
    )

    if out.get("grain_warning"):
        st.warning(out["grain_warning"])

    # Layout: cards + chart + table + SQL
    df = out.get("df")
    if df is None:
        # Some versions of answer() may not return df; handle gracefully
        st.error("No dataframe returned. Ensure answer() returns df in rag/answer_pipeline.py.")
        st.stop()

    st.markdown("### 📌 Summary")
    render_kpi_cards(df)

    st.markdown("### 📈 Chart")
    render_chart(df)

    col1, col2 = st.columns([1.2, 0.8])
    with col1:
        st.markdown("### ✅ Data")
        st.dataframe(df, use_container_width=True)
    with col2:
        st.markdown("### 🧾 SQL")
        st.code(out.get("sql", ""), language="sql")

        st.markdown("### 🔎 Evidence (KPI Doc)")
        evidence = out.get("evidence", "")
        st.code(evidence[:2000])
