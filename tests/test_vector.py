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


def test_vector_order_by_distance(client):
    _setup_table(client)
    data = _sql(
        client,
        (
            "USE NS test DB test; "
            "SELECT id, vector::distance::euclidean(embedding, [8,9,10]) AS dist "
            "FROM item ORDER BY dist LIMIT 1;"
        ),
    )
    result = [row["result"] for row in data if row.get("result")][0][0]
    assert result["id"] == "item:8", f"Expected closest item:8, got {result}"


def test_vector_dot_product(client):
    _setup_table(client)
    data = _sql(
        client,
        (
            "USE NS test DB test; "
            "SELECT vector::dot(embedding, [1,1,1]) AS dot FROM item WHERE id = item:4;"
        ),
    )
    dot = [row["result"] for row in data if row.get("result")][0][0]["dot"]
    assert dot == 15, f"Expected dot 15, got {dot}"


def test_vector_cross_length_error(client):
    data = _sql(
        client,
        "RETURN vector::cross([1,2,3], [1,2]);",
    )
    status = data[0]["status"]
    assert status == "ERR", "Expected length mismatch error"


def test_vector_search_invalid_dimension(client):
    _setup_table(client)
    data = _sql(
        client,
        "USE NS test DB test; SELECT id FROM item WHERE embedding <|4|> [1,2,3,4];",
    )
    status = data[1]["status"] if len(data) > 1 else data[0]["status"]
    assert status == "ERR" or "Incorrect vector dimension" in str(
        data
    ), "Expected dimension error"


def test_vector_compound_magnitude(client):
    data = _sql(
        client,
        "RETURN vector::magnitude(vector::add(vector::cross([1,0,0], [0,1,0]), [0,0,1]));",
    )
    mag = data[0]["result"]
    assert mag == 2, f"Expected magnitude 2, got {mag}"


def test_vector_add_dimension_error(client):
    data = _sql(
        client,
        "RETURN vector::dot(vector::add([1,2,3], [4,5]), [1,1,1]);",
    )
    status = data[0]["status"]
    assert status == "ERR", "Expected dimension mismatch error"
