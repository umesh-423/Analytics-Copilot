from pathlib import Path
import chromadb

DB_DIR = Path("data/processed/chroma_kpi")

def search(query: str, n: int = 3):
    client = chromadb.PersistentClient(path=str(DB_DIR))
    col = client.get_collection("kpi_defs")
    res = col.query(query_texts=[query], n_results=n)
    return res

if __name__ == "__main__":
    q = "What is average order value and how do you calculate it?"
    out = search(q, n=3)
    for i, doc in enumerate(out["documents"][0], start=1):
        meta = out["metadatas"][0][i-1]
        print(f"\n--- Result {i} (kpi={meta.get('kpi')}, grain={meta.get('grain')}) ---\n")
        print(doc[:800])
