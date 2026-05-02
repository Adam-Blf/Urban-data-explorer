# Urban Data Explorer

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com/)
[![MapLibre](https://img.shields.io/badge/MapLibre-GL%20JS-396CB2.svg)](https://maplibre.org/)
[![Architecture](https://img.shields.io/badge/architecture-medallion-FFC857.svg)](docs/ARCHITECTURE.md)
[![Version](https://img.shields.io/badge/version-1.0.0-success.svg)](#)

> Plateforme open data Paris · pipeline médaillon (Bronze / Silver / Gold), API REST sécurisée et dashboard cartographique pour explorer les dynamiques du logement parisien.

## Sommaire

- [Le projet](#le-projet)
- [Architecture](#architecture)
- [Sources de données](#sources-de-données)
- [4 indicateurs composites](#4-indicateurs-composites)
- [Quickstart](#quickstart)
- [Pipeline](#pipeline)
- [API](#api)
- [Frontend](#frontend)
- [Tests](#tests)
- [Structure du repo](#structure-du-repo)
- [Auteurs](#auteurs)

## Le projet

Urban Data Explorer aggrège plusieurs jeux de données publics (DVF, logements sociaux, INSEE Filosofi, Airparif, géofond Paris) pour offrir une lecture **multi-niveaux du marché immobilier parisien à l'échelle de l'arrondissement**.

L'utilisateur explore une carte choroplèthe interactive, anime la timeline pour observer l'évolution depuis 2019, ouvre le mode comparaison entre deux arrondissements, et lit en direct des KPIs croisés (prix m² médian, accessibilité, tension, effort social, attractivité).

## Architecture

```
┌─ Sources ouvertes ─────────────────────────────────────────────┐
│  data.gouv DVF · OpenData Paris · INSEE Filosofi · Airparif    │
└────────────────────────────────────────────────────────────────┘
              │   (HTTPS · pull idempotent · planifié)
              ▼
┌─ Bronze /raw ──────────────────────────────────────────────────┐
│  Données brutes versionnées par year=YYYY/month=MM/day=DD      │
│  Format Parquet (snappy) ou GeoJSON pour les fonds carto       │
└────────────────────────────────────────────────────────────────┘
              │   processor.py · clean + validate + join + window
              ▼
┌─ Silver /silver ───────────────────────────────────────────────┐
│  Données nettoyées, normalisées, géocodées + enrichissement    │
│  arrondissement (jointure spatiale via GeoPandas)              │
└────────────────────────────────────────────────────────────────┘
              │   datamart.py · agrégats + 4 indicateurs custom
              ▼
┌─ Gold /gold ───────────────────────────────────────────────────┐
│  DuckDB relationnel · datamarts arrondissement / mois          │
│  + indicateurs composites + timeline                           │
└────────────────────────────────────────────────────────────────┘
              │
              ├─► FastAPI · JWT · pagination · filtres ──► Frontend
              └─► Tuiles GeoJSON / endpoints timeline    (MapLibre + Chart.js)
```

Détails dans [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Sources de données

| Source | Fournisseur | Volume | Usage |
|---|---|---|---|
| DVF géolocalisé | data.gouv.fr | ~250 000 mutations Paris 2019-2024 | Prix m², volumes |
| Logements sociaux financés | OpenData Paris | ~5 000 lignes | Effort social |
| Filosofi 2021 (revenus) | INSEE | 1 ligne / commune et IRIS | Accessibilité |
| Arrondissements | OpenData Paris | 20 polygones GeoJSON | Choroplèthe + jointure spatiale |
| Qualité de l'air | Airparif via OpenData Paris | ~30 000 mesures horaires | Indicateur env. |

Voir [docs/DATA_CATALOG.md](docs/DATA_CATALOG.md) pour le détail (schéma, fraîcheur, licence).

## 4 indicateurs composites

| Indicateur | Formule | Lecture |
|---|---|---|
| **Accessibilité logement** | `revenu_median / (prix_m2 * 50)` | >0.6 = accessible · <0.3 = élu très tendu |
| **Tension immobilière** | `transactions_an / parc_logements * 1000` | rotation pour 1 000 logements |
| **Effort social** | `log_sociaux_finances / population * 10000` | unités sociales pour 10 000 hab. |
| **Attractivité composite** | moyenne pondérée (transports z + qualité air z + parc activités z) | z-score 0 = moyenne Paris |

## Quickstart

```bash
# 1. Cloner
git clone https://github.com/Adam-Blf/urban-data-explorer.git
cd urban-data-explorer

# 2. Environnement Python
python -m venv .venv
.venv\Scripts\activate                  # Windows
source .venv/bin/activate               # Unix
pip install -r requirements.txt

# 3. Configurer
cp .env.example .env
# > éditer JWT_SECRET, DEMO_PASSWORD

# 4. Pipeline complet (bronze + silver + gold)
python -m pipeline.run_pipeline --layers all

# 5. API
uvicorn api.main:app --reload --port 8000

# 6. Frontend (dans un autre terminal)
cd frontend && python -m http.server 5500
# > http://localhost:5500
```

## Pipeline

Chaque couche est une commande paramétrable, sans chemin codé en dur.

```bash
# Bronze (ingestion ciblée)
python -m pipeline.feeder --source dvf --year 2024
python -m pipeline.feeder --source social_housing
python -m pipeline.feeder --source filosofi
python -m pipeline.feeder --source arrondissements
python -m pipeline.feeder --source air_quality

# Silver
python -m pipeline.processor --source dvf

# Gold
python -m pipeline.datamart --build all
```

Logs : `logs/feeder_*.txt`, `logs/processor_*.txt`, `logs/datamart_*.txt`.

## API

Endpoints principaux · auth `Bearer` JWT obligatoire (sauf `/auth/login`, `/health`, `/docs`).

| Method | Path | Description |
|---|---|---|
| POST | `/auth/login` | Échange `username/password` contre un JWT |
| GET | `/health` | Liveness |
| GET | `/datamarts/arrondissements` | Liste des datamarts arrondissement (filtres + pagination) |
| GET | `/datamarts/timeline` | Série temporelle filtrable par arrondissement / indicateur |
| GET | `/datamarts/indicators` | Indicateurs composites (accessibilité, tension, ...) |
| GET | `/geo/arrondissements.geojson` | Fond cartographique enrichi (utilisé par le front) |

Doc OpenAPI auto · `http://localhost:8000/docs`.

## Frontend

- `MapLibre GL JS` · choroplèthe sur les 20 arrondissements
- `Chart.js` · barres et lignes dans le panneau latéral
- `IntersectionObserver` · révèle les sections au scroll
- Mode **comparaison** · sélection de 2 arrondissements, métriques côte à côte
- Mode **timeline** · slider par mois, animation choroplèthe

Aucun build JS · pur HTML + ESM via CDN.

## Tests

```bash
pytest -q
ruff check .
```

## Structure du repo

```
.
├── api/                  # FastAPI + JWT
├── frontend/             # MapLibre + Chart.js (statique)
├── pipeline/
│   ├── feeder.py         # Bronze
│   ├── processor.py      # Silver
│   ├── datamart.py       # Gold
│   ├── run_pipeline.py   # Orchestrateur CLI
│   ├── config.py
│   ├── logging_utils.py
│   └── sources/          # Connecteurs source par source
├── docs/                 # Architecture, data catalog, ADRs
├── tests/                # Tests pytest
├── data/                 # Data lake local (gitignored)
└── logs/                 # Logs .txt (gitignored)
```

## Auteurs

- **Adam Beloucif** · [@Adam-Blf](https://github.com/Adam-Blf) · Data Engineer
- **Emilien Morice** · [@emilien754](https://github.com/emilien754) · Data Engineer

Projet réalisé dans le cadre du cours **Data Architecture / Data Engineering** · M1 Data Engineering & IA · EFREI Paris.
