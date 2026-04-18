import streamlit as st
import pandas as pd
import plotly.express as px

# 1. KONFIGURASI HALAMAN
st.set_page_config(layout="wide")

st.markdown("""
    <style>
    .block-container { max-width: 1200px; padding-top: 2rem; }
    
    /* Box Filter Area Utama */
    .filter-container {
        background-color: #f8fafc;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        margin-bottom: 25px;
    }
    
    .report-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border-top: 4px solid #2E5BFF;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. LOAD DATA
def load_data():
    try:
        df = pd.read_csv('dataset_with_clusters.csv')
        df['date'] = pd.to_datetime(df['date'])
        return df
    except:
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # Mapping Cluster
    cluster_order = df.groupby('cluster')['total_ton'].mean().sort_values(ascending=False).index
    mapping = {cluster_order[0]: "High", cluster_order[1]: "Medium", cluster_order[2]: "Low"}
    df['Status'] = df['cluster'].map(mapping)

    # --- HEADER ---
    st.title("📄 Production Reports")
    st.markdown("Summary of coal hauling performance and cluster distribution.")
    
    # --- ROW 1: FILTER DI AREA UTAMA (Bukan di Sidebar) ---
    st.write("")
    with st.container():
        # Membuat box filter yang rapi
        st.info("💡 **Filter Periode Laporan**")
        col_f1, col_f2, col_f3 = st.columns([2, 2, 1])
        
        with col_f1:
            start_date = st.date_input("Mulai Tanggal", df['date'].min())
        with col_f2:
            end_date = st.date_input("Sampai Tanggal", df['date'].max())
        with col_f3:
            st.write("") # Spacer
            st.write("") # Spacer
            # Tombol reset atau sekadar info jika perlu
            if st.button("Reset Filter", use_container_width=True):
                st.rerun()

    # Logika Filter Tanggal
    mask = (df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)
    report_df = df.loc[mask]

    st.write("---")

    # --- ROW 2: SUMMARY STATS (KPI) ---
    counts = report_df['Status'].value_counts()
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"<div class='report-card'><p style='color:gray; font-size:12px;'>Total Days</p><h3>{len(report_df)}</h3></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='report-card' style='border-top-color:#22c55e'><p style='color:gray; font-size:12px;'>High Days</p><h3 style='color:#22c55e'>{counts.get('High', 0)}</h3></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='report-card' style='border-top-color:#f59e0b'><p style='color:gray; font-size:12px;'>Medium Days</p><h3 style='color:#f59e0b'>{counts.get('Medium', 0)}</h3></div>", unsafe_allow_html=True)
    with c4:
        st.markdown(f"<div class='report-card' style='border-top-color:#ef4444'><p style='color:gray; font-size:12px;'>Low Days</p><h3 style='color:#ef4444'>{counts.get('Low', 0)}</h3></div>", unsafe_allow_html=True)

    st.write("")

    # --- ROW 3: CHARTS ---
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.subheader("Cluster Distribution")
        fig_pie = px.pie(report_df, names='Status', hole=0.4,
                         color='Status',
                         color_discrete_map={'High':'#22c55e', 'Medium':'#f59e0b', 'Low':'#ef4444'})
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_chart2:
        st.subheader("Tonnage Contribution")
        contrib = report_df.groupby('Status')['total_ton'].sum().reset_index()
        fig_bar = px.bar(contrib, x='Status', y='total_ton', color='Status',
                         color_discrete_map={'High':'#22c55e', 'Medium':'#f59e0b', 'Low':'#ef4444'})
        st.plotly_chart(fig_bar, use_container_width=True)

    # --- ROW 4: EXPORT DATA ---
    st.write("---")
    st.subheader("Detailed Record Table")
    st.dataframe(report_df[['date', 'total_ton', 'trip_day', 'Status']].sort_values('date', ascending=False), use_container_width=True)
    
    st.write("")
    csv = report_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Analyzed Data (.CSV)",
        data=csv,
        file_name=f'report_{start_date}_to_{end_date}.csv',
        mime='text/csv',
        use_container_width=True
    )

else:
    st.error("Data tidak ditemukan atau file CSV rusak.")