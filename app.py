import streamlit as st

# 1. KONFIGURASI HALAMAN
st.set_page_config(
    page_title="Coal Monitor", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. CSS CUSTOM UNTUK SIDEBAR (Font Besar & Hover Effect)
st.markdown("""
    <style>
    /* 1. Memperbesar Font Judul di Sidebar */
    [data-testid="stSidebar"] h1 {
        font-size: 28px !important;
        font-weight: bold !important;
        color: #1E293B !important;
    }

    /* 2. Memperbesar Font Menu Navigasi (Halaman) */
    [data-testid="stSidebarNav"] span {
        font-size: 18px !important; /* Ukuran menu lebih besar */
        font-weight: 500 !important;
        margin-left: 10px;
    }

    /* 3. Memberikan Efek Interaktif (Hover) pada Menu */
    [data-testid="stSidebarNav"] li:hover {
        background-color: #E2E8F0 !important; /* Warna abu muda saat kursor di atasnya */
        border-radius: 10px;
        transition: 0.3s;
    }

    /* 4. Memperbesar Font Caption/Teks Biasa di Sidebar */
    [data-testid="stSidebar"] .stMarkdown p {
        font-size: 16px !important;
        line-height: 1.5;
    }

    /* 5. Mengatur Lebar Sidebar agar tidak terlalu sempit */
    [data-testid="stSidebar"] {
        width: 320px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. DEFINISI HALAMAN (Sistem Navigasi Baru)
# Pastikan file-file ini ada di folder 'pages'
home_page = st.Page("pages/home.py", title="Dashboard Utama", default=True)
prod_page = st.Page("pages/production.py", title="Tren Produksi")
clust_page = st.Page("pages/clustering.py", title="Analisis K-Means")
report_page = st.Page("pages/report.py", title="Laporan Akhir",)

# 4. EKSEKUSI NAVIGASI
pg = st.navigation({
    "MAIN MENU": [home_page],
    "ANALYTICS": [prod_page, clust_page, report_page]
})

# 5. BRANDING DI SIDEBAR
with st.sidebar:
    st.markdown("# Coal Monitor")
    st.caption("Production Management System v1.0")
    st.markdown("---")
    # Slot untuk info user atau logo tambahan
    st.write("**Role:** Mining Manager")

pg.run()