# db/migrate.py
# Jalankan semua migration SQL secara berurutan

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.connection import get_connection, release_connection

MIGRATIONS_DIR = os.path.join(os.path.dirname(__file__), "migrations")

def run_migrations():
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Ambil semua file .sql, sort berurutan
        sql_files = sorted([
            f for f in os.listdir(MIGRATIONS_DIR)
            if f.endswith(".sql")
        ])

        print("=" * 50)
        print("  RUNNING MIGRATIONS")
        print("=" * 50)

        for sql_file in sql_files:
            file_path = os.path.join(MIGRATIONS_DIR, sql_file)
            print("Running: " + sql_file + " ...")

            with open(file_path, "r") as f:
                sql = f.read()

            cursor.execute(sql)
            conn.commit()
            print("  -> OK")

        print("=" * 50)
        print("  ALL MIGRATIONS COMPLETED")
        print("=" * 50)

    except Exception as e:
        if conn:
            conn.rollback()
        print("[FAILED] Migration error: " + str(e))
        raise

    finally:
        if conn:
            release_connection(conn)

if __name__ == "__main__":
    run_migrations()
