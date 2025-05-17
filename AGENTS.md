## Repository tour

| Path                            | What lives here                 | Notes                                                                                              |
| ------------------------------- | ------------------------------- | -------------------------------------------------------------------------------------------------- |
| `run_tests.sh`                  | Single‑entry test harness       | Launches SurrealDB in‑memory, wires credentials, then executes the pytest suite. citeturn0file0 |
| `wheelhouse/`                   | Pre‑downloaded manylinux wheels | Keeps the sandbox offline‑friendly; refreshed with `wheelhouse-refresher.txt`. citeturn0file1   |
| `tests/` + `test_surreal_ws.py` | Pytest suite                    | Sanity‑checks `/info` endpoint for both *root* and *guest*. citeturn0file2                      |
| `bin/surreal`                   | Static SurrealDB binary         | Linux x86‑64; memory‑mode only.                                                                    |

## Coding conventions

* **Linting**: We follow `ruff`‑strict (`pyproject.toml` pending).
* **Formatting**: `black` stable.
* **Commits**: Conventional Commits (`feat:`, `fix:`…).