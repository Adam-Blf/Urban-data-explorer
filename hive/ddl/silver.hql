CREATE DATABASE IF NOT EXISTS ude;
USE ude;

CREATE EXTERNAL TABLE IF NOT EXISTS silver_sources (
  source_title STRING,
  family STRING,
  raw_payload STRING,
  load_ts STRING,
  arrondissement_code STRING,
  postal_code STRING,
  status STRING,
  category STRING,
  latitude DOUBLE,
  longitude DOUBLE,
  quality_flag STRING
)
PARTITIONED BY (source_id STRING, snapshot_date STRING)
STORED AS PARQUET
LOCATION '/data/silver/sources';

