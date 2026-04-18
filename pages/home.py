import streamlit as st
import pandas as pd
import plotly.express as px

# 1. KONFIGURASI & CSS CUSTOM
st.markdown("""
    <style>
    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
    }
    
    /* Styling Metric Card */
    [data-testid="stMetric"] {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03);
        border: 1px solid #edf2f7;
    }

    /* Styling Status Card */
    .status-box {
        padding: 20px;
        border-radius: 12px;
        color: white;
        text-align: center;
        font-family: sans-serif;
    }
    
    /* Menghilangkan label default pada segmented control agar lebih bersih */
    div[data-testid="stSegmentedControl"] label {
        display: none;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. LOAD DATA
def load_data():
    try:
        df = pd.read_csv('dataset_with_clusters.csv')
        df['date'] = pd.to_datetime(df['date'])
        return df
    except Exception as e:
        st.error(f"Gagal memuat data: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # --- LOGIKA MAPPING CLUSTER ---
    cluster_order = df.groupby('cluster')['total_ton'].mean().sort_values(ascending=False).index
    mapping = {cluster_order[0]: "High", cluster_order[1]: "Medium", cluster_order[2]: "Low"}

    # --- HEADER ---
    st.title("Coal Hauling Production Dashboard")
    st.markdown("Real-time monitoring and insights for mining operations")
    st.write("")

    # --- ROW 1: KPI CARDS ---
    latest_row = df.sort_values('date').iloc[-1]
    c1, c2, c3, c4 = st.columns(4, gap="medium")

    with c1:
        st.metric("Total Production Today", f"{latest_row['total_ton']:,.0f}", "tonnes/day")
    with c2:
        st.metric("Average Production", f"{df['total_ton'].mean():,.0f}", "tonnes/day")
    with c3:
        st.metric("Total Trips", f"{latest_row['trip_day']:.0f}", "trips today")
    with c4:
        current_status = mapping.get(latest_row['cluster'], "Unknown")
        bg_color = "#22c55e" if current_status == "High" else "#f59e0b" if current_status == "Medium" else "#ef4444"
        st.markdown(f"""
            <div class="status-box" style="background-color: {bg_color};">
                <p style="margin:0; font-size:12px; opacity:0.9;">Production Status</p>
                <h2 style="margin:0; font-weight:bold;">{current_status}</h2>
                <p style="margin:0; font-size:11px;">● Live monitoring</p>
            </div>
            """, unsafe_allow_html=True)

    st.write("---")

    # --- ROW 2: TREND CHART DENGAN SEGMENTED CONTROL (FIGMA STYLE) ---
    col_title, col_toggle = st.columns([2, 1])
    
    with col_title:
        st.subheader("Daily Production Trend")
    
    with col_toggle:
        # Menggunakan Segmented Control agar mirip tombol Figma (Per Hari, Per Bulan)
        period = st.segmented_control(
            "Periode",
            options=["Per Hari", "Per Bulan", "Per Tahun"],
            default="Per Hari",
            label_visibility="collapsed"
        )

    # Logika Agregasi Data
    if period == "Per Bulan":
        chart_df = df.set_index('date').resample('M')['total_ton'].sum().reset_index()
    elif period == "Per Tahun":
        chart_df = df.set_index('date').resample('Y')['total_ton'].sum().reset_index()
    else:
        chart_df = df.sort_values('date')

    fig = px.line(chart_df, x='date', y='total_ton', markers=True, 
                  line_shape='spline', color_discrete_sequence=['#2E5BFF'])

    fig.update_layout(
        xaxis_title=None, yaxis_title="Tonnage",
        margin=dict(l=0, r=0, t=10, b=0),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        hovermode="x unified"
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor='#f0f2f6')
    
    st.plotly_chart(fig, use_container_width=True)

    # --- ROW 3: HISTORY & INSIGHTS ---
    st.write("---")
    c_left, c_right = st.columns([2, 1], gap="large")

    with c_left:
        st.subheader("Recent Production History")
        history = df[['date', 'total_ton', 'trip_day', 'cluster']].tail(5).copy()
        history['Status'] = history['cluster'].map(mapping)
        st.dataframe(history.drop(columns=['cluster']), use_container_width=True, hide_index=True)

    with c_right:
        st.subheader("Quick Insights")
        if current_status == "High":
            st.info("**Performance Excellent!** Produksi sangat optimal hari ini.")
        elif current_status == "Medium":
            st.warning("**Performance Normal.** Produksi stabil, tetap pantau ritase.")
        else:
            st.error("**Performance Alert!** Produksi rendah, cek faktor hambatan.")

else:
    st.warning("Data tidak ditemukan.")
