--- db/logdb_seed.sql

BEGIN;

-- =========================================================
-- logdb_seed.sql
-- Seed data for logdb (minimal)
-- =========================================================

-- ログDBは基本的に seed 不要
-- ここでは疎通確認用のダミーレコードのみ（任意）

INSERT INTO access_logs (
    id,
    tenant_id,
    endpoint,
    action,
    meta
) VALUES (
    '00000000-0000-0000-0000-000000000000',
    'seed_tenant',
    'SYSTEM',
    'INIT',
    '{"message": "logdb initialized"}'
)
ON CONFLICT (id) DO NOTHING;

COMMIT;