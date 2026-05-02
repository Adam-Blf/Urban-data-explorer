"""Configuration centrale lue depuis l'environnement.

Aucun chemin n'est codé en dur dans le pipeline · tout passe par cette classe,
chargée depuis `.env` à la racine ou depuis les variables d'environnement.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings unique pour pipeline + API."""

    # --- Storage roots ---
    data_lake_root: Path = Field(default=Path("./data"), alias="DATA_LAKE_ROOT")
    raw_dir: Path = Field(default=Path("./data/raw"), alias="RAW_DIR")
    silver_dir: Path = Field(default=Path("./data/silver"), alias="SILVER_DIR")
    gold_dir: Path = Field(default=Path("./data/gold"), alias="GOLD_DIR")
    logs_dir: Path = Field(default=Path("./logs"), alias="LOGS_DIR")

    # --- Gold relational store ---
    gold_duckdb_path: Path = Field(
        default=Path("./data/demo/urban.duckdb"),
        alias="GOLD_DUCKDB_PATH",
    )

    # --- API ---
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    jwt_secret: str = Field(default="dev-secret-change-me", alias="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_ttl_minutes: int = Field(default=60, alias="JWT_TTL_MINUTES")
    default_page_size: int = Field(default=50, alias="DEFAULT_PAGE_SIZE")
    max_page_size: int = Field(default=500, alias="MAX_PAGE_SIZE")

    # --- Demo credentials ---
    demo_user: str = Field(default="admin", alias="DEMO_USER")
    demo_password: str = Field(default="admin", alias="DEMO_PASSWORD")

    # --- Sources ---
    dvf_base_url: str = Field(
        default="https://files.data.gouv.fr/geo-dvf/latest/csv",
        alias="DVF_BASE_URL",
    )
    paris_opendata_base_url: str = Field(
        default="https://opendata.paris.fr/api/explore/v2.1/catalog/datasets",
        alias="PARIS_OPENDATA_BASE_URL",
    )
    insee_filosofi_url: str = Field(
        default="https://www.insee.fr/fr/statistiques/fichier/8229323/cc_filosofi_2021_COM.csv",
        alias="INSEE_FILOSOFI_URL",
    )
    arrondissements_geojson_url: str = Field(
        default="https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/arrondissements/exports/geojson",
        alias="ARRONDISSEMENTS_GEOJSON_URL",
    )
    airparif_url: str = Field(
        default="https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/qualite-de-lair-mesuree-dans-la-station-paris-centre/exports/json",
        alias="AIRPARIF_URL",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    def partition_path(self, layer_root: Path, source: str, ingestion_date: str) -> Path:
        """Construit le chemin partitionné `layer/source/year=Y/month=M/day=D/`."""
        year, month, day = ingestion_date.split("-")
        return (
            layer_root
            / source
            / f"year={year}"
            / f"month={month}"
            / f"day={day}"
        )

    def ensure_dirs(self) -> None:
        """Crée les dossiers persistants au premier run."""
        for d in (self.raw_dir, self.silver_dir, self.gold_dir, self.logs_dir):
            d.mkdir(parents=True, exist_ok=True)


_settings: Settings | None = None


def get_settings() -> Settings:
    """Singleton settings · évite la relecture du .env à chaque import."""
    global _settings
    if _settings is None:
        _settings = Settings()
        _settings.ensure_dirs()
    return _settings
