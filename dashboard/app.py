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


# Display key metrics
st.title("🌍 Earthquake Monitoring System")

col1, col2, col3 = st.columns(3)

col1.metric("Total Earthquakes", len(df))
col2.metric("Max Magnitude", df["magnitude"].max())
col3.metric("Avg Magnitude", round(df["magnitude"].mean(), 2))

# Magnitude distribution
st.subheader("Magnitude Distribution")

fig = px.histogram(df, x="magnitude", nbins=40)
st.plotly_chart(fig, width='stretch')