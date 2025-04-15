CREATE INDEX IF NOT EXISTS idx_event_time
ON earthquakes(event_time);

CREATE INDEX IF NOT EXISTS idx_magnitude
ON earthquakes(magnitude);

CREATE INDEX IF NOT EXISTS idx_place
ON earthquakes(place);