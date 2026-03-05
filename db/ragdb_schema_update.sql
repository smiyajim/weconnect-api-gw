-- db/ragdb_schema_update.sql

BEGIN;

-- =========================================
-- ragdb_schema_update.sql
-- PostgreSQL 17
-- For updating existing schema to support multiple embedding types
-- =========================================

ALTER TABLE documents RENAME COLUMN embedding TO embedding_openai;

ALTER TABLE documents
 ADD COLUMN embedding_para_multi VECTOR(768),
 ADD COLUMN embedding_all_mpnet VECTOR(768),
 ADD COLUMN embedding_sbert_ja VECTOR(768);

DROP INDEX IF EXISTS idx_documents_embedding;

CREATE INDEX IF NOT EXISTS idx_documents_embedding_openai
 ON documents USING ivfflat (embedding_openai vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_documents_embedding_para_multi
 ON documents USING ivfflat (embedding_para_multi vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_documents_embedding_all_mpnet
 ON documents USING ivfflat (embedding_all_mpnet vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_documents_embedding_sbert_ja
 ON documents USING ivfflat (embedding_sbert_ja vector_cosine_ops) WITH (lists = 100);

COMMIT;