# Changelog

Semua perubahan penting pada project ini akan didokumentasikan di file ini.
Format mengacu pada [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.0.0] - 2026-06-07

### Added
- Initial project setup dengan struktur folder real-world
- PostgreSQL database dengan 5 tabel:
  - users, conversations, sync_log, shift_config, escalation_categories
- Authentication dengan JWT + Bcrypt
- 3 roles: admin, leader, viewer
- Seed data: 1 akun admin default
- Chatwoot API integration:
  - Fetch conversations semua status (open, resolved, pending, snoozed)
  - Parse labels: service, priority, escalate, type
  - Hitung FRT dari first_reply_created_at
  - Hitung Resolution Time dari activity message resolved
  - Ambil last private note, customer info
- Cron sync harian dengan argument date range
- Sync log untuk audit trail
- Dashboard Streamlit:
  - Login page dengan JWT session
  - Halaman Tickets: filter, tabel, export CSV, input escalation
  - Halaman Analytics: line chart volume, AVG FRT trend, breakdown
  - Halaman Settings: shift config, escalation categories, user management
- Windows Task Scheduler support untuk cron job
