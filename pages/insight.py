import streamlit as st
import pandas as pd

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Smart Insights & Report", layout="wide")

# =========================
# CSS STYLING
# =========================
st.markdown("""
<style>
.card-container { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 25px; }
.metric-card { background: white; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
.metric-card:hover { transform: translateY(-5px); border-color: #3b82f6; transition: 0.3s; }
.label { font-size: 13px; color: #64748b; margin-bottom: 8px; }
.value { font-size: 22px; font-weight: 700; color: #0f172a; margin-bottom: 5px; }
.delta { font-size: 12px; font-weight: 600; }
.spk-card { background: #f8fafc; border-left: 4px solid #8b5cf6; padding: 20px; border-radius: 8px; margin-bottom: 15px; height: 100%; }
</style>
""", unsafe_allow_html=True)

# =========================
# LOAD DATA (FIX NAMEERROR)
# =========================
@st.cache_data
def load_data():
    # Pastikan path file benar dari root folder
    df = pd.read_excel("hasil_cluster_final_fix.xlsx")
    df.columns = df.columns.str.strip()
    df["Date"] = pd.to_datetime(df["Date"], format="mixed", dayfirst=True, errors="coerce")
    df["Total Ton Hauler Actual"] = pd.to_numeric(df["Total Ton Hauler Actual"].astype(str).str.replace(',', '.'), errors="coerce").fillna(0)
    df["Trip/day"] = pd.to_numeric(df["Trip/day"], errors="coerce").fillna(0)
    df["Category"] = df["Cluster"].apply(lambda x: "High" if x == 2 else "Normal" if x == 1 else "Low")
    return df.sort_values("Date", ascending=False)

df = load_data()

# =========================
# 1. PREDICTIVE ANALYTICS
# =========================
st.markdown("## 🧠 Smart Insights")
st.markdown("### 🎯 Predictive Analytics")

avg_ton = df["Total Ton Hauler Actual"].mean()
cards = [
    ("Tomorrow Production", f"{avg_ton*1.03:,.0f} tonnes", "+3.2%", "positive"),
    ("End of Week Total", f"{avg_ton*7*1.02:,.0f} tonnes", "+2.1%", "positive"),
    ("Monthly Target", "105%", "On track", "positive"),
    ("Equipment Util.", "87%", "-2.5%", "negative")
]

html_cards = '<div class="card-container">'
for label, value, delta, d_class in cards:
    html_cards += f'''<div class="metric-card"><div class="label">{label}</div><div class="value">{value}</div><div class="delta {'positive' if d_class=='positive' else 'negative'}">{delta}</div></div>'''
html_cards += '</div>'
st.markdown(html_cards, unsafe_allow_html=True)

# =========================
# 2. SPK INSIGHTS
# =========================
persen_low = (len(df[df["Category"] == "Low"]) / len(df)) * 100
col_l, col_r = st.columns(2)
with col_l:
    st.markdown("### 🔍 Analisis Akar Masalah")
    st.markdown(f"""<div class="spk-card"><p>Tingkat kinerja 'Low': <b>{persen_low:.1f}%</b>.</p><p><b>Diagnosa:</b> { "Produktivitas terhambat faktor eksternal" if persen_low > 20 else "Kinerja operasional normal" }</p></div>""", unsafe_allow_html=True)
with col_r:
    st.markdown("### 💡 Saran Keputusan")
    st.markdown(f"""<div class="spk-card" style="border-left-color: #10b981;"><p><b>Rekomendasi Manajerial:</b></p><p>{ "Evaluasi rute & maintenance unit." if persen_low > 20 else "Pertahankan protokol saat ini." }</p></div>""", unsafe_allow_html=True)

# =========================
# 3. FILTER & REPORT
# =========================
st.markdown("<br>### 📊 Detailed Daily Report", unsafe_allow_html=True)
col_f1, col_f2, col_f3 = st.columns([1, 1, 2])
start_date = col_f1.date_input("Start Date", value=df["Date"].min())
end_date = col_f2.date_input("End Date", value=df["Date"].max())

mask = (df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)
df_f = df.loc[mask].copy()

df_display = df_f.copy()
df_display["Date"] = df_display["Date"].dt.strftime("%d-%b-%y")
df_display = df_display.rename(columns={"Total Ton Hauler Actual": "Total Produksi (Ton)", "Trip/day": "Jumlah Trip"})
st.dataframe(df_display[["Date", "Total Produksi (Ton)", "Jumlah Trip", "Category"]], use_container_width=True, hide_index=True)

csv = df_display.to_csv(index=False).encode('utf-8')
st.download_button("📥 Download Laporan (CSV)", data=csv, file_name='report.csv', type="primary")
