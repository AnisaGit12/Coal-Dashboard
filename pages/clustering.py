import streamlit as st
import pandas as pd
import joblib
import numpy as np
import plotly.express as px

def load_models():
    scaler = joblib.load('scaler.pkl')
    model = joblib.load('kmeans_k3.pkl')
    df = pd.read_csv('dataset_with_clusters.csv')
    return scaler, model, df

scaler, model, df = load_models()

st.title("⛏️ Analisis Klaster AI")
st.info("Masukkan 5 data operasional untuk simulasi klasifikasi.")

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        in_ton = st.number_input("Total Tonase", value=1200.0)
        in_rit = st.number_input("Total Ritase", value=4)
        in_delay = st.number_input("Delay Time (Jam)", value=1.5)
    with col2:
        in_rain = st.number_input("Rain Hours", value=0.0)
        in_slip = st.number_input("Slippery Hours", value=1.0)

    if st.button("🚀 Jalankan Analisis AI", use_container_width=True):
        # 1. Hitung Ton per Trip
        in_avg = in_ton / in_rit
        
        # 2. SUSUN 5 FITUR (Menghapus Available Time agar tidak error)
        features = np.array([[in_ton, in_avg, in_delay, in_rain, in_slip]])
        
        try:
            # 3. Scaling & Predict
            scaled_feat = scaler.transform(features)
            res = model.predict(scaled_feat)[0]
            
            # 4. Tampilkan Hasil
            cluster_names = {0: "Cluster 0", 1: "Cluster 1", 2: "Cluster 2"} # Sesuaikan dengan mapping kamu
            st.success(f"### Hasil Prediksi: {cluster_names[res]}")
            
        except Exception as e:
            st.error(f"Terjadi ketidakcocokan data: {e}")
            st.info("Pastikan model .pkl kamu menggunakan 5 fitur yang sama.")

st.write("---")
st.subheader("Peta Sebaran Klaster (PCA)")
fig = px.scatter(df, x='pca1', y='pca2', color='cluster', hover_data=['total_ton'])
st.plotly_chart(fig, use_container_width=True)