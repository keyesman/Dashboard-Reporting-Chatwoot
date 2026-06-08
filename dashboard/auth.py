# dashboard/auth.py
# Login page & session guard dengan cookie persistence

import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from streamlit_cookies_manager import EncryptedCookieManager
from services.auth_service import login, verify_token
from config.settings import JWT_SECRET_KEY

# =====================
# COOKIE MANAGER
# Enkripsi cookie pakai JWT_SECRET_KEY supaya tidak bisa di-tamper
# Cookie persist di browser — tidak hilang saat refresh
# =====================
cookies = EncryptedCookieManager(
    prefix="chatwoot_dashboard_",
    password=JWT_SECRET_KEY
)

if not cookies.ready():
    # Tunggu cookies selesai load
    st.stop()

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
                    # Simpan token ke cookie (persist saat refresh)
                    cookies["token"] = token
                    cookies.save()
                    st.session_state["token"] = token
                    st.rerun()
                else:
                    st.error(error or "Login gagal!")

def require_login():
    """
    Guard: cek apakah user sudah login.
    Cek dari session_state dulu, kalau tidak ada cek dari cookie.
    Return payload kalau valid, redirect ke login kalau tidak.
    """
    # Cek session state dulu (lebih cepat)
    token = st.session_state.get("token")

    # Kalau tidak ada di session, ambil dari cookie
    if not token:
        token = cookies.get("token")
        if token:
            # Restore ke session state
            st.session_state["token"] = token

    if not token:
        show_login_page()
        st.stop()

    # Verifikasi token valid dan belum expired
    payload = verify_token(token)
    if not payload:
        # Token expired atau invalid — clear semua
        st.session_state.clear()
        cookies["token"] = ""
        cookies.save()
        show_login_page()
        st.stop()

    return payload

def logout():
    """
    Logout — clear session state dan cookie.
    User akan redirect ke login page.
    """
    # Hapus token dari cookie
    cookies["token"] = ""
    cookies.save()

    # Clear semua session state
    st.session_state.clear()
    st.rerun()
