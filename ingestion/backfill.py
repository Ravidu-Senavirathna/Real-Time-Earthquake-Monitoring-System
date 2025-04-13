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

            "magnitude": p.get("mag"),
            "magnitude_type": p.get("magType"),

            "place": p.get("place"),

            "event_time": pd.to_datetime(
                p["time"],
                unit="ms"
            ) if p.get("time") else None,

            "updated_time": pd.to_datetime(
                p["updated"],
                unit="ms"
            ) if p.get("updated") else None,

            "latitude": g[1],
            "longitude": g[0],
            "depth": g[2],

            "tsunami": p.get("tsunami"),
            "significance": p.get("sig"),

            "status": p.get("status"),
            "event_type": p.get("type")
        })

    return pd.DataFrame(rows)


def backfill(start_date):

    start = datetime.strptime(start_date,"%Y-%m-%d").replace(tzinfo=timezone.utc)
    end = datetime.now(timezone.utc)

    current = start

    while current < end:

        next_date = current + relativedelta(days=7)

        print(f"[BACKFILL] {current.strftime('%Y-%m-%d')} → {next_date.strftime('%Y-%m-%d')}")

        df = fetch_range(current.strftime("%Y-%m-%d"), next_date.strftime("%Y-%m-%d"))

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

        current = next_date

        time.sleep(1)  # avoid API abuse



if __name__ == "__main__":
    backfill("2026-06-01")