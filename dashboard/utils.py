import folium
import pandas as pd
from database.db import engine
import streamlit as st

@st.cache_data(ttl=300)


def load_data():
    query = """
    SELECT * 
    FROM earthquakes
    """
    df = pd.read_sql(query, engine)

    df["event_time"] = pd.to_datetime(df["event_time"], utc=True)

    df["event_date"] = df["event_time"].dt.date
    df["event_clock"] = df["event_time"].dt.strftime("%H:%M:%S")

    return df


def get_top_earthquakes():
    pass


def get_tsunami_events():
    pass


def get_monthly_stats():
    pass


def get_recent_events():
    pass


def get_color(mag):

    if mag >= 7:
        return "red"

    elif mag >= 5:
        return "orange"

    elif mag >= 2.5:
        return "yellow"

    return "blue"
