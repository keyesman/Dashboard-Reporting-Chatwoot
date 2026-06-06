-- Migration 003: Create sync_log table
-- Catat history setiap kali cron sync berjalan

CREATE TABLE IF NOT EXISTS sync_log (
    id                  SERIAL PRIMARY KEY,
    sync_date           DATE NOT NULL,
    date_from           DATE,
    date_to             DATE,
    total_fetched       INTEGER DEFAULT 0,
    total_inserted      INTEGER DEFAULT 0,
    total_updated       INTEGER DEFAULT 0,
    total_failed        INTEGER DEFAULT 0,
    status              VARCHAR(20) NOT NULL DEFAULT 'success'
                            CHECK (status IN ('success', 'failed', 'partial')),
    error_message       TEXT,
    duration_seconds    FLOAT,
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sync_log_date   ON sync_log(sync_date);
CREATE INDEX IF NOT EXISTS idx_sync_log_status ON sync_log(status);
