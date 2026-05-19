CREATE DATABASE IF NOT EXISTS ude;
USE ude;

CREATE VIEW IF NOT EXISTS vw_kpi AS
SELECT
  t.code_arrondissement,
  AVG(t.prix_m2) AS prix_m2,
  s.nb_logements_finances
FROM silver_transactions t
LEFT JOIN silver_social_housing s
  ON t.code_arrondissement = s.code_arrondissement
GROUP BY t.code_arrondissement, s.nb_logements_finances;

