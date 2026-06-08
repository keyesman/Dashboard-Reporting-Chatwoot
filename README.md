# Dashboard Reporting Chatwoot

Dashboard reporting internal untuk monitoring dan analisis ticket L1 Support
berbasis data dari Chatwoot.

## Tech Stack
- **Python 3.10+** — backend & data processing
- **Streamlit** — dashboard UI
- **PostgreSQL** — local database
- **JWT + Bcrypt** — authentication

## Requirements
- Python 3.10+
- PostgreSQL 14+

## Setup & Installation

### 1. Clone repository
git clone https://github.com/keyesman/Dashboard-Reporting-Chatwoot.git
cd Dashboard-Reporting-Chatwoot

### 2. Install dependencies
pip install -r requirements.txt

### 3. Setup environment
cp .env.example .env
# Edit .env dan isi credentials yang sesuai

### 4. Jalankan migration database
python db/migrate.py

### 5. Jalankan dashboard
streamlit run dashboard/app.py

## Cron Job (Windows Task Scheduler)
Script sync harian otomatis setiap jam 09:00:
- Program : python
- Arguments: jobs/cron_sync.py
- Start in : D:\path\to\Dashboard-Reporting-Chatwoot

### Sync manual
# Sync H-1 (default)
python jobs/cron_sync.py

# Sync range tanggal tertentu
python jobs/cron_sync.py --from 2026-01-01 --to 2026-01-31

## Struktur Folder
Dashboard-Reporting-Chatwoot/
├── config/         → settings & konstanta global
├── db/             → migrations & koneksi database
│   └── migrations/ → SQL migration files
├── services/       → business logic (API, sync, auth)
├── jobs/           → cron sync harian
└── dashboard/      → Streamlit UI
    └── pages/      → halaman Tickets, Analytics, Settings

## Default Admin Account
Email    : admin@email.com
Password : Password123
PENTING  : Ganti password setelah pertama kali login!

## Roles & Akses
| Role    | Tickets | Analytics | Escalation | Settings | User Mgmt |
|---------|---------|-----------|------------|----------|-----------|
| admin   | ✓      | ✓        | ✓         | ✓       | ✓        |
| leader  | ✓      | ✓        | ✓         | ✓ Shift | ✗        |
| viewer  | ✓      | ✓        | ✗         | ✗       | ✗        |
