\connect ude

CREATE TABLE IF NOT EXISTS dim_source (
  source_id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  family TEXT NOT NULL,
  catalog_url TEXT NOT NULL,
  provider TEXT NOT NULL,
  metadata_only BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS dim_arrondissement (
  code_arrondissement TEXT PRIMARY KEY,
  label TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_arrondissement_dashboard (
  arrondissement_code TEXT PRIMARY KEY,
  green_space_count INTEGER NOT NULL DEFAULT 0,
  mobility_count INTEGER NOT NULL DEFAULT 0,
  public_service_count INTEGER NOT NULL DEFAULT 0,
  education_count INTEGER NOT NULL DEFAULT 0,
  culture_count INTEGER NOT NULL DEFAULT 0,
  health_count INTEGER NOT NULL DEFAULT 0,
  housing_count INTEGER NOT NULL DEFAULT 0,
  pressure_count INTEGER NOT NULL DEFAULT 0,
  accessibility_index DOUBLE PRECISION NOT NULL DEFAULT 0,
  pressure_index DOUBLE PRECISION NOT NULL DEFAULT 0,
  attractiveness_index DOUBLE PRECISION NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS fact_arrondissement_timeline (
  arrondissement_code TEXT NOT NULL,
  year INTEGER NOT NULL,
  month INTEGER NOT NULL,
  record_count INTEGER NOT NULL DEFAULT 0,
  accessibility_index DOUBLE PRECISION NOT NULL DEFAULT 0,
  pressure_index DOUBLE PRECISION NOT NULL DEFAULT 0,
  attractiveness_index DOUBLE PRECISION NOT NULL DEFAULT 0,
  PRIMARY KEY (arrondissement_code, year, month)
);

CREATE TABLE IF NOT EXISTS pipeline_runs (
  run_date TEXT NOT NULL,
  stage TEXT NOT NULL,
  status TEXT NOT NULL,
  row_count INTEGER NOT NULL DEFAULT 0,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (run_date, stage)
);
