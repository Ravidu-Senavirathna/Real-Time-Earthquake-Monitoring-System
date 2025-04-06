import streamlit as st
import pandas as pd
import plotly.express as px
from database.db import engine

st.title("🌍 Earthquake Analytics Dashboard")

# Load data
@st.cache_data
def load_data():
    df = pd.read_sql("SELECT * FROM earthquakes", engine)
    return df

df = load_data()

# KPIs
st.subheader("Key Metrics")

col1, col2, col3 = st.columns(3)

col1.metric("Total Earthquakes", len(df))
col2.metric("Max Magnitude", df["magnitude"].max())
col3.metric("Avg Magnitude", round(df["magnitude"].mean(), 2))

# Magnitude distribution
st.subheader("Magnitude Distribution")

fig = px.histogram(df, x="magnitude", nbins=30)
st.plotly_chart(fig, width='stretch')