import json
from pathlib import Path

import httpx
import pytest

from scripts.index_docs import simple_embedding


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


def _setup_table(client: httpx.Client, name: str, items: int = 5) -> None:
    cmds = [
        f"DEFINE TABLE {name} SCHEMALESS;",
        f"DEFINE INDEX idx_{name}_emb ON {name} FIELDS embedding MTREE DIMENSION 3;",
    ]
    for i in range(items):
        vec = [float(i), float(i + 1), float(i + 2)]
        cmds.append(f"CREATE {name}:{i} SET embedding = {vec};")
    _sql(client, "USE NS test DB test; " + " ".join(cmds))


def test_knn_returns_ordered_results(client: httpx.Client):
    _setup_table(client, "vec_order")
    data = _sql(
        client,
        "USE NS test DB test; SELECT id FROM vec_order WHERE embedding <|3|> [2,3,4] LIMIT 3;",
    )
    ids = [row["result"][0]["id"] for row in data if row.get("result")]
    assert ids == ["vec_order:2"], f"Expected nearest vec_order:2, got {ids}"


def test_multiple_tables_isolated(client: httpx.Client) -> None:
    _setup_table(client, "vec_a")
    _setup_table(client, "vec_b")
    data_a = _sql(
        client,
        "USE NS test DB test; SELECT count() FROM vec_a WHERE embedding <|3|> [1,2,3];",
    )
    data_b = _sql(
        client,
        "USE NS test DB test; SELECT count() FROM vec_b WHERE embedding <|3|> [1,2,3];",
    )
    cnt_a = data_a[-1]["result"][0]["count"]
    cnt_b = data_b[-1]["result"][0]["count"]
    assert (
        cnt_a == cnt_b == 1
    ), f"Expected one match in each table, got {cnt_a} and {cnt_b}"


def test_search_dimension_mismatch(client: httpx.Client) -> None:
    _setup_table(client, "vec_err", items=1)
    data = _sql(
        client,
        "USE NS test DB test; SELECT id FROM vec_err WHERE embedding <|3|> [1,2];",
    )
    status = data[-1]["status"]
    assert status == "ERR", "Expected dimension mismatch error"


def test_guest_vector_search_denied(client: httpx.Client) -> None:
    _setup_table(client, "guest_vec")
    with httpx.Client(
        base_url="http://127.0.0.1:8000", auth=("guest", "guest"), timeout=10.0
    ) as guest:
        response = guest.post(
            "/sql",
            headers=_SQL_HEADER,
            content="USE NS test DB test; SELECT 1 FROM guest_vec WHERE embedding <|3|> [0,0,0];",
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"


def test_simple_embedding_roundtrip(tmp_path: Path, client: httpx.Client):
    text = "Vectors are cool"
    path = tmp_path / "note.mdx"
    path.write_text(text)
    table = "simple_docs"
    _setup_table(client, table, items=0)
    emb = simple_embedding(text)
    _sql(
        client,
        f"USE NS test DB test; CREATE {table}:1 SET path = {json.dumps(str(path))}, text = {json.dumps(text)}, embedding = {emb};",
    )
    data = _sql(
        client,
        f"USE NS test DB test; SELECT text FROM {table} WHERE embedding <|3|> {emb} LIMIT 1;",
    )
    returned = data[-1]["result"][0]["text"]
    assert returned == text
