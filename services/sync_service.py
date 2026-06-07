# services/sync_service.py
# Logic upsert data conversations ke DB

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, date
from db.connection import get_connection, release_connection
from services.chatwoot_api import get_all_conversations, get_messages, build_conversation_data

# =====================
# UPSERT CONVERSATION
# =====================

def upsert_conversation(cursor, data):
    """
    Insert kalau ticket_id belum ada.
    Update kalau sudah ada — tapi TIDAK overwrite escalation fields.
    """
    cursor.execute("""
        INSERT INTO conversations (
            ticket_id, created_at, status, agent,
            service, priority, escalate, type, raw_labels,
            frt_seconds, resolution_time_seconds,
            resolve_count, is_reopened, last_note,
            company, customer, phone,
            synced_at, updated_at
        ) VALUES (
            %(ticket_id)s, %(created_at)s, %(status)s, %(agent)s,
            %(service)s, %(priority)s, %(escalate)s, %(type)s, %(raw_labels)s,
            %(frt_seconds)s, %(resolution_time_seconds)s,
            %(resolve_count)s, %(is_reopened)s, %(last_note)s,
            %(company)s, %(customer)s, %(phone)s,
            NOW(), NOW()
        )
        ON CONFLICT (ticket_id) DO UPDATE SET
            status                   = EXCLUDED.status,
            agent                    = EXCLUDED.agent,
            service                  = EXCLUDED.service,
            priority                 = EXCLUDED.priority,
            escalate                 = EXCLUDED.escalate,
            type                     = EXCLUDED.type,
            raw_labels               = EXCLUDED.raw_labels,
            frt_seconds              = EXCLUDED.frt_seconds,
            resolution_time_seconds  = EXCLUDED.resolution_time_seconds,
            resolve_count            = EXCLUDED.resolve_count,
            is_reopened              = EXCLUDED.is_reopened,
            last_note                = EXCLUDED.last_note,
            company                  = EXCLUDED.company,
            customer                 = EXCLUDED.customer,
            phone                    = EXCLUDED.phone,
            synced_at                = NOW(),
            updated_at               = NOW()
            -- escalation_note, escalation_category, escalation_updated_by
            -- TIDAK di-update supaya data manual leader tidak tertimpa
    """, data)

# =====================
# SYNC LOG
# =====================

def save_sync_log(cursor, sync_date, date_from, date_to,
                  total_fetched, total_inserted, total_updated,
                  total_failed, status, error_message, duration_seconds):
    cursor.execute("""
        INSERT INTO sync_log (
            sync_date, date_from, date_to,
            total_fetched, total_inserted, total_updated,
            total_failed, status, error_message, duration_seconds,
            created_at
        ) VALUES (
            %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s, %s,
            NOW()
        )
    """, (
        sync_date, date_from, date_to,
        total_fetched, total_inserted, total_updated,
        total_failed, status, error_message, duration_seconds
    ))

# =====================
# MAIN SYNC
# =====================

def sync(date_from, date_to):
    """
    Sync semua conversations dari Chatwoot ke DB lokal.
    date_from & date_to format: 'YYYY-MM-DD'
    """
    start_time      = datetime.now()
    total_fetched   = 0
    total_inserted  = 0
    total_updated   = 0
    total_failed    = 0
    sync_status     = "success"
    error_message   = None
    conn            = None

    print("=" * 60)
    print("  CHATWOOT SYNC SERVICE")
    print("  Periode: " + date_from + " s/d " + date_to)
    print("=" * 60)

    try:
        # 1. Ambil semua conversations dari API
        conversations = get_all_conversations(date_from, date_to)
        total_fetched = len(conversations)
        print("[INFO] Total conversations fetched: " + str(total_fetched))

        if not conversations:
            print("[INFO] Tidak ada data untuk di-sync.")
            return

        # 2. Connect ke DB
        conn   = get_connection()
        cursor = conn.cursor()

        # 3. Loop tiap conversation → upsert
        print("[INFO] Mulai upsert ke DB...")
        for i, conv in enumerate(conversations, 1):
            try:
                conv_id  = conv.get("id")
                messages = get_messages(conv_id)
                data     = build_conversation_data(conv, messages)

                # Cek apakah ticket sudah ada di DB (untuk log inserted vs updated)
                cursor.execute(
                    "SELECT id FROM conversations WHERE ticket_id = %s",
                    (data["ticket_id"],)
                )
                exists = cursor.fetchone()

                upsert_conversation(cursor, data)

                if exists:
                    total_updated += 1
                else:
                    total_inserted += 1

                # Commit setiap 10 record supaya tidak numpuk di memory
                if i % 10 == 0:
                    conn.commit()
                    print("[INFO] Progress: " + str(i) + "/" + str(total_fetched))

            except Exception as e:
                total_failed += 1
                print("[ERROR] ticket_id " + str(conv.get("id")) + ": " + str(e))
                continue

        # Final commit
        conn.commit()

    except Exception as e:
        sync_status   = "failed"
        error_message = str(e)
        print("[FAILED] Sync error: " + str(e))
        if conn:
            conn.rollback()

    finally:
        # 4. Hitung durasi
        duration = (datetime.now() - start_time).total_seconds()

        # 5. Kalau ada yang failed tapi ada yang berhasil → partial
        if total_failed > 0 and (total_inserted + total_updated) > 0:
            sync_status = "partial"

        # 6. Simpan sync log
        if conn:
            try:
                cursor = conn.cursor()
                save_sync_log(
                    cursor,
                    sync_date     = date.today(),
                    date_from     = date_from,
                    date_to       = date_to,
                    total_fetched = total_fetched,
                    total_inserted= total_inserted,
                    total_updated = total_updated,
                    total_failed  = total_failed,
                    status        = sync_status,
                    error_message = error_message,
                    duration_seconds = duration
                )
                conn.commit()
            except Exception as e:
                print("[ERROR] Gagal simpan sync_log: " + str(e))

            release_connection(conn)

        # 7. Print summary
        print("=" * 60)
        print("  SYNC SUMMARY")
        print("  Status    : " + sync_status.upper())
        print("  Fetched   : " + str(total_fetched))
        print("  Inserted  : " + str(total_inserted))
        print("  Updated   : " + str(total_updated))
        print("  Failed    : " + str(total_failed))
        print("  Duration  : " + str(round(duration, 2)) + " detik")
        print("=" * 60)
