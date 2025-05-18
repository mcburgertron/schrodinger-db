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

## New Tests

* **Offline‑only** – The tests must never hit the public internet. All HTTP interaction is against local SurrealDB instances.

* **Stateless per test run** – Because the DB is wiped between pytest sessions, each test must create (and, if relevant, clean up) its own fixture data.

* **Fast** – Keep the whole suite under ~5 s wall‑clock. Aim for ≤ 500 ms per test file.

* **Readable assertions** – Prefer plain assert with explicit error messages over hiding logic inside helpers unless the helper is reused ≥ 3×.

* **Edge cases & failures** – At least 40 % of new tests should exercise error conditions ( 4XX/5XX, bad payloads, auth failures) so we don’t drift into “happy‑path only” coverage.

* **Parametrize, don’t copy‑paste** – Use @pytest.mark.parametrize for small input matrices instead of duplicating code blocks.

* **No sleeps** – Poll or hook into Surreal’s deterministic behaviour rather than inserting arbitrary time.sleep.

* **Log hygiene** – Delete any `ollama.log` files before committing.

* **Models** – Never readd models to the repo!