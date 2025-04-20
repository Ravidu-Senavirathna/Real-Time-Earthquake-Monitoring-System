# Top Earthquakes Page

# This page focuses on displaying the most significant earthquakes that have occurred recently.
# It provides detailed information about the strongest earthquakes, including their magnitude, location, and time of occurrence.

'''
Ranking of the top earthquakes based on magnitude
Details for each earthquake:
- Magnitude
- Location
- Time of occurrence
- Depth
- Tsunami potential
'''


import streamlit as st
from dashboard.utils import load_data
import plotly.express as px

st.subheader("🏆 Strongest Earthquakes")

df = load_data()

top_n = st.slider("Top N", 10, 200, 50)

top = df.sort_values("magnitude", ascending=False).head(top_n)

st.dataframe(top)

st.subheader("Strongest Events Map")


fig = px.scatter_geo(
    top,
    lat="latitude",
    lon="longitude",
    size="magnitude",
    color="magnitude",
    hover_name="place",
    projection="natural earth"
)

st.plotly_chart(fig, width='stretch')