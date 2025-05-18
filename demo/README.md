# demo – SurrealDB Text Vector Demo

## Purpose

The **`demo/`** directory provides an **example application** demonstrating SurrealDB's vector search capability using a local LLM for embeddings. It showcases how short text snippets can be stored with 3-dimensional vector embeddings and later queried by similarity. This is a self-contained offline demo intended to illustrate integration of an LLM (the Qwen model) with SurrealDB's vector index.

## Key Contents

* **`text_vector_demo.py`** – The main demo script. It inserts sample text entries into SurrealDB with a 3-dimensional embedding for each, then queries for the closest match to a given input.
* **`README.md`** – Documentation and instructions on running the demo. It outlines the steps to set up dependencies, launch SurrealDB, and execute the demo script.

The demo leverages components from other parts of the repository:

* It calls the `scripts/ask_qwen.py` helper to generate embeddings via a local Qwen model.
* It uses the same logic as the vector unit tests (see `tests/test_vector.py`) to create a SurrealDB table with a vector index and perform similarity searches.

## How It Works

1. **Generating Embeddings**: Instead of requiring a dedicated embedding model or API, the demo uses a small Qwen language model (hosted via Ollama) to produce embeddings. The `text_vector_demo.py` script invokes `ask_qwen.py` with a prompt like *"Return a JSON array with three float numbers between 0 and 1 representing an embedding for: '<text>'"*. The Qwen model's response (a JSON array of 3 floats) serves as the vector embedding for the given text. This approach allows embeddings to be generated **offline** by the local LLM. (Note: Since the LLM is simply inventing 3 random floats for each distinct text, the "embedding" is not guaranteed to reflect semantic similarity. It is sufficient for demonstrating SurrealDB's vector index functionality in an offline setting.)
2. **Storing Data**: The script defines a SurrealDB table `item` with a 3-dimensional vector index. It inserts several hard-coded example sentences into this table, each with an embedding obtained from the LLM. SurrealDB's vector indexing (`MTREE DIMENSION 3`) allows efficient similarity search on these embeddings.
3. **Querying by Similarity**: The demo then asks the Qwen model for an embedding of a query sentence (e.g. *"What lets me find similar sentences?"*) and performs a vector similarity search in SurrealDB: `SELECT text FROM item WHERE embedding <|3|> [query_vector] LIMIT 1`. SurrealDB returns the stored text with the closest embedding. The result is printed out (the "Top result") in the console.

## Running the Demo

To run the demo completely offline, follow these steps (assuming you have Python 3.11 and have cloned the repo):

1. **Install Dependencies** – Use the vendored wheels to install required packages:

   ```bash
   python3.11 -m pip install -r requirements.lock --no-index --find-links wheelhouse
   ```

   This will install SurrealDB's Python client, OpenAI API client, and other needed libraries from the local `wheelhouse/`.
2. **Start SurrealDB** – Launch the included database server in memory mode:

   ```bash
   bin/surreal start memory --user root --pass root --allow-guests --bind 127.0.0.1:8000 &
   ```

   Ensure this runs **before** executing the demo script. The server will listen on localhost:8000 with default credentials (root/root).
3. **Run the Demo Script** – Execute the Python demo:

   ```bash
   python demo/text_vector_demo.py
   ```

   This will generate embeddings via the local model and perform the vector search, printing the closest matching sentence.

When running, you should see output ending in a line like **"Top result: <sentence>"** which is the stored text most similar to your query.

## Developer Notes

* **Local Model Setup**: The demo assumes you have the **Qwen** model (a smaller 0.6B parameter model variant) available to Ollama under the name `qwen3:0.6b`. If this model is not present, the `ask_qwen.py` calls will fail. Developers can either adjust the model name via the `-m/--model` argument when running the demo, or use the provided model vendor script (see `scripts/vendor-ollama-model.txt`) to pull the required model into `models/ollama`.
* **Cross-Reference with Tests**: This demo is a practical extension of the unit tests. It reuses patterns from `tests/test_vector.py` for setting up the vector index and from `tests/test_docs_vector.py` for embedding generation logic. This ensures that the demo's approach stays in sync with what the test suite is validating.
* **Offline Operation**: All components (SurrealDB, Qwen model, dependencies) are intended to run offline. This makes the demo a self-contained environment to experiment with vector search without external services. If modifying the demo, maintain this offline-first approach so that no internet access is required (this is especially important because the repository's maintainer agent does not permit external calls during automated runs).
