-- RAG example dataset setup
--
-- Run with: psql -f examples/rag/setup.sql

\echo 'Preparing RAG corpus tables...'

CREATE EXTENSION IF NOT EXISTS vchord;

DROP TABLE IF EXISTS rag_documents;
CREATE TABLE rag_documents (
    doc_id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    topic TEXT NOT NULL,
    audience TEXT NOT NULL,
    embedding vector(8)
);

INSERT INTO rag_documents (title, body, topic, audience, embedding) VALUES
    (
        'Scaling vector search',
        'Guidance on scaling embedding-based search with sharding strategies.',
        'infrastructure',
        'engineers',
        ARRAY[0.15, 0.42, 0.01, 0.61, 0.23, 0.57, 0.05, 0.12]
    ),
    (
        'Prompt engineering checklist',
        'Step-by-step checklist for crafting effective prompts in customer support scenarios.',
        'prompting',
        'support',
        ARRAY[0.62, 0.14, 0.18, 0.09, 0.45, 0.11, 0.37, 0.08]
    ),
    (
        'LLM latency tuning',
        'How to profile and tune LLM latency when deploying on GPU-backed instances.',
        'infrastructure',
        'engineers',
        ARRAY[0.22, 0.51, 0.07, 0.48, 0.34, 0.41, 0.16, 0.29]
    ),
    (
        'Tone customization tips',
        'Guidelines for adjusting generation tone and politeness for enterprise chatbots.',
        'prompting',
        'marketing',
        ARRAY[0.48, 0.19, 0.33, 0.12, 0.57, 0.06, 0.26, 0.17]
    ),
    (
        'Security review checklist',
        'Checklist covering data access, encryption, and auditing for AI services.',
        'governance',
        'security',
        ARRAY[0.11, 0.36, 0.09, 0.73, 0.28, 0.64, 0.02, 0.04]
    );

DROP INDEX IF EXISTS rag_documents_embedding_vchordrq_idx;
CREATE INDEX rag_documents_embedding_vchordrq_idx
    ON rag_documents
    USING vchordrq (embedding vector_l2_ops);

CREATE INDEX rag_documents_topic_idx ON rag_documents(topic);
CREATE INDEX rag_documents_audience_idx ON rag_documents(audience);

\echo 'RAG dataset ready. Five documents inserted.'
