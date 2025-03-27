CREATE TABLE IF NOT EXISTS earthquakes (
    id VARCHAR(50) PRIMARY KEY,
    magnitude FLOAT,
    place TEXT,
    event_time TIMESTAMP,
    latitude FLOAT,
    longitude FLOAT,
    depth FLOAT
);