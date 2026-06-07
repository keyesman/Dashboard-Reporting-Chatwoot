# jobs/cron_sync.py
# Entry point untuk cron job harian
# Jalankan: python jobs/cron_sync.py
# Atau dengan custom date: python jobs/cron_sync.py --date 2026-05-01 --to 2026-05-31

import sys
import os
import argparse
from datetime import date, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.sync_service import sync

def get_default_date_range():
    """Default: sync data kemarin (H-1)"""
    yesterday = date.today() - timedelta(days=1)
    return str(yesterday), str(yesterday)

def parse_args():
    parser = argparse.ArgumentParser(description="Chatwoot Sync Job")
    parser.add_argument(
        "--from",
        dest="date_from",
        type=str,
        help="Tanggal mulai (YYYY-MM-DD). Default: kemarin",
        default=None
    )
    parser.add_argument(
        "--to",
        dest="date_to",
        type=str,
        help="Tanggal selesai (YYYY-MM-DD). Default: kemarin",
        default=None
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()

    # Gunakan argument kalau ada, kalau tidak pakai H-1
    if args.date_from and args.date_to:
        date_from = args.date_from
        date_to   = args.date_to
    elif args.date_from:
        date_from = args.date_from
        date_to   = args.date_from
    else:
        date_from, date_to = get_default_date_range()

    print("[INFO] Menjalankan sync untuk periode: " + date_from + " s/d " + date_to)
    sync(date_from, date_to)