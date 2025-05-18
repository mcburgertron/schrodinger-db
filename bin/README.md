# bin – SurrealDB Binary

## Purpose

The **`bin/`** directory contains the **SurrealDB** database server binary for Linux x86-64 systems. This pre-compiled executable enables the project to run a SurrealDB instance **offline** (without needing a separate installation). By bundling the database binary, the test suite and demo can spin up a local database easily.

## Key File

* **`surreal`** – The SurrealDB server executable (Linux 64-bit).

## Usage and Integration

The SurrealDB binary is primarily used to launch an in-memory database instance for testing and demos. For example, the test harness script uses:

```bash
bin/surreal start memory --user root --pass root --allow-guests --bind 127.0.0.1:8000 &
```

to start SurrealDB in memory-only mode on port 8000. In this mode, data is not persisted to disk, aligning with the test requirements. The binary is integrated into automated workflows:

* **Test Suite** – The `run_tests.sh` script adds `bin/` to the PATH and invokes the SurrealDB server in the background before running tests.
* **Demo** – The demo instructions also have you start the server from `bin/` prior to running demo scripts.

Developers or automated agents should ensure the SurrealDB process is properly **terminated** after use. The test harness includes a trap to kill the SurrealDB process on exit, preventing orphan processes.

## Special Considerations

* **Platform**: The included binary is Linux-specific. Developers on Windows or macOS should run it under a Linux environment (e.g. WSL on Windows) or obtain a compatible SurrealDB binary for their platform. The repository's setup scripts assume a Linux environment.
* **Memory Mode**: SurrealDB is run in memory mode (no on-disk storage) by default for simplicity and test isolation. The `/info` endpoint of SurrealDB may return HTTP 404 in memory mode (which is expected) or 200 when supported, and requires admin authentication. The test suite confirms that `root` user can access `/info` while `guest` cannot.
* **Updates**: If a new SurrealDB version is needed, maintainers should update this binary file. Never attempt to edit or generate this binary from code – it should be downloaded from SurrealDB's releases. 