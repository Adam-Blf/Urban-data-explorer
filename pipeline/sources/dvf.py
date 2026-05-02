"""Source DVF · Demandes de Valeurs Foncières géolocalisées (data.gouv).

Endpoint stable · `https://files.data.gouv.fr/geo-dvf/latest/csv/{year}/full.csv.gz`
Filtrage département 75 (Paris) côté pipeline pour rester < 5M lignes par an.
"""

from __future__ import annotations

import gzip
import io
import logging
from pathlib import Path

import httpx
import polars as pl

PARIS_DEPT_CODE = "75"


def fetch(
    year: int,
    raw_partition_dir: Path,
    base_url: str,
    logger: logging.Logger,
    timeout_s: float = 600.0,
) -> Path:
    """Télécharge `full.csv.gz` pour l'année donnée, filtre Paris, écrit Parquet.

    Returns:
        Le chemin du fichier Parquet écrit.
    """
    raw_partition_dir.mkdir(parents=True, exist_ok=True)
    url = f"{base_url}/{year}/full.csv.gz"
    out = raw_partition_dir / f"dvf_paris_{year}.parquet"

    logger.info("DVF · downloading %s", url)
    with httpx.Client(timeout=timeout_s, follow_redirects=True) as client:
        resp = client.get(url)
        resp.raise_for_status()
        gz_bytes = resp.content

    logger.info("DVF · decompressing %.1f MB", len(gz_bytes) / 1024 / 1024)
    with gzip.GzipFile(fileobj=io.BytesIO(gz_bytes)) as gz:
        df = pl.read_csv(
            gz.read(),
            infer_schema_length=10_000,
            ignore_errors=True,
            null_values=["", "NA"],
        )

    before = df.height
    df = df.filter(pl.col("code_departement") == PARIS_DEPT_CODE)
    logger.info("DVF · filtered %d → %d rows (Paris only)", before, df.height)

    df.write_parquet(out, compression="snappy")
    logger.info("DVF · wrote %s (%d rows, %d cols)", out, df.height, df.width)
    return out
