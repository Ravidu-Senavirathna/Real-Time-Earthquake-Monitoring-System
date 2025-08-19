from dashboard.map_style import create_dark_map
# Top Earthquakes Page

# This page focuses on displaying the most significant earthquakes that have occurred recently.
# It provides detailed information about the strongest earthquakes, including their magnitude, location, and time of occurrence.


from folium import CircleMarker, Popup, folium
from streamlit_folium import st_folium

import streamlit as st
from dashboard.utils import get_top_earthquakes, get_color


Global_Map = create_dark_map()



# Side Bar
top_n = st.sidebar.slider("Top N", 10, 200, 50)
search = st.sidebar.text_input("Search Location")


# Filters
top = get_top_earthquakes(top_n)
filtered = top

if search:
    filtered = top[
        top["place"]
        .str.contains(
            search,
            case=False,
            na=False,
            regex=False
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
        color=get_color(row["magnitude"]),
        fill=True,
        fill_color=get_color(row["magnitude"]),
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


st_folium(Global_Map, use_container_width=True, height=700, returned_objects=[])