# Historical downloader

The downloader fetches USGS earthquake events as compressed GeoJSON. These raw
files are input for later Spark processing. PostgreSQL and the dashboard are unchanged.

## Download

Run from the project root with the existing virtual environment (Python 3.11+):

```powershell
.\.venv\Scripts\python.exe -m ingestion.historical_download --start 2026-01-01 --end 2026-02-01 --output data/historical/raw/january-2026.geojson.gz --checkpoint data/historical/checkpoints/january-2026.json
```

- Dates are UTC: start is inclusive, end is exclusive. This example covers January.
- The request includes earthquake events with no minimum-magnitude filter. The
  existing database backfill uses magnitude >= 1.5, so its counts may differ.
- Oversized ranges are split until each request fits the 20,000-event limit.
- The first batch uses the output filename above. Additional batches are named
  `january-2026.geojson.part-0002.gz`, `january-2026.geojson.part-0003.gz`, and so on.
- Parent folders are created automatically. Existing output files are never overwritten.
- Omitting `--output` fetches and counts records without saving them.
  `--checkpoint` requires `--output`.

Use new output and checkpoint paths for the first run. Generated files under
`data/historical/` are ignored by Git. Run only one process per checkpoint/output set.

## Resume

Rerun the exact same command after an interruption. The checkpoint preserves the
split-window plan and completed batch count. Completed files are checked against
their recorded SHA-256 checksums before being skipped; pending batches are fetched.

Keep the date range and output path unchanged. Missing or changed saved files stop
the run: restore the original files or start again with new output and checkpoint
paths. Older checkpoints without checksums also require a fresh download.

There is a recovery limitation: an interruption during a file write, or after the
file is saved but before its checkpoint is updated, can leave an uncheckpointed
file. Resume refuses to overwrite it. Preserve it for inspection and use fresh
output/checkpoint paths to restart; automatic recovery of that case is not implemented.

## Refresh

A completed checkpoint resumes the old download; it does not check for newer USGS
revisions. To fetch the same dates again, use a fresh pair of filenames:

```powershell
.\.venv\Scripts\python.exe -m ingestion.historical_download --start 2026-01-01 --end 2026-02-01 --output data/historical/raw/january-2026-refresh-01.geojson.gz --checkpoint data/historical/checkpoints/january-2026-refresh-01.json
```

These are separate raw downloads. Do not combine them as unique events; duplicate
and revised-event handling belongs to the later Spark step.

## Errors and checks

Requests retry connection errors, timeouts, and HTTP 429/500/502/503/504 up to four
attempts, with waits of 1, 2, and 4 seconds. Other HTTP errors stop immediately.
If the catalog count changes between planning and fetching, the run stops rather
than saving a batch with an unexpected count. If repeated resume attempts hit that
same mismatch, use fresh paths to plan a new download.

Run the downloader tests:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_historical_download.py -q --basetemp .pytest-download
```

See the [archive design](historical-archive-design.md) for the next processing steps.
