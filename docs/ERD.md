# Entity Relationship Diagram

## Tabel & Relasi

### users
Menyimpan akun yang bisa login ke dashboard.
Terpisah dari agent Chatwoot.

| Kolom             | Tipe         | Keterangan                        |
|-------------------|--------------|-----------------------------------|
| id                | SERIAL PK    |                                   |
| name              | VARCHAR(255) |                                   |
| email             | VARCHAR(255) | UNIQUE                            |
| password_hash     | VARCHAR(255) | Bcrypt hash                       |
| role              | VARCHAR(50)  | admin / leader / viewer           |
| is_active         | BOOLEAN      |                                   |
| otp_code          | VARCHAR(6)   | Untuk Phase 2 (OTP login)         |
| otp_expired_at    | TIMESTAMP    | Untuk Phase 2                     |
| otp_verified      | BOOLEAN      | Untuk Phase 2                     |
| last_login_at     | TIMESTAMP    |                                   |
| created_at        | TIMESTAMP    |                                   |
| updated_at        | TIMESTAMP    |                                   |

### conversations
Data ticket dari Chatwoot, di-sync harian via cron.

| Kolom                    | Tipe         | Keterangan                        |
|--------------------------|--------------|-----------------------------------|
| id                       | SERIAL PK    |                                   |
| ticket_id                | INTEGER      | UNIQUE — conversation.id Chatwoot |
| created_at               | TIMESTAMP    |                                   |
| status                   | VARCHAR(50)  | open/resolved/pending/snoozed     |
| agent                    | VARCHAR(255) |                                   |
| service                  | VARCHAR(100) | Dari label prefix 2_xxx           |
| priority                 | VARCHAR(10)  | P1/P2/P3/P4                       |
| escalate                 | VARCHAR(10)  | L1/L2                             |
| type                     | VARCHAR(100) | Dari label prefix 10_xxx          |
| raw_labels               | TEXT         | Original labels CSV (backup)      |
| frt_seconds              | INTEGER      | First Response Time dalam detik   |
| resolution_time_seconds  | INTEGER      | Resolution Time dalam detik       |
| resolve_count            | INTEGER      | Berapa kali di-resolve            |
| is_reopened              | BOOLEAN      | resolve_count > 1                 |
| last_note                | TEXT         | Last private note                 |
| company                  | VARCHAR(255) |                                   |
| customer                 | VARCHAR(255) |                                   |
| phone                    | VARCHAR(50)  |                                   |
| escalation_note          | TEXT         | Diisi manual oleh leader          |
| escalation_category      | VARCHAR(255) | FK ke escalation_categories       |
| escalation_updated_by    | INTEGER      | FK ke users.id                    |
| escalation_updated_at    | TIMESTAMP    |                                   |
| synced_at                | TIMESTAMP    | Kapan terakhir di-sync            |
| updated_at               | TIMESTAMP    |                                   |

### sync_log
Audit trail setiap kali cron sync berjalan.

| Kolom            | Tipe        | Keterangan                         |
|------------------|-------------|------------------------------------|
| id               | SERIAL PK   |                                    |
| sync_date        | DATE        | Tanggal sync dijalankan            |
| date_from        | DATE        | Range tanggal yang di-sync         |
| date_to          | DATE        |                                    |
| total_fetched    | INTEGER     |                                    |
| total_inserted   | INTEGER     |                                    |
| total_updated    | INTEGER     |                                    |
| total_failed     | INTEGER     |                                    |
| status           | VARCHAR(20) | success / failed / partial         |
| error_message    | TEXT        |                                    |
| duration_seconds | FLOAT       |                                    |
| created_at       | TIMESTAMP   |                                    |

### shift_config
Konfigurasi shift kerja, bisa diubah dari UI oleh leader/admin.

| Kolom          | Tipe         | Keterangan                        |
|----------------|--------------|-----------------------------------|
| id             | SERIAL PK    |                                   |
| shift_name     | VARCHAR(100) | Pagi / Siang / Malam / dll        |
| start_time     | TIME         | Format HH:MM                      |
| end_time       | TIME         | Format HH:MM                      |
| priority_order | INTEGER      | Kalau overlap, priority < = menang|
| is_active      | BOOLEAN      |                                   |
| created_at     | TIMESTAMP    |                                   |
| updated_at     | TIMESTAMP    |                                   |

### escalation_categories
Dropdown options untuk escalation category di halaman Tickets.

| Kolom      | Tipe         | Keterangan    |
|------------|--------------|---------------|
| id         | SERIAL PK    |               |
| name       | VARCHAR(255) | UNIQUE        |
| is_active  | BOOLEAN      |               |
| created_at | TIMESTAMP    |               |

## Relasi
- conversations.escalation_updated_by → users.id (1:N)
- conversations.escalation_category → escalation_categories.name
