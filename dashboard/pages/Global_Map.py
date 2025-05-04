# World map of earthquakes

# This page displays a world map of all recorded earthquakes, allowing users to visualize their locations and magnitudes.
# It provides an interactive map view for exploring earthquake data across different regions.

'''
World map of earthquakes
- Location
- Magnitude
- Time of occurrence
'''


import streamlit as st
import plotly.express as px
from dashboard.utils import load_data

st.subheader("🌍 Global Earthquake Map")

df = load_data()


# Side Bar
min_mag = st.sidebar.slider("Magnitude", 0.0, 10.0, 2.5)
only_tsunami = st.sidebar.checkbox("Tsunami Events Only")


filtered = df[df["magnitude"] >= min_mag]

if only_tsunami:
    filtered = filtered[filtered["tsunami"] == 1]

fig = px.scatter_geo(
    filtered,
    lat="latitude",
    lon="longitude",
    color="magnitude",
    size="magnitude",
    hover_name="place",
    projection="natural earth"
)

st.plotly_chart(fig, width='stretch')