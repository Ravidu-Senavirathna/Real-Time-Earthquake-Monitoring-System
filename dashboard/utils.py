import pandas as pd
from sqlalchemy import text
from database.db import engine
import streamlit as st


def format_events(df):
    df["event_time"] = pd.to_datetime(df["event_time"], utc=True)
    df["event_date"] = df["event_time"].dt.date
    df["event_clock"] = df["event_time"].dt.strftime("%H:%M:%S")
    return df


@st.cache_data(ttl=300, max_entries=64)
def load_map_data(days, min_mag, only_tsunami, limit=2000):
    query = text("""
        SELECT place, event_time, magnitude, depth, tsunami, latitude, longitude
        FROM earthquakes
        WHERE (:days IS NULL OR event_time >= CURRENT_TIMESTAMP - (:days * INTERVAL '1 day'))
          AND magnitude >= :min_mag
          AND (:only_tsunami = FALSE OR tsunami = 1)
          AND latitude IS NOT NULL AND longitude IS NOT NULL
        ORDER BY event_time DESC
        LIMIT :limit
    """)
    return format_events(pd.read_sql(query, engine, params={
        "days": days, "min_mag": min_mag,
        "only_tsunami": only_tsunami, "limit": limit,
    }))


@st.cache_data(ttl=300)
def get_overview_stats():
    return pd.read_sql(text("""
        SELECT COUNT(*) AS total, MAX(magnitude) AS max_magnitude,
               AVG(magnitude) AS avg_magnitude,
               COUNT(*) FILTER (WHERE tsunami = 1) AS tsunami_count,
               COUNT(*) FILTER (WHERE status = 'reviewed') AS reviewed
        FROM earthquakes
    """), engine).iloc[0].to_dict()


@st.cache_data(ttl=300, max_entries=32)
def get_top_earthquakes(limit=50):
    return format_events(pd.read_sql(text("""
        SELECT place, event_time, magnitude, depth, tsunami, latitude, longitude
        FROM earthquakes
        ORDER BY magnitude DESC NULLS LAST, event_time DESC
        LIMIT :limit
    """), engine, params={"limit": limit}))


@st.cache_data(ttl=300)
def get_recent_events():
    return format_events(pd.read_sql(text("""
        SELECT place, event_time, magnitude, depth, tsunami
        FROM earthquakes ORDER BY event_time DESC NULLS LAST LIMIT 10
    """), engine))


@st.cache_data(ttl=300)
def get_trend_data():
    daily = pd.read_sql(text("""
        SELECT (event_time AT TIME ZONE 'UTC')::date AS date, COUNT(*) AS count
        FROM earthquakes WHERE event_time IS NOT NULL
        GROUP BY 1 ORDER BY 1
    """), engine)
    magnitudes = pd.read_sql(text("""
        SELECT FLOOR(magnitude::numeric / 0.25) * 0.25 AS magnitude,
               COUNT(*) AS count
        FROM earthquakes WHERE magnitude IS NOT NULL
        GROUP BY 1 ORDER BY 1
    """), engine)
    return daily, magnitudes


def get_color(mag):
    if mag >= 7:
        return "red"
    if mag >= 5:
        return "orange"
    if mag >= 2.5:
        return "yellow"
    return "blue"
