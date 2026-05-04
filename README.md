# Urban Data Explorer

<!-- adam-badges:start -->
[![commits](https://img.shields.io/github/commit-activity/t/Adam-Blf/urban-data-explorer?color=001329&label=commits&style=flat-square)](https://github.com/Adam-Blf/urban-data-explorer/commits) [![visites](https://hits.sh/github.com/Adam-Blf/urban-data-explorer.svg?style=flat-square&label=visites&color=001329)](https://hits.sh/github.com/Adam-Blf/urban-data-explorer/) [![last commit](https://img.shields.io/github/last-commit/Adam-Blf/urban-data-explorer?color=D4A437&style=flat-square&label=dernier%20push)](https://github.com/Adam-Blf/urban-data-explorer/commits) [![top language](https://img.shields.io/github/languages/top/Adam-Blf/urban-data-explorer?style=flat-square)](https://github.com/Adam-Blf/urban-data-explorer) [![license](https://img.shields.io/github/license/Adam-Blf/urban-data-explorer?style=flat-square&color=D4A437)](LICENSE)
<!-- adam-badges:end -->


[![EFREI Paris](https://img.shields.io/badge/EFREI-M1%20Data%20Eng%20%26%20IA-005CA9?style=flat-square&labelColor=000000)](https://www.efrei.fr/)
[![CI](https://github.com/Adam-Blf/urban-data-explorer/actions/workflows/ci.yml/badge.svg)](https://github.com/Adam-Blf/urban-data-explorer/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com/)
[![MapLibre](https://img.shields.io/badge/MapLibre-GL%20JS-396CB2.svg)](https://maplibre.org/)
[![DuckDB](https://img.shields.io/badge/DuckDB-1.1-FFF000.svg)](https://duckdb.org/)
[![Architecture](https://img.shields.io/badge/architecture-medallion-FFC857.svg)](docs/ARCHITECTURE.md)
[![Tests](https://img.shields.io/badge/tests-20%20passing-06D6A0.svg)](#tests)
[![Version](https://img.shields.io/badge/version-1.0.0-success.svg)](#)

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/Adam-Blf/urban-data-explorer&root-directory=frontend)

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
pytest -q          # 20 tests · smoke + API + KPI invariants
ruff check .       # lint
```

CI GitHub Actions (`.github/workflows/ci.yml`) joue lint + tests + seed
DB + build PDF + build PPT + smoke API à chaque push.

## Déploiement

- **Frontend statique** · [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) ·
  `vercel --prod` depuis `frontend/`
- **API conteneurisée** · `docker compose up --build` (ou `docker build .`
  pour Render / Fly.io / Cloud Run)
- **Demo DB** · `data/demo/urban.duckdb` (2.8 MB, commitée) · l'API + le
  front fonctionnent sans rejouer le pipeline

## Schémas data

Diagrammes Mermaid (rendus nativement par GitHub) ·
[docs/schemas.md](docs/schemas.md) · pipeline médaillon, modèle
relationnel Gold (ER), flux d'auth, partitionnement Bronze/Silver.

## Soutenance

Script storytelling 10 min + Q&A · [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md).
Slides PPT premium et rapport PDF générés via les scripts
`scripts/build_slides.py` et `scripts/build_report.py` à partir des MD docs.

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