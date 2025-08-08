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

def get_color(mag):

    if mag >= 7:
        return "red"

    elif mag >= 5:
        return "orange"

    elif mag >= 3:
        return "yellow"

    return "blue"

from folium import CircleMarker, Popup, folium
from streamlit_folium import st_folium

import streamlit as st
from dashboard.utils import load_data
import plotly.express as px


df = load_data()

# Side Bar
top_n = st.sidebar.slider("Top N", 10, 200, 50)
search = st.sidebar.text_input("Search Location")


# Filters
top = df.sort_values("magnitude", ascending=False).head(top_n)
filtered = top

if search:
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

map = folium.Map(
    location=[0, 0],
    zoom_start=2,
    min_zoom = 2,
    max_zoom = 12,
    tiles="CartoDB dark_matter"
)

for _, row in filtered.iterrows():

    CircleMarker(
        location=[row["latitude"], row["longitude"]],
        radius=max(row["magnitude"] * 1.5, 5),
        color=get_color(row["magnitude"]),
        fill=True,
        fill_color=get_color(row["magnitude"]),
        fill_opacity=0.8,
        weight=1,
        popup=Popup(
            f"""
            <b>{row['place']}</b><br>
            Date: {row['event_time']}<br>
            Magnitude: {row['magnitude']}<br>
            Depth: {row['depth']} km
            """,
            max_width=250
        )
    ).add_to(map)


st_folium(map, width="stretch", height=700)