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
    # st.page_link("dashboard/pages/1_tickets.py",   label="🎫 Tickets",   icon="🎫")
    # st.page_link("dashboard/pages/2_analytics.py", label="📈 Analytics", icon="📈")
    st.write("**Navigation**")
    st.write("- 🎫 Tickets")
    st.write("- 📈 Analytics")

    # Settings hanya untuk admin dan leader
    if payload.get("role") in ["admin", "leader"]:
        # st.page_link("dashboard/pages/3_settings.py", label="⚙️ Settings", icon="⚙️")
        st.write("- ⚙️ Settings")

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
