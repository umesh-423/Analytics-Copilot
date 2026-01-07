\# 📊 Analytics Copilot — RAG → SQL → Insight



An end-to-end \*\*LLM-powered Analytics Copilot\*\* that translates natural language business questions into \*\*validated SQL queries\*\*, executes them on a DuckDB warehouse, and returns \*\*charts and insights\*\* via Streamlit.



This project demonstrates how Retrieval-Augmented Generation (RAG) can be safely applied to analytics workflows without hallucinating metrics or queries.



---



\## 🚀 Key Features



\- 🔍 \*\*Semantic KPI Retrieval (RAG)\*\* using ChromaDB

\- 🧠 \*\*LLM-powered SQL generation\*\* with fallback safety

\- 🛑 \*\*Guardrails\*\*: refuses unsupported or low-confidence questions

\- 🗄️ \*\*DuckDB analytics warehouse\*\* (Olist dataset)

\- 📈 \*\*Interactive Streamlit dashboard\*\* (charts + tables)

\- 🧪 \*\*Evaluation harness\*\* with pass/fail scoring



---



\## 🏗️ Architecture





---



\## 🧰 Tech Stack



\- Python

\- DuckDB

\- ChromaDB

\- OpenAI API

\- Streamlit

\- Pandas

\- YAML (KPI definitions)



---



\## 📌 Example Questions



✔️ Supported:

\- Show revenue by month  

\- Top products by revenue  

\- What is average order value?  

\- Number of orders  



❌ Refused (by design):

\- What is net promoter score?  

\- How many suppliers do we have?  



---



\## 🔒 Safety \& Reliability



\- Retrieval confidence gating (prevents wrong KPIs)

\- Explicit grain validation (prevents invalid aggregations)

\- SQL fallback examples when LLM cannot answer

\- No hallucinated metrics



---



\## ▶️ Run Locally



```bash

python -m venv .venv

.venv\\Scripts\\activate

pip install -r requirements.txt

python -m streamlit run app/streamlit\_app.py



