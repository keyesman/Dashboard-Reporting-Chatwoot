# =============================================================================
# dashboard/pages/2_analytics.py
# Halaman analytics: chart ticket masuk vs solved, AVG FRT, AVG Resolution Time,
# breakdown per agent, per service, per label
# Accessible by: admin, leader, viewer
# =============================================================================

import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pandas as pd
from datetime import date, timedelta
from db.connection import get_connection, release_connection
from dashboard.auth import require_login
from dashboard.components.sidebar import render_sidebar
import altair as alt

# =====================
# AUTH GUARD
# Pastikan user sudah login — return payload JWT (user_id, email, role)
# =====================
payload = require_login()

# =============================================================================
# DATABASE FUNCTIONS
# =============================================================================

def get_daily_volume(date_from, date_to):
    """
    Ambil jumlah ticket masuk (created) dan ticket selesai (resolved)
    per hari dalam range tanggal yang dipilih.
    Dipakai untuk chart line: Ticket Masuk vs Ticket Solved.

    Args:
        date_from (str): Tanggal mulai YYYY-MM-DD
        date_to   (str): Tanggal selesai YYYY-MM-DD

    Returns:
        pd.DataFrame: Kolom [date, ticket_masuk, ticket_solved]
    """
    conn = None
    try:
        conn   = get_connection()
        cursor = conn.cursor()

        # Hitung ticket masuk per hari berdasarkan created_at
        cursor.execute("""
            SELECT
                created_at::date AS tanggal,
                COUNT(*)         AS ticket_masuk
            FROM conversations
            WHERE created_at::date BETWEEN %s AND %s
            GROUP BY created_at::date
            ORDER BY tanggal
        """, (date_from, date_to))
        masuk_rows = cursor.fetchall()

        # Hitung ticket solved per hari berdasarkan status resolved
        # dan updated_at (kapan terakhir di-resolve)
        cursor.execute("""
            SELECT
                created_at::date AS tanggal,
                COUNT(*)         AS ticket_solved
            FROM conversations
            WHERE created_at::date BETWEEN %s AND %s
            AND status = 'resolved'
            GROUP BY created_at::date
            ORDER BY tanggal
        """, (date_from, date_to))
        solved_rows = cursor.fetchall()

        # Gabungkan kedua hasil ke dalam DataFrame
        df_masuk  = pd.DataFrame(masuk_rows,  columns=["date", "Ticket Created"])
        df_solved = pd.DataFrame(solved_rows, columns=["date", "Ticket Solved"])

        # Merge berdasarkan tanggal — fill 0 kalau tidak ada data di hari itu
        df = pd.merge(df_masuk, df_solved, on="date", how="outer").fillna(0)
        df = df.sort_values("date")
        df["Ticket Masuk"]  = df["Ticket Created"].astype(int)
        df["Ticket Solved"] = df["Ticket Solved"].astype(int)

        return df

    except Exception as e:
        st.error("Error retrieving data volume: " + str(e))
        return pd.DataFrame()

    finally:
        # Selalu kembalikan connection ke pool setelah selesai
        if conn:
            release_connection(conn)

def get_avg_metrics(date_from, date_to):
    """
    Hitung AVG FRT dan AVG Resolution Time dalam range tanggal.
    Hanya menghitung ticket yang punya nilai (tidak None/NULL).

    Args:
        date_from (str): Tanggal mulai YYYY-MM-DD
        date_to   (str): Tanggal selesai YYYY-MM-DD

    Returns:
        dict: {
            avg_frt: float (detik),
            avg_rt: float (detik),
            total_tickets: int,
            tickets_with_frt: int,
            tickets_resolved: int
        }
    """
    conn = None
    try:
        conn   = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                COUNT(*)                            AS total_tickets,
                COUNT(frt_seconds)                  AS tickets_with_frt,
                COUNT(resolution_time_seconds)      AS tickets_resolved,
                AVG(frt_seconds)                    AS avg_frt,
                AVG(resolution_time_seconds)        AS avg_rt
            FROM conversations
            WHERE created_at::date BETWEEN %s AND %s
        """, (date_from, date_to))

        row = cursor.fetchone()
        return {
            "total_tickets"    : row[0] or 0,
            "tickets_with_frt" : row[1] or 0,
            "tickets_resolved" : row[2] or 0,
            "avg_frt"          : float(row[3]) if row[3] else 0,
            "avg_rt"           : float(row[4]) if row[4] else 0,
        }

    except Exception as e:
        st.error("Error calculating metrics: " + str(e))
        return {}

    finally:
        if conn:
            release_connection(conn)

def get_breakdown_by(date_from, date_to, group_by):
    """
    Ambil breakdown jumlah ticket berdasarkan kolom tertentu.
    Dipakai untuk bar chart: per agent, per service, per type.

    Args:
        date_from (str) : Tanggal mulai YYYY-MM-DD
        date_to   (str) : Tanggal selesai YYYY-MM-DD
        group_by  (str) : Nama kolom untuk group by (agent/service/type/priority)

    Returns:
        pd.DataFrame: Kolom [group_by, total]
    """
    conn = None
    try:
        conn   = get_connection()
        cursor = conn.cursor()

        # Query dinamis berdasarkan kolom yang dipilih
        # Hanya ambil yang tidak NULL
        cursor.execute("""
            SELECT
                {col}    AS label,
                COUNT(*) AS total
            FROM conversations
            WHERE created_at::date BETWEEN %s AND %s
            AND {col} IS NOT NULL
            GROUP BY {col}
            ORDER BY total DESC
        """.format(col=group_by), (date_from, date_to))

        rows = cursor.fetchall()
        return pd.DataFrame(rows, columns=["Label", "Total"])

    except Exception as e:
        st.error("Error retrieving breakdown data: " + str(e))
        return pd.DataFrame()

    finally:
        if conn:
            release_connection(conn)

def get_daily_avg_frt(date_from, date_to):
    """
    Ambil AVG FRT per hari untuk ditampilkan sebagai trend line chart.
    Hanya menghitung ticket have FRT (tidak NULL).

    Args:
        date_from (str): Tanggal mulai YYYY-MM-DD
        date_to   (str): Tanggal selesai YYYY-MM-DD

    Returns:
        pd.DataFrame: Kolom [date, avg_frt_minutes]
    """
    conn = None
    try:
        conn   = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                created_at::date     AS tanggal,
                AVG(frt_seconds)/60  AS avg_frt_minutes
            FROM conversations
            WHERE created_at::date BETWEEN %s AND %s
            AND frt_seconds IS NOT NULL
            GROUP BY created_at::date
            ORDER BY tanggal
        """, (date_from, date_to))

        rows = cursor.fetchall()
        df   = pd.DataFrame(rows, columns=["date", "AVG FRT (minute)"])
        # Convert ke float dulu (dari Decimal), lalu round
        df["AVG FRT (minute)"] = df["AVG FRT (minute)"].astype(float).round(2)
        return df

    except Exception as e:
        st.error("Error fetching daily AVG FRT: " + str(e))
        return pd.DataFrame()

    finally:
        if conn:
            release_connection(conn)

def seconds_to_hhmmss(seconds):
    """
    Konversi detik ke format HH:MM:SS untuk display metric card.

    Args:
        seconds (float): Durasi dalam detik

    Returns:
        str: Format HH:MM:SS
    """
    if not seconds:
        return "00:00:00"
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return str(h).zfill(2) + ":" + str(m).zfill(2) + ":" + str(s).zfill(2)

# =============================================================================
# SIDEBAR
# Info user yang sedang login + tombol logout
# =============================================================================
# Render sidebar yang konsisten dari shared component
render_sidebar(payload)

# =============================================================================
# HEADER
# =============================================================================
st.title("📈 Analytics")
st.divider()

# =============================================================================
# FILTER PERIODE
# User pilih range tanggal untuk semua chart di halaman ini
# =============================================================================
col1, col2, col3 = st.columns([2, 2, 4])
with col1:
    # Default: 30 hari terakhir
    date_from = st.date_input("From", value=date.today() - timedelta(days=30))
with col2:
    date_to = st.date_input("To", value=date.today())
with col3:
    st.write("")  # Spacer kosong

apply = st.button("Show Analytics", type="primary")

# Simpan tanggal ke session state supaya tidak reset saat interaksi UI
if apply:
    st.session_state["analytics_from"] = str(date_from)
    st.session_state["analytics_to"]   = str(date_to)

# Gunakan tanggal dari session state kalau sudah pernah apply
date_from_str = st.session_state.get("analytics_from", str(date_from))
date_to_str   = st.session_state.get("analytics_to",   str(date_to))

if "analytics_from" not in st.session_state and not apply:
    # Belum ada data — tampilkan pesan
    st.info("Select the period and click 'Show Analytics'.")
    st.stop()

# =============================================================================
# METRIC CARDS — Row 1
# Summary angka utama: total ticket, ticket resolved, AVG FRT, AVG RT
# =============================================================================
st.subheader("▪ Summary")
metrics = get_avg_metrics(date_from_str, date_to_str)

if metrics:
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        # Total semua ticket dalam periode
        st.metric("Total Tickets", metrics["total_tickets"])

    with col2:
        # Ticket yang sudah resolved
        st.metric("Tickets Resolved", metrics["tickets_resolved"])

    with col3:
        # Ticket yang masih open (belum resolved)
        backlog = metrics["total_tickets"] - metrics["tickets_resolved"]
        st.metric("Backlog (Open)", backlog)

    with col4:
        # AVG FRT — Only from ticket have FRT
        st.metric(
            "AVG FRT",
            seconds_to_hhmmss(metrics["avg_frt"]),
            help="Only from " + str(metrics["tickets_with_frt"]) + " ticket have FRT"
        )

    with col5:
        # AVG Resolution Time — Only from ticket resolved
        st.metric(
            "AVG Resolution Time",
            seconds_to_hhmmss(metrics["avg_rt"]),
            help="Only from " + str(metrics["tickets_resolved"]) + " ticket resolved"
        )

st.divider()

# =============================================================================
# CHART 1 — Ticket Masuk vs Ticket Solved (Line Chart)
# Menunjukkan volume dan performa tim per hari
# Kalau Solved > Masuk → tim catch up backlog
# Kalau Masuk > Solved → backlog numpuk
# =============================================================================
st.subheader("📈 Total Tickets per Day")

df_volume = get_daily_volume(date_from_str, date_to_str)
if not df_volume.empty:
    # Set date sebagai index untuk chart
    df_chart = df_volume.set_index("date")
    st.line_chart(df_chart[["Ticket Created"]])

    # Tampilkan juga tabel data di bawah chart
    with st.expander("View Data"):
        st.dataframe(df_volume[["date", "Ticket Created"]], use_container_width=True)
else:
    st.info("There is no data for this period.")

st.divider()

# =============================================================================
# CHART 2 — AVG FRT Trend per Hari (Line Chart)
# Menunjukkan tren kecepatan respons tim dari hari ke hari
# =============================================================================
st.subheader("⏱️ AVG FRT per Day")

df_frt = get_daily_avg_frt(date_from_str, date_to_str)
if not df_frt.empty:
    df_frt_chart = df_frt.set_index("date")
    st.line_chart(df_frt_chart["AVG FRT (minute)"])

    with st.expander("View Data"):
        st.dataframe(df_frt, use_container_width=True)
else:
    st.info("There is no data for this period.")

st.divider()

# =============================================================================
# CHART 3 — Breakdown per Kategori (Bar Chart)
# User bisa pilih mau lihat breakdown per apa:
# agent, service, type, atau priority
# =============================================================================
st.subheader(" Breakdown Ticket")

# Dropdown pilih kategori breakdown
breakdown_options = {
    "Agent"    : "agent",
    "Service"  : "service",
    "Type"     : "type",
    "Priority" : "priority",
    "Escalate" : "escalate"
}
sel_breakdown = st.selectbox(
    "Breakdown by",
    list(breakdown_options.keys())
)

df_breakdown = get_breakdown_by(
    date_from_str,
    date_to_str,
    group_by=breakdown_options[sel_breakdown]
)

if not df_breakdown.empty:
    chart = alt.Chart(df_breakdown).mark_bar().encode(
        x=alt.X("Label:N", sort="-y", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("Total:Q"),
        tooltip=["Label", "Total"]
    )
    st.altair_chart(chart, use_container_width=True)

    with st.expander("Viewt Data"):
        st.dataframe(df_breakdown, use_container_width=True)