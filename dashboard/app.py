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
# Import SETELAH set_page_config
# Supaya tidak ada Streamlit command yang jalan sebelum set_page_config
# =====================
from dashboard.auth import require_login

# Import component sidebar
from dashboard.components.sidebar import render_sidebar

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
# Render sidebar yang konsisten dari shared component
render_sidebar(payload)

# =====================
# HOME CONTENT
# =====================
st.title("▪ Chatwoot Reporting Dashboard")
st.write("Selamat datang, **" + payload.get("name", "") + "**!")
st.divider()

# Quick info cards
col1, col2, col3 = st.columns(3)
with col1:
    st.info("🎫 **Tickets** Lihat dan filter semua ticket")
with col2:
    st.info("📈 **Analytics** Chart dan metrik performa tim")
with col3:
    st.info("⚙️ **Settings** Kelola shift, kategori, dan user")