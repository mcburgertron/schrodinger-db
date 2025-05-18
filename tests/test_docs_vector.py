import json
import subprocess
from pathlib import Path

import httpx
import pytest

from scripts.index_docs import index_docs, simple_embedding

_SQL_HEADER = {"Accept": "application/json"}


def _sql(client: httpx.Client, query: str) -> list[dict]:
    res = client.post("/sql", headers=_SQL_HEADER, content=query)
    res.raise_for_status()
    return res.json()


@pytest.fixture(scope="module")
def client():
    with httpx.Client(
        base_url="http://127.0.0.1:8000",
        auth=("root", "root"),
        timeout=10.0,
    ) as c:
        yield c


def test_index_contains_full_text(client, tmp_path):
    # exercise the CLI on a single .md file
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


def test_index_docs_success(tmp_path: Path, client: httpx.Client):
    # exercise the programmatic API on a .mdx
    sample = tmp_path / "intro.mdx"
    sample.write_text("SurrealDB docs are great")
    index_docs(tmp_path, client, table="docs_test")

    vec = simple_embedding(sample.read_text())
    data = _sql(
        client,
        f"USE NS test DB test; SELECT text FROM docs_test WHERE embedding <|3|> {vec} LIMIT 1;",
    )
    texts = [
        row["text"] for item in data if item.get("result") for row in item["result"]
    ]
    assert sample.read_text() in texts


def test_index_docs_missing_dir(client: httpx.Client):
    with pytest.raises(FileNotFoundError):
        index_docs(Path("/no/such/path"), client, table="docs_err")
