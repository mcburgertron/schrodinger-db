from pathlib import Path

import httpx
import pytest

from scripts.index_docs import index_docs, simple_embedding


@pytest.fixture(scope="module")
def client():
    with httpx.Client(
        base_url="http://127.0.0.1:8000", auth=("root", "root"), timeout=10.0
    ) as c:
        yield c


_SQL_HEADER = {"Accept": "application/json"}


def _sql(client: httpx.Client, query: str):
    res = client.post("/sql", headers=_SQL_HEADER, content=query)
    res.raise_for_status()
    return res.json()


def test_index_docs_success(tmp_path: Path, client: httpx.Client):
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
