# Copilot instructions — Urban Data Explorer

## Build, test, and lint
- **Install (Python):** `pip install -r requirements.txt`
- **Pre-commit:** `pip install pre-commit && pre-commit install` (run: `pre-commit run --all-files`)
- **Lint:** `ruff check .` (format: `ruff format .`)
- **Security lint:** `bandit -c .bandit.yaml -r api pipeline scripts`
- **Tests:** `pytest -q`
- **Single test example:** `pytest tests/test_api.py::test_health`
- **Build artifacts:** `python scripts/build_report.py`, `python scripts/build_guide.py`, `python scripts/build_slides.py`
- **Seed demo DB (CI parity):** `python scripts/seed_demo_db.py`
- **Run API:** `uvicorn api.main:app --reload --port 8000`
- **Run full pipeline:** `python -m pipeline.run_pipeline --layers all`
- **Run frontend (static):** `cd frontend && python -m http.server 5500`
- **Demo video (Remotion, optional):** `cd video && npm install && npm run start` (render: `npm run build`)

## High-level architecture
- **Medallion pipeline** in `pipeline/`: `feeder.py` ingests raw sources into `data/raw/<source>/year=YYYY/month=MM/day=DD/`, `processor.py` cleans/validates and writes Silver parquet, `datamart.py` builds Gold in **DuckDB**.
- **Gold store** is `data/demo/urban.duckdb` by default; APIs and tests read from it (override with `GOLD_DUCKDB_PATH`).
- **API** in `api/`: FastAPI with JWT auth, paginated `/datamarts/*` endpoints, and GeoJSON in `/geo/*`.
- **Frontend** in `frontend/`: static HTML/ESM (no JS build) consuming the API; MapLibre + Chart.js.
- **Docs/Deliverables** in `docs/` and `scripts/`: CI rebuilds PDF report, guide, and slides.

## Key conventions
- **Single source of config:** all paths and secrets come from `pipeline.config.Settings` (Pydantic). No hardcoded paths; use `get_settings()` and `Settings.partition_path()` for bronze/silver layouts.
- **Demo-first defaults:** `GOLD_DUCKDB_PATH` defaults to the committed demo DB so API/tests work without re-running the pipeline.
- **Public API style:** type hints are required on public signatures; module and main function docstrings are in **French**.
- **Data source additions:** add new sources under `pipeline/sources/`, register POI sources in `paris_poi.POI_REGISTRY` or `datagouv_poi.DATAGOUV_REGISTRY`, document in `docs/DATA_CATALOG.md`, and add a `tests/test_<source>.py`.
- **Ruff settings:** line length 100; `E501` and `B008` are intentionally ignored (see `pyproject.toml`).
