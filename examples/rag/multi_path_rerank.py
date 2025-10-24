"""Client-side multi-path retrieval with reranking.

The script executes two complementary candidate generation strategies:

1. Dense vector similarity using the `vchord` index.
2. Keyword search via PostgreSQL full-text ranking.

The candidates are merged and reranked in Python to illustrate how you can
experiment with custom heuristics before handing results to an LLM.

Steps:
- Connect using environment variables (PGHOST, PGPORT, PGUSER, PGPASSWORD, PGDATABASE).
- Collect vector and lexical candidates.
- Combine them with configurable weights.
- Print the final reranked list with per-source contributions.

Run with:
    python examples/rag/multi_path_rerank.py
"""

import asyncio
import os
from dataclasses import dataclass
from typing import Sequence

import asyncpg


@dataclass
class Candidate:
    """Representation of a retrieved document and its scoring details."""

    doc_id: int
    title: str
    topic: str
    audience: str
    vector_score: float = 0.0
    text_score: float = 0.0

    @property
    def fused(self) -> float:
        """Weighted score used for reranking."""

        return 0.6 * self.vector_score + 0.4 * self.text_score


def _env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None:
        raise RuntimeError(f"Environment variable {name} is required")
    return value


async def fetch_vector_candidates(conn: asyncpg.Connection, query_vector: Sequence[float]) -> list[Candidate]:
    """Retrieve top-k vector neighbors and convert distance into similarity."""

    sql = """
    SELECT doc_id,
           title,
           topic,
           audience,
           -1 * (embedding <-> $1::vector) AS vector_score
    FROM rag_documents
    ORDER BY embedding <-> $1::vector
    LIMIT 5;
    """
    rows = await conn.fetch(sql, query_vector)
    return [Candidate(row["doc_id"], row["title"], row["topic"], row["audience"], vector_score=row["vector_score"]) for row in rows]


async def fetch_text_candidates(conn: asyncpg.Connection, keywords: str) -> list[Candidate]:
    """Retrieve keyword-based matches with text ranking."""

    sql = """
    SELECT doc_id,
           title,
           topic,
           audience,
           ts_rank(to_tsvector('english', title || ' ' || body), plainto_tsquery('english', $1)) AS text_score
    FROM rag_documents
    WHERE plainto_tsquery('english', $1) <> ''
    ORDER BY text_score DESC
    LIMIT 5;
    """
    rows = await conn.fetch(sql, keywords)
    return [Candidate(row["doc_id"], row["title"], row["topic"], row["audience"], text_score=row["text_score"]) for row in rows]


async def main() -> None:
    """Run both retrieval paths and rerank the merged candidates."""

    conn = await asyncpg.connect(
        host=_env("PGHOST"),
        port=int(_env("PGPORT", "5432")),
        user=_env("PGUSER"),
        password=_env("PGPASSWORD"),
        database=_env("PGDATABASE"),
    )

    query_vector = [0.18, 0.45, 0.08, 0.58, 0.27, 0.50, 0.08, 0.15]
    keywords = "checklist security"

    try:
        vector_results, text_results = await asyncio.gather(
            fetch_vector_candidates(conn, query_vector),
            fetch_text_candidates(conn, keywords),
        )
    finally:
        await conn.close()

    combined: dict[int, Candidate] = {}
    for candidate in vector_results + text_results:
        existing = combined.get(candidate.doc_id)
        if existing is None:
            combined[candidate.doc_id] = candidate
        else:
            # Merge scores from both retrieval paths.
            existing.vector_score = max(existing.vector_score, candidate.vector_score)
            existing.text_score = max(existing.text_score, candidate.text_score)

    reranked = sorted(combined.values(), key=lambda c: c.fused, reverse=True)

    print("Multi-path reranked results:")
    for cand in reranked:
        print(
            f"- doc_id={cand.doc_id} title={cand.title!r} topic={cand.topic} audience={cand.audience} "
            f"vector_score={cand.vector_score:.3f} text_score={cand.text_score:.3f} fused={cand.fused:.3f}"
        )


if __name__ == "__main__":
    asyncio.run(main())
