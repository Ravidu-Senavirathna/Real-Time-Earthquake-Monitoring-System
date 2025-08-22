"""Fetch one historical USGS range; start is inclusive and end is exclusive."""

import argparse
from datetime import datetime, timedelta, timezone
import gzip
import json
from pathlib import Path

import requests

API_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"


def fetch_range(start_date, end_date):
    start = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    end = datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    if start >= end:
        raise ValueError("End date must be later than start date")

    # USGS includes its end boundary; catalog timestamps have millisecond precision.
    api_end = end - timedelta(milliseconds=1)
    response = requests.get(
        API_URL,
        params={
            "format": "geojson",
            "starttime": start.isoformat(timespec="milliseconds"),
            "endtime": api_end.isoformat(timespec="milliseconds"),
            "eventtype": "earthquake",
            "orderby": "time-asc",
        },
        timeout=(10, 60),
    )
    response.raise_for_status()
    if response.status_code == 204:
        return {"type": "FeatureCollection", "features": []}
    payload = response.json()
    if (
        not isinstance(payload, dict)
        or payload.get("type") != "FeatureCollection"
        or not isinstance(payload.get("features"), list)
    ):
        raise ValueError("USGS did not return a GeoJSON FeatureCollection")
    return payload


def save_response(payload, output):
    """Save the source response as gzip JSON, refusing to overwrite existing files."""
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(output, "xt", encoding="utf-8") as handle:
        json.dump(payload, handle, allow_nan=False)
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", required=True, help="Inclusive UTC date: YYYY-MM-DD")
    parser.add_argument("--end", required=True, help="Exclusive UTC date: YYYY-MM-DD")
    parser.add_argument(
        "--output",
        type=Path,
        help="Save to a new compressed GeoJSON file (.geojson.gz)",
    )
    args = parser.parse_args()
    try:
        payload = fetch_range(args.start, args.end)
        if args.output is not None:
            save_response(payload, args.output)
    except (ValueError, OSError, requests.RequestException) as exc:
        parser.exit(1, f"Historical download failed: {exc}\n")
    print(f"Fetched {len(payload['features']):,} earthquake records")
    if args.output is not None:
        print(f"Saved compressed response to {args.output}")


if __name__ == "__main__":
    main()
