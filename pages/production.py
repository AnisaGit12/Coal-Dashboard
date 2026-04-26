import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. KONFIGURASI HALAMAN
st.set_page_config(layout="wide")

# 2. CUSTOM CSS
st.markdown("""
    <style>
    .block-container { max-width: 1200px; padding-top: 2rem; }
    .metric-card {
        background-color: #ffffff; padding: 20px; border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05); border: 1px solid #f0f2f6;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. LOAD DATA & CALCULATE METRICS
def load_data():
    try:
        df = pd.read_csv('dataset_with_clusters.csv')
        df['date'] = pd.to_datetime(df['date'])
        
        # Menghitung Jam Kerja Efektif (Asumsi 24 jam - Downtime)
        df['effective_hrs'] = 24 - (df['actual_rain_hours'] + df['slippery_hours'])
        df['effective_hrs'] = df['effective_hrs'].clip(lower=1)
        
        # Hitung Produktivitas per Jam
        df['ton_per_hour'] = df['total_ton'] / df['effective_hrs']
        return df
    except:
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # --- LOGIKA MAPPING STATUS ---
    # Mengurutkan cluster agar 0,1,2 berubah jadi teks High, Medium, Low secara otomatis
    means = df.groupby('cluster')['total_ton'].mean().sort_values(ascending=False)
    mapping = {means.index[0]: "High", means.index[1]: "Medium", means.index[2]: "Low"}
    df['Category'] = df['cluster'].map(mapping)

    st.title("Production & Efficiency Analysis")
    st.markdown("Analisis performa produksi batubara dan efisiensi jam kerja alat.")

    # --- ROW 1: KPI CARDS ---
    latest = df.sort_values('date').iloc[-1]
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown(f"<div class='metric-card'><p style='color:gray; font-size:12px;'>Hourly Productivity</p><h3>{latest['ton_per_hour']:.1f} <small>Ton/Hr</small></h3></div>", unsafe_allow_html=True)
    with c2:
        utilization = (latest['effective_hrs'] / 24) * 100
        st.markdown(f"<div class='metric-card'><p style='color:gray; font-size:12px;'>Time Utilization</p><h3>{utilization:.1f} %</h3></div>", unsafe_allow_html=True)
    with c3:
        status_color = "#22c55e" if latest['Category'] == "High" else "#f59e0b" if latest['Category'] == "Medium" else "#ef4444"
        st.markdown(f"<div class='metric-card'><p style='color:gray; font-size:12px;'>Current Category</p><h3 style='color:{status_color}'>{latest['Category']}</h3></div>", unsafe_allow_html=True)

    st.write("---")

    # --- ROW 2: HOURLY PRODUCTION & EFFICIENCY CHART ---
    st.subheader("Hourly Production & Efficiency Trend")
    
    fig = go.Figure()
    # Area Chart Produktivitas
    fig.add_trace(go.Scatter(
        x=df['date'], y=df['ton_per_hour'],
        mode='lines+markers', name='Actual (Ton/Hr)',
        line=dict(color='#2E5BFF', width=3),
        fill='tozeroy', fillcolor='rgba(46, 91, 255, 0.1)'
    ))
    # Target Line (100 Ton/Hr)
    fig.add_trace(go.Scatter(
        x=df['date'], y=[100]*len(df),
        mode='lines', name='Target (100 T/Hr)',
        line=dict(color='#ef4444', width=2, dash='dot')
    ))

    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', hovermode="x unified", margin=dict(t=10, b=0))
    st.plotly_chart(fig, use_container_width=True)

    st.write("---")

    # --- ROW 3: PERFORMANCE ANALYSIS TABLE ---
    st.subheader("Performance Analysis Record")
    
    # Menyiapkan tabel untuk manajemen
    table_df = df.sort_values('date', ascending=False).copy()
    table_df['Date'] = table_df['date'].dt.strftime('%d %b %Y')
    
    

    st.dataframe(
        table_df[['Date', 'total_ton', 'ton_per_hour', 'actual_rain_hours', 'slippery_hours', 'Category']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Date": "Tanggal Ops",
            "total_ton": st.column_config.NumberColumn("Total Produksi (Ton)", format="%d"),
            "ton_per_hour": st.column_config.ProgressColumn(
                "Produktivitas (Ton/Jam)",
                help="Produksi rata-rata per jam kerja efektif",
                format="%.1f",
                min_value=0,
                max_value=200,
            ),
            "actual_rain_hours": "Hujan (Jam)",
            "slippery_hours": "Slippery (Jam)",
            "Category": "Kategori Produksi" # NAMA DIUBAH DI SINI
        }
    )
