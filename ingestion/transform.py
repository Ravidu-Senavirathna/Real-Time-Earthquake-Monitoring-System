import pandas as pd


def parse_earthquake(event):

    try:

        props = event["properties"]
        geo = event["geometry"]["coordinates"]

        return {
            "id": event["id"],

            "magnitude": props.get("mag"),
            "magnitude_type": props.get("magType"),

            "place": props.get("place"),

            "event_time": pd.to_datetime(
                props["time"],
                unit="ms"
            ) if props.get("time") else None,

            "updated_time": pd.to_datetime(
                props["updated"],
                unit="ms"
            ) if props.get("updated") else None,

            "latitude": geo[1],
            "longitude": geo[0],
            "depth": geo[2],

            "tsunami": props.get("tsunami"),
            "significance": props.get("sig"),

            "status": props.get("status"),
            "event_type": props.get("type")
        }
    
    except Exception as e:

        print(
            f"[TRANSFORM ERROR] "
            f"{event.get('id')} : {e}"
        )

        return None