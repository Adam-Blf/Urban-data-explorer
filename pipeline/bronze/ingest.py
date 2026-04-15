"""Bronze · ingestion brute des sources vers data/bronze/<source>/<date>.ext"""
from __future__ import annotations
import json
from datetime import date
from pathlib import Path
import requests

BRONZE = Path(__file__).resolve().parents[2] / "data" / "bronze"

SOURCES = {
    "arrondissements": {
        "url": "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/arrondissements/exports/geojson",
        "ext": "geojson",
    },
    "logements_sociaux": {
        "url": "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/logement-social-finance-a-paris/exports/json",
        "ext": "json",
    },
    "dvf_paris": {
        "url": "https://files.data.gouv.fr/geo-dvf/latest/csv/2024/communes/75/75056.csv",
        "ext": "csv",
    },
}


def fetch(name: str, cfg: dict) -> Path:
    out_dir = BRONZE / name
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{date.today().isoformat()}.{cfg['ext']}"
    print(f"[bronze] GET {cfg['url']}")
    r = requests.get(cfg["url"], timeout=120)
    r.raise_for_status()
    out.write_bytes(r.content)
    print(f"[bronze] wrote {out} ({len(r.content)} bytes)")
    return out


def run() -> dict[str, Path]:
    return {name: fetch(name, cfg) for name, cfg in SOURCES.items()}


if __name__ == "__main__":
    run()
