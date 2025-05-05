# Main bash commands

Run all of these in the root directory

* to ingest data from a specific start date

```bash
python -m ingestion.backfill
```

* to get live data

```bash
python -m ingestion.live_loader
```

* to run the streamlit app

```bash
python -m streamlit run dashboard/app.py
```
