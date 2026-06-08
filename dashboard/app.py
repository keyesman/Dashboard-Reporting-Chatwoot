# =============================================================================
# dashboard/app.py
# Entry point Streamlit dashboard — halaman utama setelah login
# =============================================================================

import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# =====================
# PAGE CONFIG
# WAJIB dipanggil pertama sebelum import apapun yang trigger Streamlit command
# =====================
st.set_page_config(
    page_title="Chatwoot Dashboard",
    page_icon="▪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================
# HIDE DEFAULT STREAMLIT NAVIGATION
# Sembunyikan auto-generated nav dari Streamlit supaya tidak double
# =====================
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] { display: none; }
    </style>
""", unsafe_allow_html=True)

# =====================
# Import SETELAH set_page_config
# Supaya tidak ada Streamlit command yang jalan sebelum set_page_config
# =====================
from dashboard.auth import require_login, logout

# =====================
# AUTH GUARD
# Cek apakah user sudah login via cookie/session
# Return payload JWT berisi user_id, email, role
# =====================
payload = require_login()

# =====================
# SIDEBAR CUSTOM
# Path page_link relatif dari folder dashboard/ (tempat app.py berada)
# =====================
with st.sidebar:
    st.title("▪ Chatwoot Dashboard")
    st.divider()

    # Info user yang sedang login
    st.write("👤 " + payload.get("email", ""))
    st.write("🏷️ " + payload.get("role", "").upper())
    st.divider()

    # Navigation — path relatif dari folder dashboard/
    st.page_link("app.py",              label="🏠 Home")
    st.page_link("pages/1_tickets.py",  label="🎫 Tickets")
    st.page_link("pages/2_analytics.py",label="📈 Analytics")

    # Settings hanya untuk admin dan leader
    if payload.get("role") in ["admin", "leader"]:
        st.page_link("pages/3_settings.py", label="⚙️ Settings")

    st.divider()

    # Tombol logout — clear session & cookie, redirect ke login
    if st.button("🚪 Logout", use_container_width=True):
        logout()

# =====================
# HOME CONTENT
# =====================
st.title("▪ Chatwoot Reporting Dashboard")
st.write("Selamat datang, **" + payload.get("email", "") + "**!")
st.divider()

# Quick info cards
col1, col2, col3 = st.columns(3)
with col1:
    st.info("🎫 **Tickets** Lihat dan filter semua ticket")
with col2:
    st.info("📈 **Analytics** Chart dan metrik performa tim")
with col3:
    st.info("⚙️ **Settings** Kelola shift, kategori, dan user")
