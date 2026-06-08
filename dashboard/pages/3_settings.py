# =============================================================================
# dashboard/pages/3_settings.py
# Halaman settings: manage shift config, escalation categories, user management
# Accessible by: admin (semua), leader (shift config only)
# =============================================================================

import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from db.connection import get_connection, release_connection
from dashboard.auth import require_login, logout
from services.auth_service import hash_password

# =====================
# AUTH GUARD
# Pastikan user sudah login — return payload JWT
# =====================
payload = require_login()

# =====================
# ROLE CHECK
# Halaman ini hanya untuk admin dan leader
# Viewer tidak punya akses
# =====================
if payload.get("role") not in ["admin", "leader"]:
    st.error("Anda tidak memiliki akses ke halaman ini!")
    st.stop()

# =============================================================================
# DATABASE FUNCTIONS — SHIFT CONFIG
# =============================================================================

def get_shifts():
    """
    Ambil semua data shift config dari DB, diurutkan by priority_order.
    Dipakai untuk tampilkan tabel shift yang ada.

    Returns:
        list of tuples: [(id, shift_name, start_time, end_time, priority_order, is_active)]
    """
    conn = None
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, shift_name, start_time, end_time, priority_order, is_active
            FROM shift_config
            ORDER BY priority_order ASC
        """)
        return cursor.fetchall()
    except Exception as e:
        st.error("Error mengambil shift config: " + str(e))
        return []
    finally:
        if conn:
            release_connection(conn)

def add_shift(shift_name, start_time, end_time, priority_order):
    """
    Tambah shift baru ke DB.

    Args:
        shift_name     (str): Nama shift (Pagi, Siang, Malam, dll)
        start_time     (str): Jam mulai format HH:MM
        end_time       (str): Jam selesai format HH:MM
        priority_order (int): Urutan prioritas kalau ada overlap

    Returns:
        bool: True kalau berhasil, False kalau gagal
    """
    conn = None
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO shift_config (shift_name, start_time, end_time, priority_order, is_active)
            VALUES (%s, %s, %s, %s, TRUE)
        """, (shift_name, start_time, end_time, priority_order))
        conn.commit()
        return True
    except Exception as e:
        st.error("Error menambah shift: " + str(e))
        return False
    finally:
        if conn:
            release_connection(conn)

def delete_shift(shift_id):
    """
    Hapus shift dari DB berdasarkan ID.

    Args:
        shift_id (int): ID shift yang akan dihapus

    Returns:
        bool: True kalau berhasil, False kalau gagal
    """
    conn = None
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM shift_config WHERE id = %s", (shift_id,))
        conn.commit()
        return True
    except Exception as e:
        st.error("Error menghapus shift: " + str(e))
        return False
    finally:
        if conn:
            release_connection(conn)

def toggle_shift(shift_id, current_status):
    """
    Toggle status aktif/nonaktif shift.
    Kalau aktif → nonaktifkan, kalau nonaktif → aktifkan.

    Args:
        shift_id       (int) : ID shift yang akan di-toggle
        current_status (bool): Status aktif saat ini

    Returns:
        bool: True kalau berhasil
    """
    conn = None
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE shift_config SET is_active = %s, updated_at = NOW()
            WHERE id = %s
        """, (not current_status, shift_id))
        conn.commit()
        return True
    except Exception as e:
        st.error("Error update shift: " + str(e))
        return False
    finally:
        if conn:
            release_connection(conn)

# =============================================================================
# DATABASE FUNCTIONS — ESCALATION CATEGORIES
# =============================================================================

def get_escalation_categories():
    """
    Ambil semua escalation categories dari DB.
    Termasuk yang tidak aktif untuk management di settings.

    Returns:
        list of tuples: [(id, name, is_active)]
    """
    conn = None
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, is_active
            FROM escalation_categories
            ORDER BY name ASC
        """)
        return cursor.fetchall()
    except Exception as e:
        st.error("Error mengambil categories: " + str(e))
        return []
    finally:
        if conn:
            release_connection(conn)

def add_escalation_category(name):
    """
    Tambah escalation category baru ke DB.

    Args:
        name (str): Nama category baru

    Returns:
        bool: True kalau berhasil, False kalau gagal (termasuk duplicate)
    """
    conn = None
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO escalation_categories (name, is_active)
            VALUES (%s, TRUE)
        """, (name,))
        conn.commit()
        return True
    except Exception as e:
        st.error("Error: " + str(e))
        return False
    finally:
        if conn:
            release_connection(conn)

def toggle_escalation_category(cat_id, current_status):
    """
    Toggle aktif/nonaktif escalation category.

    Args:
        cat_id         (int) : ID category
        current_status (bool): Status aktif saat ini

    Returns:
        bool: True kalau berhasil
    """
    conn = None
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE escalation_categories SET is_active = %s WHERE id = %s
        """, (not current_status, cat_id))
        conn.commit()
        return True
    except Exception as e:
        st.error("Error update category: " + str(e))
        return False
    finally:
        if conn:
            release_connection(conn)

# =============================================================================
# DATABASE FUNCTIONS — USER MANAGEMENT
# Hanya admin yang bisa akses bagian ini
# =============================================================================

def get_users():
    """
    Ambil semua data users dari DB.
    Tidak include password_hash untuk keamanan.

    Returns:
        list of tuples: [(id, name, email, role, is_active, last_login_at)]
    """
    conn = None
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, email, role, is_active, last_login_at
            FROM users
            ORDER BY created_at ASC
        """)
        return cursor.fetchall()
    except Exception as e:
        st.error("Error mengambil users: " + str(e))
        return []
    finally:
        if conn:
            release_connection(conn)

def add_user(name, email, password, role):
    """
    Tambah user baru ke DB.
    Password di-hash dengan bcrypt sebelum disimpan.

    Args:
        name     (str): Nama user
        email    (str): Email user (harus unik)
        password (str): Password plain text (akan di-hash)
        role     (str): Role user (admin/leader/viewer)

    Returns:
        bool: True kalau berhasil, False kalau gagal (misal email duplikat)
    """
    conn = None
    try:
        conn   = get_connection()
        cursor = conn.cursor()

        # Hash password sebelum simpan ke DB — tidak boleh simpan plain text
        hashed = hash_password(password)

        cursor.execute("""
            INSERT INTO users (name, email, password_hash, role, is_active)
            VALUES (%s, %s, %s, %s, TRUE)
        """, (name, email, hashed, role))
        conn.commit()
        return True
    except Exception as e:
        st.error("Error menambah user: " + str(e))
        return False
    finally:
        if conn:
            release_connection(conn)

def toggle_user(user_id, current_status):
    """
    Toggle aktif/nonaktif user.
    User yang dinonaktifkan tidak bisa login.

    Args:
        user_id        (int) : ID user
        current_status (bool): Status aktif saat ini

    Returns:
        bool: True kalau berhasil
    """
    conn = None
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users SET is_active = %s, updated_at = NOW()
            WHERE id = %s
        """, (not current_status, user_id))
        conn.commit()
        return True
    except Exception as e:
        st.error("Error update user: " + str(e))
        return False
    finally:
        if conn:
            release_connection(conn)

def reset_password(user_id, new_password):
    """
    Reset password user oleh admin.
    Password baru di-hash sebelum disimpan.

    Args:
        user_id      (int): ID user yang passwordnya akan direset
        new_password (str): Password baru plain text

    Returns:
        bool: True kalau berhasil
    """
    conn = None
    try:
        conn   = get_connection()
        cursor = conn.cursor()

        # Hash password baru sebelum update ke DB
        hashed = hash_password(new_password)

        cursor.execute("""
            UPDATE users SET password_hash = %s, updated_at = NOW()
            WHERE id = %s
        """, (hashed, user_id))
        conn.commit()
        return True
    except Exception as e:
        st.error("Error reset password: " + str(e))
        return False
    finally:
        if conn:
            release_connection(conn)

# =============================================================================
# SIDEBAR
# Info user yang sedang login + tombol logout
# =============================================================================
with st.sidebar:
    st.title("▪ Chatwoot Dashboard")
    st.divider()

    # Tampilkan email dan role user yang sedang login
    st.write("👤 " + payload.get("email", ""))
    st.write("🏷️ " + payload.get("role", "").upper())
    st.divider()

    # Tombol logout — clear session dan redirect ke login
    if st.button("🚪 Logout", use_container_width=True):
        logout()

# =============================================================================
# HEADER
# =============================================================================
st.title("⚙️ Settings")
st.divider()

# =============================================================================
# SECTION 1 — SHIFT CONFIG
# Accessible by: admin dan leader
# Leader bisa manage shift karena dia yang buat jadwal
# =============================================================================
st.subheader("🕐 Shift Configuration")
st.caption("Atur shift kerja tim. Shift digunakan untuk kategorisasi ticket berdasarkan jam created_at.")

# Tampilkan tabel shift yang ada
shifts = get_shifts()
if shifts:
    # Render setiap shift sebagai row dengan tombol aksi
    for shift in shifts:
        shift_id, name, start, end, priority, is_active = shift
        col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 1, 2])

        with col1:
            # Nama shift dengan indikator aktif/nonaktif
            status_icon = "○" if is_active else "●"
            st.write(status_icon + " **" + name + "**")
        with col2:
            st.write("⏰ " + str(start) + " - " + str(end))
        with col3:
            st.write("Priority: " + str(priority))
        with col4:
            # Tombol toggle aktif/nonaktif
            toggle_label = "Nonaktifkan" if is_active else "Aktifkan"
            if st.button(toggle_label, key="toggle_shift_" + str(shift_id)):
                if toggle_shift(shift_id, is_active):
                    st.rerun()
        with col5:
            # Tombol hapus shift
            if st.button("🗑️ Hapus", key="del_shift_" + str(shift_id)):
                if delete_shift(shift_id):
                    st.success("Shift dihapus!")
                    st.rerun()
else:
    st.info("Belum ada shift config.")

# Form tambah shift baru
st.write("")
with st.expander("➕ Tambah Shift Baru"):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        new_shift_name = st.text_input("Nama Shift", placeholder="Contoh: Pagi")
    with col2:
        new_start = st.text_input("Jam Mulai", placeholder="05:00")
    with col3:
        new_end = st.text_input("Jam Selesai", placeholder="13:59")
    with col4:
        new_priority = st.number_input("Priority Order", min_value=1, value=1)

    if st.button("💾 Simpan Shift", type="primary"):
        # Validasi semua field terisi
        if not new_shift_name or not new_start or not new_end:
            st.error("Semua field wajib diisi!")
        else:
            if add_shift(new_shift_name, new_start, new_end, new_priority):
                st.success("Shift berhasil ditambahkan!")
                st.rerun()

st.divider()

# =============================================================================
# SECTION 2 — ESCALATION CATEGORIES
# Accessible by: admin only
# Leader tidak bisa manage categories
# =============================================================================
if payload.get("role") == "admin":
    st.subheader("▪ Escalation Categories")
    st.caption("Kelola pilihan dropdown escalation category di halaman Tickets.")

    # Tampilkan semua categories dengan tombol toggle aktif/nonaktif
    categories = get_escalation_categories()
    if categories:
        for cat in categories:
            cat_id, name, is_active = cat
            col1, col2 = st.columns([5, 2])

            with col1:
                # Nama category dengan indikator status
                status_icon = "○" if is_active else "●"
                st.write(status_icon + " " + name)
            with col2:
                # Toggle aktif/nonaktif
                toggle_label = "Nonaktifkan" if is_active else "Aktifkan"
                if st.button(toggle_label, key="toggle_cat_" + str(cat_id)):
                    if toggle_escalation_category(cat_id, is_active):
                        st.rerun()
    else:
        st.info("Belum ada escalation categories.")

    # Form tambah category baru
    st.write("")
    with st.expander("➕ Tambah Category Baru"):
        new_cat_name = st.text_input("Nama Category", placeholder="Contoh: Action L2 - New Category")
        if st.button("💾 Simpan Category", type="primary"):
            if not new_cat_name:
                st.error("Nama category wajib diisi!")
            else:
                if add_escalation_category(new_cat_name):
                    st.success("Category berhasil ditambahkan!")
                    st.rerun()

    st.divider()

    # =============================================================================
    # SECTION 3 — USER MANAGEMENT
    # Accessible by: admin only
    # Admin bisa tambah user, toggle aktif, reset password
    # =============================================================================
    st.subheader("👥 User Management")
    st.caption("Kelola akun yang bisa login ke dashboard ini.")

    # Tampilkan semua users
    users = get_users()
    if users:
        for user in users:
            user_id, name, email, role, is_active, last_login = user

            col1, col2, col3, col4, col5 = st.columns([2, 3, 2, 2, 2])

            with col1:
                # Nama user dengan status aktif
                status_icon = "○" if is_active else "●"
                st.write(status_icon + " **" + name + "**")
            with col2:
                st.write("📧 " + email)
            with col3:
                st.write("🏷️ " + role.upper())
            with col4:
                # Toggle aktif/nonaktif user
                # Jangan bisa nonaktifkan diri sendiri
                if user_id == payload.get("user_id"):
                    st.write("_(Akun aktif)_")
                else:
                    toggle_label = "Nonaktifkan" if is_active else "Aktifkan"
                    if st.button(toggle_label, key="toggle_user_" + str(user_id)):
                        if toggle_user(user_id, is_active):
                            st.rerun()
            with col5:
                # Tombol reset password
                if st.button("🔑 Reset Pass", key="reset_" + str(user_id)):
                    # Simpan user yang akan di-reset di session state
                    st.session_state["reset_user_id"]   = user_id
                    st.session_state["reset_user_name"] = name
    else:
        st.info("Belum ada users.")

    # Form reset password — muncul kalau ada user yang dipilih
    if "reset_user_id" in st.session_state:
        st.write("")
        with st.expander(
            "🔑 Reset Password: " + st.session_state.get("reset_user_name", ""),
            expanded=True
        ):
            new_pass    = st.text_input("Password Baru", type="password")
            confirm_pass = st.text_input("Konfirmasi Password", type="password")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Simpan Password Baru", type="primary"):
                    # Validasi password baru
                    if not new_pass:
                        st.error("Password tidak boleh kosong!")
                    elif new_pass != confirm_pass:
                        st.error("Password tidak cocok!")
                    elif len(new_pass) < 8:
                        st.error("Password minimal 8 karakter!")
                    else:
                        if reset_password(st.session_state["reset_user_id"], new_pass):
                            st.success("Password berhasil direset!")
                            # Clear session state reset
                            del st.session_state["reset_user_id"]
                            del st.session_state["reset_user_name"]
                            st.rerun()
            with col2:
                if st.button("Batal"):
                    # Batal reset — clear session state
                    del st.session_state["reset_user_id"]
                    del st.session_state["reset_user_name"]
                    st.rerun()

    st.divider()

    # Form tambah user baru
    st.write("")
    with st.expander("➕ Tambah User Baru"):
        col1, col2 = st.columns(2)
        with col1:
            new_name  = st.text_input("Nama",  placeholder="John Doe")
            new_email = st.text_input("Email", placeholder="john@csicube.com")
        with col2:
            new_role = st.selectbox("Role", ["viewer", "leader", "admin"])
            new_pass = st.text_input("Password", type="password")

        if st.button("💾 Tambah User", type="primary"):
            # Validasi semua field
            if not new_name or not new_email or not new_pass:
                st.error("Semua field wajib diisi!")
            elif len(new_pass) < 8:
                st.error("Password minimal 8 karakter!")
            else:
                if add_user(new_name, new_email, new_pass, new_role):
                    st.success("User " + new_email + " berhasil ditambahkan!")
                    st.rerun()
