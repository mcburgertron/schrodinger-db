# wheelhouse – Vendored Python Dependencies

## Purpose

The **`wheelhouse/`** directory contains **pre-downloaded Python wheel files** for all the project's Python dependencies. This allows the environment to be set up **entirely offline** by installing from these local packages, rather than reaching out to PyPI. It is essentially a local package repository, ensuring deterministic builds and no reliance on network connectivity or external package versions.

## Contents

Inside `wheelhouse/` you will find `.whl` files corresponding to each dependency pinned in `requirements.lock`. Key packages include:

* **openai** – OpenAI API client (used for the local Ollama OpenAI-compatible interface).
* **surrealdb** – SurrealDB Python client library.
* **pytest** (and plugins like **pytest-httpx**, **pytest-asyncio**) – Testing framework and helpers.
* **aiohttp** and **websockets** – Async HTTP and WebSocket libraries.
* **jiter** – A small utility library.

Each wheel file is named with the package name, version, and platform (manylinux2014_x86_64) and Python version (cp311 for CPython 3.11).

## Using the Wheelhouse

The wheelhouse is utilized automatically by the setup scripts:

* The `run_tests.sh` script sets the environment variable `PIP_FIND_LINKS="$PWD/wheelhouse"` and `PIP_NO_INDEX=1` to force pip to install from the local `wheelhouse` only. It then runs `pip install -r requirements.lock`, which causes pip to look into `wheelhouse/` for each required package.
* In the quickstart instructions, users are directed to use the `--no-index --find-links wheelhouse` options to pip, achieving the same effect.
* This approach guarantees that the environment uses the exact versions we've vendored, eliminating surprises from upstream version changes.

## Maintenance – Updating Dependencies

When you need to add or upgrade a dependency:

1. Update `requirements.lock` with the desired package versions.
2. On a machine with internet access, run the steps in **`scripts/wheelhouse-refresher.txt`**. This downloads all wheels for the specified platform and Python version into the `wheelhouse/` folder.
3. Check that `wheelhouse/` now contains the updated packages. Remove any obsolete wheels if a package was removed or downgraded.
4. Commit the updated `requirements.lock` and the new/changed files in `wheelhouse/` to the repo.

## Platform Compatibility

The wheels are for **Linux (manylinux)** on **CPython 3.11**. This matches the environment in which the tests are run. If you are on a different platform:

* On Windows or macOS, these Linux wheels won't install. It's recommended to use a Python 3.11 Linux environment (or container) for this project. For Windows, WSL2 Ubuntu is an effective solution.
* If absolutely necessary to work on a non-Linux platform, you could set up a venv and pip install the requirements from PyPI (online) just for development. **Do not** commit those platform-specific wheels.

## Special Considerations

* **No Source Builds**: We use `--only-binary=:all:` in the refresher, so pip will fail if a wheel isn't available. All dependencies must have prebuilt wheels for Linux x64.
* **Pinning**: The `requirements.lock` file pins exact versions. The wheelhouse should always be in sync with those pins.
* **Size Management**: Remove wheels of packages that are no longer used to save space.
* The presence of the wheelhouse means the AI agent can install packages in its environment without network. This is crucial for the agent's tool usage (like running tests). 