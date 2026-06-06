-- Migration 002: Create conversations table
-- Data ticket dari Chatwoot

CREATE TABLE IF NOT EXISTS conversations (
    id                          SERIAL PRIMARY KEY,
    ticket_id                   INTEGER NOT NULL UNIQUE,
    created_at                  TIMESTAMP,
    status                      VARCHAR(50),

    -- Agent
    agent                       VARCHAR(255),

    -- Dari label parsing
    service                     VARCHAR(100),
    priority                    VARCHAR(10),
    escalate                    VARCHAR(10),
    type                        VARCHAR(100),
    raw_labels                  TEXT,

    -- Metrics
    frt_seconds                 INTEGER,
    resolution_time_seconds     INTEGER,
    resolve_count               INTEGER DEFAULT 0,
    is_reopened                 BOOLEAN DEFAULT FALSE,

    -- Content
    last_note                   TEXT,

    -- Customer info
    company                     VARCHAR(255),
    customer                    VARCHAR(255),
    phone                       VARCHAR(50),

    -- Escalation (diisi manual oleh leader)
    escalation_note             TEXT,
    escalation_category         VARCHAR(255),
    escalation_updated_by       INTEGER REFERENCES users(id),
    escalation_updated_at       TIMESTAMP,

    -- Sync metadata
    synced_at                   TIMESTAMP,
    updated_at                  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_conv_ticket_id  ON conversations(ticket_id);
CREATE INDEX IF NOT EXISTS idx_conv_created_at ON conversations(created_at);
CREATE INDEX IF NOT EXISTS idx_conv_status     ON conversations(status);
CREATE INDEX IF NOT EXISTS idx_conv_agent      ON conversations(agent);
CREATE INDEX IF NOT EXISTS idx_conv_service    ON conversations(service);
CREATE INDEX IF NOT EXISTS idx_conv_priority   ON conversations(priority);
CREATE INDEX IF NOT EXISTS idx_conv_escalate   ON conversations(escalate);
CREATE INDEX IF NOT EXISTS idx_conv_type       ON conversations(type);
