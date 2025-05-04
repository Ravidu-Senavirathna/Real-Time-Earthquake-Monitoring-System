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


df = load_data()

# Side Bar
top_n = st.sidebar.slider("Top N", 10, 200, 50)
search = st.sidebar.text_input("Search Location")


# Filters
top = df.sort_values("magnitude", ascending=False).head(top_n)

filtered = top[
    top["place"]
    .str.contains(
        search,
        case=False,
        na=False
    )
]


# Titles and Diagrams
st.subheader("🏆 Strongest Earthquakes")

st.dataframe(filtered)



st.subheader("Strongest Events Map")

fig = px.scatter_geo(
    filtered,
    lat="latitude",
    lon="longitude",
    size="magnitude",
    color="magnitude",
    hover_name="place",
    projection="natural earth"
)

st.plotly_chart(fig, width='stretch')