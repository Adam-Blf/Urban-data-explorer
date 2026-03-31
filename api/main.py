import os
import json
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Urban Data Explorer API",
    description="API des indicateurs urbains de Paris. Sert les données Bronze, Silver et Gold.",
    version="1.0.0"
)

# Autoriser requêtes CORS depuis le frontend local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
SILVER_DIR = os.path.join(DATA_DIR, "silver")
GOLD_DIR = os.path.join(DATA_DIR, "gold")

def load_json(path):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def to_geojson(data_list, lat_col="lat", lon_col="lon"):
    """Convertit une liste de dicts (contenant lat/lon) en GeoJSON FeatureCollection."""
    if not isinstance(data_list, list): return data_list
    
    features = []
    for item in data_list:
        if item.get(lat_col) is None or item.get(lon_col) is None:
            continue
        properties = {k: v for k, v in item.items() if k not in [lat_col, lon_col]}
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [item[lon_col], item[lat_col]]
            },
            "properties": properties
        })
    
    return {
        "type": "FeatureCollection",
        "features": features
    }

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API Urban Data Explorer"}

@app.get("/api/arrondissements")
def get_arrondissements():
    """Retourne les polygones des arrondissements fusionnés avec les 4 indicateurs Gold."""
    data = load_json(os.path.join(GOLD_DIR, "arrondissements_stats.geojson"))
    if not data:
        # Fallback si l'agrégation geo n'a pas pu se faire correctement
        return {"type": "FeatureCollection", "features": []}
    return data

@app.get("/api/indicateurs")
def get_indicateurs():
    """Retourne uniquement les indicateurs par arrondissement (dict)."""
    data = load_json(os.path.join(GOLD_DIR, "indicateurs.json"))
    if not data:
        raise HTTPException(status_code=404, detail="Indicateurs introuvables. Lancez le pipeline.")
    return data

@app.get("/api/dataset/{dataset_name}")
def get_dataset(dataset_name: str, geojson: bool = False, arrondissement: int = None):
    """
    Retourne n'importe quel dataset au niveau Silver (ex: velib, ecoles, monuments_historiques).
    - geojson=true pour formater en FeatureCollection (utile pour MapLibre)
    - arrondissement=X pour filtrer
    """
    path = os.path.join(SILVER_DIR, f"{dataset_name}.json")
    data = load_json(path)
    
    if not data:
        raise HTTPException(status_code=404, detail=f"Dataset {dataset_name} introuvable.")
        
    if arrondissement is not None:
        data = [d for d in data if d.get("arrondissement") == arrondissement]
        
    if geojson:
        # Cas spécial pour espaces verts qui peuvent avoir geo_shape ou rien
        return to_geojson(data)
        
    return data

@app.get("/api/compare")
def compare_arrondissements(a1: str, a2: str):
    """Prépare la comparaison entre deux arrondissements."""
    data = load_json(os.path.join(GOLD_DIR, "indicateurs.json"))
    if not data:
        raise HTTPException(status_code=404, detail="Indicateurs introuvables.")
        
    res1 = data.get(a1)
    res2 = data.get(a2)
    if not res1 or not res2:
        raise HTTPException(status_code=404, detail="Arrondissement non trouvé (utiliser un id de 1 à 20).")
        
    return {
        "arrondissement_1": res1,
        "arrondissement_2": res2
    }
