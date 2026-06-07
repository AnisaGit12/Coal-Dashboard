import streamlit as st

st.set_page_config(
    page_title="Coal Hauling Dashboard",
    layout="wide"
)

with st.sidebar:
    st.title("Coal Hauling")
    st.markdown("---")
    st.caption("K-Means Operational Intelligence")

home = st.Page("pages/home.py", title="Dashboard", default=True)
prod = st.Page("pages/production.py", title="Production")
clus = st.Page("pages/clustering.py", title="Cluster Analysis")
ins  = st.Page("pages/insight.py", title="Insight and Report")

pg = st.navigation({
    "EXECUTIVE": [home],
    "OPERATIONS": [prod],
    "ANALYTICS": [clus, ins]
})

pg.run()
