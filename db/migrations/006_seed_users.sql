-- Migration 006: Seed initial admin user
-- Email    : admin@email.com
-- Password : Password123 (bcrypt hashed)
-- IMPORTANT: Ganti password setelah pertama kali login!

INSERT INTO users (
    name,
    email,
    password_hash,
    role,
    is_active,
    created_at,
    updated_at
)
VALUES (
    'Administrator',
    'admin@email.com',
    '$2b$12$8FtQRWJUkkwx9aCyuvf5s.J2h92a4Gx4sMzdLzwfrgLNKFybnJiXy',
    'admin',
    TRUE,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
)
ON CONFLICT (email) DO NOTHING;
