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


def test_create_user(client):
    data = _sql(
        client,
        'USE NS test DB test; DEFINE USER bob ON DATABASE PASSWORD "pass" ROLES OWNER;',
    )
    assert data[1]["status"] == "OK"


def test_duplicate_user_conflict(client):
    data = _sql(
        client,
        'USE NS test DB test; DEFINE USER bob ON DATABASE PASSWORD "pass" ROLES OWNER;',
    )
    assert data[1]["status"] == "ERR"


def test_list_users_filtered_by_role(client):
    data = _sql(client, "USE NS test DB test; INFO FOR DB;")
    users = data[1]["result"]["users"]
    owners = {name: defn for name, defn in users.items() if "ROLES OWNER" in defn}
    assert "bob" in owners


def test_delete_user(client):
    _sql(client, "USE NS test DB test; REMOVE USER bob ON DATABASE;")
    data = _sql(client, "USE NS test DB test; INFO FOR DB;")
    users = data[1]["result"]["users"]
    assert "bob" not in users
