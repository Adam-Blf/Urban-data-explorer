# Architecture · Urban Data Explorer

## Vue d'ensemble

Pipeline médaillon **Bronze → Silver → Gold**, exposé par une API REST FastAPI sécurisée par JWT, consommée par un frontend statique (MapLibre + Chart.js).

```
┌─────────────────────────────────────────────────────────────────────┐
│                       SOURCES OUVERTES                              │
│  data.gouv DVF · OpenData Paris (10 datasets) · INSEE · Airparif    │
└──────────────────────────────┬──────────────────────────────────────┘
                               │  feeder.py (CLI · paramétrable)
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│ BRONZE  /raw/<source>/year=YYYY/month=MM/day=DD/*.parquet           │
│         (snapshot brut versionné, idempotent)                       │
└──────────────────────────────┬──────────────────────────────────────┘
                               │  processor.py (clean + validate +
                               │                join + window + cache)
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│ SILVER  /silver/<source>/year=YYYY/month=MM/day=DD/<source>.parquet │
│         (typé, géocodé, jointure spatiale arrondissement)           │
└──────────────────────────────┬──────────────────────────────────────┘
                               │  datamart.py (DuckDB · agrégats Gold)
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│ GOLD    /gold/urban.duckdb                                          │
│         dim_arrondissement, dim_poi,                                │
│         fact_transactions_arr_mois, fact_logements_sociaux,         │
│         fact_revenus_arr, fact_air_quality, fact_poi_arr,           │
│         kpi_arrondissement, timeline_arrondissement                 │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
            ┌──────────────────┴──────────────────┐
            ▼                                     ▼
┌──────────────────────┐               ┌──────────────────────────┐
│ FastAPI (JWT, page,  │  HTTP/JSON    │ Frontend (HTML+JS)       │
│ filtres) :8000       │ ─────────────►│ MapLibre + Chart.js :5500│
└──────────────────────┘               └──────────────────────────┘
```

## Composants

### 1. Bronze · `pipeline/feeder.py`

- **CLI paramétrable** · aucun chemin codé en dur, tout passe par `Settings` (Pydantic) lue depuis `.env`.
- **Sources** ·
  - `dvf`               · DVF géolocalisé data.gouv (Paris filtré, ~250k mutations)
  - `social_housing`    · OpenData Paris `logements-sociaux-finances`
  - `filosofi`          · INSEE Filosofi 2021 (revenus / inégalités)
  - `arrondissements`   · GeoJSON 20 arrondissements (Paris OpenData)
  - `air_quality`       · Airparif via Paris OpenData
  - `poi`               · Vélib stations, Belib bornes, écoles, collèges, marchés, événements culturels, espaces verts, sanisettes, aménagements cyclables (registry `paris_poi.POI_REGISTRY`)
  - `datagouv`          · Musées de France, hôpitaux IDF, monuments historiques (registry `datagouv_poi.DATAGOUV_REGISTRY`)
- **Partitionnement** · `year=YYYY/month=MM/day=DD` calculé via `Settings.partition_path()`.
- **Logs** · `logs/feeder_<source>_<runid>.txt` (`log.info` + `log.error`).

### 2. Silver · `pipeline/processor.py`

- **Lecture** · dernière partition Bronze (glob).
- **5+ règles de validation** sur DVF · `non_null_date`, `non_null_valeur`, `non_null_surface`, `valeur_realistic`, `geo_within_paris`, `type_local_logement`. Chaque règle log le nombre de lignes rejetées.
- **Cleaning** · cast types stricts, parsing dates ISO, dérivation `prix_m2 = valeur / surface`.
- **Jointure spatiale** · point-in-polygon Shapely sur le GeoJSON arrondissements (raw partition la plus récente).
- **Window functions** ·
  - `MEDIAN(prix_m2) OVER (PARTITION BY code_arrondissement)`
  - `RANK() OVER (PARTITION BY year, month ORDER BY prix_m2 DESC)`
  - `LAG(prix_m2, 1) OVER (PARTITION BY code_arrondissement, year)` pour le delta MoM
- **Cache** · `df.cache()` Polars sur le silver DVF avant écriture (équivalent persist Spark).
- **POI** · `_silver_poi` concatène tous les POI bruts (Paris + data.gouv) en un schéma unifié `(code_arrondissement, category, subcategory, name, lon, lat)`.

### 3. Gold · `pipeline/datamart.py`

- **DuckDB** · base relationnelle `gold/urban.duckdb`. Approche colonnaire, lecture directe Parquet via `read_parquet()`.
- **Tables** ·
  - `dim_arrondissement` (réf spatiale)
  - `dim_poi` (points pour la carte)
  - `fact_transactions_arr_mois` (DVF agrégé arr × mois)
  - `fact_logements_sociaux` (silver passé tel quel)
  - `fact_revenus_arr` (Filosofi par arr)
  - `fact_air_quality` (Airparif)
  - `fact_poi_arr` (comptages catégories × subcat × arr)
  - `kpi_arrondissement` (synthèse + 4 indicateurs composites)
  - `timeline_arrondissement` (série mensuelle prix m² + lissage 3 mois + delta MoM)
- **4 indicateurs composites** ·
  | Indicateur          | Formule simplifiée                                        |
  |---------------------|-----------------------------------------------------------|
  | `idx_accessibilite` | `revenu_median / (prix_m2 * 50)`                          |
  | `idx_tension`       | `transactions_an * 1000 / parc_logements`                 |
  | `idx_effort_social` | `log_sociaux_finances * 10000 / population`               |
  | `idx_attractivite`  | combinaison pondérée z-scores `accessibilité+POI−tension` |

### 4. API · `api/`

- **FastAPI 0.115** · routers `/auth`, `/datamarts`, `/geo`, `/health`.
- **JWT** · `python-jose` HS256, TTL configurable. Login : `POST /auth/login`.
- **Pagination** · enveloppe `Page[T]` standardisée (`page, page_size, total, pages, next_page, prev_page`).
- **Filtres** · sur `code_arrondissement`, `min_attractivite`, `max_prix_m2`, plage d'années pour la timeline, catégorie POI, sous-catégorie POI.
- **Doc** · OpenAPI auto à `/docs`.

### 5. Frontend · `frontend/`

- **Statique** · pas de build, ESM via CDN.
- **MapLibre GL JS** · choroplèthe sur les 20 arrondissements, couches POI activables (transport / culture / santé / ...), fond Carto Dark.
- **Chart.js** · panneau latéral · barres équipements + ligne prix m² mensuel + radar comparaison.
- **Timeline** · slider mensuel qui repaint la choroplèthe en direct.
- **Comparaison** · sélecteurs Arr A vs Arr B, radar 5 dimensions.

## Décisions clés

Voir [DECISIONS.md](DECISIONS.md) pour le détail (5 ADRs).

## Déploiement

- **API** · `uvicorn api.main:app --host 0.0.0.0 --port 8000` (Docker possible via `python:3.12-slim`).
- **Frontend** · n'importe quel CDN/static host (Vercel, Netlify, S3, GitHub Pages) · variable `API_BASE` à pointer.
- **Pipeline** · `python -m pipeline.run_pipeline` orchestrable via `cron`, GitHub Actions ou Airflow.
