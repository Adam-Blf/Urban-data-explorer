CREATE DATABASE IF NOT EXISTS ude;
USE ude;

CREATE EXTERNAL TABLE IF NOT EXISTS gold_arrondissement_dashboard (
  arrondissement_code STRING,
  green_space_count INT,
  mobility_count INT,
  public_service_count INT,
  education_count INT,
  culture_count INT,
  health_count INT,
  housing_count INT,
  pressure_count INT,
  accessibility_index DOUBLE,
  pressure_index DOUBLE,
  attractiveness_index DOUBLE
)
STORED AS PARQUET
LOCATION '/data/gold/dashboard';

CREATE EXTERNAL TABLE IF NOT EXISTS gold_arrondissement_timeline (
  arrondissement_code STRING,
  year INT,
  month INT,
  record_count INT,
  accessibility_index DOUBLE,
  pressure_index DOUBLE,
  attractiveness_index DOUBLE
)
STORED AS PARQUET
LOCATION '/data/gold/timeline';
