import os
import requests
import time
import urllib.parse
from config import BASE_DIR, BRONZE_DIR, PARIS_OPENDATA_BASE, PARIS_OPENDATA_GEOJSON_BASE, PARIS_DATASETS, DATA_GOUV_DATASETS

def ensure_bronze_dir():
    if not os.path.exists(BRONZE_DIR):
        os.makedirs(BRONZE_DIR)
        print(f"📁 Création du répertoire: {BRONZE_DIR}")

def download_file(url, target_path):
    print(f"📥 Téléchargement: {url}...")
    try:
        response = requests.get(url, stream=True, timeout=120)
        response.raise_for_status()
        
        with open(target_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print(f"✅ Sauvegardé: {target_path} ({(os.path.getsize(target_path) / 1024 / 1024):.2f} MB)")
    except Exception as e:
        print(f"❌ Erreur lors du téléchargement de {url}: {str(e)}")

def ingest_all():
    ensure_bronze_dir()
    
    total_datasets = len(PARIS_DATASETS) + len(DATA_GOUV_DATASETS)
    current = 1
    
    print("\n🚀 Démarrage de la Phase Bronze (Ingestion)")
    print("=" * 50)
    
    # 1. OpenData Paris
    for name, info in PARIS_DATASETS.items():
        print(f"\n[{current}/{total_datasets}] Traitement de '{name}' (Paris OpenData)")
        
        url_template = PARIS_OPENDATA_BASE if info["format"] == "json" else PARIS_OPENDATA_GEOJSON_BASE
        # L'export API v2.1 de Paris Opendata ramène tout le dataset par défaut.
        url = url_template.format(dataset=urllib.parse.quote(info["id"]))
        
        target_path = os.path.join(BRONZE_DIR, f"{name}.{info['format']}")
        
        # Test file existence to avoid redownloading if already there (for dev purposes)
        # Note: In a real pipeline, we might want to replace. Here we overwrite.
        download_file(url, target_path)
        current += 1
        
        # Petit sleep pour ne pas spammer l'API
        time.sleep(1)
        
    # 2. Data.gouv.fr
    for name, info in DATA_GOUV_DATASETS.items():
        print(f"\n[{current}/{total_datasets}] Traitement de '{name}' (Data.gouv.fr)")
        url = info["url"]
        target_path = os.path.join(BRONZE_DIR, f"{name}.{info['format']}")
        download_file(url, target_path)
        current += 1
        
    print("\n✨ Ingestion terminée avec succès! Toutes les données sont dans 'data/bronze/'.")

if __name__ == "__main__":
    ingest_all()
