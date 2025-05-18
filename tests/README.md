# tests – Test Suite

## Purpose

The **`tests/`** directory contains the **Pytest test suite** for the project. These tests validate the functionality of SurrealDB in this setup, the integration with the local LLM model, and other utility components. The goal is to catch regressions and ensure that core features (like vector search, authentication, etc.) work as expected in the offline environment. Because the repository is primarily maintained by an AI agent, the tests also serve as an executable specification, guiding the AI (and human contributors) on the intended behavior of the system.

## Test Coverage and Key Files

Each test file focuses on a specific domain of functionality:

* **`test_surreal_ws.py`** – SurrealDB webservice basics. Checks that the `/info` endpoint of SurrealDB responds as expected for different users, verifying authentication and permissions.
* **`test_users.py`** – User management and authentication. Creates a test user, ensures a duplicate user cannot be created, lists users, and deletes the user, verifying access control definitions.
* **`test_vector.py`** – Vector index and functions. Sets up a table with a vector index and dummy data, then tests SurrealDB's vector search and math functions, including error cases and ordering by vector distance.
* **`test_docs_vector.py`** – Documentation indexing and search. Validates the `index_docs.py` script and the concept of storing docs in the database, confirming that documentation can be ingested and queried by similarity.
* **`test_discord_emulator.py`** – Discord emulator functionality. Spins up the local Discord emulator and tests a basic gateway handshake and message flow, ensuring the emulator behaves like a minimal Discord server.

## Running Tests

Run all tests via the provided `run_tests.sh` script (which handles environment setup):

```bash
./scripts/run_tests.sh
```

Or run pytest directly (after starting SurrealDB):

```bash
python -m pytest -q
```

## Testing Conventions and Notes

* **Offline-Only**: Tests never hit external networks. All interactions are with the local SurrealDB or local servers.
* **Stateless**: The SurrealDB instance is fresh for each test session. Tests use the same instance but are expected to isolate their data or clean up as needed.
* **Performance**: The suite should run quickly. Tests avoid unnecessary delays and use small fixed data.
* **Clarity & Assertions**: Test code is written for clarity – straightforward assertions with helpful messages are preferred. Each test targets a single behavior.
* **Coverage of Edge Cases**: The suite covers both normal and error cases to ensure robustness.
* **Integration Tests**: Some tests are integration-style, spinning up components and verifying end-to-end behavior.

## Developer & LLM Maintainer Tips

* Before committing changes, always run the full test suite.
* If a test fails, read its code and error message to understand what behavior is expected.
* When extending functionality, also extend the tests accordingly.
* Keep test functions focused and use descriptive names.
* The tests double as documentation of expected outcomes. 