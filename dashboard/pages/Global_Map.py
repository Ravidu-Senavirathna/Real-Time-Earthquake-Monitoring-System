from dashboard.map_style import create_dark_map
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
from dashboard.utils import load_map_data, get_color

import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap




Global_Map = create_dark_map()





# Side Bar
days = st.sidebar.selectbox(
    "Date range", [1, 7, 30, 90, 365, None], index=1,
    format_func=lambda value: "All dates" if value is None else f"Past {value} days",
)
min_mag = st.sidebar.slider("Magnitude", 0.0, 10.0, 2.5)
only_tsunami = st.sidebar.checkbox("Tsunami Events Only")
show_heatmap = st.sidebar.checkbox("Show Heatmap", value=False)


# Title 
st.subheader("🌍 Global Earthquake Map")



filtered = load_map_data(days, min_mag, only_tsunami)
st.caption(f"Showing {len(filtered):,} events (maximum 2,000 most recent matches). Times are UTC.")
if filtered.empty:
    st.info("No events match these filters. Try All dates, a lower magnitude, or turning off Tsunami Events Only.")

if show_heatmap and not filtered.empty:

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
            color=get_color(row["magnitude"]),
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



st_folium(Global_Map, use_container_width=True, height=700, returned_objects=[])