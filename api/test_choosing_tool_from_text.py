# lc_tool_router.py  (~60–70 lines)
from __future__ import annotations

import time

import requests
from urllib.parse import urljoin
from typing import Dict, List, Optional
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS

_VS: Optional[FAISS] = None

def _fetch_openapi(base_url: str) -> Dict:
    r = requests.get(urljoin(base_url, "/openapi.json"), timeout=10)
    r.raise_for_status()
    return r.json()

def _ops_from_openapi(oas: Dict) -> List[Dict]:
    ops = []
    for path, methods in (oas.get("paths") or {}).items():
        for m, spec in (methods or {}).items():
            if not isinstance(spec, dict):
                continue
            op_id = spec.get("operationId")
            if not op_id:
                continue
            text = " ".join(filter(None, [
                op_id, spec.get("summary",""), spec.get("description",""),
                " ".join(spec.get("tags") or []), path, m.upper()
            ]))
            ops.append({"id": op_id, "method": m.upper(), "path": path, "text": text})
    if not ops:
        raise RuntimeError("No operations in openapi.json")
    return ops

def init_tool_index(base_url: str):
    """Call once at app startup."""
    global _VS
    oas = _fetch_openapi(base_url)
    ops = _ops_from_openapi(oas)
    emb = OllamaEmbeddings(
        model="nomic-embed-text",          # pull with: ollama pull nomic-embed-text
        base_url="http://localhost:11434"  # Ollama server
    )

    texts = [o["text"] for o in ops]
    metas = [{"operationId": o["id"], "method": o["method"], "path": o["path"]} for o in ops]
    _VS = FAISS.from_texts(texts, emb, metadatas=metas)

def choose_tool(vsclient, user_query: str) -> Dict:
    if _VS is None:
        raise RuntimeError("Index not initialized. Call init_tool_index(base_url) first.")
    doc, _score = vsclient.similarity_search_with_score(user_query, k=1)[0]
    return doc.metadata  # {"operationId", "method", "path"}

# --- Example ---
if __name__ == "__main__":
    BASE = "http://localhost:8000"   # FastAPI root (not /mcp)

    t0 = time.perf_counter()
    init_tool_index(BASE)
    t1 = time.perf_counter()
    print(f"init_tool_index took {t1 - t0:.4f} seconds")

    queries = ["list all products", "create a new product", "delete product by id"]

    t2 = time.perf_counter()
    for q in queries:
        print(q, "→", choose_tool(_VS, q))
    t3 = time.perf_counter()
    print(f"Query loop took {t3 - t2:.4f} seconds")

    t2 = time.perf_counter()
    for q in queries:
        print(q, "→", choose_tool(_VS, q))
    t3 = time.perf_counter()
    print(f"Query loop took {t3 - t2:.4f} seconds")

    t2 = time.perf_counter()
    for q in queries:
        print(q, "→", choose_tool(_VS, q))
    t3 = time.perf_counter()
    print(f"Query loop took {t3 - t2:.4f} seconds")

    t2 = time.perf_counter()
    for q in queries:
        print(q, "→", choose_tool(_VS, q))
    t3 = time.perf_counter()
    print(f"Query loop took {t3 - t2:.4f} seconds")
