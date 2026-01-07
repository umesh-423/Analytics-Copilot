from pathlib import Path
import yaml
import chromadb

DB_DIR = Path("data/processed/chroma_kpi")
KPI_YAML = Path("knowledge/kpi_definitions.yml")

def main():
    if not KPI_YAML.exists():
        raise FileNotFoundError(f"Missing {KPI_YAML}. Create it first.")

    data = yaml.safe_load(KPI_YAML.read_text(encoding="utf-8"))
    kpis = data.get("kpis", {})

    client = chromadb.PersistentClient(path=str(DB_DIR))

    # Recreate collection for repeatability
    try:
        client.delete_collection("kpi_defs")
    except Exception:
        pass
    col = client.get_or_create_collection(name="kpi_defs")

    docs, ids, metas = [], [], []
    for kpi_name, kpi in kpis.items():
        tables = kpi.get("tables", [])
        text = (
            f"KPI: {kpi_name}\n"
            f"Definition: {kpi.get('definition','')}\n"
            f"Grain: {kpi.get('grain','')}\n"
            f"Tables: {', '.join(tables)}\n"
            f"Constraint: Use ONLY these tables and their existing columns.\n"
            f"SQL Example:\n{kpi.get('sql_example','')}\n"
        )
        docs.append(text)
        ids.append(kpi_name)
        metas.append({
            "kpi": kpi_name,
            "grain": kpi.get("grain", ""),
            "tables": ",".join(tables),
            "source": "kpi_definitions.yml",
        })

    col.add(documents=docs, metadatas=metas, ids=ids)
    print(f"✅ Ingested {len(ids)} KPI docs into Chroma at {DB_DIR}")

if __name__ == "__main__":
    main()
