# =============================================================================
# dashboard/auth.py
# Login page & session guard dengan cookie persistence
# =============================================================================

import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import extra_streamlit_components as stx
from services.auth_service import login, verify_token

def get_cookie_manager():
    """
    Inisialisasi CookieManager sebagai singleton.
    Disimpan di session_state supaya tidak dibuat ulang setiap rerun
    dan tidak menyebabkan duplicate key error.
    """
    # Cek apakah sudah ada di session state
    if "cookie_manager" not in st.session_state:
        st.session_state["cookie_manager"] = stx.CookieManager(
            key="chatwoot_cookie_manager"
        )
    return st.session_state["cookie_manager"]

def show_login_page():
    """
    Tampilkan halaman login.
    set_page_config() tidak dipanggil di sini —
    sudah dipanggil di app.py sebagai command pertama.
    """
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🔐 Chatwoot Dashboard")
        st.subheader("Login")
        st.divider()

        with st.form("login_form"):
            email    = st.text_input("Email", placeholder="admin@email.com")
            password = st.text_input("Password", type="password")
            submit   = st.form_submit_button("Login", use_container_width=True)

        if submit:
            if not email or not password:
                st.error("Email dan password wajib diisi!")
            else:
                token, error = login(email, password)
                if token:
                    # Simpan token ke session state
                    st.session_state["token"] = token

                    # Simpan token ke cookie untuk persist saat refresh
                    cookie_manager = get_cookie_manager()
                    cookie_manager.set(
                        "token",
                        token,
                        key="set_token"
                    )
                    st.rerun()
                else:
                    st.error(error or "Login gagal!")

def require_login():
    """
    Guard: cek apakah user sudah login.
    Urutan pengecekan:
    1. Cek session_state (paling cepat)
    2. Kalau tidak ada, cek cookie (persist saat refresh)
    3. Kalau keduanya tidak ada → tampilkan login page

    Returns:
        dict: JWT payload berisi user_id, email, role
    """
    cookie_manager = get_cookie_manager()

    # 1. Cek session state dulu
    token = st.session_state.get("token")

    # 2. Kalau tidak ada di session, coba ambil dari cookie
    if not token:
        token = cookie_manager.get("token")
        if token:
            # Restore ke session state
            st.session_state["token"] = token

    # 3. Kalau masih tidak ada → tampilkan login page
    if not token:
        show_login_page()
        st.stop()

    # Verifikasi token masih valid dan belum expired
    payload = verify_token(token)
    if not payload:
        # Token expired → clear semua dan minta login ulang
        st.session_state.clear()
        cookie_manager.delete("token", key="delete_expired_token")
        st.error("Sesi kamu sudah expired. Silakan login kembali.")
        show_login_page()
        st.stop()

    return payload

def logout():
    """
    Logout — hapus cookie dan clear session state.
    User akan redirect ke login page otomatis.
    """
    # Hapus cookie token
    cookie_manager = get_cookie_manager()
    cookie_manager.delete("token", key="logout_delete_token")

    # Clear semua session state termasuk cookie_manager
    st.session_state.clear()
    st.rerun()
