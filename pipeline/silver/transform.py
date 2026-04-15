"""Silver · nettoyage + normalisation → parquet"""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
import geopandas as gpd

ROOT = Path(__file__).resolve().parents[2]
BRONZE = ROOT / "data" / "bronze"
SILVER = ROOT / "data" / "silver"


def _latest(src: str, ext: str) -> Path:
    files = sorted((BRONZE / src).glob(f"*.{ext}"))
    if not files:
        raise FileNotFoundError(f"no bronze file for {src}.{ext}")
    return files[-1]


def arrondissements() -> Path:
    gdf = gpd.read_file(_latest("arrondissements", "geojson"))
    # harmonise la clé
    code_col = next(c for c in ["c_ar", "c_arinsee", "arrondissement"] if c in gdf.columns)
    gdf = gdf.rename(columns={code_col: "code_ar"})
    gdf["code_ar"] = gdf["code_ar"].astype(int)
    keep = ["code_ar", "l_ar", "surface", "perimetre", "geometry"]
    gdf = gdf[[c for c in keep if c in gdf.columns]]
    out = SILVER / "arrondissements.parquet"
    SILVER.mkdir(parents=True, exist_ok=True)
    gdf.to_parquet(out)
    print(f"[silver] {out} · {len(gdf)} rows")
    return out


def dvf() -> Path:
    df = pd.read_csv(_latest("dvf_paris", "csv"), low_memory=False)
    df = df[df["nature_mutation"] == "Vente"].copy()
    df = df[df["type_local"].isin(["Appartement", "Maison"])]
    df = df.dropna(subset=["valeur_fonciere", "surface_reelle_bati", "code_postal"])
    df = df[df["surface_reelle_bati"] > 9]
    df["prix_m2"] = df["valeur_fonciere"] / df["surface_reelle_bati"]
    df = df[df["prix_m2"].between(1000, 50000)]
    df["code_ar"] = (df["code_postal"].astype(int) - 75000).clip(1, 20)
    df["annee"] = pd.to_datetime(df["date_mutation"]).dt.year
    out = SILVER / "dvf.parquet"
    df[["code_ar", "annee", "prix_m2", "surface_reelle_bati", "type_local"]].to_parquet(out)
    print(f"[silver] {out} · {len(df)} rows")
    return out


def logements_sociaux() -> Path:
    raw = json.loads(_latest("logements_sociaux", "json").read_text(encoding="utf-8"))
    df = pd.DataFrame(raw)
    if "arrondissement" in df.columns:
        df["code_ar"] = df["arrondissement"].astype(str).str.extract(r"(\d+)").astype(int)
    out = SILVER / "logements_sociaux.parquet"
    df.to_parquet(out)
    print(f"[silver] {out} · {len(df)} rows")
    return out


def run():
    arrondissements()
    dvf()
    try:
        logements_sociaux()
    except Exception as e:
        print(f"[silver] logements_sociaux skipped: {e}")


if __name__ == "__main__":
    run()
