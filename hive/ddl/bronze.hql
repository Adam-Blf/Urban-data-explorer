CREATE DATABASE IF NOT EXISTS ude;
USE ude;

CREATE EXTERNAL TABLE IF NOT EXISTS bronze_transactions (
  code_arrondissement STRING,
  date_mutation STRING,
  prix_m2 DOUBLE,
  lat DOUBLE,
  lon DOUBLE
)
ROW FORMAT SERDE 'org.apache.hive.hcatalog.data.JsonSerDe'
LOCATION '/data/bronze/transactions';

CREATE EXTERNAL TABLE IF NOT EXISTS bronze_social_housing (
  code_arrondissement STRING,
  year INT,
  nb_logements_finances INT
)
ROW FORMAT SERDE 'org.apache.hive.hcatalog.data.JsonSerDe'
LOCATION '/data/bronze/social_housing';

CREATE EXTERNAL TABLE IF NOT EXISTS bronze_air_quality (
  date_obs STRING,
  aqi_mean_paris DOUBLE
)
ROW FORMAT SERDE 'org.apache.hive.hcatalog.data.JsonSerDe'
LOCATION '/data/bronze/air_quality';

