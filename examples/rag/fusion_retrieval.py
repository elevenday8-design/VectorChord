"""Hybrid retrieval example for VectorChord.

This script demonstrates how to combine vector similarity scoring with
full-text ranking directly inside PostgreSQL.  It:

1. Connects to PostgreSQL using connection details from environment variables.
2. Defines both a dense embedding query and lexical keywords.
3. Runs a SQL query that fuses the scores using a weighted average.
4. Prints the ranked results with both component scores.

Required environment variables:
    PGHOST, PGPORT, PGUSER, PGPASSWORD, PGDATABASE

Run with:
    python examples/rag/fusion_retrieval.py
"""

import asyncio
import os
from typing import Sequence

import asyncpg


def _env(name: str, default: str | None = None) -> str:
    """Fetch a required environment variable with an optional default."""

    value = os.getenv(name, default)
    if value is None:
        raise RuntimeError(f"Environment variable {name} is required")
    return value


async def fetch_results(conn: asyncpg.Connection, query_vector: Sequence[float], keywords: str) -> list[asyncpg.Record]:
    """Run a hybrid retrieval SQL query and return the result records."""

    sql = """
    WITH
    query_embedding AS (
        SELECT $1::vector AS embedding,
               plainto_tsquery('english', $2) AS ts_query
    ),
    vector_candidates AS (
        SELECT d.doc_id,
               d.title,
               d.body,
               d.topic,
               d.audience,
               -- Convert distance into similarity by flipping sign.
               -1 * (d.embedding <-> q.embedding) AS vector_score
        FROM rag_documents AS d
        CROSS JOIN query_embedding AS q
        ORDER BY d.embedding <-> q.embedding
        LIMIT 5
    ),
    lexical_scores AS (
        SELECT d.doc_id,
               ts_rank(to_tsvector('english', d.title || ' ' || d.body), q.ts_query) AS text_score
        FROM rag_documents AS d
        CROSS JOIN query_embedding AS q
        WHERE q.ts_query <> ''
    )
    SELECT vc.doc_id,
           vc.title,
           vc.topic,
           vc.audience,
           vc.vector_score,
           COALESCE(ls.text_score, 0.0) AS text_score,
           (0.7 * vc.vector_score + 0.3 * COALESCE(ls.text_score, 0.0)) AS fused_score
    FROM vector_candidates AS vc
    LEFT JOIN lexical_scores AS ls USING (doc_id)
    ORDER BY fused_score DESC
    LIMIT 3;
    """
    return await conn.fetch(sql, query_vector, keywords)


async def main() -> None:
    """Entry point: connect, run hybrid retrieval, and print results."""

    conn = await asyncpg.connect(
        host=_env("PGHOST"),
        port=int(_env("PGPORT", "5432")),
        user=_env("PGUSER"),
        password=_env("PGPASSWORD"),
        database=_env("PGDATABASE"),
    )

    query_vector = [0.20, 0.50, 0.05, 0.55, 0.30, 0.45, 0.10, 0.20]
    keywords = "latency tuning"

    try:
        rows = await fetch_results(conn, query_vector, keywords)
    finally:
        await conn.close()

    print("Hybrid retrieval results (vector + lexical fusion):")
    for row in rows:
        print(
            f"- doc_id={row['doc_id']} title={row['title']!r} topic={row['topic']} "
            f"vector_score={row['vector_score']:.3f} text_score={row['text_score']:.3f} "
            f"fused={row['fused_score']:.3f}"
        )


if __name__ == "__main__":
    asyncio.run(main())
