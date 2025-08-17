import streamlit as st
import plotly.express as px
from dashboard.utils import get_trend_data

st.subheader("Earthquake Trends")
daily, magnitudes = get_trend_data()
fig = px.line(daily, x="date", y="count", title="Daily Earthquakes (UTC)")
st.plotly_chart(fig, width="stretch")
fig2 = px.bar(magnitudes, x="magnitude", y="count", title="Magnitude Distribution (0.25 bins)")
st.plotly_chart(fig2, width="stretch")
