from sqlalchemy import text
from database.db import engine

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT
            COUNT(*) as total,
            MAX(magnitude) as max_mag,
            MIN(event_time) as earliest,
            MAX(event_time) as latest
        FROM earthquakes;
    """))

    print(result.fetchone())