"""
Urban Data Explorer API - Backend FastAPI
Auteur : Adam BELOUCIF (Adam-Blf)
Rôle : Exposition des indicateurs urbains et datasets via endpoints REST.
Interface avec la couche Gold et Silver du pipeline Médaille.
"""

import os
import json
import asyncio
import httpx
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

# --- Initialisation de l'API ---
app = FastAPI(
    title="🏢 Urban Data Explorer API",
    description="Backend de service des données immobilières et urbaines de Paris (Master DE2).",
    version="1.0.0",
    contact={
        "name": "Adam BELOUCIF",
        "url": "https://github.com/Adam-Blf",
        "email": "adam.beloucif@efrei.net"
    }
)

# Configuration CORS pour autoriser le frontend (Web & Mobile)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Adapté pour le développement local
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Configuration des chemins ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
SILVER_DIR = os.path.join(DATA_DIR, "silver")
GOLD_DIR = os.path.join(DATA_DIR, "gold")

# --- Système Anti-Sommeil (Keep-alive) ---
async def keep_alive_task():
    """Effectue une requête sur elle-même toutes les 14 minutes pour Render."""
    url = os.getenv("RENDER_EXTERNAL_URL")
    if not url:
        print("Keep-alive: RENDER_EXTERNAL_URL non défini. Désactivé.")
        return
        
    client = httpx.AsyncClient()
    while True:
        await asyncio.sleep(14 * 60) # 14 minutes
        try:
            await client.get(f"{url}/api/health")
            print("Keep-alive: Ping réussi.")
        except Exception as e:
            print(f"Keep-alive: Erreur lors du ping -> {e}")

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(keep_alive_task())

# --- Fonctions Utilitaires ---

def load_json(path):
    """
    Charge un fichier JSON de manière sécurisée.
    
    Args:
        path (str): Chemin absolu vers le fichier.
    Returns:
        dict/list: Le contenu JSON ou None si erreur.
    """
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def to_geojson(data_list, lat_col="lat", lon_col="lon"):
    """
    Transforme une liste d'objets plats en FeatureCollection GeoJSON sur le vol.
    Utilisable pour un affichage direct sur MapLibre sans post-processing.
    """
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

# --- Endpoints API ---

@app.get("/api/health", tags=["Diagnostic"])
def health_check():
    """Endpoint utilisé pour le keep-alive."""
    return {"status": "alive", "timestamp": os.getloadavg() if hasattr(os, "getloadavg") else None}

@app.get("/api/arrondissements", tags=["Map Data"])
def get_arrondissements():
    """
    Récupère le fond de carte GeoJSON enrichi des indicateurs composites (Couche Gold).
    """
    data = load_json(os.path.join(GOLD_DIR, "arrondissements_stats.geojson"))
    if not data:
        raise HTTPException(status_code=404, detail="Cartographie Gold non générée. Lancez le pipeline.")
    return data

@app.get("/api/indicateurs", tags=["Analytics"])
def get_indicateurs():
    """
    Récupère uniquement les scores numériques (0-100) par arrondissement.
    Utile pour les graphiques (Radar Chart, Bars).
    """
    data = load_json(os.path.join(GOLD_DIR, "indicateurs.json"))
    if not data:
        raise HTTPException(status_code=404, detail="Statistiques Gold manquantes.")
    return data

@app.get("/api/dataset/{dataset_name}", tags=["Raw Data"])
def get_dataset(dataset_name: str, geojson: bool = False, arrondissement: int = None):
    """
    Accès granulaire aux données Silver (nettoyées).
    
    - geojson=True : Convertit les points en FeatureCollection (GeoJSON).
    - arrondissement=X : Filtre les résultats par quartier (1-20).
    """
    path = os.path.join(SILVER_DIR, f"{dataset_name}.json")
    data = load_json(path)
    
    if data is None:
        raise HTTPException(status_code=404, detail=f"Dataset {dataset_name} introuvable dans Silver Layer.")
        
    if arrondissement is not None:
        data = [d for d in data if d.get("arrondissement") == arrondissement]
        
    if geojson:
        return to_geojson(data)
        
    return data

@app.get("/api/compare", tags=["Analytics"])
def compare_arrondissements(a1: str, a2: str):
    """
    Fournit les données de comparaison entre deux zones géographiques.
    
    Args:
        a1 (str): Numero du premier arrondissement (ex: "1").
        a2 (str): Numero du second arrondissement (ex: "18").
    """
    data = load_json(os.path.join(GOLD_DIR, "indicateurs.json"))
    if not data:
        raise HTTPException(status_code=404, detail="Données analytiques indisponibles.")
        
    res1 = data.get(a1)
    res2 = data.get(a2)
    if not res1 or not res2:
        raise HTTPException(status_code=404, detail="Identifiants d'arrondissements invalides (1 à 20).")
        
    return {
        "arrondissement_1": {**res1, "id": a1},
        "arrondissement_2": {**res2, "id": a2}
    }
