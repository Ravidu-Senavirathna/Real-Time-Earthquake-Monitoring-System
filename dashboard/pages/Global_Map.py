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
from dashboard.utils import load_data

import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
import utils



Global_Map = folium.Map(location=[0, 0], 
                 zoom_start=2,
                 min_zoom = 2,
                 max_zoom = 12,
                 tiles='CartoDB dark_matter')

df = load_data()



# Side Bar
min_mag = st.sidebar.slider("Magnitude", 0.0, 10.0, 2.5)
only_tsunami = st.sidebar.checkbox("Tsunami Events Only")
show_heatmap = st.sidebar.checkbox("Show Heatmap", value=False)


# Title 
st.subheader("🌍 Global Earthquake Map")



filtered = df[df["magnitude"] >= min_mag]

if only_tsunami:
    filtered = filtered[filtered["tsunami"] == 1]



if show_heatmap:

    heat_layer = folium.FeatureGroup(name="Heatmap")
    heat_layer.add_to(Global_Map)

    heat_data = filtered[["latitude", "longitude", "magnitude"]].values.tolist()

    HeatMap(
        heat_data,
        radius=13,
        blur=5
        ).add_to(heat_layer)
    

else:

    marker_layer = folium.FeatureGroup(name="Earthquake Markers")
    marker_layer.add_to(Global_Map)

    for _, row in filtered.iterrows():

        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=max(row["magnitude"] * 2, 3),
            color=utils.get_color(row["magnitude"]),
            fill=True,
            popup= folium.Popup(f"""
            <b>{row['place']}</b><br>
            Date: {row['event_date']}<br>
            Time: {row['event_clock']}<br>
            Magnitude: {row['magnitude']}<br>
            Depth: {row['depth']}
            """,
            max_width=250
            )
        ).add_to(marker_layer)



st_folium(Global_Map, width='stretch', height=700)