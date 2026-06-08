# =============================================================================
# dashboard/components/theme.py
# Custom theme CSS — inject ke semua pages via render_theme()
# Design inspired by BudgetZen design system
# =============================================================================

import streamlit as st

def render_theme():
    """
    Inject custom CSS untuk override tampilan default Streamlit.
    Panggil di setiap page setelah set_page_config atau di sidebar component.

    Design elements:
    - Primary color: Mint (#10B981) — untuk aksen, link, highlight
    - Background: Soft white (#FAFFFE) — calm, tidak harsh
    - Surface: Pure white (#FFFFFF) — cards, panels
    - Font: Nunito (body), Manrope (headings)
    """
    st.markdown("""
        <style>
            /* =====================
               GOOGLE FONTS
               Import Manrope (headings) dan Nunito (body)
               ===================== */
            @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@600;700;800&family=Nunito:wght@400;600;700&display=swap');

            /* =====================
               ROOT VARIABLES
               Warna utama dari BudgetZen design system
               ===================== */
            :root {
                --primary: #10B981;
                --primary-hover: #059669;
                --secondary: #38BDF8;
                --background: #FAFFFE;
                --surface: #FFFFFF;
                --text-primary: #1C1917;
                --text-secondary: #57534E;
                --text-muted: #78716C;
                --border: #E7E5E4;
                --success: #10B981;
                --warning: #F59E0B;
                --error: #EF4444;
            }

            /* =====================
               GLOBAL BACKGROUND
               Background app keseluruhan
               ===================== */
            .stApp {
                background-color: var(--background);
            }

            /* =====================
               TYPOGRAPHY
               Override semua font ke Nunito (body) dan Manrope (headings)
               ===================== */
            html, body, [class*="css"] {
                font-family: 'Nunito', sans-serif;
                color: var(--text-primary);
            }

            /* Headings pakai Manrope */
            h1, h2, h3 {
                font-family: 'Manrope', sans-serif !important;
                color: var(--text-primary) !important;
            }

            h1 {
                font-weight: 800 !important;
            }

            h2, h3 {
                font-weight: 700 !important;
            }

            /* =====================
               SIDEBAR
               Background sidebar lebih gelap supaya kontras
               ===================== */
            [data-testid="stSidebar"] {
                background-color: #1C1917;
            }

            [data-testid="stSidebar"] * {
                color: #FAFAFA !important;
            }

            [data-testid="stSidebar"] .stButton > button {
                background-color: transparent;
                border: 1.5px solid #FAFAFA;
                color: #FAFAFA !important;
                border-radius: 8px;
            }

            [data-testid="stSidebar"] .stButton > button:hover {
                background-color: #292524;
                border-color: var(--primary);
                color: var(--primary) !important;
            }

            /* =====================
               BUTTONS
               Primary button pakai warna mint
               ===================== */
            .stButton > button[kind="primary"],
            .stFormSubmitButton > button {
                background-color: var(--primary) !important;
                border: none !important;
                color: white !important;
                border-radius: 10px !important;
                font-family: 'Nunito', sans-serif !important;
                font-weight: 600 !important;
            }

            .stButton > button[kind="primary"]:hover,
            .stFormSubmitButton > button:hover {
                background-color: var(--primary-hover) !important;
            }

            /* Secondary buttons */
            .stButton > button {
                border-radius: 10px !important;
                font-family: 'Nunito', sans-serif !important;
                font-weight: 600 !important;
            }

            /* =====================
               INPUTS
               Border radius dan focus color override
               ===================== */
            .stTextInput > div > div > input,
            .stSelectbox > div > div,
            .stDateInput > div > div > input {
                border-radius: 10px !important;
                font-family: 'Nunito', sans-serif !important;
            }

            .stTextInput > div > div > input:focus {
                border-color: var(--primary) !important;
                box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.15) !important;
            }

            /* =====================
               METRICS / CARDS
               Slight shadow dan rounded corners
               ===================== */
            [data-testid="metric-container"] {
                background-color: var(--surface);
                border: 1px solid var(--border);
                border-radius: 12px;
                padding: 16px;
                box-shadow: 0 1px 3px rgba(28, 25, 23, 0.06);
            }

            /* =====================
               DATAFRAME / TABLE
               Clean table styling
               ===================== */
            .stDataFrame {
                border-radius: 12px;
                overflow: hidden;
            }

            /* =====================
               EXPANDER
               Rounded corners
               ===================== */
            .streamlit-expanderHeader {
                font-family: 'Manrope', sans-serif !important;
                font-weight: 600 !important;
                border-radius: 10px !important;
            }

            /* =====================
               INFO / SUCCESS / ERROR BOXES
               Override warna sesuai design system
               ===================== */
            .stAlert [data-testid="stNotificationContentInfo"] {
                background-color: #38BDF81A;
            }

            .stAlert [data-testid="stNotificationContentSuccess"] {
                background-color: #10B9811A;
            }

            .stAlert [data-testid="stNotificationContentError"] {
                background-color: #EF44441A;
            }

            /* =====================
               PAGE LINKS (sidebar navigation)
               Override styling supaya lebih clean
               ===================== */
            [data-testid="stSidebar"] a {
                text-decoration: none !important;
            }

            /* =====================
               DOWNLOAD BUTTON
               Styled sama seperti primary button
               ===================== */
            .stDownloadButton > button {
                background-color: var(--primary) !important;
                border: none !important;
                color: white !important;
                border-radius: 10px !important;
                font-family: 'Nunito', sans-serif !important;
                font-weight: 600 !important;
            }

            .stDownloadButton > button:hover {
                background-color: var(--primary-hover) !important;
            }
        </style>
    """, unsafe_allow_html=True)