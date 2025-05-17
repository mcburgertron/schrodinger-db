import httpx
import pytest


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


def _setup_table(client: httpx.Client):
    cmds = [
        "DEFINE TABLE item SCHEMALESS;",
        "DEFINE INDEX idx_emb ON item FIELDS embedding MTREE DIMENSION 3;",
    ]
    for i in range(20):
        vec = [i, i + 1, i + 2]
        cmds.append(f"CREATE item:{i} SET embedding = {vec};")
    _sql(client, "USE NS test DB test; " + " ".join(cmds))


def test_vector_search_success(client):
    _setup_table(client)
    data = _sql(
        client,
        "USE NS test DB test; SELECT id FROM item WHERE embedding <|3|> [5,6,7];",
    )
    ids = [row["result"][0]["id"] for row in data if row.get("result")]
    assert ids and ids[0] == "item:5", f"Expected item:5 first, got {ids}"


def test_vector_dimension_mismatch(client):
    _setup_table(client)
    data = _sql(
        client,
        "USE NS test DB test; SELECT id FROM item WHERE embedding <|3|> [1,2];",
    )
    status = data[1]["status"] if len(data) > 1 else data[0]["status"]
    assert status == "ERR" or "Incorrect vector dimension" in str(
        data
    ), "Expected dimension error"
