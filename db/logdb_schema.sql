-- db/logdb_schema.sql

BEGIN;

-- =========================================================
-- logdb_schema.sql
-- Access / Audit / Tool execution logs
-- =========================================================

-- UUID を使うなら有効化（今回は文字列UUIDなので任意）
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ---------------------------------------------------------
-- Access Logs
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS access_logs (
    id           VARCHAR(36) PRIMARY KEY,
    tenant_id    VARCHAR(64) NOT NULL,

    endpoint     VARCHAR(255),
    action       VARCHAR(255),

    prompt       TEXT,
    tool_used    VARCHAR(255),
    tool_result  JSONB,
    llm_response TEXT,

    meta         JSONB,

    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ---------------------------------------------------------
-- Indexes
-- ---------------------------------------------------------

-- tenant 単位検索
CREATE INDEX IF NOT EXISTS idx_access_logs_tenant
    ON access_logs (tenant_id);

-- 時系列検索（ログ可視化・削除用）
CREATE INDEX IF NOT EXISTS idx_access_logs_created_at
    ON access_logs (created_at);

-- JSON 検索用（将来 Kibana / Grafana 連携）
CREATE INDEX IF NOT EXISTS idx_access_logs_meta
    ON access_logs
    USING GIN (meta);

-- =========================================================
-- Future tables (commented)
-- =========================================================
-- CREATE TABLE tool_logs ( ... );
-- CREATE TABLE audit_logs ( ... );

COMMIT;