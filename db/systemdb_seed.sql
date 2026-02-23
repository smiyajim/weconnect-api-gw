--  db/systemdb_seed.sql

BEGIN;

-- =========================================
-- 初期データ投入用
-- =========================================

SET search_path = public;

-- -------------------------
-- customers
-- -------------------------
-- INSERT INTO customers (id, name) VALUES
--     ('customer_001', 'Example Customer')
-- ON CONFLICT (id) DO NOTHING;
INSERT INTO customers (id, name) VALUES
    ('default', 'Default Tenant')
ON CONFLICT (id) DO NOTHING;
-- -------------------------
-- rag_endpoints
-- -------------------------
-- INSERT INTO rag_endpoints (
--     customer_id,
--     rag_type,
--     base_url,
--     api_key
-- ) VALUES (
--     'customer_001',
--     'openai',
--     'https://api.openai.com/v1',
--     'DUMMY_API_KEY'
-- )
-- ON CONFLICT (customer_id) DO NOTHING;
INSERT INTO rag_endpoints (
    customer_id,
    rag_type,
    base_url,
    api_key
) VALUES (
    'default',
    'pgvector',
    'http://localhost:8080',
    'DUMMY_API_KEY'
)
ON CONFLICT (customer_id) DO NOTHING;

COMMIT;