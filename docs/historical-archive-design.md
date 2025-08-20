# Historical earthquake archive: implementation plan

Status: design only. Implementation will proceed one reviewed step at a time.

## Goal and boundaries

Support individual historical earthquakes and charts across roughly 40 years for a
single-user portfolio project, while learning Spark. Begin with one month of data;
measure correctness and query performance before downloading the full history.

The existing PostgreSQL records, live loader, dashboard, dark maps, and previous
performance fixes remain in place. New historical processing is developed alongside
them. A later explicit historical mode will use the archive; existing pages will
not silently switch sources. Live and historical results will not initially be
combined, because their overlapping event IDs would otherwise cause double counts.

## Proposed data flow

```text
USGS historical API
    -> Python downloader: bounded requests, retries, checkpoints
    -> compressed raw GeoJSON responses
    -> Spark: normalize, validate, resolve duplicate event IDs
    -> published clean Parquet archive
        -> DuckDB: filtered individual events for the historical map/table
        -> Spark summaries: historical Overview and Trends

Existing live feed -> existing PostgreSQL path -> existing dashboard mode
```

Spark runs as a separate batch command. DuckDB queries Parquet directly when a
user requests historical events; the archive is not imported into PostgreSQL.
Raw responses are retained so transformation errors can be repaired offline.

## Storage layout (proposed, not created by this step)

```text
data/historical/
  raw/<download-run>/<window>.geojson.gz
  checkpoints/<download-run>.json
  rejected/<processing-run>/...
  snapshots/<snapshot-id>/
    events/year=YYYY/part-*.parquet
    summaries/daily/...
    summaries/magnitude_bins/...
  current.json
```

Start by evaluating yearly event partitions. Measure file sizes, date-filtered
reads, and geographic queries before deciding whether monthly partitions are
worthwhile. Request windows and storage partitions are separate: many small API
batches may be compacted into a larger Parquet file. Do not create one file per event.

## Download and record contract

- All internal timestamps and request windows use UTC. Internally, ranges are
  start-inclusive and end-exclusive. USGS includes both endpoints, so downstream
  filtering must remove the exclusive-end boundary before combining adjacent ranges.
- Historical scope defaults to `eventtype=earthquake`, with no minimum-magnitude
  filter. Save the exact request parameters in the download metadata. The existing
  backfill uses magnitude >= 1.5, so comparisons must align their filters.
- Split oversized windows rather than assuming one month fits one API response.
  USGS has a 20,000-event request limit. An empty successful result is a completed
  window; an error, incomplete response, or exhausted retry is not.
- Checkpoint a window only after its response and metadata are safely saved. Resume
  only compatible requests; changing filters requires a separate run/checkpoint.
- Preserve the existing 13 event fields: `id`, `magnitude`, `magnitude_type`, `place`,
  `event_time`, `updated_time`, `latitude`, `longitude`, `depth`, `tsunami`,
  `significance`, `status`, and `event_type`. Use strings, double-precision numeric
  measurements, nullable integers for flags, and UTC microsecond timestamps.
- Require a nonempty ID, valid event timestamp, and finite coordinates within their
  valid ranges. Preserve missing magnitudes as null; magnitude statistics exclude
  them, while total event counts include them. Record rejected rows and reasons.
  These rules extend the current validator and must be tested explicitly before use.
- Deduplicate by event ID, preferring the latest non-null `updated_time`. Define a
  deterministic tie policy and report conflicting equal-timestamp versions before
  publication. Do not silently choose whichever row Spark happens to return.

## Refresh and publication rules

Initially, refresh is an explicit command for a selected date range. Routine recent
refreshes and occasional older-range reconciliation will be separate operations;
no automatic refresh schedule is installed during early development.

A successful full-window refresh replaces that window's previous membership, then
rebuilds affected storage partitions and summaries. This must remove superseded
versions rather than append duplicates. Revisions that move an event's date/year
require resolving the same ID in both its old and new partitions. Missing records
can be removed only from a completely fetched replacement window, not after an
API failure. Full-window reconciliation is needed to handle deleted/withdrawn events;
an update-only feed is insufficient on its own.

Build output in a new version and verify it before atomically switching `current.json`.
Readers use only files referenced by that published snapshot, never a wildcard over
all old versions. A failed run leaves the previous snapshot available. One writer
is supported initially. Old versions require an explicit retention policy that
protects files still in use by readers.

## Query and summary behavior

- Historical queries accept date, magnitude, tsunami, and geographic bounds. Apply
  partition predicates as well as exact event-time filters. Benchmark the query plan;
  a row limit alone does not guarantee a small scan.
- Individual maps retain a visible result limit (initially 2,000), deterministic
  ordering, and an explanation of the selected subset. A limited event heatmap must
  not be presented as the density of the full archive. Geographic aggregation and
  zoom-dependent detail are a later change.
- Daily summaries store event count, magnitude sum/count/max, tsunami count, and
  reviewed count. Magnitude bins use the existing 0.25 interval. Compute overall
  averages from sum/count, not an average of daily averages.
- The UI eventually displays archive coverage and publication time. Analytics can
  lag the live feed; no claim of a continuously synchronized catalog is made.

## Small steps and commit order

| Step | Commit | Evidence required before committing |
| --- | --- | --- |
| 1 | `docs: define historical archive and query architecture` | Review this design; no executable changes. |
| 2 | `feat: download checkpointed historical USGS batches` | One-month download; retries, split windows, resume, empty and failed results checked. |
| 3 | `build: configure and verify local Spark runtime` | A small local Spark job starts, produces expected results, and shuts down. |
| 4 | `feat: transform historical batches into validated Parquet` | Types, UTC boundaries, duplicate versions, rejected rows, and record accounting checked. |
| 5 | `feat: publish refreshed archive partitions safely` | Repeat run, corrections, moved/deleted events, and interrupted publication checked. |
| 6 | `feat: query historical earthquake records with DuckDB` | Returned IDs match fixtures; date/area filters, limits, ordering, and pruning measured. |
| 7 | `feat: generate historical analytics summaries with Spark` | Counts, null handling, weighted averages, and bins match independent calculations. |
| 8 | `feat: connect historical queries to the dashboard` | Explicit historical mode works; existing mode and map styling remain functional. |

For each step: explain the change, implement only that step, show the verification,
and pause for review before committing or starting the next step. Commit dates are
not inherited from the earlier backdating request; agree on dates separately if needed.

## References

- [USGS catalog API](https://earthquake.usgs.gov/fdsnws/event/1/): query bounds,
  request limits, event types, updates, and deleted events.
- [Spark Parquet support](https://spark.apache.org/docs/latest/sql-data-sources-parquet.html).
- [DuckDB Parquet querying](https://duckdb.org/docs/stable/data/parquet/overview).
