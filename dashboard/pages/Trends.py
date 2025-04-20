# Trends Page

# This page focuses on analyzing trends in earthquake activity over time.
# It provides insights into patterns and changes in earthquake occurrences, magnitudes, and other relevant metrics.

'''
Trends in earthquake activity over time
- Monthly/Yearly earthquake counts
- Average magnitude trends
- Frequency of strong earthquakes
- Tsunami event trends
- Regional trends in earthquake activity
'''


import streamlit as st
import pandas as pd
import plotly.express as px
from dashboard.utils import load_data

st.subheader("📈 Earthquake Trends")

df = load_data()
df["event_time"] = pd.to_datetime(df["event_time"])

# Daily counts
daily = df.groupby(df["event_time"].dt.date).size().reset_index()
daily.columns = ["date", "count"]

fig = px.line(daily, x="date", y="count", title="Daily Earthquakes")
st.plotly_chart(fig, width='stretch')

# Magnitude distribution
fig2 = px.histogram(df, x="magnitude", nbins=40, title="Magnitude Distribution")
st.plotly_chart(fig2, width='stretch')