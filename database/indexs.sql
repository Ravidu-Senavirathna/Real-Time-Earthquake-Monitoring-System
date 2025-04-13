CREATE INDEX idx_event_time
ON earthquakes(event_time);

CREATE INDEX idx_magnitude
ON earthquakes(magnitude);

CREATE INDEX idx_place
ON earthquakes(place);