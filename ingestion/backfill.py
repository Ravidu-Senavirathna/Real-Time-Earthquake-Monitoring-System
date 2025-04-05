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
            "magnitude": p["mag"] if p["mag"] is not None else 0.0,
            "place": p["place"],
            "event_time": pd.to_datetime(p["time"], unit="ms"),
            "longitude": g[0],
            "latitude": g[1],
            "depth": g[2]
        })

    return pd.DataFrame(rows)


def backfill(start_date):

    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.utcnow()

    current = start

    while current < end:

        next_month = current + relativedelta(months=1)

        print(f"[BACKFILL] {current.strftime('%Y-%m-%d')} → {next_month.strftime('%Y-%m-%d')}")

        df = fetch_range(current.strftime("%Y-%m-%d"), next_month.strftime("%Y-%m-%d"))

        if not df.empty:
            df.to_sql(
                "earthquakes",
                engine,
                if_exists="append",
                index=False,
                method="multi"
            )

        current = next_month

        time.sleep(2)  # avoid API abuse



if __name__ == "__main__":
    backfill("2020-01-01")