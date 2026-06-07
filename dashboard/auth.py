# dashboard/auth.py
# Login page & session guard untuk Streamlit

import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.auth_service import login, verify_token

def show_login_page():
    """Tampilkan halaman login"""

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
                    st.session_state["token"] = token
                    st.rerun()
                else:
                    st.error(error or "Login gagal!")

def require_login():
    """
    Guard: cek apakah user sudah login.
    Return payload kalau sudah login, redirect ke login kalau belum.
    """
    token = st.session_state.get("token")

    if not token:
        show_login_page()
        st.stop()

    payload = verify_token(token)
    if not payload:
        st.session_state.clear()
        show_login_page()
        st.stop()

    return payload

def require_role(payload, allowed_roles):
    """
    Cek apakah user punya role yang diizinkan.
    allowed_roles: list, contoh ["admin", "leader"]
    """
    if payload.get("role") not in allowed_roles:
        st.error("Anda tidak memiliki akses ke halaman ini!")
        st.stop()

def logout():
    """Logout — clear session"""
    st.session_state.clear()
    st.rerun()
