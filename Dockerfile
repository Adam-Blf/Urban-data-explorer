# Urban Data Explorer · API · production image
# Builds a slim Python 3.12 image with the FastAPI app + the demo DuckDB seed.

FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Native deps for shapely / pyproj (geo) — kept minimal.
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc g++ libgeos-dev libproj-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY pipeline ./pipeline
COPY api      ./api
COPY scripts  ./scripts
COPY data/demo ./data/demo

ENV GOLD_DUCKDB_PATH=/app/data/demo/urban.duckdb \
    DATA_LAKE_ROOT=/app/data \
    RAW_DIR=/app/data/raw \
    SILVER_DIR=/app/data/silver \
    GOLD_DIR=/app/data/gold \
    LOGS_DIR=/app/logs \
    JWT_SECRET=please-change-me-in-prod-use-openssl-rand-hex-32 \
    DEMO_USER=admin \
    DEMO_PASSWORD=admin \
    API_HOST=0.0.0.0 \
    API_PORT=8000

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health').read()"

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
