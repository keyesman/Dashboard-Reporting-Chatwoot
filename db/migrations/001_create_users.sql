-- Migration 001: Create users table
-- Users untuk login ke dashboard (terpisah dari agent Chatwoot)

CREATE TABLE IF NOT EXISTS users (
    id                  SERIAL PRIMARY KEY,
    name                VARCHAR(255) NOT NULL,
    email               VARCHAR(255) NOT NULL UNIQUE,
    password_hash       VARCHAR(255) NOT NULL,
    role                VARCHAR(50)  NOT NULL DEFAULT 'viewer'
                            CHECK (role IN ('admin', 'leader', 'viewer')),
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,

    -- OTP (Phase 2 nanti)
    otp_code            VARCHAR(6),
    otp_expired_at      TIMESTAMP,
    otp_verified        BOOLEAN DEFAULT FALSE,

    last_login_at       TIMESTAMP,
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_email  ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role   ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);
