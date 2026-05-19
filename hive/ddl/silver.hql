CREATE DATABASE IF NOT EXISTS ude;
USE ude;

CREATE EXTERNAL TABLE IF NOT EXISTS silver_transactions (
  code_arrondissement STRING,
  date_mutation DATE,
  prix_m2 DOUBLE,
  lat DOUBLE,
  lon DOUBLE,
  year INT,
  month INT
)
STORED AS PARQUET
LOCATION '/data/silver/transactions';

CREATE EXTERNAL TABLE IF NOT EXISTS silver_social_housing (
  code_arrondissement STRING,
  year INT,
  nb_logements_finances INT
)
STORED AS PARQUET
LOCATION '/data/silver/social_housing';

CREATE EXTERNAL TABLE IF NOT EXISTS silver_air_quality (
  date_obs STRING,
  aqi_mean_paris DOUBLE
)
STORED AS PARQUET
LOCATION '/data/silver/air_quality';

