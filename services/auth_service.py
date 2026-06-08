# services/auth_service.py
# Authentication: JWT + Bcrypt

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bcrypt
import jwt
from datetime import datetime, timedelta
from db.connection import get_connection, release_connection
from config.settings import JWT_SECRET_KEY, JWT_EXPIRE_HOURS

# =====================
# PASSWORD
# =====================

def hash_password(plain_password):
    """Hash password pakai bcrypt"""
    return bcrypt.hashpw(
        plain_password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

def verify_password(plain_password, hashed_password):
    """Verifikasi password vs hash"""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )

# =====================
# JWT TOKEN
# =====================

def generate_token(user_id, email, role):
    """Generate JWT token setelah login berhasil"""
    payload = {
        "user_id"  : user_id,
        "email"    : email,
        "role"     : role,
        "exp"      : datetime.utcnow() + timedelta(hours=JWT_EXPIRE_HOURS),
        "iat"      : datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")

def verify_token(token):
    """
    Verifikasi JWT token.
    Return payload kalau valid, None kalau expired/invalid.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# =====================
# LOGIN
# =====================

def login(email, password):
    """
    Login dengan email + password.
    Return token kalau berhasil, None kalau gagal.
    """
    conn = None
    try:
        conn   = get_connection()
        cursor = conn.cursor()

        # Cari user by email
        cursor.execute("""
            SELECT id, name, email, password_hash, role, is_active
            FROM users
            WHERE email = %s
        """, (email,))

        user = cursor.fetchone()

        # User tidak ditemukan
        if not user:
            return None, "Email atau password salah"

        user_id, name, user_email, password_hash, role, is_active = user

        # User tidak aktif
        if not is_active:
            return None, "Akun tidak aktif"

        # Verifikasi password
        if not verify_password(password, password_hash):
            return None, "Email atau password salah"

        # Update last_login_at
        cursor.execute("""
            UPDATE users SET last_login_at = NOW()
            WHERE id = %s
        """, (user_id,))
        conn.commit()

        # Generate token
        token = generate_token(user_id, user_email, role)

        return token, None

    except Exception as e:
        return None, "Login error: " + str(e)

    finally:
        if conn:
            release_connection(conn)

# =====================
# USER INFO
# =====================

def get_user_by_id(user_id):
    """Ambil data user by ID"""
    conn = None
    try:
        conn   = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, name, email, role, is_active, last_login_at
            FROM users
            WHERE id = %s
        """, (user_id,))

        row = cursor.fetchone()
        if not row:
            return None

        return {
            "id"            : row[0],
            "name"          : row[1],
            "email"         : row[2],
            "role"          : row[3],
            "is_active"     : row[4],
            "last_login_at" : row[5]
        }

    except Exception as e:
        return None

    finally:
        if conn:
            release_connection(conn)

# =====================
# ROLE CHECK
# =====================

def is_admin(token_payload):
    return token_payload.get("role") == "admin"

def is_leader_or_above(token_payload):
    return token_payload.get("role") in ["admin", "leader"]

def is_viewer_or_above(token_payload):
    return token_payload.get("role") in ["admin", "leader", "viewer"]
