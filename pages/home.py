import streamlit as st
import pandas as pd
import plotly.express as px

st.markdown("<style>.block-container {max-width: 1200px;}</style>", unsafe_allow_html=True)

def load_data():
    df = pd.read_csv('dataset_with_clusters.csv')
    df['date'] = pd.to_datetime(df['date'])
    return df

df = load_data()

if not df.empty:
    cluster_order = df.groupby('cluster')['total_ton'].mean().sort_values(ascending=False).index
    mapping = {cluster_order[0]: "High", cluster_order[1]: "Medium", cluster_order[2]: "Low"}
    latest = df.sort_values('date').iloc[-1]

    st.title("Coal Hauling Production Dashboard")
    
    # KPI CARDS
    c1, c2, c3, c4 = st.columns(4, gap="medium")
    c1.metric("Production Today", f"{latest['total_ton']:,.0f} T")
    c2.metric("Avg Production", f"{df['total_ton'].mean():,.0f} T")
    c3.metric("Total Trips", f"{latest['trip_day']:.0f}")
    
    status_label = mapping.get(latest['cluster'])
    color = "#22c55e" if status_label == "High" else "#f59e0b" if status_label == "Medium" else "#ef4444"
    with c4:
        st.markdown(f"<div style='background:{color}; color:white; padding:15px; border-radius:12px; text-align:center;'><b>Status: {status_label}</b></div>", unsafe_allow_html=True)

    # TREND DENGAN FIXED FREQUENCY
    st.write("---")
    col_t, col_f = st.columns([2, 1])
    with col_t: st.subheader("Production Trend")
    with col_f:
        period = st.segmented_control("Periode", ["Harian", "Bulanan", "Tahunan"], default="Harian", label_visibility="collapsed")

    if period == "Bulanan":
        chart_df = df.set_index('date').resample('ME')['total_ton'].sum().reset_index()
    elif period == "Tahunan":
        chart_df = df.set_index('date').resample('YE')['total_ton'].sum().reset_index()
    else:
        chart_df = df.sort_values('date')

    fig = px.line(chart_df, x='date', y='total_ton', markers=True, line_shape='spline', color_discrete_sequence=['#2E5BFF'])
    fig.update_layout(xaxis_title=None, yaxis_title="Tonnage", plot_bgcolor="white", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)
