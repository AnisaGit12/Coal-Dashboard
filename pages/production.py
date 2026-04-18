import streamlit as st
import pandas as pd

# 1. KONFIGURASI HALAMAN & CSS CUSTOM
st.set_page_config(layout="wide")

st.markdown("""
    <style>
    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
    }
    /* Styling Card Custom seperti Figma */
    .kpi-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: 1px solid #f0f2f6;
        display: flex;
        flex-direction: column;
        height: 100%;
    }
    .kpi-icon {
        width: 40px;
        height: 40px;
        background-color: #f0f4ff;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        margin-bottom: 15px;
    }
    .kpi-label { color: #64748b; font-size: 14px; margin-bottom: 5px; }
    .kpi-value { color: #1e293b; font-size: 24px; font-weight: bold; margin: 0; }
    .kpi-delta { color: #94a3b8; font-size: 12px; margin-top: 5px; }
    
    /* Status Badge Khusus */
    .status-high { color: #22c55e; font-weight: bold; font-size: 28px; }
    </style>
    """, unsafe_allow_html=True)

# 2. LOAD DATA
def load_data():
    df = pd.read_csv('dataset_with_clusters.csv')
    df['date'] = pd.to_datetime(df['date'])
    return df

df = load_data()

if not df.empty:
    # Logic Mapping Status
    cluster_order = df.groupby('cluster')['total_ton'].mean().sort_values(ascending=False).index
    mapping = {cluster_order[0]: "High", cluster_order[1]: "Medium", cluster_order[2]: "Low"}
    
    # Ambil data terbaru
    latest = df.sort_values('date').iloc[-1]
    avg_val = df['total_ton'].mean()

    # --- HEADER ---
    st.title("Coal Hauling Production Dashboard")
    st.markdown("Real-time monitoring and insights for mining operations")
    st.write("")

    # --- ROW 1: FIGMA STYLE KPI CARDS ---
    c1, c2, c3, c4 = st.columns(4, gap="medium")

    with c1:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon">📊</div>
                <div class="kpi-label">Total Production today</div>
                <div class="kpi-value">{latest['total_ton']:,.0f}</div>
                <div class="kpi-delta">tonnes/day</div>
            </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon">📈</div>
                <div class="kpi-label">Average Production</div>
                <div class="kpi-value">{avg_val:,.0f}</div>
                <div class="kpi-delta">tonnes/day</div>
            </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon">🚚</div>
                <div class="kpi-label">Total Trips</div>
                <div class="kpi-value">{latest['trip_day']:.0f}</div>
                <div class="kpi-delta">trips today</div>
            </div>
        """, unsafe_allow_html=True)

    with c4:
        status = mapping.get(latest['cluster'])
        color_class = "status-high" if status == "High" else ""
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon">✨</div>
                <div class="kpi-label">Production Status</div>
                <div class="status-high">{status}</div>
                <div class="kpi-delta">● Live monitoring</div>
            </div>
        """, unsafe_allow_html=True)

    st.write("---")

    # --- ROW 2: PRODUCTION HISTORY TABLE ---
    st.subheader("Recent Production History")
    
    # Menyiapkan DataFrame untuk tabel
    table_df = df.sort_values('date', ascending=False).head(10).copy()
    table_df['Status'] = table_df['cluster'].map(mapping)
    table_df['Date'] = table_df['date'].dt.strftime('%b %d')
    
    # Mengatur tampilan tabel dengan indikator warna (dot)
    st.dataframe(
        table_df[['Date', 'total_ton', 'trip_day', 'Status']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Date": "Date",
            "total_ton": st.column_config.NumberColumn("Tonnage", format="%d"),
            "trip_day": st.column_config.NumberColumn("Trips", format="%d"),
            "Status": st.column_config.SelectboxColumn(
                "Status",
                options=["High", "Medium", "Low"],
                # Menampilkan dot warna di depan teks
            )
        }
    )

    # --- ROW 3: QUICK INSIGHTS ---
    st.write("")
    with st.container():
        st.markdown("""
            <div style="background-color: #f0fdf4; padding: 20px; border-radius: 12px; border-left: 5px solid #22c55e;">
                <h4 style="margin:0; color: #166534;">✅ Performance Excellent</h4>
                <p style="margin:0; color: #166534; font-size: 14px;">Production consistently high this week. Current operations performing optimally.</p>
            </div>
        """, unsafe_allow_html=True)

else:
    st.error("File 'dataset_with_clusters.csv' tidak ditemukan.")