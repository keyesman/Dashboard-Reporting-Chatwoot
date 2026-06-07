# db/connection.py
# PostgreSQL connection pool

import psycopg2
import psycopg2.pool
from config.settings import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

_pool = None

def get_pool():
    global _pool
    if _pool is None:
        _pool = psycopg2.pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
    return _pool

def get_connection():
    """Ambil connection dari pool"""
    return get_pool().getconn()

def release_connection(conn):
    """Kembalikan connection ke pool"""
    get_pool().putconn(conn)

def close_all():
    """Tutup semua connection saat app shutdown"""
    global _pool
    if _pool:
        _pool.closeall()
        _pool = None
