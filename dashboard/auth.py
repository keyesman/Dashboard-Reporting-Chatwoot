# =============================================================================
# dashboard/auth.py
# Login page & session guard dengan cookie persistence
# Pakai streamlit-cookies-controller — compatible dengan Streamlit terbaru
# =============================================================================

import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from streamlit_cookies_controller import CookieController
from services.auth_service import login, verify_token

# =====================
# COOKIE CONTROLLER
# Inisialisasi di level module — singleton otomatis
# Tidak perlu @st.cache_resource atau session_state
# =====================
cookies = CookieController()


def show_login_page():
    """
    Tampilkan halaman login.
    CSS hide sidebar bawaan Streamlit ada di sini
    supaya menu tidak muncul saat belum login.
    """
    # Sembunyikan default Streamlit navigation saat login page
    st.markdown("""
        <style>
            [data-testid="stSidebarNav"] { display: none; }
        </style>
    """, unsafe_allow_html=True)

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

                    # Simpan token ke cookie (persist saat refresh)
                    cookies.set("token", token)
                    st.rerun()
                else:
                    st.error(error or "Login gagal!")


def require_login():
    """
    Guard: cek apakah user sudah login.
    Urutan pengecekan:
    1. Cek session_state (paling cepat, tidak perlu read cookie)
    2. Kalau tidak ada, cek cookie (persist saat refresh)
    3. Kalau keduanya tidak ada → tampilkan login page

    Returns:
        dict: JWT payload berisi user_id, email, role
    """
    # 1. Cek session state dulu
    token = st.session_state.get("token")

    # 2. Kalau tidak ada di session, coba ambil dari cookie
    if not token:
        token = cookies.get("token")
        if token:
            # Restore ke session state untuk akses lebih cepat
            st.session_state["token"] = token

    # 3. Kalau masih tidak ada → tampilkan login page
    if not token:
        show_login_page()
        st.stop()

    # Verifikasi token masih valid dan belum expired
    payload = verify_token(token)
    if not payload:
        # Token expired → clear semua
        st.session_state.clear()
        cookies.remove("token")
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
    cookies.remove("token")

    # Clear semua session state
    st.session_state.clear()
    st.rerun()
