import streamlit as st
import pandas as pd
import plotly.express as px
import pickle
import os

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Peta Kinerja & Simulasi",
    layout="wide"
)

# =========================
# CSS STYLING
# =========================
st.markdown("""
<style>
.kalkulator-box {
    background-color: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 24px;
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

st.title("Peta Kinerja & Simulasi Target")
st.markdown("---")

# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_data():
    df = pd.read_excel("hasil_cluster_final_fix.xlsx")
    df.columns = df.columns.str.strip()

    required_cols = ["Total Ton Hauler Actual", "Trip/day", "Cluster"]
    for col in required_cols:
        if col not in df.columns:
            st.error(f"Kolom {col} tidak ditemukan di dataset")
            st.stop()

    df["Total Ton Hauler Actual"] = pd.to_numeric(df["Total Ton Hauler Actual"], errors="coerce").fillna(0)
    df["Trip/day"] = pd.to_numeric(df["Trip/day"], errors="coerce").fillna(0)

    # Mengubah angka cluster menjadi label bahasa awam
    def label_cluster(x):
        if x == 2: return "High (Aman)"
        elif x == 1: return "Normal (Waspada)"
        else: return "Low (Kritis)"
    
    df["Kategori Kinerja"] = df["Cluster"].apply(label_cluster)
    return df

df = load_data()

# Pengaturan Warna Konsisten untuk seluruh grafik
color_map = {
    "High (Aman)": "#10b981",       # Hijau
    "Normal (Waspada)": "#f59e0b",  # Kuning
    "Low (Kritis)": "#ef4444"       # Merah
}

# =========================
# ROW 1: GRAFIK SEBARAN & DISTRIBUSI
# =========================
col_chart1, col_chart2 = st.columns([2, 1])

with col_chart1:
    st.subheader("Peta Sebaran Kinerja Harian")
    # Scatter plot yang lebih cantik dan bahasanya mudah dimengerti
    fig_scatter = px.scatter(
        df,
        x="Total Ton Hauler Actual",
        y="Trip/day",
        color="Kategori Kinerja",
        color_discrete_map=color_map,
        labels={"Total Ton Hauler Actual": "Total Produksi (Ton)", "Trip/day": "Jumlah Trip"},
        title="Distribusi Historis Kinerja"
    )
    fig_scatter.update_layout(plot_bgcolor='white', margin=dict(t=40, b=0, l=0, r=0))
    fig_scatter.update_xaxes(showgrid=True, gridcolor='#f1f5f9')
    fig_scatter.update_yaxes(showgrid=True, gridcolor='#f1f5f9')
    st.plotly_chart(fig_scatter, use_container_width=True)

with col_chart2:
    st.subheader("Frekuensi Status")
    cluster_count = df["Kategori Kinerja"].value_counts().reset_index()
    cluster_count.columns = ["Kategori", "Jumlah Hari"]
    
    fig_bar = px.bar(
        cluster_count,
        x="Kategori",
        y="Jumlah Hari",
        color="Kategori",
        color_discrete_map=color_map,
        text="Jumlah Hari"
    )
    fig_bar.update_layout(showlegend=False, plot_bgcolor='white', margin=dict(t=40, b=0, l=0, r=0))
    fig_bar.update_xaxes(title="")
    st.plotly_chart(fig_bar, use_container_width=True)

# =========================
# ROW 2: STANDAR KINERJA (FULL WIDTH)
# =========================
st.markdown("<br>", unsafe_allow_html=True)

st.subheader("Standar Batas Kinerja")
st.markdown("Rata-rata pencapaian untuk masing-masing kategori operasional berdasarkan analisis data historis:")

# Menghitung nilai rata-rata sesungguhnya dari data
cluster_summary = df.groupby("Kategori Kinerja").agg({
    "Total Ton Hauler Actual": "mean",
    "Trip/day": "mean"
}).round(0).reset_index()

cluster_summary.columns = ["Kategori", "Rata-rata Tonase", "Rata-rata Trip"]

# Mengurutkan tabel dari High ke Low
cluster_summary['sort'] = cluster_summary['Kategori'].map({"High (Aman)": 1, "Normal (Waspada)": 2, "Low (Kritis)": 3})
cluster_summary = cluster_summary.sort_values('sort').drop('sort', axis=1)

# Tabel dirender langsung tanpa masuk ke dalam kolom agar melebar penuh
st.dataframe(cluster_summary, use_container_width=True, hide_index=True)
