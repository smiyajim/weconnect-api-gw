--  db/systemdb_schema.sql

BEGIN;

-- =========================================
-- systemdb_schema.sql
-- PostgreSQL 17
-- =========================================

-- 念のため public スキーマを明示
SET search_path = public;

-- -------------------------
-- customers
-- -------------------------
CREATE TABLE IF NOT EXISTS customers (
    id   text NOT NULL,
    name text NOT NULL,
    CONSTRAINT customers_pkey PRIMARY KEY (id)
);

-- -------------------------
-- rag_endpoints
-- -------------------------
CREATE TABLE IF NOT EXISTS rag_endpoints (
    id          bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
    customer_id text   NOT NULL,
    rag_type    text   NOT NULL,
    base_url    text,
    api_key     text,
    CONSTRAINT rag_endpoints_pkey PRIMARY KEY (id),
    CONSTRAINT rag_endpoints_customer_id_key UNIQUE (customer_id),
    CONSTRAINT rag_endpoints_customer_fk
        FOREIGN KEY (customer_id)
        REFERENCES customers(id)
        ON DELETE CASCADE
);

COMMIT;