import streamlit as st
import pandas as pd
import joblib
import numpy as np
import plotly.express as px

# 1. KONFIGURASI
st.set_page_config(layout="wide")

st.markdown("""
    <style>
    .block-container { max-width: 1200px; padding-top: 2rem; }
    .status-box {
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        border: 2px solid #e2e8f0;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. LOAD DATA & MODEL
def load_essentials():
    df = pd.read_csv('dataset_with_clusters.csv')
    scaler = joblib.load('scaler.pkl')
    model = joblib.load('kmeans_k3.pkl')
    return df, scaler, model

df, scaler, model = load_essentials()

# Mapping Status Otomatis
means = df.groupby('cluster')['total_ton'].mean().sort_values(ascending=False)
mapping = {means.index[0]: "Produksi Tinggi (High)", 
           means.index[1]: "Produksi Normal (Medium)", 
           means.index[2]: "Produksi Rendah (Low)"}
colors = {means.index[0]: "#22c55e", means.index[1]: "#f59e0b", means.index[2]: "#ef4444"}

df['Kategori'] = df['cluster'].map(mapping)

# --- HEADER ---
st.title("Analisis Operasional")
st.write("Sistem ini mengelompokkan data operasional secara otomatis untuk memahami faktor yang mempengaruhi produksi.")

# --- BAGIAN 1: PROFIL KARAKTERISTIK (Poin 2) ---
st.write("---")
st.subheader("Perbandingan Karakteristik Produksi")
st.info("Tabel ini menunjukkan kondisi rata-rata pada setiap kategori produksi.")

# Menghitung rata-rata per kategori
profile_table = df.groupby('Kategori')[['total_ton', 'actual_rain_hours', 'ton_per_trip']].mean().reset_index()
profile_table.columns = ['Kategori', 'Rata-rata Tonase', 'Rata-rata Hujan (Jam)', 'Efisiensi (T/Trip)']

col_table, col_chart = st.columns([1.2, 1])

with col_table:
    st.table(profile_table.style.format({
        'Rata-rata Tonase': '{:,.0f}',
        'Rata-rata Hujan (Jam)': '{:.1f}',
        'Efisiensi (T/Trip)': '{:.2f}'
    }))

with col_chart:
    # Grafik Bar Sederhana yang Sangat Mudah Dimengerti
    fig_bar = px.bar(profile_table, x='Kategori', y='Rata-rata Tonase', 
                     color='Kategori', 
                     color_discrete_map={v: colors[k] for k, v in mapping.items()},
                     title="Produksi vs Kategori")
    fig_bar.update_layout(showlegend=False, height=300)
    st.plotly_chart(fig_bar, use_container_width=True)

# --- BAGIAN 2: SIMULATOR "WHAT-IF" (Poin 4) ---
st.write("---")
st.subheader("Simulator Prediksi Kategori")
st.write("Gunakan slider di bawah untuk mensimulasikan kondisi operasional hari ini.")

with st.container():
    c1, c2, c3 = st.columns(3)
    with c1:
        s_ton = st.slider("Target Tonase", 0, 3000, 1500)
        s_rit = st.number_input("Estimasi Ritase", 1, 10, 5)
    with c2:
        s_rain = st.slider("Prediksi Hujan (Jam)", 0.0, 12.0, 1.0)
        s_slip = st.slider("Prediksi Jalan Licin (Jam)", 0.0, 12.0, 0.5)
    with c3:
        s_delay = st.slider("Hambatan/Delay (Jam)", 0.0, 10.0, 2.0)
        
    if st.button("Jalankan Simulasi AI", use_container_width=True):
        # Hitung input
        s_avg = s_ton / s_rit
        # Urutan 5 fitur: Ton, Avg, Delay, Rain, Slip
        feat = np.array([[s_ton, s_avg, s_delay, s_rain, s_slip]])
        
        scaled_feat = scaler.transform(feat)
        pred = model.predict(scaled_feat)[0]
        
        res_label = mapping[pred]
        res_color = colors[pred]
        
        st.markdown(f"""
            <div class="status-box" style="background-color: {res_color}15; border-color: {res_color};">
                <p style="margin:0; color: #64748b;">Hasil Analisis Sistem:</p>
                <h1 style="margin:0; color: {res_color};">{res_label}</h1>
                <p style="margin:10px 0 0 0; font-size:14px; color: #64748b;">
                    Berdasarkan pola historis, kondisi ini masuk dalam kategori <b>{res_label}</b>.
                </p>
            </div>
        """, unsafe_allow_html=True)

st.write("---")
st.caption("Analisis ini didasarkan pada model Machine Learning K-Means yang mempelajari data 6 bulan terakhir.")
