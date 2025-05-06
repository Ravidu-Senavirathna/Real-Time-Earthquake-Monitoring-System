import time

from ingestion.get_data import get_live_earthquakes
from database.queries import get_existing_ids
from database.db import engine



def run_live_loader():

    while True:

        print("[LIVE] Fetching latest earthquakes")

        existing_ids = get_existing_ids()

        df = get_live_earthquakes()

        required_columns = {
            "id",
            "magnitude",
            "magnitude_type",
            "place",
            "event_time",
            "updated_time",
            "latitude",
            "longitude",
            "depth",
            "tsunami",
            "significance",
            "status",
            "event_type"
        }

        if not required_columns.issubset(df.columns):
            print("[ERROR] Missing required columns")
            print("Found:", list(df.columns))
            time.sleep(30)
            continue

        if df.empty:
            print("[LIVE] No data received")

        else:

            new_df = df[
                ~df["id"].isin(existing_ids)
            ]

            if not new_df.empty:

                new_df.to_sql(
                    "earthquakes",
                    engine,
                    if_exists="append",
                    index=False,
                    method="multi"
                )

                print(
                    f"[LIVE] Inserted "
                    f"{len(new_df)} new earthquakes"
                )

            else:

                print(
                    "[LIVE] No new earthquakes found"
                )

        print(
            "[LIVE] Sleeping for 30 secs..."
        )

        time.sleep(30)


if __name__ == "__main__":
    run_live_loader()