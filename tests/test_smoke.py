"""Smoke tests · vérifient que les modules s'importent et que la config est saine."""

from __future__ import annotations

import importlib

MODULES = [
    "pipeline.config",
    "pipeline.logging_utils",
    "pipeline.feeder",
    "pipeline.processor",
    "pipeline.datamart",
    "pipeline.run_pipeline",
    "pipeline.sources.dvf",
    "pipeline.sources.social_housing",
    "pipeline.sources.filosofi",
    "pipeline.sources.arrondissements",
    "pipeline.sources.air_quality",
    "pipeline.sources.paris_poi",
    "pipeline.sources.datagouv_poi",
    "pipeline.sources.poi_silver",
    "api.main",
    "api.security",
    "api.schemas",
    "api.db",
    "api.routers.auth",
    "api.routers.datamarts",
    "api.routers.geo",
]


def test_imports():
    for m in MODULES:
        importlib.import_module(m)


def test_settings_partition_path(tmp_path, monkeypatch):
    monkeypatch.setenv("RAW_DIR", str(tmp_path / "raw"))
    monkeypatch.setenv("SILVER_DIR", str(tmp_path / "silver"))
    monkeypatch.setenv("GOLD_DIR", str(tmp_path / "gold"))
    monkeypatch.setenv("LOGS_DIR", str(tmp_path / "logs"))
    monkeypatch.setenv("GOLD_DUCKDB_PATH", str(tmp_path / "gold" / "u.duckdb"))

    import pipeline.config as cfg
    cfg._settings = None  # reset singleton
    s = cfg.get_settings()
    p = s.partition_path(s.raw_dir, "dvf", "2024-05-03")
    assert p.as_posix().endswith("/raw/dvf/year=2024/month=05/day=03")


def test_jwt_roundtrip(monkeypatch, tmp_path):
    monkeypatch.setenv("JWT_SECRET", "test-secret-1234567890abcdef")
    monkeypatch.setenv("LOGS_DIR", str(tmp_path / "logs"))
    import pipeline.config as cfg
    cfg._settings = None

    from api.security import create_access_token, get_current_user
    tok = create_access_token("alice")
    assert isinstance(tok, str) and len(tok) > 20
    sub = get_current_user(token=tok)
    assert sub == "alice"
