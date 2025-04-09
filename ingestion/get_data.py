import requests
import pandas as pd

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


        props = event["properties"]
        geo = event["geometry"]["coordinates"]

        print(event)
        print("")

        # Append earthquake data to the list
        earthquakes.append({
            "id": event["id"],
            "magnitude": props["mag"],
            "place": props["place"],
            "event_time": pd.to_datetime(
                props["time"],
                unit="ms"
            ),
            "longitude": geo[0],
            "latitude": geo[1],
            "depth": geo[2]
        })

    return pd.DataFrame(earthquakes)

print("Fetching earthquake data...")
df = get_live_earthquakes()


if __name__ == "__main__":
    get_live_earthquakes()