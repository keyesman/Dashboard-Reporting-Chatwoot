-- Migration 004: Create shift_config table
-- Konfigurasi shift kerja, bisa diubah dari UI oleh leader/admin

CREATE TABLE IF NOT EXISTS shift_config (
    id              SERIAL PRIMARY KEY,
    shift_name      VARCHAR(100) NOT NULL,
    start_time      TIME NOT NULL,
    end_time        TIME NOT NULL,
    priority_order  INTEGER NOT NULL DEFAULT 1,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_shift_active ON shift_config(is_active);

-- Seed data default
INSERT INTO shift_config (shift_name, start_time, end_time, priority_order, is_active)
VALUES
    ('Pagi',         '05:00', '07:59', 1, TRUE),
    ('Siang',        '08:00', '17:00', 2, TRUE),
    ('Malam',        '17:01', '23:00', 3, TRUE),
    ('Out of Hours', '23:01', '04:59', 4, TRUE)
ON CONFLICT DO NOTHING;
