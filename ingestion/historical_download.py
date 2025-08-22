"""Fetch one historical USGS range; start is inclusive and end is exclusive."""

import argparse
from datetime import datetime, timedelta, timezone
import gzip
import json
from pathlib import Path

import requests

API_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"
MAX_EVENTS = 20000


def date_range(start_date, end_date):
    start = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    end = datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    if start >= end:
        raise ValueError("End date must be later than start date")
    return start, end


def request_params(start, end):
    # USGS includes its end boundary; catalog timestamps have millisecond precision.
    api_end = end - timedelta(milliseconds=1)
    return {
        "starttime": start.isoformat(timespec="milliseconds"),
        "endtime": api_end.isoformat(timespec="milliseconds"),
        "eventtype": "earthquake",
    }


def split_windows(start, end):
    """Yield disjoint windows and expected counts that fit the catalog limit."""
    response = requests.get(
        API_URL.removesuffix("query") + "count",
        params=request_params(start, end),
        timeout=(10, 60),
    )
    response.raise_for_status()
    count = int(response.text)
    if count < 0:
        raise ValueError("USGS returned a negative event count")
    if count <= MAX_EVENTS:
        yield start, end, count
        return
    milliseconds = (end - start) // timedelta(milliseconds=1)
    if milliseconds <= 1:
        raise ValueError("Cannot split an oversized one-millisecond window")
    midpoint = start + timedelta(milliseconds=milliseconds // 2)
    yield from split_windows(start, midpoint)
    yield from split_windows(midpoint, end)


def fetch_range(start_date, end_date):
    return fetch_window(*date_range(start_date, end_date))


def fetch_window(start, end):
    response = requests.get(
        API_URL,
        params={
            "format": "geojson",
            **request_params(start, end),
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
        help="First output file (.geojson.gz); extra batches get numbered filenames",
    )
    args = parser.parse_args()
    try:
        total = 0
        for index, (start, end, expected) in enumerate(
            split_windows(*date_range(args.start, args.end)), start=1
        ):
            payload = fetch_window(start, end)
            count = len(payload["features"])
            if count != expected:
                raise ValueError("Catalog count changed or response is incomplete")
            if args.output is not None:
                output = (
                    args.output
                    if index == 1
                    else args.output.with_stem(f"{args.output.stem}.part-{index:04d}")
                )
                save_response(payload, output)
                print(f"Saved compressed response to {output}")
            total += count
    except (ValueError, OSError, requests.RequestException) as exc:
        parser.exit(1, f"Historical download failed: {exc}\n")
    print(f"Fetched {total:,} earthquake records")


if __name__ == "__main__":
    main()
