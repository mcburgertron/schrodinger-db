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


def _sql(client: httpx.Client, query: str) -> list[dict]:
    """Send a SQL POST; return the parsed JSON payload."""
    res = client.post("/sql", headers=_SQL_HEADER, content=query)
    res.raise_for_status()
    return res.json()


def index_docs(
    base: Path,
    client: httpx.Client,
    table: str = "docs",
) -> None:
    """
    Walk `base` (file or directory), find all *.md and *.mdx,
    compute embeddings, and CREATE into SurrealDB `table`.
    """
    # allow single‐file invocation:
    if base.is_file():
        files = [base]
    elif base.is_dir():
        files = list(base.rglob("*.md")) + list(base.rglob("*.mdx"))
    else:
        raise FileNotFoundError(f"{base!r} does not exist")

    # ensure table + index exist
    setup = [
        f"DEFINE TABLE {table} SCHEMALESS;",
        f"DEFINE INDEX idx_{table}_emb ON {table} FIELDS embedding MTREE DIMENSION 3;",
    ]
    _sql(client, "USE NS test DB test; " + " ".join(setup))

    for path in files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        emb = simple_embedding(text)
        q = (
            "USE NS test DB test; "
            f"CREATE {table} SET "
            f"path = {json.dumps(str(path))}, "
            f"text = {json.dumps(text)}, "
            f"embedding = {emb};"
        )
        _sql(client, q)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "doc_root",
        type=Path,
        nargs="?",
        default=Path("docs"),
        help="Path to a .md/.mdx file or a directory of docs",
    )
    parser.add_argument("--url", default="http://127.0.0.1:8000")
    parser.add_argument("--user", default="root")
    parser.add_argument("--password", default="root")
    parser.add_argument("--table", default="docs")
    args = parser.parse_args()

    with httpx.Client(
        base_url=args.url,
        auth=(args.user, args.password),
        timeout=10.0,
    ) as client:
        index_docs(args.doc_root, client, table=args.table)


if __name__ == "__main__":
    main()
