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


from folium import CircleMarker, Popup, folium
from streamlit_folium import st_folium

import streamlit as st
from dashboard.utils import load_data
import utils

Global_Map = folium.Map(location=[0, 0], 
                 zoom_start=2,
                 min_zoom = 2,
                 max_zoom = 12,
                 tiles='CartoDB dark_matter')

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

st.dataframe(filtered[[
    "place",
    "event_date",
    "event_clock",
    "magnitude",
    "depth",
    "tsunami"
]])



st.subheader("Strongest Events Map")


for _, row in filtered.iterrows():

    CircleMarker(
        location=[row["latitude"], row["longitude"]],
        radius=max(row["magnitude"] * 1.5, 5),
        color=utils.get_color(row["magnitude"]),
        fill=True,
        fill_color=utils.get_color(row["magnitude"]),
        fill_opacity=0.8,
        weight=1,
        popup=Popup(
            f"""
            <b>{row['place']}</b><br>
            Date: {row['event_date']}<br>
            Time: {row['event_clock']}<br>
            Magnitude: {row['magnitude']}<br>
            Depth: {row['depth']} km
            """,
            max_width=250
        )
    ).add_to(Global_Map)


st_folium(Global_Map, width="stretch", height=700)