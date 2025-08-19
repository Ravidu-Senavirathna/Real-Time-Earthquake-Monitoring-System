"""Shared Folium map styling for the dashboard."""

import folium
from branca.element import Element


def create_dark_map():
    map_view = folium.Map(
        location=[0, 0],
        zoom_start=2,
        min_zoom=2,
        max_zoom=12,
        tiles="OpenStreetMap",
    )
    # Filter only background tiles; markers, heatmaps and attribution stay intact.
    map_view.get_root().header.add_child(Element("""
        <style>
        .leaflet-container { background: #151a22; }
        .leaflet-tile-pane {
            filter: invert(100%) hue-rotate(180deg)
                    brightness(85%) contrast(90%);
        }
        </style>
    """))
    return map_view
