import requests
import pandas as pd

from ingestion.transform import parse_earthquake

# USGS Earthquake API endpoint for all earthquakes in the past hour
URL = (
    "https://earthquake.usgs.gov/"
    "earthquakes/feed/v1.0/summary/all_day.geojson"
)


def get_live_earthquakes():

    # Fetch earthquake data from the USGS API
    response = requests.get(URL, timeout=10)

    # Handle HTTP errors
    response.raise_for_status()

    # Parse the JSON response
    data = response.json()

    earthquakes = []

    for event in data["features"]:
        earthquakes.append(
            parse_earthquake(event)
            )

    return pd.DataFrame(earthquakes)



if __name__ == "__main__":
    get_live_earthquakes()