import pytest
import httpx

def test_surrealdb_info_root():
    url = "http://127.0.0.1:8000/info"
    auth = ("root", "root")
    response = httpx.get(url, auth=auth, timeout=10.0)
    # 404 is normal for /info in memory mode, 401 means auth failed
    assert response.status_code in (200, 404), f"Unexpected status: {response.status_code} {response.text}"

def test_surrealdb_info_guest():
    url = "http://127.0.0.1:8000/info"
    auth = ("guest", "guest")
    response = httpx.get(url, auth=auth, timeout=10.0)
    assert response.status_code == 401, "Guest should not be able to access /info"
