import streamlit as st
import pandas as pd
import pickle
import plotly.express as px


st.set_page_config(
    page_title="Clustering Analysis",
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


    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
    )


    df = df.dropna(
        subset=["Date"]
    )


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
# MODEL
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



fitur = [

    "Actual Rain Hours",
    "Slippery Hours",
    "Rest Time",
    "Trip/day",
    "Total Ton Hauler Actual"

]



X = df[fitur]


X_scaled = scaler.transform(
    X
)



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



df["Performance"] = (
    df["Cluster"]
    .apply(label_cluster)
)



warna = {

    "Low":"#ef4444",

    "Normal":"#f59e0b",

    "High":"#10b981"

}



# =========================
# HEADER
# =========================

st.title(
    "📊 K-Means Cluster Performance"
)


st.markdown("---")



# =========================
# JUMLAH CLUSTER
# =========================


col1,col2 = st.columns(2)



with col1:


    jumlah = (
        df["Performance"]
        .value_counts()
        .reset_index()
    )


    jumlah.columns = [
        "Cluster",
        "Jumlah Hari"
    ]


    fig = px.bar(

        jumlah,

        x="Cluster",

        y="Jumlah Hari",

        color="Cluster",

        color_discrete_map=warna,

        text="Jumlah Hari"

    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )



with col2:


    fig2 = px.scatter(

        df,

        x="Total Ton Hauler Actual",

        y="Trip/day",

        color="Performance",

        color_discrete_map=warna,

        hover_data=[
            "Date",
            "Actual Rain Hours",
            "Slippery Hours"
        ]

    )


    st.plotly_chart(
        fig2,
        use_container_width=True
    )



# =========================
# PROFIL CLUSTER
# =========================


st.subheader(
    "Profil Rata-rata Cluster"
)


profil = (

    df.groupby("Performance")[fitur]
    .mean()
    .round(2)

)



st.dataframe(
    profil,
    use_container_width=True
)



st.subheader(
    "Detail Data Cluster"
)


st.dataframe(
    df[
        [
        "Date",
        "Total Ton Hauler Actual",
        "Trip/day",
        "Performance"
        ]
    ],
    use_container_width=True
)
