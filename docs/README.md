# docs – Offline Documentation Archive

## Purpose

The **`docs/`** directory contains an **offline archive of documentation** for SurrealDB and the Ollama LLM runtime. These are markdown/MDX files copied from official documentation sources. Storing them in the repository serves two main purposes:

* Provide reference materials for developers and the AI agent maintaining the project (e.g. SurrealQL syntax, SurrealDB usage examples, Ollama configuration) without requiring internet access.
* Serve as input data for the vector search system. Documentation files can be indexed into the database so that the LLM (or other tools) can query them to answer questions or generate context-aware responses.

## Contents

The documentation is organized into subdirectories that mirror the structure of the original docs sources:

* **SurrealDB Docs (`docs.surrealdb.com/`)** – An offline snapshot of SurrealDB's official documentation site. This includes guides, reference materials, and tutorials on SurrealDB, SurrealQL (the query language), Surrealist (UI/clients), etc. Files are primarily in **MDX format** (Markdown with JSX components), preserving the content and structure of the docs site. For example, `docs/docs.surrealdb.com/doc-surrealdb/…` contains SurrealDB core documentation (introduction, deployment, reference guides), while `doc-surrealql/…` contains the SurrealQL language reference, and `doc-surrealist/…` covers the Surrealist UI and cloud concepts.
* **Ollama Docs (`ollama/` directory)** – Documentation for the **Ollama** model-serving tool. These are plain Markdown files (e.g. `faq.md`, `api.md`, `gpu.md`, `troubleshooting.md`, etc.) that describe how to use Ollama: frequently asked questions, API usage, GPU support, troubleshooting, and more. This helps maintainers understand how local model serving works and how to configure it.

All told, this directory acts as a self-hosted knowledge base about the database and model server technologies used in the project.

## How Documentation Is Used

**1. Human Reference:** If working on the code (especially as an AI agent), these files allow looking up details on SurrealDB's behavior or Ollama's configuration without internet. For example, one can open the SurrealDB **reference guide** on vector search or the **Ollama API** docs to recall usage details.

**2. Programmatic Indexing:** The project includes a script (`scripts/index_docs.py`) that reads all `.md` and `.mdx` files under `docs/` and indexes their content into a SurrealDB table for vector-based retrieval. This means the documentation content can be searched via embedding similarity. The test suite confirms this functionality: it runs the indexer on a sample doc and then queries SurrealDB to ensure the full text was stored and can be retrieved. In future, this could power an LLM agent that answers questions using the docs as context.

**3. Demo/Tutorial Potential:** While not currently in a user-facing demo, the presence of offline docs and the indexing capability suggests that one could ask the AI questions about SurrealDB or Ollama and have it pull answers from this local docs vector index. This is a likely *"generation pathway"* the maintainer AI might use to assist development (for example, automatically consulting SurrealDB docs when writing new queries or tests).

## Maintenance

Because this is an **offline copy** of external documentation, it does not automatically update. If SurrealDB or Ollama release updates to their docs:

* **Manual Updates**: A developer (or instructed AI agent) should periodically refresh these files by pulling the latest versions from the official sources. Care should be taken to preserve the directory structure and file names so that links and references remain consistent.
* **Volume**: The docs set is fairly large. Avoid making arbitrary changes. Large-scale edits or reformatting of these files by an AI agent is discouraged, as they should remain faithful to the source. Edits should be limited to necessary updates or corrections.
* **Format**: Many files use MDX (with frontmatter and imports at the top). When indexing, the `index_docs.py` script will treat them similar to Markdown, but note that any Astro/JSX components or imports are likely ignored or treated as text. This is fine for embedding text content. If adding new docs, ensure they are in `.md` or `.mdx` so they will be picked up by the indexer logic.
* **No Serving**: This directory is **not** intended to be a live documentation website. It's purely for local use. Viewing the MDX files directly (without the original site's styling) is possible but not pretty. The primary use is via search or reading raw content.

## Special Considerations for LLM Maintainers

This directory provides valuable context for the AI agent maintaining the code. When making decisions, the agent can cross-reference these docs (e.g., to recall SurrealDB error codes or API usage). We encourage the agent (and human devs) to leverage this knowledge base rather than relying on potentially outdated training data. However, the agent should avoid plagiarizing large verbatim sections of these docs in outputs or commit messages; instead, use them to inform code and explanations. Any summarization or incorporation of doc content into code (e.g., in comments or user-facing messages) should be done carefully and likely with attribution if appropriate. 