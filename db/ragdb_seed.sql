-- db/ragdb_seed.sql

BEGIN;

-- =========================================================
-- ragdb_seed.sql
-- Seed data for ragdb (minimal)
-- =========================================================

INSERT INTO customers (id, name)
VALUES ('default', 'Default Tenant')
ON CONFLICT (id) DO NOTHING;

INSERT INTO rag_endpoints (customer_id, rag_type)
VALUES ('default', 'pgvector')
ON CONFLICT (customer_id) DO NOTHING;

COMMIT;