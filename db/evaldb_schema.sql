-- db/evaldb_schema.sql
BEGIN;

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS embedding_eval_runs (
    id UUID PRIMARY KEY,
    customer_id TEXT NOT NULL,
    query TEXT NOT NULL,
    top_k INT NOT NULL,
    filter_meta JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS embedding_eval_results (
    id UUID PRIMARY KEY,
    run_id UUID NOT NULL,
    model_key TEXT NOT NULL,
    results JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT embedding_eval_results_run_fk
        FOREIGN KEY (run_id) REFERENCES embedding_eval_runs (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_embedding_eval_runs_customer_time
  ON embedding_eval_runs (customer_id, created_at);

CREATE INDEX IF NOT EXISTS idx_embedding_eval_results_run
  ON embedding_eval_results (run_id);

COMMIT;