"""Accès lecture-seule au datamart Gold (DuckDB)."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

import duckdb

from pipeline.config import get_settings


@contextmanager
def gold_connection() -> Iterator[duckdb.DuckDBPyConnection]:
    """Connexion DuckDB read-only sur le fichier Gold (par requête)."""
    s = get_settings()
    if not s.gold_duckdb_path.exists():
        raise FileNotFoundError(
            f"Gold DuckDB introuvable à {s.gold_duckdb_path} · "
            "lance d'abord `python -m pipeline.run_pipeline`."
        )
    con = duckdb.connect(s.gold_duckdb_path.as_posix(), read_only=True)
    try:
        yield con
    finally:
        con.close()
