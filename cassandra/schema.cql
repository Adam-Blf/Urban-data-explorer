CREATE KEYSPACE IF NOT EXISTS ude
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

USE ude;

CREATE TABLE IF NOT EXISTS events_by_type (
  event_type TEXT,
  event_time TIMESTAMP,
  event_id TEXT,
  source_id TEXT,
  arrondissement_code TEXT,
  payload TEXT,
  PRIMARY KEY ((event_type), event_time, event_id)
) WITH CLUSTERING ORDER BY (event_time DESC);

CREATE TABLE IF NOT EXISTS latest_service_events (
  arrondissement_code TEXT,
  source_id TEXT,
  event_time TIMESTAMP,
  event_id TEXT,
  payload TEXT,
  PRIMARY KEY ((arrondissement_code), source_id, event_time, event_id)
) WITH CLUSTERING ORDER BY (source_id ASC, event_time DESC);

