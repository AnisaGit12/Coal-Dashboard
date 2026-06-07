import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Production Analysis",
    layout="wide"
)

# =========================
# CSS STYLING
# =========================
st.markdown("""
<style>
.sub-header { font-size: 14px; color: #64748b; margin-bottom: 24px; margin-top: -15px; text-align: center; }
.kpi-card {
    background-color: #ffffff;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
    border: 1px solid #f1f5f9;
    height: 100%;
}
.icon-box {
    width: 40px;
    height: 40px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    margin-bottom: 15px;
}
.kpi-title { font-size: 13px; color: #64748b; font-weight: 500; margin-bottom: 5px; }
.kpi-value { font-size: 28px; font-weight: 700; color: #0f172a; margin-bottom: 5px; }
.kpi-subtext { font-size: 12px; font-weight: 500; }
.text-green { color: #10b981; }
.text-red { color: #ef4444; }

.bg-green-icon { background-color: #dcfce7; color: #22c55e; }
.bg-purple-icon { background-color: #f3e8ff; color: #a855f7; }
.bg-orange-icon { background-color: #ffedd5; color: #f97316; }

div.stDownloadButton > button {
    background-color: #2563eb;
    color: white;
    border-radius: 8px;
    font-weight: 600;
    padding: 4px 16px;
    border: none;
    transition: all 0.3s ease;
}
div.stDownloadButton > button:hover {
    background-color: #1d4ed8;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# =========================
# LOAD DATA & CLEANING
# =========================
@st.cache_data
def load_data():
    df = pd.read_excel("hasil_cluster_final_fix.xlsx")
    df.columns = df.columns.str.strip()
    
    df["Date"] = pd.to_datetime(df["Date"], format="mixed", dayfirst=True, errors="coerce")
    
    if df["Total Ton Hauler Actual"].dtype == object:
        df["Total Ton Hauler Actual"] = df["Total Ton Hauler Actual"].astype(str).str.replace(',', '.')
    
    df["Total Ton Hauler Actual"] = pd.to_numeric(df["Total Ton Hauler Actual"], errors="coerce").fillna(0)
    df["Trip/day"] = pd.to_numeric(df["Trip/day"], errors="coerce").fillna(0)
    
    df = df.dropna(subset=["Date"])
    df = df.sort_values("Date").reset_index(drop=True)
    
    # Hitung rasio Ton per Trip
    df["Ton/Trip"] = df["Total Ton Hauler Actual"] / df["Trip/day"]
    df["Ton/Trip"] = df["Ton/Trip"].fillna(0)
    
    # Konversi ke Persentase (Berdasarkan muatan maksimal yang pernah dicapai)
    max_capacity = df["Ton/Trip"].max()
    if max_capacity > 0:
        df["Efficiency"] = (df["Ton/Trip"] / max_capacity) * 100
    else:
        df["Efficiency"] = 0
        
    return df

df = load_data()

# =========================
# PERHITUNGAN DELTA (HARI INI vs KEMARIN)
# =========================
latest_data = df.iloc[-1]
prev_data = df.iloc[-2] if len(df) > 1 else latest_data

eff_today = latest_data["Efficiency"]
eff_prev = prev_data["Efficiency"]
eff_diff = eff_today - eff_prev
eff_pct = (eff_diff / eff_prev * 100) if eff_prev > 0 else 0
eff_color = "text-green" if eff_diff >= 0 else "text-red"
eff_sign = "+" if eff_diff >= 0 else ""

rain_today = latest_data["Actual Rain Hours"]
rain_prev = prev_data["Actual Rain Hours"]
rain_diff = rain_today - rain_prev
rain_pct = (rain_diff / rain_prev * 100) if rain_prev > 0 else 0
rain_color = "text-green" if rain_diff <= 0 else "text-red" 
rain_sign = "+" if rain_diff > 0 else ""

trip_today = latest_data["Trip/day"]
trip_prev = prev_data["Trip/day"]
trip_diff = trip_today - trip_prev
trip_pct = (trip_diff / trip_prev * 100) if trip_prev > 0 else 0
trip_color = "text-green" if trip_diff >= 0 else "text-red"
trip_sign = "+" if trip_diff >= 0 else ""

# =========================
# HEADER
# =========================
st.markdown("<div class='sub-header'>Detailed production analysis and efficiency performance</div>", unsafe_allow_html=True)

# =========================
# KPI CARDS
# =========================
spacer_kiri, col1, col2, col3, spacer_kanan = st.columns([1, 2.5, 2.5, 2.5, 1]) 

with col1:
    st.markdown(f"""
<div class="kpi-card">
<div class="icon-box bg-green-icon">📈</div>
<div class="kpi-title">Efficiency</div>
<div class="kpi-value">{eff_today:.0f}<span style="font-size:20px; font-weight:700; color:#0f172a;">%</span></div>
<div class="kpi-subtext {eff_color}">{eff_sign}{eff_pct:.1f}% from yesterday</div>
</div>
""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""
<div class="kpi-card">
<div class="icon-box bg-purple-icon">⏱️</div>
<div class="kpi-title">Rain Hours Impact</div>
<div class="kpi-value">{rain_today:.1f} <span style="font-size:14px; font-weight:500; color:#64748b;">Hours</span></div>
<div class="kpi-subtext {rain_color}">{rain_sign}{rain_pct:.1f}% from yesterday</div>
</div>
""", unsafe_allow_html=True)

with col3:
    st.markdown(f"""
<div class="kpi-card">
<div class="icon-box bg-orange-icon">📍</div>
<div class="kpi-title">Active Hauler Trips</div>
<div class="kpi-value">{trip_today:.0f} <span style="font-size:14px; font-weight:500; color:#64748b;">trips</span></div>
<div class="kpi-subtext {trip_color}">{trip_sign}{trip_pct:.1f}% from yesterday</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# =========================
# CHART HEADER & EXPORT BUTTON
# =========================
st.markdown("""
<div style="background-color:#ffffff; border:1px solid #f1f5f9; border-radius:12px; padding:20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
""", unsafe_allow_html=True)

col_chart_title, col_export = st.columns([4, 1])

with col_chart_title:
    st.markdown("<h3 style='margin:0; font-size:18px; color:#0f172a;'>Hourly Production & Efficiency</h3>", unsafe_allow_html=True)

# with col_export:
#     csv_data = df.to_csv(index=False).encode('utf-8')
#     st.download_button(
#         label="📥 Export Data",
#         data=csv_data,
#         file_name='detailed_production.csv',
#         mime='text/csv',
#         use_container_width=True
#     )

st.markdown("<br>", unsafe_allow_html=True)

# =========================
# PLOTLY AREA CHART
# =========================
df_plot = df.tail(30)
fig = make_subplots(specs=[[{"secondary_y": True}]])

# Garis 1: Tonnage (Warna Biru)
fig.add_trace(
    go.Scatter(
        x=df_plot["Date"], 
        y=df_plot["Total Ton Hauler Actual"],
        fill='tozeroy',
        mode='lines',
        line_shape='spline',
        line=dict(color='#3b82f6', width=2),
        fillcolor='rgba(59, 130, 246, 0.2)',
        name='Tonnage',
        hovertemplate="Tonnage : %{y:,.0f}<extra></extra>" 
    ),
    secondary_y=False,
)

# Garis 2: Efficiency Persen (Warna Hijau)
fig.add_trace(
    go.Scatter(
        x=df_plot["Date"], 
        y=df_plot["Efficiency"],
        fill='tozeroy',
        mode='lines',
        line_shape='spline',
        line=dict(color='#10b981', width=2),
        fillcolor='rgba(16, 185, 129, 0.3)',
        name='Efficiency',
        hovertemplate="Efficiency % : %{y:,.0f}<extra></extra>" 
    ),
    secondary_y=True,
)

# Kustomisasi Hover Tooltip agar box-nya putih bersih dan menyatu (x unified)
fig.update_layout(
    plot_bgcolor='white',
    paper_bgcolor='white',
    height=400,
    margin=dict(l=0, r=0, t=10, b=0),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    hovermode="x unified", 
    hoverlabel=dict(
        bgcolor="white", 
        font_size=14,
        font_family="Arial",
        bordercolor="#e2e8f0"
    )
)

fig.update_xaxes(
    showgrid=True, gridwidth=1, gridcolor='#f1f5f9', griddash='dash',
    tickformat="%d %b"
)
fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f1f5f9', griddash='dash', secondary_y=False)
fig.update_yaxes(showgrid=False, secondary_y=True)

# (Ganti bagian akhir kode Anda mulai dari pemanggilan st.plotly_chart dengan ini)

st.plotly_chart(fig, use_container_width=True)
# Menutup tag div putih container grafik
st.markdown("</div>", unsafe_allow_html=True)

# ==================================================
# PRODUCTION SEGMENT ANALYSIS
# ==================================================
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("Production Segment Analysis")

# Menggunakan df (bukan df_filtered)
cluster_summary = (
    df
    .groupby("Cluster")
    .agg({
        "Total Ton Hauler Actual":"mean",
        "Trip/day":"mean",
        "Actual Rain Hours":"mean" # Saya ganti dari Delay Time ke Actual Rain Hours karena di dataset sebelumnya tidak ada kolom Delay Time
    })
    .round(2)
)

cluster_summary = cluster_summary.reset_index()

def performance_label(cluster):
    if cluster == 2:
        return "High"
    elif cluster == 0:
        return "Medium"
    else:
        return "Low"

cluster_summary["Performance"] = (
    cluster_summary["Cluster"]
    .apply(performance_label)
)

st.dataframe(
    cluster_summary.rename(columns={
        "Cluster":"Cluster ID",
        "Total Ton Hauler Actual":"Avg Production (Ton)",
        "Trip/day":"Avg Trips",
        "Actual Rain Hours":"Avg Rain Hours" 
    }),
    use_container_width=True
)
