import requests
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from database.db import engine
import time


# Backfill earthquake data from a range
def fetch_range(start, end):
    url = (
        "https://earthquake.usgs.gov/fdsnws/event/1/query"
        f"?format=geojson&starttime={start}&endtime={end}"
    )

    r = requests.get(url, timeout=20)
    r.raise_for_status()
    data = r.json()

    rows = []

    for e in data["features"]:
        p = e["properties"]
        g = e["geometry"]["coordinates"]

        rows.append({
            "id": e["id"],
            "magnitude": p["mag"],
            "place": p["place"],
            "event_time": pd.to_datetime(p["time"], unit="ms"),
            "longitude": g[0],
            "latitude": g[1],
            "depth": g[2]
        })

    return pd.DataFrame(rows)


