#!/usr/bin/env python3
"""Index SurrealDB documentation into a SurrealDB vector table."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import httpx

_SQL_HEADER = {"Accept": "application/json"}


def simple_embedding(text: str) -> list[float]:
    """Return a deterministic 3-dimensional embedding for *text*."""
    digest = hashlib.sha256(text.encode()).digest()
    return [b / 255 for b in digest[:3]]


def _sql(client: httpx.Client, query: str) -> None:
    res = client.post("/sql", headers=_SQL_HEADER, content=query)
    res.raise_for_status()


def index_docs(base_dir: Path, client: httpx.Client, table: str = "docs") -> None:
    """Index all ``*.mdx`` files under ``base_dir`` into ``table``."""
    if not base_dir.is_dir():
        raise FileNotFoundError(base_dir)

    setup = [
        f"DEFINE TABLE {table} SCHEMALESS;",
        f"DEFINE INDEX idx_{table}_emb ON {table} FIELDS embedding MTREE DIMENSION 3;",
    ]
    _sql(client, "USE NS test DB test; " + " ".join(setup))

    for path in base_dir.rglob("*.mdx"):
        text = path.read_text(errors="ignore")
        emb = simple_embedding(text)
        q = (
            "USE NS test DB test; "
            f"CREATE {table} SET path = {json.dumps(str(path))}, text = {json.dumps(text)}, embedding = {emb};"
        )
        _sql(client, q)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("doc_root", type=Path, help="Path to SurrealDB docs base")
    parser.add_argument("--url", default="http://127.0.0.1:8000")
    parser.add_argument("--user", default="root")
    parser.add_argument("--password", default="root")
    parser.add_argument("--table", default="docs")
    args = parser.parse_args()

    with httpx.Client(
        base_url=args.url, auth=(args.user, args.password), timeout=10.0
    ) as c:
        index_docs(args.doc_root, c, table=args.table)


if __name__ == "__main__":
    main()
