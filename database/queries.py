from sqlalchemy import text
from database.db import engine


def get_existing_ids():
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT id FROM earthquakes")
        )

        return {row[0] for row in result}