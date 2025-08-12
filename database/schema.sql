CREATE TABLE IF NOT EXISTS earthquakes (
    id VARCHAR(50) PRIMARY KEY,

    magnitude FLOAT,
    magnitude_type VARCHAR(10),

    place TEXT,

    event_time TIMESTAMPTZ,
    updated_time TIMESTAMPTZ,

    latitude FLOAT,
    longitude FLOAT,

    depth FLOAT,

    tsunami INTEGER,
    significance INTEGER,

    status VARCHAR(20),
    event_type VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS daily_aggregations (
    event_date DATE PRIMARY KEY,
    total_events INTEGER,
    max_magnitude FLOAT,
    avg_magnitude FLOAT
);

CREATE TABLE IF NOT EXISTS country_summaries (
    place_name TEXT PRIMARY KEY,
    total_events INTEGER,
    max_magnitude FLOAT,
    avg_magnitude FLOAT
);