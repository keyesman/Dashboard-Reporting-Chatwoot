# =============================================================================
# dashboard/components/sidebar.py
# Shared sidebar component — dipanggil dari semua pages supaya konsisten
# =============================================================================

import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dashboard.auth import logout


def render_sidebar(payload):
    """
    Render sidebar yang konsisten di semua halaman.
    Termasuk hide default Streamlit navigation supaya tidak double.
    Dipanggil setelah require_login() di setiap page.

    Args:
        payload (dict): JWT payload berisi user_id, email, role
    """
    # =====================
    # HIDE DEFAULT STREAMLIT NAVIGATION
    # Ditaruh di sini supaya berlaku di semua pages
    # yang memanggil render_sidebar()
    # =====================
    st.markdown("""
        <style>
            /* Sembunyikan default Streamlit page navigation di sidebar */
            [data-testid="stSidebarNav"] {
                display: none;
            }
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        # Judul dashboard
        st.title("Chatwoot Dashboard")
        st.divider()

        # Navigation links — path relatif dari folder dashboard/
        st.page_link("app.py",               label="🏠 Home")
        st.page_link("pages/1_tickets.py",   label="🎫 Tickets")
        st.page_link("pages/2_analytics.py", label="📈 Analytics")

        # Settings hanya untuk admin dan leader
        if payload.get("role") in ["admin", "leader"]:
            st.page_link("pages/3_settings.py", label="⚙️ Settings")

        st.divider()

        # Info user yang sedang login
        st.write("👤 " + payload.get("name", ""))
        st.write("🏷️ " + payload.get("role", "").upper())
        st.divider()

        # Tombol logout — clear session dan redirect ke login
        if st.button("🚪 Logout", use_container_width=True):
            logout()
