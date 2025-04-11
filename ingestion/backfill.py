import requests
import pandas as pd
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from database.db import engine
import time


# Backfill earthquake data from a range
def fetch_range(start, end):
    url = (
        "https://earthquake.usgs.gov/fdsnws/event/1/query"
        f"?format=geojson&starttime={start}&endtime={end}&minmagnitude=2"
    )

    print(url)

    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        data = r.json()

    except requests.RequestException as e:
        print(f"Error fetching data for {start} to {end}: {e}")
        return pd.DataFrame()

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

    start = start = datetime.strptime(start_date,"%Y-%m-%d").replace(tzinfo=timezone.utc)
    end = datetime.now(timezone.utc)

    current = start

    while current < end:

        next = current + relativedelta(days=7)

        print(f"[BACKFILL] {current.strftime('%Y-%m-%d')} → {next.strftime('%Y-%m-%d')}")

        df = fetch_range(current.strftime("%Y-%m-%d"), next.strftime("%Y-%m-%d"))

        if not df.empty:
            print(
                f"[INFO] "
                f"Fetched {len(df)} earthquakes "
                f"for {current.strftime('%Y-%m-%d')}"
            )

            df.to_sql(
                "earthquakes",
                engine,
                if_exists="append",
                index=False,
                method="multi"
            )

            print(
                f"[SUCCESS] "
                f"{current.strftime('%Y-%m-%d')} "
                f"Rows: {len(df)}"
            )


        else:
            print("Skipped empty or failed batch")

        current = next

        time.sleep(1)  # avoid API abuse



if __name__ == "__main__":
    backfill("2026-01-01")