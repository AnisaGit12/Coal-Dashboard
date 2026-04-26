import streamlit as st
import pandas as pd
import plotly.express as px

# 1. KONFIGURASI & STYLING (Agar tampilan padat & profesional)
st.markdown("""
    <style>
    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
    }
    /* Styling Kartu KPI ala Figma */
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
        width: 35px;
        height: 35px;
        background-color: #f0f4ff;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        margin-bottom: 10px;
    }
    .kpi-label { color: #64748b; font-size: 13px; font-weight: 500; }
    .kpi-value { color: #1e293b; font-size: 24px; font-weight: bold; margin: 0; }
    .kpi-sub { color: #94a3b8; font-size: 11px; margin-top: 4px; }
    
    /* Menghilangkan label default pada segmented control */
    div[data-testid="stSegmentedControl"] label { display: none; }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNGSI LOAD DATA
def load_data():
    try:
        df = pd.read_csv('dataset_with_clusters.csv')
        df['date'] = pd.to_datetime(df['date'])
        return df
    except:
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # --- LOGIKA MAPPING ---
    cluster_order = df.groupby('cluster')['total_ton'].mean().sort_values(ascending=False).index
    mapping = {cluster_order[0]: "High", cluster_order[1]: "Medium", cluster_order[2]: "Low"}
    latest = df.sort_values('date').iloc[-1]
    
    # --- HEADER ---
    st.title("Coal Hauling Production Dashboard")
    st.markdown("Real-time monitoring and insights for mining operations")
    st.write("")

    # --- ROW 1: KPI CARDS (FIGMA STYLE) ---
    c1, c2, c3, c4 = st.columns(4, gap="medium")

    with c1:
        st.markdown(f"""<div class='kpi-card'><div class='kpi-icon'>📊</div><div class='kpi-label'>Total Production Today</div>
            <div class='kpi-value'>{latest['total_ton']:,.0f}</div><div class='kpi-sub'>tonnes / day</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class='kpi-card'><div class='kpi-icon'>📈</div><div class='kpi-label'>Average Production</div>
            <div class='kpi-value'>{df['total_ton'].mean():,.0f}</div><div class='kpi-sub'>overall average</div></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class='kpi-card'><div class='kpi-icon'>🚚</div><div class='kpi-label'>Total Trips</div>
            <div class='kpi-value'>{latest['trip_day']:.0f}</div><div class='kpi-sub'>trips today</div></div>""", unsafe_allow_html=True)
    with c4:
        status = mapping.get(latest['cluster'])
        bg = "#22c55e" if status == "High" else "#f59e0b" if status == "Medium" else "#ef4444"
        st.markdown(f"""<div class='kpi-card' style='background:{bg}; border:none;'>
            <div class='kpi-icon' style='background:rgba(255,255,255,0.2)'>✨</div>
            <div class='kpi-label' style='color:white; opacity:0.8;'>Production Status</div>
            <div class='kpi-value' style='color:white;'>{status}</div>
            <div class='kpi-sub' style='color:white; opacity:0.8;'>● Live monitoring</div></div>""", unsafe_allow_html=True)

    st.write("---")

    # --- ROW 2: DAILY PRODUCTION TREND (WITH SEGMENTED CONTROL) ---
    col_t, col_s = st.columns([2, 1])
    with col_t:
        st.subheader("Daily Production Trend")
    with col_s:
        period = st.segmented_control("Periode", ["Harian", "Bulanan", "Tahunan"], default="Harian", label_visibility="collapsed")

    if period == "Bulanan":
        chart_df = df.set_index('date').resample('ME')['total_ton'].sum().reset_index()
    elif period == "Tahunan":
        chart_df = df.set_index('date').resample('YE')['total_ton'].sum().reset_index()
    else:
        chart_df = df.sort_values('date')

    fig = px.line(chart_df, x='date', y='total_ton', markers=True, line_shape='spline', color_discrete_sequence=['#2E5BFF'])
    fig.update_layout(xaxis_title=None, yaxis_title="Tonnage", plot_bgcolor="rgba(0,0,0,0)", hovermode="x unified", margin=dict(t=10, b=0))
    st.plotly_chart(fig, use_container_width=True)

    st.write("---")

    # --- ROW 3: HISTORY & INSIGHTS (SIDE BY SIDE) ---
    col_hist, col_ins = st.columns([1.8, 1], gap="large")

    with col_hist:
        st.subheader("Recent Production History")
        history_df = df.sort_values('date', ascending=False).head(5).copy()
        history_df['Status'] = history_df['cluster'].map(mapping)
        history_df['Date'] = history_df['date'].dt.strftime('%b %d, %Y')
        
        st.dataframe(
            history_df[['Date', 'total_ton', 'trip_day', 'Status']],
            use_container_width=True,
            hide_index=True,
            column_config={
                "total_ton": st.column_config.NumberColumn("Tonnage", format="%d"),
                "trip_day": st.column_config.NumberColumn("Trips", format="%d")
            }
        )

    with col_ins:
        st.subheader("Quick Insights")
        if status == "High":
            st.success("**Performance Excellent!** Produksi hari ini berada di level maksimal. Pastikan ketersediaan unit tetap terjaga untuk shift berikutnya.")
        elif status == "Medium":
            st.warning("**Performance Normal.** Produksi stabil. Perhatikan *delay time* agar tidak meningkat pada jam operasional sibuk.")
        else:
            st.error("**Performance Alert!** Produksi rendah terdeteksi. Segera lakukan evaluasi pada faktor cuaca atau hambatan teknis di lapangan.")

else:
    st.error("Data 'dataset_with_clusters.csv' tidak ditemukan.")
