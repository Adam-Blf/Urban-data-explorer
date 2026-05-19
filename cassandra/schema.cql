CREATE KEYSPACE IF NOT EXISTS ude
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

USE ude;

CREATE TABLE IF NOT EXISTS events_by_type (
  event_type TEXT,
  event_time TIMESTAMP,
  event_id TEXT,
  payload TEXT,
  PRIMARY KEY ((event_type), event_time, event_id)
) WITH CLUSTERING ORDER BY (event_time DESC);

