# =============================================================================
# dashboard/pages/1_tickets.py
# Halaman utama: list ticket, filter, export CSV, input escalation
# Accessible by: admin, leader, viewer
# =============================================================================

import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pandas as pd
from datetime import date, timedelta
from db.connection import get_connection, release_connection
from dashboard.auth import require_login, logout

# =====================
# PAGE CONFIG
# Konfigurasi halaman Streamlit — harus dipanggil pertama
# =====================
st.set_page_config(
    page_title="Tickets — Chatwoot Dashboard",
    page_icon="🎫",
    layout="wide"
)

# =====================
# AUTH GUARD
# Pastikan user sudah login sebelum akses halaman ini
# Return payload JWT berisi user_id, email, role
# =====================
payload = require_login()

# =============================================================================
# DATABASE FUNCTIONS
# =============================================================================

def get_tickets(date_from, date_to, agent=None, service=None,
                priority=None, escalate=None, status=None):
    """
    Ambil data tickets dari DB berdasarkan filter yang dipilih user.

    Args:
        date_from (str) : Tanggal mulai format YYYY-MM-DD
        date_to   (str) : Tanggal selesai format YYYY-MM-DD
        agent     (str) : Filter by nama agent, None = semua
        service   (str) : Filter by service, None = semua
        priority  (str) : Filter by priority (P1-P4), None = semua
        escalate  (str) : Filter by escalate (L1/L2), None = semua
        status    (str) : Filter by status, None = semua

    Returns:
        pd.DataFrame: Data tickets sesuai filter
    """
    conn = None
    try:
        conn   = get_connection()
        cursor = conn.cursor()

        # Base query — filter wajib by date range
        query = """
            SELECT
                ticket_id, created_at, status, agent,
                service, priority, escalate, type,
                frt_seconds, resolution_time_seconds,
                resolve_count, is_reopened,
                last_note, company, customer, phone,
                escalation_note, escalation_category,
                raw_labels
            FROM conversations
            WHERE created_at::date BETWEEN %s AND %s
        """
        params = [date_from, date_to]

        # Tambah filter opsional sesuai input user
        if agent:
            query += " AND agent = %s"
            params.append(agent)
        if service:
            query += " AND service = %s"
            params.append(service)
        if priority:
            query += " AND priority = %s"
            params.append(priority)
        if escalate:
            query += " AND escalate = %s"
            params.append(escalate)
        if status:
            query += " AND status = %s"
            params.append(status)

        # Urutkan dari yang terbaru
        query += " ORDER BY created_at DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()

        # Mapping kolom sesuai urutan SELECT
        columns = [
            "Ticket ID", "Created At", "Status", "Agent",
            "Service", "Priority", "Escalate", "Type",
            "FRT (seconds)", "Resolution Time (seconds)",
            "Resolve Count", "Reopened",
            "Last Note", "Company", "Customer", "Phone",
            "Escalation Note", "Escalation Category",
            "Raw Labels"
        ]
        return pd.DataFrame(rows, columns=columns)

    except Exception as e:
        st.error("Error mengambil data: " + str(e))
        return pd.DataFrame()

    finally:
        # Selalu kembalikan connection ke pool
        if conn:
            release_connection(conn)

def get_filter_options():
    """
    Ambil list unik nilai untuk setiap dropdown filter.
    Diambil dari data yang sudah ada di DB — bukan hardcode.

    Returns:
        tuple: (agents, services, priorities, escalates)
    """
    conn = None
    try:
        conn   = get_connection()
        cursor = conn.cursor()

        # Ambil distinct value untuk setiap kolom filter
        cursor.execute("SELECT DISTINCT agent    FROM conversations WHERE agent    IS NOT NULL ORDER BY agent")
        agents = [r[0] for r in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT service  FROM conversations WHERE service  IS NOT NULL ORDER BY service")
        services = [r[0] for r in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT priority FROM conversations WHERE priority IS NOT NULL ORDER BY priority")
        priorities = [r[0] for r in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT escalate FROM conversations WHERE escalate IS NOT NULL ORDER BY escalate")
        escalates = [r[0] for r in cursor.fetchall()]

        return agents, services, priorities, escalates

    except Exception as e:
        st.error("Error mengambil filter options: " + str(e))
        return [], [], [], []

    finally:
        if conn:
            release_connection(conn)

def get_escalation_categories():
    """
    Ambil list escalation categories yang aktif dari DB.
    Dipakai untuk dropdown di form input escalation.

    Returns:
        list: List nama kategori yang is_active = TRUE
    """
    conn = None
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM escalation_categories
            WHERE is_active = TRUE
            ORDER BY name
        """)
        return [r[0] for r in cursor.fetchall()]

    except Exception as e:
        st.error("Error mengambil escalation categories: " + str(e))
        return []

    finally:
        if conn:
            release_connection(conn)

def update_escalation(ticket_id, note, category, updated_by):
    """
    Simpan escalation note & category ke DB.
    Hanya bisa dilakukan oleh role admin dan leader.

    Args:
        ticket_id  (int) : ID ticket yang di-update
        note       (str) : Isi escalation note
        category   (str) : Escalation category yang dipilih
        updated_by (int) : user_id yang melakukan update (dari JWT payload)

    Returns:
        bool: True kalau berhasil, False kalau gagal
    """
    conn = None
    try:
        conn   = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE conversations
            SET
                escalation_note       = %s,
                escalation_category   = %s,
                escalation_updated_by = %s,
                escalation_updated_at = NOW(),
                updated_at            = NOW()
            WHERE ticket_id = %s
        """, (note, category, updated_by, ticket_id))

        conn.commit()
        return True

    except Exception as e:
        st.error("Error menyimpan escalation: " + str(e))
        if conn:
            conn.rollback()
        return False

    finally:
        if conn:
            release_connection(conn)

def seconds_to_hhmmss(seconds):
    """
    Konversi durasi dalam detik ke format HH:MM:SS.
    Dipakai untuk display FRT dan Resolution Time di tabel.

    Args:
        seconds (int/None): Durasi dalam detik

    Returns:
        str: Format HH:MM:SS atau "-" kalau None
    """
    if seconds is None:
        return "-"
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return str(h).zfill(2) + ":" + str(m).zfill(2) + ":" + str(s).zfill(2)

# =============================================================================
# SIDEBAR
# Tampilkan info user yang sedang login + tombol logout
# =============================================================================
with st.sidebar:
    st.title("▪ Chatwoot Dashboard")
    st.divider()

    # Info user yang sedang login
    st.write("👤 " + payload.get("email", ""))
    st.write("🏷️ " + payload.get("role", "").upper())
    st.divider()

    # Tombol logout — clear session dan redirect ke login
    if st.button("🚪 Logout", use_container_width=True):
        logout()

# =============================================================================
# HEADER
# =============================================================================
st.title("🎫 Tickets")
st.divider()

# =============================================================================
# FILTER SECTION
# Form filter data — collapsed by default, expanded saat pertama buka
# =============================================================================
agents, services, priorities, escalates = get_filter_options()

with st.expander("🔍 Filter", expanded=True):
    col1, col2, col3 = st.columns(3)

    with col1:
        # Filter periode tanggal — default 7 hari terakhir
        date_from  = st.date_input("Dari Tanggal",    value=date.today() - timedelta(days=7))
        date_to    = st.date_input("Sampai Tanggal",  value=date.today())
        sel_status = st.selectbox("Status", ["Semua", "open", "resolved", "pending", "snoozed"])

    with col2:
        # Filter by agent dan service
        sel_agent   = st.selectbox("Agent",   ["Semua"] + agents)
        sel_service = st.selectbox("Service", ["Semua"] + services)

    with col3:
        # Filter by priority dan escalate level
        sel_priority = st.selectbox("Priority", ["Semua"] + priorities)
        sel_escalate = st.selectbox("Escalate", ["Semua"] + escalates)

    # Tombol trigger fetch data
    apply = st.button("🔍 Tampilkan Data", type="primary", use_container_width=True)

# =============================================================================
# DATA TABLE SECTION
# Tampilkan data setelah tombol filter ditekan
# Data di-cache di session_state supaya tidak re-fetch saat ada interaksi UI
# =============================================================================
if apply or "tickets_df" in st.session_state:

    # Fetch data baru kalau tombol filter ditekan
    if apply:
        df = get_tickets(
            date_from = str(date_from),
            date_to   = str(date_to),
            agent     = None if sel_agent    == "Semua" else sel_agent,
            service   = None if sel_service  == "Semua" else sel_service,
            priority  = None if sel_priority == "Semua" else sel_priority,
            escalate  = None if sel_escalate == "Semua" else sel_escalate,
            status    = None if sel_status   == "Semua" else sel_status,
        )
        # Simpan ke session state supaya tidak hilang saat ada interaksi
        st.session_state["tickets_df"] = df

    # Ambil dari session state
    df = st.session_state.get("tickets_df", pd.DataFrame())

    if df.empty:
        st.info("Tidak ada data untuk filter yang dipilih.")
    else:
        # Format kolom waktu ke HH:MM:SS untuk display
        df["FRT"]             = df["FRT (seconds)"].apply(seconds_to_hhmmss)
        df["Resolution Time"] = df["Resolution Time (seconds)"].apply(seconds_to_hhmmss)

        # Format boolean ke Yes/No
        df["Reopened"] = df["Reopened"].apply(lambda x: "Yes" if x else "No")

        # Summary total ticket
        st.write("**Total:** " + str(len(df)) + " tickets")

        # Kolom yang ditampilkan di tabel (urutan sesuai kebutuhan)
        display_cols = [
            "Ticket ID", "Created At", "Status", "Agent",
            "Service", "Priority", "Escalate", "Type",
            "FRT", "Resolution Time", "Resolve Count", "Reopened",
            "Company", "Customer", "Phone",
            "Escalation Note", "Escalation Category",
            "Last Note"
        ]
        st.dataframe(df[display_cols], use_container_width=True, height=400)

        # =====================
        # EXPORT CSV
        # Download data yang sedang ditampilkan sebagai CSV
        # Nama file otomatis include tanggal range
        # =====================
        csv = df[display_cols].to_csv(index=False).encode("utf-8")
        st.download_button(
            label     = "⬇️ Export CSV",
            data      = csv,
            file_name = "tickets_" + str(date_from) + "_" + str(date_to) + ".csv",
            mime      = "text/csv"
        )

        st.divider()

        # =====================
        # INPUT ESCALATION
        # Hanya tampil untuk role admin dan leader
        # Viewer tidak bisa input escalation
        # =====================
        if payload.get("role") in ["admin", "leader"]:
            st.subheader("📝 Input Escalation")

            esc_categories = get_escalation_categories()
            ticket_ids     = df["Ticket ID"].tolist()

            col1, col2 = st.columns(2)
            with col1:
                # Dropdown pilih ticket yang mau di-escalate
                sel_ticket = st.selectbox("Pilih Ticket ID", ticket_ids)
            with col2:
                # Dropdown kategori escalation dari DB
                sel_category = st.selectbox(
                    "Escalation Category",
                    [""] + esc_categories
                )

            # Text area untuk isi note escalation
            esc_note = st.text_area("Escalation Note", height=100)

            if st.button("💾 Simpan Escalation", type="primary"):
                # Validasi input sebelum save
                if not sel_ticket:
                    st.error("Pilih ticket dulu!")
                elif not sel_category and not esc_note:
                    st.error("Isi category atau note!")
                else:
                    success = update_escalation(
                        ticket_id  = sel_ticket,
                        note       = esc_note,
                        category   = sel_category,
                        updated_by = payload.get("user_id")
                    )
                    if success:
                        st.success("Escalation berhasil disimpan!")
                        # Clear cache supaya tabel refresh dengan data terbaru
                        del st.session_state["tickets_df"]
                        st.rerun()
