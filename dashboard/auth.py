# dashboard/auth.py
# Login page & session guard dengan cookie persistence

import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.auth_service import login, verify_token

def show_login_page():
    """
    Tampilkan halaman login.
    Tidak ada set_page_config() di sini —
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
                    # Simpan token di session state
                    st.session_state["token"] = token
                    st.rerun()
                else:
                    st.error(error or "Login gagal!")

def require_login():
    """
    Guard: cek apakah user sudah login via session state.
    Return payload JWT kalau valid.
    Redirect ke login page kalau belum/token expired.
    """
    token = st.session_state.get("token")

    if not token:
        show_login_page()
        st.stop()

    # Verifikasi token masih valid dan belum expired
    payload = verify_token(token)
    if not payload:
        # Token expired — clear session dan tampilkan login
        st.session_state.clear()
        st.error("Sesi kamu sudah expired. Silakan login kembali.")
        show_login_page()
        st.stop()

    return payload

def logout():
    """
    Logout — clear semua session state.
    User akan redirect ke login page otomatis.
    """
    st.session_state.clear()
    st.rerun()
