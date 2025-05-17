from __future__ import annotations

import argparse
import json
from pathlib import Path

import httpx

DB_URL = "http://127.0.0.1:8000"
_SQL_HEADER = {"Accept": "application/json"}


def _sql(client: httpx.Client, query: str) -> list:
    res = client.post("/sql", headers=_SQL_HEADER, content=query)
    res.raise_for_status()
    return res.json()


def _index_file(client: httpx.Client, file_path: Path) -> None:
    text = file_path.read_text(encoding="utf-8")
    path = str(file_path)
    query = (
        "USE NS test DB test; "
        f"CREATE docs SET path = {json.dumps(path)}, text = {json.dumps(text)};"
    )
    _sql(client, query)


def index_docs(root: Path) -> None:
    files = [root] if root.is_file() else list(root.rglob("*.md"))
    with httpx.Client(base_url=DB_URL, auth=("root", "root"), timeout=10.0) as c:
        for f in files:
            _index_file(c, f)


def main() -> None:
    parser = argparse.ArgumentParser(description="Index markdown docs into SurrealDB")
    parser.add_argument("path", type=Path, nargs="?", default=Path("docs"))
    args = parser.parse_args()
    index_docs(args.path)


if __name__ == "__main__":
    main()
