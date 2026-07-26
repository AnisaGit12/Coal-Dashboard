import streamlit as st
import pandas as pd
import pickle
import plotly.express as px


st.set_page_config(
    page_title="Coal Hauling Dashboard",
    layout="wide"
)


# =========================
# LOAD DATA
# =========================

@st.cache_data
def load_data():

    df = pd.read_excel(
        "hasil_cluster_final.xlsx"
    )


    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
    )


    # tanggal
    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
    )


    # hapus baris kosong tanggal
    df = df.dropna(
        subset=["Date"]
    )


    # angka
    numeric = [
        "Actual Rain Hours",
        "Slippery Hours",
        "Rest Time",
        "Trip/day",
        "Total Ton Hauler Actual"
    ]


    for col in numeric:

        df[col] = (
            df[col]
            .astype(str)
            .str.replace(",",".")
        )

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )


    df = df.fillna(0)


    return df



df = load_data()



# =========================
# LOAD MODEL
# =========================

with open(
    "scaler.pkl",
    "rb"
) as f:

    scaler = pickle.load(f)



with open(
    "kmeans_model.pkl",
    "rb"
) as f:

    kmeans = pickle.load(f)



# =========================
# FITUR SAMA DENGAN COLAB
# =========================

fitur = [

    "Actual Rain Hours",
    "Slippery Hours",
    "Rest Time",
    "Trip/day",
    "Total Ton Hauler Actual"

]


X = df[fitur]



# scaling

X_scaled = scaler.transform(
    X
)



# prediksi

df["Cluster"] = kmeans.predict(
    X_scaled
)



# =========================
# LABEL
# =========================

def label_cluster(x):

    if x == 0:
        return "Low"

    elif x == 1:
        return "Normal"

    else:
        return "High"



df["Status"] = (
    df["Cluster"]
    .apply(label_cluster)
)



# =========================
# HEADER
# =========================

st.title(
    "⛏ Coal Hauling Dashboard"
)


# =========================
# KPI
# =========================


c1,c2,c3 = st.columns(3)


with c1:

    st.metric(
        "Total Production",
        f"{df['Total Ton Hauler Actual'].sum():,.2f} ton"
    )


with c2:

    st.metric(
        "Average Trip",
        f"{df['Trip/day'].mean():.2f}"
    )


with c3:

    st.metric(
        "Dominant Cluster",
        df["Status"].value_counts().idxmax()
    )



# =========================
# PRODUCTION TREND
# =========================

st.subheader("Production Trend")


view = st.radio(
    "Tampilan:",
    [
        "Tahunan",
        "Bulanan",
        "Mingguan"
    ],
    horizontal=True
)



df_trend = df.copy()


if view == "Tahunan":

    trend = (
        df_trend
        .groupby(
            df_trend["Date"].dt.year
        )["Total Ton Hauler Actual"]
        .sum()
        .reset_index()
    )

    trend.columns = [
        "Periode",
        "Production"
    ]

    trend["Periode"] = trend["Periode"].astype(str)



elif view == "Bulanan":

    trend = (
        df_trend
        .groupby(
            df_trend["Date"].dt.to_period("M")
        )["Total Ton Hauler Actual"]
        .sum()
        .reset_index()
    )

    trend["Periode"] = (
        trend["Date"]
        .astype(str)
    )

    trend = trend[
        [
        "Periode",
        "Total Ton Hauler Actual"
        ]
    ]

    trend.columns=[
        "Periode",
        "Production"
    ]



else:


    trend = (
        df_trend
        .groupby(
            df_trend["Date"]
            .dt.to_period("W")
        )["Total Ton Hauler Actual"]
        .sum()
        .reset_index()
    )


    trend["Periode"] = (
        trend["Date"]
        .astype(str)
    )


    trend = trend[
        [
        "Periode",
        "Total Ton Hauler Actual"
        ]
    ]


    trend.columns=[
        "Periode",
        "Production"
    ]




fig = px.line(

    trend,

    x="Periode",

    y="Production",

    markers=True,

    line_shape="spline"

)


fig.update_traces(
    line_color="#2563eb",
    marker_size=8
)


fig.update_layout(
    height=400,
    plot_bgcolor="white"
)



st.plotly_chart(
    fig,
    use_container_width=True
)

# =========================
# RECENT PRODUCTION
# =========================


st.markdown("---")

st.subheader(
    "Recent Production"
)



recent = (

    df.sort_values(
        "Date",
        ascending=False
    )
    .head(10)

)


recent_display = recent[
    [
    "Date",
    "Total Ton Hauler Actual",
    "Cluster"
    ]
].copy()



recent_display["Date"] = (
    recent_display["Date"]
    .dt.strftime("%d %B %Y")
)



st.dataframe(

    recent_display,

    use_container_width=True,

    hide_index=True

)
