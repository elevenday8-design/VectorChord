-- Basic VectorChord usage walkthrough
--
-- Run with: psql -f examples/basic/basic_usage.sql

\echo 'Creating extension and sample table for VectorChord demo...'

CREATE EXTENSION IF NOT EXISTS vchord;

DROP TABLE IF EXISTS demo_embeddings;
CREATE TABLE demo_embeddings (
    id SERIAL PRIMARY KEY,
    label TEXT NOT NULL,
    embedding vector(4)
);

INSERT INTO demo_embeddings (label, embedding) VALUES
    ('alpha', ARRAY[0.1, 0.0, 0.2, 0.9]),
    ('bravo', ARRAY[0.9, 0.1, 0.2, 0.0]),
    ('charlie', ARRAY[0.0, 0.8, 0.2, 0.1]),
    ('delta', ARRAY[0.3, 0.2, 0.7, 0.6]);

\echo 'Building vchordrq index...'

DROP INDEX IF EXISTS demo_embeddings_embedding_vchordrq_idx;
CREATE INDEX demo_embeddings_embedding_vchordrq_idx
    ON demo_embeddings
    USING vchordrq (embedding vector_l2_ops);

\echo 'Running nearest-neighbor search for query vector [0.0, 0.2, 0.4, 0.8]...'

WITH query AS (
    SELECT ARRAY[0.0, 0.2, 0.4, 0.8]::vector AS q
)
SELECT d.id,
       d.label,
       (d.embedding <-> q) AS distance
FROM demo_embeddings AS d,
     query
ORDER BY d.embedding <-> q
LIMIT 3;
