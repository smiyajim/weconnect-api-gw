-- db/ragdb_schema.sql

BEGIN;

-- =========================================
-- ragdb_schema.sql
-- PostgreSQL 17
-- =========================================

-- pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- customers
CREATE TABLE IF NOT EXISTS customers (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL
);

-- rag_endpoints
CREATE TABLE IF NOT EXISTS rag_endpoints (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id TEXT NOT NULL,
    rag_type TEXT NOT NULL,
    base_url TEXT,
    api_key TEXT,
    CONSTRAINT rag_endpoints_customer_id_key UNIQUE (customer_id),
    CONSTRAINT rag_endpoints_customer_fk FOREIGN KEY (customer_id) REFERENCES customers (id) ON DELETE CASCADE
);

-- documents (RAG Vector Store)
-- [改修点] meta JSONB カラムを追加し、柔軟なフィルタリングを可能にする
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY,
    customer_id TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR (1536) NOT NULL,
    meta JSONB, 
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT documents_customer_fk FOREIGN KEY (customer_id) REFERENCES customers (id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_documents_customer ON documents (customer_id);
-- [改修点] metaカラムへのGINインデックス追加
CREATE INDEX IF NOT EXISTS idx_documents_meta ON documents USING GIN (meta);
-- ベクトル検索 (Cosine)
CREATE INDEX IF NOT EXISTS idx_documents_embedding ON documents USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

COMMIT;