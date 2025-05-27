CREATE TABLE earthquakes (
    id VARCHAR(50) PRIMARY KEY,

    magnitude FLOAT,
    magnitude_type VARCHAR(10),

    place TEXT,

    event_time TIMESTAMPZ,
    updated_time TIMESTAMPZ,

    latitude FLOAT,
    longitude FLOAT,

    depth FLOAT,

    tsunami INTEGER,
    significance INTEGER,

    status VARCHAR(20),
    event_type VARCHAR(20)
);