import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


st.set_page_config(
    page_title="Production Analysis",
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

    df.columns = df.columns.str.strip()


    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
    )


    df = df.dropna(
        subset=["Date"]
    )


    numeric_cols = [
        "Actual Rain Hours",
        "Slippery Hours",
        "Trip/day",
        "Total Ton Hauler Actual",
        "Cluster"
    ]


    for col in numeric_cols:

        if col in df.columns:

            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )


    df = df.fillna(0)


    return df



df = load_data()



# =========================
# HEADER
# =========================

st.title(
    "Production Analysis"
)

st.caption(
    "Production performance and weather impact analysis"
)



# =========================
# KPI
# =========================

col1, col2, col3 = st.columns(3)


with col1:

    total_prod = df["Total Ton Hauler Actual"].sum()

    st.metric(
        "Total Production",
        f"{total_prod:,.2f} Ton"
    )


with col2:

    avg_trip = df["Trip/day"].mean()

    st.metric(
        "Average Trip/day",
        f"{avg_trip:.1f}"
    )


with col3:

    rain = df["Actual Rain Hours"].sum()

    st.metric(
        "Total Rain Hours",
        f"{rain:.1f} Hours"
    )



st.divider()



# =========================
# PRODUCTION TREND
# =========================

st.subheader(
    "Production Trend"
)


trend = (

    df.groupby("Date")
    ["Total Ton Hauler Actual"]
    .sum()
    .reset_index()

)



fig1 = go.Figure()


fig1.add_trace(

    go.Scatter(

        x=trend["Date"],

        y=trend["Total Ton Hauler Actual"],

        mode="lines",

        line=dict(
            color="#2563eb",
            width=3
        ),

        fill="tozeroy",

        fillcolor="rgba(37,99,235,0.2)",

        name="Production"

    )

)



fig1.update_layout(

    template="plotly_white",

    height=400,

    hovermode="x unified",

    margin=dict(
        l=0,
        r=0,
        t=30,
        b=0
    )

)



st.plotly_chart(

    fig1,

    use_container_width=True,

    key="production_trend_chart"

)



# =========================
# WEATHER IMPACT
# =========================

st.subheader(
    "Weather Impact"
)



weather = (

    df.groupby("Date")
    .agg({

        "Actual Rain Hours":"sum",

        "Slippery Hours":"sum"

    })

    .reset_index()

)



fig2 = go.Figure()



fig2.add_trace(

    go.Bar(

        x=weather["Date"],

        y=weather["Actual Rain Hours"],

        name="Rain Hours",

        marker_color="#8b5cf6"

    )

)



fig2.add_trace(

    go.Bar(

        x=weather["Date"],

        y=weather["Slippery Hours"],

        name="Slippery Hours",

        marker_color="#f97316"

    )

)



fig2.update_layout(

    template="plotly_white",

    height=400,

    barmode="group",

    hovermode="x unified",

    margin=dict(
        l=0,
        r=0,
        t=30,
        b=0
    )

)



st.plotly_chart(

    fig2,

    use_container_width=True,

    key="weather_impact_chart"

)



# =========================
# CLUSTER PERFORMANCE
# =========================

st.subheader(
    "Cluster Performance"
)



cluster = (

    df.groupby("Cluster")

    .agg({

        "Total Ton Hauler Actual":"mean",

        "Trip/day":"mean",

        "Actual Rain Hours":"mean"

    })

    .round(2)

    .reset_index()

)



cluster.columns = [

    "Cluster",

    "Avg Production",

    "Avg Trip",

    "Avg Rain Hours"

]



st.dataframe(

    cluster,

    use_container_width=True

)



# =========================
# RECENT DATA
# =========================

st.subheader(
    "Recent Production Data"
)


st.dataframe(

    df.sort_values(
        "Date",
        ascending=False
    )
    [
        [
            "Date",
            "Total Ton Hauler Actual",
            "Trip/day",
            "Actual Rain Hours",
            "Cluster"
        ]
    ]
    .head(20),

    use_container_width=True

)
