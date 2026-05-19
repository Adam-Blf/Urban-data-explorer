CREATE TABLE IF NOT EXISTS datamart_kpi (
  code_arrondissement TEXT PRIMARY KEY,
  label TEXT NOT NULL,
  prix_m2 DOUBLE PRECISION,
  idx_accessibilite DOUBLE PRECISION,
  idx_tension DOUBLE PRECISION,
  idx_effort_social DOUBLE PRECISION,
  idx_attractivite DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS datamart_timeline (
  code_arrondissement TEXT,
  year INT,
  month INT,
  prix_m2_median DOUBLE PRECISION
);

