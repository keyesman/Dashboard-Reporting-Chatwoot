# ADR-001: Authentication menggunakan JWT + Bcrypt

## Status
Accepted

## Context
Dashboard membutuhkan sistem login yang secure namun simpel untuk
diimplementasikan, dengan kemungkinan extend ke OTP di masa depan.

## Decision
Menggunakan JWT (JSON Web Token) + Bcrypt.

## Reasoning
- **Bcrypt** → industry standard untuk password hashing, sudah battle-tested
- **JWT** → stateless, tidak perlu tabel sessions di DB, mudah di-extend
- **8 jam expiry** → sesuai dengan durasi 1 shift kerja
- Mudah di-extend ke OTP (Phase 2) tanpa perubahan arsitektur

## Consequences
- Token tidak bisa di-invalidate sebelum expire (logout hanya clear session)
- Perlu handle token refresh kalau butuh session lebih panjang
- OTP bisa ditambah di Phase 2 dengan tambah kolom di tabel users
  (sudah disiapkan: otp_code, otp_expired_at, otp_verified)
