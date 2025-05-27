import requests
import pandas as pd
import time

from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta

from database.db import engine
from ingestion.transform import parse_earthquake
from ingestion.validation import validate_earthquake


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

    for event in data["features"]:
        row = parse_earthquake(event)
        
        if rows:
            if validate_earthquake(row):
                rows.append(row)

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