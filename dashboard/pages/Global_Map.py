# World map of earthquakes

# This page displays a world map of all recorded earthquakes, allowing users to visualize their locations and magnitudes.
# It provides an interactive map view for exploring earthquake data across different regions.

'''
World map of earthquakes
- Location
- Magnitude
- Time of occurrence
'''


def get_color(mag):

    if mag >= 7:
        return "red"

    elif mag >= 5:
        return "orange"

    elif mag >= 3:
        return "yellow"

    return "blue"




import streamlit as st
from dashboard.utils import load_data

import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster, HeatMap

# Side Bar
min_mag = st.sidebar.slider("Magnitude", 0.0, 10.0, 2.5)
only_tsunami = st.sidebar.checkbox("Tsunami Events Only")


# Title 
st.subheader("🌍 Global Earthquake Map")

df = load_data()
map = folium.Map(location=[0, 0], zoom_start=2)


filtered = df[df["magnitude"] >= min_mag]

if only_tsunami:
    filtered = filtered[filtered["tsunami"] == 1]


heat_data = filtered[
    ["latitude", "longitude"]
].values.tolist()


HeatMap(heat_data).add_to(map)
cluster = MarkerCluster().add_to(map)


for _, row in filtered.iterrows():

    folium.CircleMarker(
        location=[row["latitude"], row["longitude"]],
        radius=max(row["magnitude"] * 2, 3),
        color=get_color(row["magnitude"]),
        fill=True,
        popup=f"""
        Magnitude: {row['magnitude']},
        Depth: {row['depth']}
         """
    ).add_to(cluster)

st_folium(map, width='stretch', height=700)