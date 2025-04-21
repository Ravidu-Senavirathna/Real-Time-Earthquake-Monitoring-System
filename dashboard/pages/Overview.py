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
import pandas as pd

st.subheader("🌍 Overview")

df = load_data()

strongest = df.loc[df["magnitude"].idxmax()]
tsunami_count = df[df["tsunami"] == 1].shape[0]
reviewed = df[df["status"] == "reviewed"].shape[0]

# KPIs
col1, col2, col3 = st.columns(3)

col1.metric("Total Earthquakes", len(df))
col2.metric("Max Magnitude", round(df["magnitude"].max(), 2))
col3.metric("Avg Magnitude", round(df["magnitude"].mean(), 2))

coll1, coll2, coll3 = st.columns(3)

coll1.metric("Strongest Event", strongest["magnitude"])
coll2.metric("Tsunami Events", tsunami_count)
coll3.metric("Total Reviewed", reviewed)

st.subheader("Latest Earthquakes")
st.dataframe(df.sort_values("event_time", ascending=False).head(10))