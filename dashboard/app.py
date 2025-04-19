import streamlit as st

st.title("Earthquake Monitoring System")


# Define your page objects
page_1 = st.Page("pages/Overview.py", title="Overview")
page_2 = st.Page("pages/Global_Map.py", title="Global Map")
page_3 = st.Page("pages/Trends.py", title="Trends")
page_4 = st.Page("pages/Top_Earthquakes.py", title="Analysis")

# Pass pages into st.navigation
nav = st.navigation([page_1, page_2, page_3, page_4])
nav.run()
