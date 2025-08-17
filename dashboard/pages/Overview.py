import streamlit as st
from dashboard.utils import get_overview_stats, get_recent_events

st.subheader("Overview")
stats = get_overview_stats()
if not stats["total"]:
    st.info("No earthquakes available. Run ingestion to populate the database.")
    st.stop()

col1, col2, col3 = st.columns(3)
col1.metric("Total Earthquakes", int(stats["total"]))
col2.metric("Max Magnitude", round(stats["max_magnitude"], 2) if stats["max_magnitude"] is not None else "N/A")
col3.metric("Avg Magnitude", round(stats["avg_magnitude"], 2) if stats["avg_magnitude"] is not None else "N/A")
coll1, coll2, coll3 = st.columns(3)
coll1.metric("Strongest Event", stats["max_magnitude"])
coll2.metric("Tsunami Events", int(stats["tsunami_count"]))
coll3.metric("Total Reviewed", int(stats["reviewed"]))

st.subheader("Latest Earthquakes")
st.dataframe(get_recent_events()[[
    "place", "event_date", "event_clock", "magnitude", "depth", "tsunami"
]])
