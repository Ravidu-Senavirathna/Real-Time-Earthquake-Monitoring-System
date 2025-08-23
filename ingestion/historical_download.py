"""Fetch one historical USGS range; start is inclusive and end is exclusive."""

import argparse
from datetime import datetime, timedelta, timezone
import gzip
import hashlib
import json
import os
from pathlib import Path
import time

import requests

API_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"
MAX_EVENTS = 20000
RETRY_STATUSES = {429, 500, 502, 503, 504}


def request_with_retries(url, params):
    """Try a GET at most four times, waiting 1, 2 and 4 seconds between attempts."""
    for attempt in range(4):
        try:
            response = requests.get(url, params=params, timeout=(10, 60))
        except (requests.ConnectionError, requests.Timeout):
            if attempt == 3:
                raise
        else:
            if response.status_code not in RETRY_STATUSES or attempt == 3:
                response.raise_for_status()
                return response
            response.close()
        time.sleep(2**attempt)


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
    response = request_with_retries(
        API_URL.removesuffix("query") + "count",
        params=request_params(start, end),
    )
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
    response = request_with_retries(
        API_URL,
        params={
            "format": "geojson",
            **request_params(start, end),
            "orderby": "time-asc",
        },
    )
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


def save_checkpoint(path, state):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    try:
        temporary.write_text(json.dumps(state), encoding="utf-8")
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def file_checksum(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def prepare_checkpoint(path, start_date, end_date, output):
    request = {
        "start": start_date,
        "end": end_date,
        "output": str(output.resolve()),
        "api": API_URL,
        "eventtype": "earthquake",
    }
    if path.exists():
        state = json.loads(path.read_text(encoding="utf-8"))
        if state.get("version") != 1 or state.get("request") != request:
            raise ValueError(
                "Checkpoint belongs to different parameters; use a new checkpoint and output"
            )
        return state
    windows = [
        [start.isoformat(), end.isoformat(), expected]
        for start, end, expected in split_windows(*date_range(start_date, end_date))
    ]
    state = {
        "version": 1,
        "request": request,
        "windows": windows,
        "completed": 0,
        "checksums": {},
    }
    save_checkpoint(path, state)
    return state


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", required=True, help="Inclusive UTC date: YYYY-MM-DD")
    parser.add_argument("--end", required=True, help="Exclusive UTC date: YYYY-MM-DD")
    parser.add_argument(
        "--output",
        type=Path,
        help="First output file (.geojson.gz); extra batches get numbered filenames",
    )
    parser.add_argument(
        "--checkpoint",
        type=Path,
        help="Save/resume batch progress (requires --output; one writer only)",
    )
    args = parser.parse_args()
    if args.checkpoint is not None and args.output is None:
        parser.error("--checkpoint requires --output")
    try:
        state = None
        if args.checkpoint is not None:
            if args.checkpoint.resolve() == args.output.resolve():
                raise ValueError("Checkpoint and output must be different files")
            state = prepare_checkpoint(
                args.checkpoint, args.start, args.end, args.output
            )
            windows = (
                (datetime.fromisoformat(start), datetime.fromisoformat(end), expected)
                for start, end, expected in state["windows"]
            )
        else:
            windows = split_windows(*date_range(args.start, args.end))
        total = 0
        for index, (start, end, expected) in enumerate(windows, start=1):
            output = args.output
            if output is not None and index > 1:
                output = output.with_stem(f"{output.stem}.part-{index:04d}")
            if state is not None and index <= state["completed"]:
                expected_checksum = state.get("checksums", {}).get(str(index))
                if expected_checksum is None:
                    raise ValueError(
                        "Completed batch has no recorded checksum; use a new checkpoint and output"
                    )
                if not output.is_file() or file_checksum(output) != expected_checksum:
                    raise ValueError(
                        f"Saved batch is missing or changed: {output}. Restore it or use a new checkpoint and output"
                    )
                print(f"Skipped completed batch {index}")
                total += expected
                continue
            payload = fetch_window(start, end)
            count = len(payload["features"])
            if count != expected:
                raise ValueError("Catalog count changed or response is incomplete")
            if args.output is not None:
                save_response(payload, output)
                if state is not None:
                    state.setdefault("checksums", {})[str(index)] = file_checksum(
                        output
                    )
                    state["completed"] = index
                    save_checkpoint(args.checkpoint, state)
                print(f"Saved compressed response to {output}")
            total += count
    except (ValueError, OSError, requests.RequestException) as exc:
        parser.exit(1, f"Historical download failed: {exc}\n")
    print(f"Total earthquake records: {total:,}")


if __name__ == "__main__":
    main()
