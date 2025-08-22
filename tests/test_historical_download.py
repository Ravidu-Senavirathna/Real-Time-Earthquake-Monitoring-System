from unittest.mock import Mock, patch
import gzip
import json

import pytest
import requests

from ingestion.historical_download import (
    date_range,
    fetch_range,
    main,
    request_params,
    save_response,
    split_windows,
)


def test_fetch_preserves_response_and_requests_exact_utc_range():
    payload = {"type": "FeatureCollection", "features": [{"id": "example"}]}
    response = Mock(status_code=200)
    response.json.return_value = payload
    with patch(
        "ingestion.historical_download.requests.get", return_value=response
    ) as get:
        assert fetch_range("2026-01-01", "2026-01-02") is payload
    params = get.call_args.kwargs["params"]
    assert params["starttime"] == "2026-01-01T00:00:00.000+00:00"
    assert params["endtime"] == "2026-01-01T23:59:59.999+00:00"
    assert params["eventtype"] == "earthquake"
    assert "minmagnitude" not in params
    # No limit parameter: oversized requests must fail rather than be truncated.
    assert "limit" not in params


@pytest.mark.parametrize(
    "start,end",
    [
        ("2026-01-02", "2026-01-01"),
        ("2026-01-01", "2026-01-01"),
        ("invalid", "2026-01-01"),
    ],
)
def test_invalid_dates_make_no_http_request(start, end):
    with patch("ingestion.historical_download.requests.get") as get:
        with pytest.raises(ValueError):
            fetch_range(start, end)
        get.assert_not_called()


def test_http_failure_is_not_treated_as_an_empty_range():
    response = Mock(status_code=500)
    response.raise_for_status.side_effect = requests.HTTPError("server error")
    with patch("ingestion.historical_download.requests.get", return_value=response):
        with pytest.raises(requests.HTTPError):
            fetch_range("2026-01-01", "2026-01-02")
    response.json.assert_not_called()


def test_successful_no_content_returns_empty_features():
    response = Mock(status_code=204)
    with patch("ingestion.historical_download.requests.get", return_value=response):
        assert fetch_range("2026-01-01", "2026-01-02")["features"] == []
    response.json.assert_not_called()


def test_invalid_response_is_rejected():
    response = Mock(status_code=200)
    response.json.return_value = {"message": "unexpected payload"}
    with patch("ingestion.historical_download.requests.get", return_value=response):
        with pytest.raises(ValueError, match="FeatureCollection"):
            fetch_range("2026-01-01", "2026-01-02")


def test_saved_response_roundtrips_all_source_fields(tmp_path):
    payload = {
        "type": "FeatureCollection",
        "metadata": {"count": 1},
        "features": [{"id": "example", "properties": {"place": "日本", "mag": None}}],
    }
    output = tmp_path / "raw" / "sample.geojson.gz"
    assert save_response(payload, output) == output
    assert output.read_bytes().startswith(b"\x1f\x8b")
    with gzip.open(output, "rt", encoding="utf-8") as handle:
        assert json.load(handle) == payload
    with pytest.raises(FileExistsError):
        save_response({"features": []}, output)
    with gzip.open(output, "rt", encoding="utf-8") as handle:
        assert json.load(handle) == payload


def test_cli_saves_response_when_output_is_provided(tmp_path, capsys):
    output = tmp_path / "sample.geojson.gz"
    payloads = [
        {"type": "FeatureCollection", "features": [{"id": name}]}
        for name in ["first", "second"]
    ]
    responses = [
        Mock(text="2"),
        Mock(text="1"),
        Mock(status_code=200),
        Mock(text="1"),
        Mock(status_code=200),
    ]
    responses[2].json.return_value = payloads[0]
    responses[4].json.return_value = payloads[1]
    with patch(
        "sys.argv",
        [
            "historical_download",
            "--start",
            "2026-01-01",
            "--end",
            "2026-01-02",
            "--output",
            str(output),
        ],
    ):
        with patch("ingestion.historical_download.MAX_EVENTS", 1):
            with patch(
                "ingestion.historical_download.requests.get", side_effect=responses
            ):
                main()
    for path, expected in zip(
        [output, output.with_stem("sample.geojson.part-0002")], payloads
    ):
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            assert json.load(handle) == expected
    assert "Fetched 2 earthquake records" in capsys.readouterr().out


def test_oversized_windows_split_recursively_without_gaps_or_overlap():
    start, end = date_range("2026-01-01", "2026-01-02")
    responses = [Mock(text=str(count)) for count in [40001, 20001, 10000, 10001, 20000]]
    with patch("ingestion.historical_download.requests.get", side_effect=responses):
        windows = list(split_windows(start, end))
    assert len(windows) == 3
    assert windows[0][0] == start
    assert windows[-1][1] == end
    assert all(expected <= 20000 for _, _, expected in windows)
    for left, right in zip(windows, windows[1:]):
        assert left[1] == right[0]
        left_end = request_params(left[0], left[1])["endtime"]
        right_start = request_params(right[0], right[1])["starttime"]
        from datetime import datetime, timedelta

        assert datetime.fromisoformat(right_start) - datetime.fromisoformat(
            left_end
        ) == timedelta(milliseconds=1)


@pytest.mark.parametrize("count", [0, 20000])
def test_empty_and_exact_limit_windows_are_not_split(count):
    start, end = date_range("2026-01-01", "2026-01-02")
    with patch(
        "ingestion.historical_download.requests.get", return_value=Mock(text=str(count))
    ) as get:
        assert list(split_windows(start, end)) == [(start, end, count)]
        get.assert_called_once()


def test_unsplittable_window_stops_instead_of_looping():
    from datetime import timedelta

    start, _ = date_range("2026-01-01", "2026-01-02")
    with patch(
        "ingestion.historical_download.requests.get", return_value=Mock(text="20001")
    ):
        with pytest.raises(ValueError, match="one-millisecond"):
            list(split_windows(start, start + timedelta(milliseconds=1)))
