"""Example storing short text with 3D embeddings."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import httpx

DB_URL = "http://127.0.0.1:8000"
ASK_QWEN = Path(__file__).resolve().parents[1] / "scripts" / "ask_qwen.py"

_SQL_HEADER = {"Accept": "application/json"}


def _sql(client: httpx.Client, query: str) -> list:
    res = client.post("/sql", headers=_SQL_HEADER, content=query)
    res.raise_for_status()
    return res.json()


def _get_embedding(text: str) -> list[float]:
    prompt = (
        "Return a JSON array with three float numbers between 0 and 1 "
        f"representing an embedding for: {text!r}"
    )
    result = subprocess.run(
        ["python", str(ASK_QWEN), prompt], capture_output=True, text=True, check=True
    )
    return json.loads(result.stdout.strip())


def main() -> None:
    with httpx.Client(base_url=DB_URL, auth=("root", "root"), timeout=10.0) as c:
        setup = [
            "DEFINE TABLE item SCHEMALESS;",
            "DEFINE INDEX idx_emb ON item FIELDS embedding MTREE DIMENSION 3;",
        ]
        _sql(c, "USE NS test DB test; " + " ".join(setup))

        docs = [
            "The quick brown fox jumps over the lazy dog",
            "SurrealDB unifies multiple data models",
            "Vectors enable similarity search",
        ]
        for i, doc in enumerate(docs):
            vec = _get_embedding(doc)
            q = (
                "USE NS test DB test; "
                f"CREATE item:{i} SET text = {json.dumps(doc)}, embedding = {vec};"
            )
            _sql(c, q)

        query_vec = _get_embedding("What lets me find similar sentences?")
        res = _sql(
            c,
            f"USE NS test DB test; SELECT text FROM item WHERE embedding <|3|> {query_vec} LIMIT 1;",
        )
        top = (
            res[0]["result"][0]["text"]
            if res and res[0].get("result")
            else "(no match)"
        )
        print("Top result:", top)


if __name__ == "__main__":
    main()
