# dashboard/app.py
# Entry point Streamlit dashboard

import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dashboard.auth import require_login, logout

# =====================
# PAGE CONFIG
# =====================
st.set_page_config(
    page_title="Chatwoot Dashboard",
    page_icon="▪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================
# HIDE DEFAULT STREAMLIT NAVIGATION
# Sembunyikan auto-generated navigation dari Streamlit
# supaya tidak double dengan sidebar custom kita
# =====================
st.markdown("""
    <style>
        /* Sembunyikan default Streamlit page navigation di sidebar */
        [data-testid="stSidebarNav"] {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)

# =====================
# AUTH GUARD
# =====================
payload = require_login()

# =====================
# SIDEBAR
# =====================
with st.sidebar:
    st.title("▪ Chatwoot Dashboard")
    st.divider()

    # Info user yang login
    st.write("👤 " + payload.get("email", ""))
    st.write("🏷️ " + payload.get("role", "").upper())
    st.divider()

    # Navigasi
    st.page_link("app.py",         label="🏠 Home")
    st.page_link("pages/1_tickets.py",    label="🎫 Tickets")
    st.page_link("pages/2_analytics.py",  label="📈 Analytics")
    if payload.get("role") in ["admin", "leader"]:
        st.page_link("pages/3_settings.py", label="⚙️ Settings")

    st.divider()

    # Logout button
    if st.button("🚪 Logout", use_container_width=True):
        logout()

# =====================
# HOME CONTENT
# =====================
st.title("▪ Chatwoot Reporting Dashboard")
st.write("Selamat datang, **" + payload.get("email", "") + "**!")
st.divider()

st.info("Gunakan menu di sidebar untuk navigasi.")

# Quick stats — 3 card ringkasan
col1, col2, col3 = st.columns(3)
with col1:
    st.info("🎫 **Tickets** Lihat dan filter semua ticket")
with col2:
    st.info("📈 **Analytics** Chart dan metrik performa tim")
with col3:
    st.info("⚙️ **Settings** Kelola shift, kategori, dan user")