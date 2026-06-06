-- Migration 005: Create escalation_categories table
-- Dropdown options untuk escalation category

CREATE TABLE IF NOT EXISTS escalation_categories (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(255) NOT NULL UNIQUE,
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_esc_cat_active ON escalation_categories(is_active);

-- Seed data
INSERT INTO escalation_categories (name, is_active)
VALUES
    ('Action L2 - Adjustment Code',     TRUE),
    ('Action L2 - Adjustment Database', TRUE),
    ('Action L2 - Adjustment Server',   TRUE),
    ('Action L2 - Cross-check',         TRUE),
    ('Action L2 - Discuss & Confirm',   TRUE),
    ('Action L2 - Manual Trigger',      TRUE)
ON CONFLICT DO NOTHING;
