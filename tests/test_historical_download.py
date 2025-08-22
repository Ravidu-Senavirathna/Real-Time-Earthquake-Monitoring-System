from unittest.mock import Mock, patch
import gzip
import json

import pytest
import requests

from ingestion.historical_download import fetch_range, main, save_response


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
    payload = {"type": "FeatureCollection", "features": []}
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
        with patch("ingestion.historical_download.fetch_range", return_value=payload):
            main()
    with gzip.open(output, "rt", encoding="utf-8") as handle:
        assert json.load(handle) == payload
    assert "Saved compressed response" in capsys.readouterr().out
