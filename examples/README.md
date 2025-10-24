# VectorChord Examples

The `examples/` directory collects guided walkthroughs for trying VectorChord's PostgreSQL extension in both simple and retrieval-augmented generation (RAG) workflows. Each scenario provides SQL or Python assets you can run directly against a PostgreSQL instance with the `vchord` extension installed.

## Prerequisites

Before running any example, ensure the following prerequisites are met:

- **PostgreSQL with the `vchord` extension available.** You can use Docker to start a container that has the extension, or install it on an existing database server.
- **`psql` command-line client.** Used to execute the provided SQL scripts.
- **Python 3.9+ (optional).** Required for examples that use a Python client library.
- **Python client library.** The RAG walkthroughs demonstrate usage with [`asyncpg`](https://github.com/MagicStack/asyncpg); install dependencies via `pip install -r examples/rag/requirements.txt`.

Set the following environment variables so both `psql` and the Python scripts know how to reach your database (adjust values for your setup):

```bash
export PGHOST=localhost
export PGPORT=5432
export PGUSER=postgres
export PGPASSWORD=postgres
export PGDATABASE=postgres
```

For Docker-based setups, use the container's exposed host/port combination.

## Running the examples

Use `psql` to run SQL files and the Python interpreter to execute client scripts. Each scenario describes the expected commands and outputs.

- Execute an SQL walkthrough:

  ```bash
  psql -f examples/<scenario>/<script>.sql
  ```

- Run a Python script (after installing requirements):

  ```bash
  pip install -r examples/rag/requirements.txt
  python examples/rag/<script>.py
  ```

The Python scripts print query results and summary statistics to stdout.

## Scenario index

### 1. Basic usage (`examples/basic/`)

Demonstrates enabling the `vchord` extension, creating a table with vector embeddings, inserting sample rows, building a `vchordrq` index, and running a nearest-neighbor query. Run with:

```bash
psql -f examples/basic/basic_usage.sql
```

### 2. Retrieval-Augmented Generation workflows (`examples/rag/`)

Includes a small dataset and Python scripts illustrating hybrid retrieval strategies:

- `setup.sql` loads sample documents with vector and metadata columns. Run with:

  ```bash
  psql -f examples/rag/setup.sql
  ```

- `fusion_retrieval.py` shows dense + keyword fusion queries using `asyncpg`.
- `metadata_filtering.py` applies SQL-level metadata filters before vector search.
- `multi_path_rerank.py` performs multiple candidate retrieval paths and reranks results in Python.

Execute the scripts with:

```bash
python examples/rag/<script>.py
```

Refer to each script's inline documentation for details on connection usage, query construction, and expected output format.
