"""Datamart · Gold layer.

Construit les datamarts relationnels DuckDB depuis le silver. Les chemins
proviennent de `Settings`, rien n'est codé en dur.

Tables produites dans `gold/urban.duckdb` ·
    - `dim_arrondissement` (réf. spatiale)
    - `fact_transactions_arr_mois` (DVF agrégé)
    - `fact_logements_sociaux` (logements sociaux financés / arr / an)
    - `fact_revenus_arr` (Filosofi)
    - `fact_air_quality` (snapshot Airparif)
    - `kpi_arrondissement` (synthèse par arr · 4 indicateurs composites + KPI)
    - `timeline_arrondissement` (série mensuelle prix m²)

Usage::

    python -m pipeline.datamart --build all
    python -m pipeline.datamart --build kpi
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import duckdb
import polars as pl

from .config import get_settings
from .logging_utils import get_logger

DATAMARTS = {"all", "dim", "facts", "kpi", "timeline"}


def _latest_silver(silver_root: Path, source: str) -> Path:
    files = sorted((silver_root / source).rglob(f"{source}.parquet"))
    if not files:
        raise FileNotFoundError(f"no silver parquet for {source} under {silver_root / source}")
    return files[-1]


def _build_dim(con: duckdb.DuckDBPyConnection, silver_root: Path, logger) -> None:
    p = _latest_silver(silver_root, "arrondissements")
    logger.info("gold · building dim_arrondissement from %s", p)
    con.execute(f"""
        CREATE OR REPLACE TABLE dim_arrondissement AS
        SELECT * FROM read_parquet('{p.as_posix()}');
    """)


def _build_facts(con: duckdb.DuckDBPyConnection, silver_root: Path, logger) -> None:
    dvf = _latest_silver(silver_root, "dvf")
    sh = _latest_silver(silver_root, "social_housing")
    fil = _latest_silver(silver_root, "filosofi")
    air = _latest_silver(silver_root, "air_quality")

    logger.info("gold · building fact_transactions_arr_mois")
    con.execute(f"""
        CREATE OR REPLACE TABLE fact_transactions_arr_mois AS
        SELECT
            code_arrondissement,
            year,
            month,
            COUNT(*)               AS nb_transactions,
            MEDIAN(prix_m2)        AS prix_m2_median,
            AVG(prix_m2)           AS prix_m2_moyen,
            QUANTILE_CONT(prix_m2, 0.25) AS prix_m2_p25,
            QUANTILE_CONT(prix_m2, 0.75) AS prix_m2_p75,
            SUM(valeur_fonciere)   AS volume_eur
        FROM read_parquet('{dvf.as_posix()}')
        WHERE prix_m2 BETWEEN 1000 AND 40000
        GROUP BY code_arrondissement, year, month;
    """)

    logger.info("gold · building fact_logements_sociaux")
    con.execute(f"""
        CREATE OR REPLACE TABLE fact_logements_sociaux AS
        SELECT * FROM read_parquet('{sh.as_posix()}');
    """)

    logger.info("gold · building fact_revenus_arr")
    con.execute(f"""
        CREATE OR REPLACE TABLE fact_revenus_arr AS
        SELECT * FROM read_parquet('{fil.as_posix()}');
    """)

    logger.info("gold · building fact_air_quality")
    con.execute(f"""
        CREATE OR REPLACE TABLE fact_air_quality AS
        SELECT * FROM read_parquet('{air.as_posix()}');
    """)

    poi_files = sorted((silver_root / "poi").rglob("poi.parquet"))
    if poi_files:
        poi_path = poi_files[-1]
        logger.info("gold · building fact_poi_arr from %s", poi_path)
        con.execute(f"""
            CREATE OR REPLACE TABLE fact_poi_arr AS
            SELECT
                code_arrondissement,
                category,
                subcategory,
                COUNT(*) AS nb_poi
            FROM read_parquet('{poi_path.as_posix()}')
            GROUP BY code_arrondissement, category, subcategory;
        """)
        logger.info("gold · building dim_poi (raw points for the map)")
        con.execute(f"""
            CREATE OR REPLACE TABLE dim_poi AS
            SELECT
                code_arrondissement,
                category,
                subcategory,
                name,
                lon,
                lat
            FROM read_parquet('{poi_path.as_posix()}')
            WHERE lon IS NOT NULL AND lat IS NOT NULL;
        """)
    else:
        logger.info("gold · no POI silver found · creating empty placeholders")
        con.execute("""
            CREATE OR REPLACE TABLE fact_poi_arr (
                code_arrondissement VARCHAR,
                category            VARCHAR,
                subcategory         VARCHAR,
                nb_poi              BIGINT
            );
            CREATE OR REPLACE TABLE dim_poi (
                code_arrondissement VARCHAR,
                category            VARCHAR,
                subcategory         VARCHAR,
                name                VARCHAR,
                lon                 DOUBLE,
                lat                 DOUBLE
            );
        """)


def _build_kpi(con: duckdb.DuckDBPyConnection, logger) -> None:
    """4 indicateurs composites + KPIs synthèse · 1 ligne par arr."""
    logger.info("gold · building kpi_arrondissement (4 composite indicators)")

    populations = ", ".join(
        f"('{f'751{i:02d}'}', {pop})"
        for i, pop in enumerate([
            16_888, 20_796, 35_011, 27_487, 58_283, 40_580, 49_988, 35_879,
            58_730, 89_603, 144_492, 138_188, 178_544, 137_105, 233_392,
            166_851, 167_835, 197_309, 184_787, 193_098,
        ], start=1)
    )

    parc = ", ".join(
        f"('{f'751{i:02d}'}', {p})"
        for i, p in enumerate([
            10_500, 14_300, 23_000, 19_400, 35_000, 28_000, 31_500, 25_700,
            42_000, 60_500, 91_000, 80_700, 105_000, 84_500, 142_500,
            108_000, 109_500, 121_300, 110_000, 117_400,
        ], start=1)
    )

    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE _pop AS
        SELECT * FROM (VALUES {populations}) AS t(code_arrondissement, population);

        CREATE OR REPLACE TEMP TABLE _parc AS
        SELECT * FROM (VALUES {parc}) AS t(code_arrondissement, parc_logements);
    """)

    con.execute("""
        CREATE OR REPLACE TABLE kpi_arrondissement AS
        WITH poi_per_cat AS (
            SELECT
                code_arrondissement,
                SUM(CASE WHEN category = 'transport'      THEN nb_poi ELSE 0 END) AS nb_transport,
                SUM(CASE WHEN category = 'service_public' THEN nb_poi ELSE 0 END) AS nb_service_public,
                SUM(CASE WHEN category = 'commerce'       THEN nb_poi ELSE 0 END) AS nb_commerce,
                SUM(CASE WHEN category = 'culture'        THEN nb_poi ELSE 0 END) AS nb_culture,
                SUM(CASE WHEN category = 'sante'          THEN nb_poi ELSE 0 END) AS nb_sante,
                SUM(CASE WHEN category = 'environnement'  THEN nb_poi ELSE 0 END) AS nb_environnement
            FROM fact_poi_arr
            GROUP BY code_arrondissement
        ),
        base AS (
            SELECT
                d.code_arrondissement,
                d.label,
                d.centroid_lon,
                d.centroid_lat,
                COALESCE(p.population, 0)        AS population,
                COALESCE(pa.parc_logements, 0)   AS parc_logements,
                r.MED21                          AS revenu_median,
                (SELECT MEDIAN(prix_m2_median)
                   FROM fact_transactions_arr_mois f
                  WHERE f.code_arrondissement = d.code_arrondissement
                    AND f.year = (SELECT MAX(year) FROM fact_transactions_arr_mois)
                ) AS prix_m2,
                (SELECT SUM(nb_transactions)
                   FROM fact_transactions_arr_mois f
                  WHERE f.code_arrondissement = d.code_arrondissement
                    AND f.year = (SELECT MAX(year) FROM fact_transactions_arr_mois)
                ) AS transactions_an,
                (SELECT SUM(nb_logements_finances)
                   FROM fact_logements_sociaux s
                  WHERE s.code_arrondissement = d.code_arrondissement
                ) AS log_sociaux_finances,
                (SELECT AVG(aqi_mean_paris) FROM fact_air_quality)
                  AS aqi_paris,
                COALESCE(poi.nb_transport,      0) AS nb_transport,
                COALESCE(poi.nb_service_public, 0) AS nb_service_public,
                COALESCE(poi.nb_commerce,       0) AS nb_commerce,
                COALESCE(poi.nb_culture,        0) AS nb_culture,
                COALESCE(poi.nb_sante,          0) AS nb_sante,
                COALESCE(poi.nb_environnement,  0) AS nb_environnement
            FROM dim_arrondissement d
            LEFT JOIN _pop  p  USING (code_arrondissement)
            LEFT JOIN _parc pa USING (code_arrondissement)
            LEFT JOIN fact_revenus_arr r USING (code_arrondissement)
            LEFT JOIN poi_per_cat poi USING (code_arrondissement)
        ),
        scored AS (
            SELECT
                *,
                /* 1. Accessibilité logement · revenu / (prix_m2 * 50 m²) */
                CASE WHEN prix_m2 IS NULL OR prix_m2 = 0 THEN NULL
                     ELSE revenu_median / (prix_m2 * 50.0)
                END AS idx_accessibilite,
                /* 2. Tension immobilière · transactions pour 1000 logements */
                CASE WHEN parc_logements = 0 THEN NULL
                     ELSE transactions_an * 1000.0 / parc_logements
                END AS idx_tension,
                /* 3. Effort social · log sociaux pour 10 000 hab */
                CASE WHEN population = 0 THEN NULL
                     ELSE COALESCE(log_sociaux_finances, 0) * 10000.0 / population
                END AS idx_effort_social,
                /* density POI / 1000 hab pour le composite */
                CASE WHEN population = 0 THEN 0
                     ELSE (nb_transport + nb_culture + nb_sante + nb_environnement)
                          * 1000.0 / population
                END AS poi_density
            FROM base
        ),
        zscored AS (
            SELECT
                *,
                (idx_accessibilite - AVG(idx_accessibilite) OVER ())
                    / NULLIF(STDDEV_SAMP(idx_accessibilite) OVER (), 0)
                    AS z_accessibilite,
                (idx_tension - AVG(idx_tension) OVER ())
                    / NULLIF(STDDEV_SAMP(idx_tension) OVER (), 0)
                    AS z_tension,
                (idx_effort_social - AVG(idx_effort_social) OVER ())
                    / NULLIF(STDDEV_SAMP(idx_effort_social) OVER (), 0)
                    AS z_effort_social,
                (poi_density - AVG(poi_density) OVER ())
                    / NULLIF(STDDEV_SAMP(poi_density) OVER (), 0)
                    AS z_poi_density
            FROM scored
        )
        SELECT
            code_arrondissement,
            label,
            centroid_lon,
            centroid_lat,
            population,
            parc_logements,
            revenu_median,
            prix_m2,
            transactions_an,
            log_sociaux_finances,
            aqi_paris,
            nb_transport,
            nb_service_public,
            nb_commerce,
            nb_culture,
            nb_sante,
            nb_environnement,
            idx_accessibilite,
            idx_tension,
            idx_effort_social,
            /* 4. Attractivité composite réel · z-scores équipements + accessibilité */
            (
                COALESCE(z_accessibilite, 0) * 0.30 +
                COALESCE(z_poi_density,   0) * 0.40 +
                COALESCE(z_effort_social, 0) * 0.15 +
                COALESCE(-z_tension,      0) * 0.15
            ) AS idx_attractivite
        FROM zscored
        ORDER BY code_arrondissement;
    """)


def _build_timeline(con: duckdb.DuckDBPyConnection, logger) -> None:
    logger.info("gold · building timeline_arrondissement (mensuel)")
    con.execute("""
        CREATE OR REPLACE TABLE timeline_arrondissement AS
        SELECT
            code_arrondissement,
            year,
            month,
            CAST(year AS VARCHAR) || '-' || LPAD(CAST(month AS VARCHAR), 2, '0') AS year_month,
            prix_m2_median,
            nb_transactions,
            volume_eur,
            /* prix médian glissant 3 mois par arr */
            AVG(prix_m2_median) OVER (
                PARTITION BY code_arrondissement
                ORDER BY year, month
                ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
            ) AS prix_m2_median_3m,
            /* delta MoM */
            prix_m2_median - LAG(prix_m2_median) OVER (
                PARTITION BY code_arrondissement
                ORDER BY year, month
            ) AS delta_prix_m2_mom
        FROM fact_transactions_arr_mois
        ORDER BY code_arrondissement, year, month;
    """)


def run(build: str) -> int:
    settings = get_settings()
    logger = get_logger("datamart")
    settings.gold_duckdb_path.parent.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect(settings.gold_duckdb_path.as_posix())
    try:
        if build in {"all", "dim"}:
            _build_dim(con, settings.silver_dir, logger)
        if build in {"all", "facts"}:
            _build_facts(con, settings.silver_dir, logger)
        if build in {"all", "kpi"}:
            _build_kpi(con, logger)
        if build in {"all", "timeline"}:
            _build_timeline(con, logger)
        con.commit()
    except Exception as exc:
        logger.error("datamart · failed: %s", exc, exc_info=True)
        return 1
    finally:
        con.close()

    logger.info("datamart · OK · DB at %s", settings.gold_duckdb_path)
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="datamart", description="Gold layer (DuckDB).")
    p.add_argument("--build", default="all", choices=sorted(DATAMARTS))
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    return run(args.build)


if __name__ == "__main__":
    sys.exit(main())


# polars import only used in feeders/silver (kept here for typing parity)
_ = pl
