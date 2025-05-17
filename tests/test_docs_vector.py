import json
import subprocess
from pathlib import Path

import httpx
import pytest

_SQL_HEADER = {"Accept": "application/json"}


def _sql(client: httpx.Client, query: str) -> list:
    res = client.post("/sql", headers=_SQL_HEADER, content=query)
    res.raise_for_status()
    return res.json()


@pytest.fixture(scope="module")
def client():
    with httpx.Client(
        base_url="http://127.0.0.1:8000", auth=("root", "root"), timeout=10.0
    ) as c:
        yield c


def test_index_contains_full_text(client, tmp_path):
    doc = Path("docs/ollama/benchmark.md")
    subprocess.run(["python", "scripts/index_docs.py", str(doc)], check=True)
    data = _sql(
        client,
        f"USE NS test DB test; SELECT text FROM docs WHERE path = {json.dumps(str(doc))};",
    )
    result_rows = [row["result"] for row in data if row.get("result")]
    assert result_rows, "No results returned"
    stored = result_rows[0][0]["text"]
    assert stored == doc.read_text(encoding="utf-8")
