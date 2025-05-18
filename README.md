This repo is largely operated by OpenAI Codex. It's not really safe to use since there's a ton of binaries.

## Quickstart

1. Install the Python dependencies from the vendored wheelhouse:

   ```bash
   python3.11 -m pip install -r requirements.lock --no-index --find-links wheelhouse
   ```

2. Launch SurrealDB in memory mode on `localhost:8000`:

   ```bash
   bin/surreal start memory --user root --pass root --allow-guests --bind 127.0.0.1:8000
   ```

3. Run the pytest suite using the provided harness:

   ```bash
   ./scripts/run_tests.sh
   ```

## Repository layout

| Path          | Purpose                                                        |
|---------------|----------------------------------------------------------------|
| `bin/`        | Static SurrealDB binary (Linux x86-64).                         |
| `demo/`       | Example showing text vector search with a small Qwen model.    |
| `docs/`       | Offline copies of SurrealDB and Ollama documentation.          |
| `models/`     | Ollama model blobs. Do not add them back into the repo!       |
| `scripts/`    | Helper scripts such as `run_tests.sh` and `ask_qwen.py`.       |
| `tests/`      | Pytest suite exercising basic SurrealDB features.              |
| `wheelhouse/` | Pre‑downloaded manylinux wheels for offline installation.      |

See `AGENTS.md` for additional contribution guidelines and coding conventions.

