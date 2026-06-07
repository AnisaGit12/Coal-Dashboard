import streamlit as st
import pandas as pd
import plotly.express as px

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Coal Hauling Dashboard",
    layout="wide"
)

# =========================
# CSS STYLING (GABUNGAN FULL)
# =========================
st.markdown("""
<style>
/* Jarak Atas */
.title-alignment { margin-top: -15px; }

/* Komponen History & Insight */
.card-container {
    background-color: #ffffff;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    border: 1px solid #e2e8f0;
    height: 100%;
}
.section-title { font-size: 18px; font-weight: 700; color: #0f172a; margin-bottom: 4px; }
.section-subtitle { font-size: 13px; color: #64748b; margin-bottom: 20px; }

/* Style Tabel */
.history-table { width: 100%; border-collapse: collapse; }
.history-table th { text-align: left; padding: 12px 8px; color: #64748b; font-size: 11px; font-weight: 600; text-transform: uppercase; border-bottom: 1px solid #f1f5f9; }
.history-table td { padding: 14px 8px; font-size: 14px; color: #334155; border-bottom: 1px solid #f8fafc; }

/* Style Badge / Status Pill */
.badge { padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; display: inline-flex; align-items: center; gap: 6px; }
.bg-green { background-color: #dcfce7; color: #166534; }
.bg-yellow { background-color: #fef08a; color: #854d0e; }
.bg-red { background-color: #fee2e2; color: #991b1b; }
.dot { width: 6px; height: 6px; border-radius: 50%; }
.dot-green { background-color: #16a34a; }
.dot-yellow { background-color: #eab308; }
.dot-red { background-color: #dc2626; }

/* Style Insight Cards */
.insight-card { display: flex; gap: 16px; padding: 16px; border-radius: 8px; background: #ffffff; border: 1px solid #f1f5f9; box-shadow: 0 1px 2px rgba(0,0,0,0.02); margin-bottom: 12px; }
.insight-green { border-left: 4px solid #22c55e; }
.insight-yellow { border-left: 4px solid #eab308; }
.insight-blue { border-left: 4px solid #3b82f6; }
.icon-wrapper { font-size: 20px; display: flex; align-items: center; }
.insight-content h4 { margin: 0 0 4px 0; font-size: 14px; color: #0f172a; }
.insight-content p { margin: 0; font-size: 13px; color: #64748b; line-height: 1.4;}
</style>
""", unsafe_allow_html=True)

# =========================
# LOAD DATA & CLEANING ANGKA
# =========================
@st.cache_data
def load_data():
    df = pd.read_excel("hasil_cluster_final_fix.xlsx")
    df.columns = df.columns.str.strip()
    
    # Memaksa format tanggal dibaca dengan benar
    df["Date"] = pd.to_datetime(df["Date"], format="mixed", dayfirst=True, errors="coerce")
    
    # Membersihkan koma agar angka desimal/ribuan versi Indonesia bisa dibaca Python
    if df["Total Ton Hauler Actual"].dtype == object:
        df["Total Ton Hauler Actual"] = df["Total Ton Hauler Actual"].astype(str).str.replace(',', '.')
    
    df["Total Ton Hauler Actual"] = pd.to_numeric(df["Total Ton Hauler Actual"], errors="coerce").fillna(0)
    df["Trip/day"] = pd.to_numeric(df["Trip/day"], errors="coerce").fillna(0)
    
    df = df.dropna(subset=["Date"])
    return df

df = load_data()

# =========================
# 1. HEADER UTAMA
# =========================
st.markdown("<h1 class='title-alignment'>⛏ Coal Hauling Production Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<hr style='margin-top: 0px; margin-bottom: 20px;'>", unsafe_allow_html=True)

# =========================
# 2. KPI CALCULATIONS
# =========================
total_prod = df["Total Ton Hauler Actual"].sum()
avg_prod = df["Total Ton Hauler Actual"].mean()
total_trips = df["Trip/day"].sum()

dominant_cluster = df["Cluster"].value_counts().idxmax() if not df.empty else 0

def cluster_label(x):
    if x == 0: return "Low"
    elif x == 1: return "Anomaly"
    else: return "High"

status = cluster_label(dominant_cluster)

def kpi_card(title, value, subtitle, icon, color):
    return f"""
    <div style="
        padding:18px;
        border-radius:12px;
        background: linear-gradient(135deg,{color[0]},{color[1]});
        color:white;
        box-shadow:0px 4px 12px rgba(0,0,0,0.15);
    ">
        <div style="font-size:14px; opacity:0.9;">{icon} {title}</div>
        <div style="font-size:26px;font-weight:bold;margin-top:6px;">{value}</div>
        <div style="font-size:12px;opacity:0.85;">{subtitle}</div>
    </div>
    """

col1, col2, col3, col4 = st.columns(4)

# Format :,.2f ditambahkan agar menampilkan koma/desimal dengan akurat
with col1:
    st.markdown(kpi_card("Total Production", f"{total_prod:,.2f}", "tonnes produced", "⛏", ("#2563eb", "#1e3a8a")), unsafe_allow_html=True)
with col2:
    st.markdown(kpi_card("Average Production", f"{avg_prod:,.2f}", "ton/day", "📊", ("#7c3aed", "#4c1d95")), unsafe_allow_html=True)
with col3:
    st.markdown(kpi_card("Total Trips", f"{total_trips:,.0f}", "haul trips", "🚛", ("#f97316", "#c2410c")), unsafe_allow_html=True)
with col4:
    st.markdown(kpi_card("Dominant Cluster", status, "operational status", "📌", ("#22c55e", "#15803d")), unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# =========================
# 3. TREND CHART & FILTER WAKTU
# =========================
col_chart_title, col_chart_filter = st.columns([2.5, 1.5])

with col_chart_title:
    st.markdown("<h3 style='margin-top: -10px;'>Production Trend</h3>", unsafe_allow_html=True)

with col_chart_filter:
    view_mode = st.segmented_control(
        "Time View:", 
        options=["Weekly", "Monthly", "Yearly"],
        default="Monthly",
        label_visibility="collapsed"
    )
    if not view_mode:
        view_mode = "Monthly"

def aggregate_data(data, mode):
    temp = data.copy()
    if mode == "Weekly":
        result = temp.resample("W", on="Date").sum(numeric_only=True).reset_index()
    elif mode == "Monthly":
        result = temp.resample("ME", on="Date").sum(numeric_only=True).reset_index()
    elif mode == "Yearly":
        result = temp.resample("YE", on="Date").sum(numeric_only=True).reset_index()
    return result

agg_df = aggregate_data(df, view_mode)

fig = px.line(agg_df, x="Date", y="Total Ton Hauler Actual", markers=True, title=None)
fig.update_traces(line_color="#2563eb", marker=dict(color="#1e3a8a", size=8))

if view_mode == "Monthly":
    fig.update_xaxes(tickmode="linear", dtick="M1", tickformat="%b %Y", tickangle=-45)
elif view_mode == "Yearly":
    fig.update_xaxes(tickmode="linear", dtick="M12", tickformat="%Y")

fig.update_layout(height=400, margin=dict(t=10, b=0, l=0, r=0), xaxis_title="")
st.plotly_chart(fig, use_container_width=True)

# =========================
# 4. RECENT HISTORY & QUICK INSIGHTS
# =========================
st.markdown("<br>", unsafe_allow_html=True)
col_hist, col_ins = st.columns([1.2, 1])

# --- KIRI: RECENT HISTORY ---
with col_hist:
    df_recent = df.sort_values("Date", ascending=False).head(5)
    
    table_rows = ""
    for _, row in df_recent.iterrows():
        date_str = row["Date"].strftime("%b %d")
        ton_str = f"{row['Total Ton Hauler Actual']:,.2f} t"
        trip_str = f"{row['Trip/day']:.0f}"
        
        cluster_val = row["Cluster"]
        if cluster_val == 2: # High
            status_text, bg_class, dot_class = "High", "bg-green", "dot-green"
        elif cluster_val == 1: # Anomaly / Normal
            status_text, bg_class, dot_class = "Normal", "bg-yellow", "dot-yellow"
        else: # Low
            status_text, bg_class, dot_class = "Low", "bg-red", "dot-red"
            
        # HTML rata kiri agar tidak dianggap code block
        table_rows += f"""<tr>
<td>{date_str}</td>
<td style="font-weight: 700;">{ton_str}</td>
<td>{trip_str}</td>
<td><div class="badge {bg_class}"><div class="dot {dot_class}"></div> {status_text}</div></td>
</tr>"""
        
    st.markdown(f"""
<div class="card-container">
<div class="section-title">Recent Production History</div>
<div class="section-subtitle">Last 5 days performance</div>
<table class="history-table">
<thead>
<tr>
<th>Date</th>
<th>Tonnage</th>
<th>Trips</th>
<th>Status</th>
</tr>
</thead>
<tbody>
{table_rows}
</tbody>
</table>
</div>
""", unsafe_allow_html=True)

# --- KANAN: QUICK INSIGHTS ---
with col_ins:
    st.markdown("""
<div class="card-container" style="background-color: transparent; border: none; box-shadow: none; padding: 0;">
<div class="section-title">Quick Insights</div>
<div class="section-subtitle">Performance recommendations</div>

<div class="insight-card insight-green">
<div class="icon-wrapper"></div>
<div class="insight-content">
<h4>Performance Excellent</h4>
<p>Production consistently high this week. Current operations performing optimally.</p>
</div>
</div>

<div class="insight-card insight-yellow">
<div class="icon-wrapper"></div>
<div class="insight-content">
<h4>Shift Balance Review</h4>
<p>Night shift 8% lower than morning. Consider crew allocation review.</p>
</div>
</div>

<div class="insight-card insight-blue">
<div class="icon-wrapper"></div>
<div class="insight-content">
<h4>Route Optimization</h4>
<p>Review hauling routes to reduce cycle time and increase daily trips.</p>
</div>
</div>
</div>
""", unsafe_allow_html=True)
