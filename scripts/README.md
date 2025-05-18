# scripts – Helper Scripts and Utilities

## Purpose

The **`scripts/`** directory holds various utility scripts that assist with development, testing, and maintenance tasks. These scripts are designed to automate common workflows such as running tests, querying the local AI model, indexing documentation, managing dependencies, and adding models. They help keep the project's operations **repeatable** and **offline-friendly**.

## Contents Overview

* **`run_tests.sh`** – The main test harness script. This bash script sets up the environment and runs the full test suite with one command. It installs Python dependencies from `wheelhouse/`, ensures any stray SurrealDB process is terminated, launches a fresh SurrealDB instance (in memory mode) on the default port, bootstraps a test namespace/database, and then triggers `pytest`. It's the recommended way to run tests, encapsulating all prerequisites (so developers or CI can just execute this single script).
* **`ask_qwen.py`** – A convenience script to query a local **Qwen** model through the Ollama server. It uses the OpenAI Python SDK interface pointed at the local Ollama API (base URL `http://localhost:11434/v1`, API key "ollama") to mimic an OpenAI ChatCompletion request. You can provide a prompt and get a completion from the model. By default it targets the model `qwen3:0.6b`. Usage example:

  ```bash
  python scripts/ask_qwen.py -m qwen3:0.6b "Hello, world!"
  ```

  If no prompt is given, it enters an interactive mode where you can type after the model name prompt. This script is useful for testing that the local model is working and for obtaining embeddings or answers manually.
* **`index_docs.py`** – A Python script to **index documentation files** into a SurrealDB vector table. It scans a given directory (by default the `docs/` directory) for all `.md` and `.mdx` files, computes a simple embedding for each file's text, and inserts the content into a SurrealDB table (default table name `docs`). The embedding logic here currently uses a dummy 3-dimensional embedding (`simple_embedding`) for determinism, or can use the same approach as the demo (prompting an LLM) if integrated. Developers can run this script to refresh the docs index. It's also used programmatically in tests (see `tests/test_docs_vector.py`) to verify that documentation can be ingested and queried.
* **`wheelhouse-refresher.txt`** – Instructions to update the offline Python wheels in `wheelhouse/`. It's a bash script that uses `pip download` for each pinned requirement, targeting manylinux2014 x86_64 and CPython 3.11 wheels. Maintainers should run this (in an environment with internet) whenever `requirements.lock` changes, to fetch the corresponding new wheels. The script's `.txt` extension suggests it's not meant to run directly as part of the app, but rather a guide for the developer.
* **`vendor-ollama-model.txt`** – A script to **vendor (add) a new model** to the `models/` directory using Git LFS (described in the models README). It automates setting the `OLLAMA_MODELS` path, pulling the model via `ollama pull`, and updating Git tracking. This script should be executed manually by a developer; it's not invoked during normal runtime or tests. It ensures large model files are added correctly.

*(There may be additional minor scripts or text files, but the above are the primary ones.)*

## Interactions and Integration

* **Test Integration**: The `run_tests.sh` script ties together **bin**, **wheelhouse**, and **tests**. It relies on `bin/surreal` to be present and on the `wheelhouse` for packages. It is referenced in documentation (the main README's quickstart) as the way to run tests. Internally, tests use some scripts too; e.g., `tests/test_docs_vector.py` imports and calls `scripts/index_docs.index_docs()` to index a doc for verification. This means if `index_docs.py` changes, corresponding tests should be updated to match.
* **Demo Integration**: The `demo/text_vector_demo.py` uses `scripts/ask_qwen.py` by spawning it as a subprocess to get embeddings. This cross-link means improvements to `ask_qwen.py` (such as better parsing or error handling) benefit both standalone use and the demo.
* **Environment Setup**: Both `run_tests.sh` and `wheelhouse-refresher.txt` contribute to making the environment reproducible. For instance, `run_tests.sh` exports `PIP_NO_INDEX=1` and `PIP_FIND_LINKS=wheelhouse` so that pip installs only from local wheels, enforcing offline installation. The refresher script, conversely, is run when online to populate those wheels. This separation allows the CI/agent to run tests in a hermetic environment, while a developer with internet can update dependencies in a controlled way.

## Usage Examples

* Running the full test suite: `./scripts/run_tests.sh` (execute from the repository root). This will output log messages (installing deps, launching DB, running tests) and ultimately print test results. It's the one-step command to verify everything.
* Querying the Qwen model: `python3 scripts/ask_qwen.py "What is 2+2?"` will prompt the local Qwen model for an answer to a simple question. Ensure Ollama is running and the model is available before using this.
* Re-indexing docs: `python3 scripts/index_docs.py docs/ollama` will take the markdown files in `docs/ollama` and insert them into SurrealDB (running at the default localhost:8000). You can then query the `docs` table in SurrealDB to confirm the content is stored. Use `--table` if you want a different target table to avoid clobbering the main docs index.
* Adding a new dependency: Edit `requirements.lock` (or use pip-tools to update it), then run the steps in `scripts/wheelhouse-refresher.txt` on a Linux machine. This will download the new wheels. Commit the updated wheels in `wheelhouse/` along with the changed requirements file.

## Developer Notes

* Keep scripts **simple and POSIX-compliant** (for shell scripts) or **Pythonic and modular** (for Python scripts). Since an LLM often maintains this code, clarity is crucial. The scripts contain comments and straightforward logic to make it easy for automation to modify them.
* **Offline First**: All scripts are written with the assumption of no internet access at runtime. If you add a new script (or modify existing ones), do not introduce network calls or dependencies on online resources when the script is executed as part of tests or demos.
* **Executable Permissions**: Remember that `.sh` scripts should be marked executable. Currently, `run_tests.sh` is executable. If an LLM adds a new shell script, a human might need to adjust file permissions in Git accordingly (as the AI might not handle that).
* **Cross-Platform**: The scripts assume a Unix-like environment (use of bash, POSIX commands, etc.). Windows developers should use WSL or Git Bash. Python scripts should run anywhere Python 3.11 is available.
* **Maintenance by AI**: Given that these are maintained by an AI agent, they use consistent patterns (for example, printing progress messages with emojis for clarity in logs, as seen in `run_tests.sh`). Maintainers (human or AI) should preserve such conventions for consistency. 