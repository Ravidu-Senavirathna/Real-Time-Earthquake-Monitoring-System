import pandas as pd
from database.db import engine
import streamlit as st

@st.cache_data
def load_data():
    query = "SELECT * FROM earthquakes"
    return pd.read_sql(query, engine)