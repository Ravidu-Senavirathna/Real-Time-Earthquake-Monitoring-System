import streamlit as st
import pandas as pd
import plotly.express as px
from database.db import engine



st.set_page_config(page_title="Earthquake Monitor", layout="wide")


# Title
st.title("Real-Time Earthquake Monitoring Dashboard")
@st.cache_data
def load_data():
    return pd.read_sql("SELECT * FROM earthquakes", engine)

df = load_data()



# Sidebar filters
st.sidebar.header("Filters")

min_mag = st.sidebar.slider("Minimum Magnitude", 0.0, 10.0, 3.0)
filtered = df[df["magnitude"] >= min_mag]



# Display key metrics
st.title("🌍 Earthquake Monitoring System")

col1, col2, col3 = st.columns(3)

col1.metric("Total Earthquakes", len(filtered))
col2.metric("Max Magnitude", filtered["magnitude"].max())
col3.metric("Avg Magnitude", round(filtered["magnitude"].mean(), 2))

# Magnitude distribution
st.subheader("Magnitude Distribution")

fig = px.histogram(filtered, x="magnitude", nbins=40)
st.plotly_chart(fig, width='stretch')


# World map of earthquakes
st.subheader("Global Earthquake Map")

fig_map = px.scatter_geo(
    filtered,
    lat="latitude",
    lon="longitude",
    color="magnitude",
    size="magnitude",
    hover_name="place",
    projection="natural earth"
)

st.plotly_chart(fig_map, width='stretch')