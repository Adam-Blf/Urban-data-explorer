CREATE DATABASE IF NOT EXISTS ude;
USE ude;

CREATE EXTERNAL TABLE IF NOT EXISTS bronze_sources (
  source_title STRING,
  family STRING,
  raw_payload STRING,
  load_ts STRING
)
PARTITIONED BY (source_id STRING, snapshot_date STRING)
STORED AS PARQUET
LOCATION '/data/bronze/sources';

CREATE EXTERNAL TABLE IF NOT EXISTS bronze_events (
  event_id STRING,
  event_type STRING,
  source_id STRING,
  arrondissement_code STRING,
  payload STRING,
  event_time TIMESTAMP
)
ROW FORMAT SERDE 'org.apache.hive.hcatalog.data.JsonSerDe'
LOCATION '/data/bronze/events';
