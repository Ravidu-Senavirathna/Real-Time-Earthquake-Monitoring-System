from sqlalchemy import text
from database.db import engine

with engine.connect() as conn:


    total = conn.execute(
        text("SELECT COUNT(*) FROM earthquakes")
    ).scalar()

    duplicates = conn.execute(
        text("""
            SELECT COUNT(*)
            FROM (
                SELECT id
                FROM earthquakes
                GROUP BY id
                HAVING COUNT(*) > 1
            ) t
        """)
    ).scalar()

    max_mag = conn.execute(
        text("SELECT MAX(magnitude) FROM earthquakes")
    ).scalar()

    oldest_date = conn.execute(
        text("SELECT MIN(event_time) FROM earthquakes")
    ).scalar()

    newest_date = conn.execute(
        text("SELECT MAX(event_time) FROM earthquakes")
    ).scalar()

    print("\n===== DATA QUALITY REPORT =====")
    print(f"Total Rows      : {total}")
    print(f"Duplicate IDs   : {duplicates}")
    print(f"Max Magnitude   : {max_mag}")
    print(f"Oldest Event    : {oldest_date}")
    print(f"Newest Event    : {newest_date}")