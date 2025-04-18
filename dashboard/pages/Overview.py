# Overview page for the dashboard

# Mainly used to display key metrics and summaries for the user. 
# This page provides a quick glance at the most important information

'''
Total Earthquakes
Average Magnitude
Maximum Magnitude
Strongest Earthquake Location
Tsunami Events
'''

import streamlit as st
from dashboard.utils import load_data

st.subheader("🌍 Overview")

df = load_data()

# KPIs
col1, col2, col3 = st.columns(3)

col1.metric("Total Earthquakes", len(df))
col2.metric("Max Magnitude", round(df["magnitude"].max(), 2))
col3.metric("Avg Magnitude", round(df["magnitude"].mean(), 2))

st.subheader("Latest Earthquakes")
st.dataframe(df.sort_values("event_time", ascending=False).head(10))