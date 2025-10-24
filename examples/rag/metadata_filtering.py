"""Vector search with SQL-level metadata filtering.

This script illustrates how to restrict candidate documents based on
structured metadata columns before executing vector similarity search.

Steps:
1. Connect to PostgreSQL using credentials from environment variables.
2. Filter documents by `topic` and `audience` in SQL.
3. Order the remaining rows by L2 distance using the `<->` operator.
4. Display the nearest matches.

Run with:
    python examples/rag/metadata_filtering.py
"""

import asyncio
import os
from typing import Sequence

import asyncpg


def _env(name: str, default: str | None = None) -> str:
    """Retrieve an environment variable or raise if missing."""

    value = os.getenv(name, default)
    if value is None:
        raise RuntimeError(f"Environment variable {name} is required")
    return value


async def query_with_filters(
    conn: asyncpg.Connection,
    query_vector: Sequence[float],
    topic: str,
    audience: str,
) -> list[asyncpg.Record]:
    """Execute a metadata-filtered nearest-neighbor search."""

    sql = """
    SELECT doc_id,
           title,
           topic,
           audience,
           embedding <-> $1::vector AS distance
    FROM rag_documents
    WHERE topic = $2
      AND audience = $3
    ORDER BY embedding <-> $1::vector
    LIMIT 3;
    """
    return await conn.fetch(sql, query_vector, topic, audience)


async def main() -> None:
    """Entry point: run the filtered vector search demo."""

    conn = await asyncpg.connect(
        host=_env("PGHOST"),
        port=int(_env("PGPORT", "5432")),
        user=_env("PGUSER"),
        password=_env("PGPASSWORD"),
        database=_env("PGDATABASE"),
    )

    query_vector = [0.10, 0.40, 0.05, 0.60, 0.20, 0.55, 0.05, 0.10]

    try:
        rows = await query_with_filters(conn, query_vector, topic="infrastructure", audience="engineers")
    finally:
        await conn.close()

    print("Metadata-filtered vector search results:")
    for row in rows:
        print(
            f"- doc_id={row['doc_id']} title={row['title']!r} "
            f"topic={row['topic']} audience={row['audience']} distance={row['distance']:.3f}"
        )


if __name__ == "__main__":
    asyncio.run(main())
