import os
import json
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from config import BASE_DIR, BRONZE_DIR, SILVER_DIR, PARIS_DATASETS, DATA_GOUV_DATASETS

def ensure_silver_dir():
    if not os.path.exists(SILVER_DIR):
        os.makedirs(SILVER_DIR)
        print(f"📁 Création du répertoire: {SILVER_DIR}")

def load_arrondissements():
    path = os.path.join(BRONZE_DIR, "arrondissements.geojson")
    if not os.path.exists(path):
        print("❌ Fichier arrondissements.geojson introuvable (Bronze) !")
        return None
    gdf = gpd.read_file(path)
    # L'API Paris renvoie souvent l'arrondissement sous c_ar ou c_arint
    if 'c_ar' in gdf.columns:
        gdf['arrondissement'] = gdf['c_ar'].astype(int)
    elif 'c_arint' in gdf.columns:
        gdf['arrondissement'] = gdf['c_arint'].astype(int)
    else:
        # Fallback au code postal ou nom
        pass 
    return gdf[['arrondissement', 'geometry']]

def assign_arrondissement(df, lat_col, lon_col, arrondissements_gdf):
    """Assigne un arrondissement à chaque point via un Spatial Join."""
    if arrondissements_gdf is None or df.empty or lat_col not in df.columns or lon_col not in df.columns:
        return df
    
    # Nettoyer les NaN
    df_clean = df.dropna(subset=[lat_col, lon_col]).copy()
    
    # Créer les points géométriques
    geometry = [Point(xy) for xy in zip(df_clean[lon_col], df_clean[lat_col])]
    gdf_points = gpd.GeoDataFrame(df_clean, geometry=geometry, crs="EPSG:4326")
    
    # L'arrondissement GeoJSON est souvent en EPSG:4326 (WGS84)
    # Spatial join
    joined = gpd.sjoin(gdf_points, arrondissements_gdf, how="left", predicate="within")
    
    # Recuperer la colonne arrondissement
    if 'arrondissement' in joined.columns:
        df_clean['arrondissement'] = joined['arrondissement']
        
    # Re-fusionner avec le df original
    df['arrondissement'] = df_clean['arrondissement']
    df['arrondissement'] = df['arrondissement'].fillna(0).astype(int)
    return df

def clean_and_save(data, name):
    target_path = os.path.join(SILVER_DIR, f"{name}.json")
    with open(target_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ Transformé et sauvegardé: {target_path} ({(len(data))} records)")

def transform_logements_sociaux():
    path = os.path.join(BRONZE_DIR, "logements_sociaux.json")
    if not os.path.exists(path): return
    
    with open(path, 'r', encoding='utf-8') as f:
        raw = json.load(f)
    
    cleaned = []
    for item in raw:
        if not item.get("geo_point_2d"): continue
        cleaned.append({
            "adresse": item.get("adresse_programme"),
            "arrondissement": int(item.get("arrdt", 0)),
            "annee": int(item.get("annee", 0)) if item.get("annee") else None,
            "nb_logements": int(item.get("nb_logmt_total", 0)),
            "categorie": item.get("bs"),
            "lat": item["geo_point_2d"]["lat"],
            "lon": item["geo_point_2d"]["lon"]
        })
    clean_and_save(cleaned, "logements_sociaux")

def transform_espaces_verts():
    path = os.path.join(BRONZE_DIR, "espaces_verts.json")
    if not os.path.exists(path): return
    
    with open(path, 'r', encoding='utf-8') as f:
        raw = json.load(f)
        
    cleaned = []
    for item in raw:
        cp = str(item.get("adresse_codepostal", ""))
        arr = int(cp[-2:]) if cp.startswith("75") and len(cp) == 5 else 0
        
        # Pour les espaces verts, on garde le point central pour l'API
        lat, lon = None, None
        if item.get("geom_x_y"):
            lat, lon = item["geom_x_y"].get("lat"), item["geom_x_y"].get("lon")
            
        cleaned.append({
            "nom": item.get("nom_ev"),
            "categorie": item.get("categorie"),
            "surface": item.get("surface_totale_reelle", 0),
            "arrondissement": arr,
            "lat": lat,
            "lon": lon
        })
    clean_and_save(cleaned, "espaces_verts")

def transform_velib(arr_gdf):
    path = os.path.join(BRONZE_DIR, "velib.json")
    if not os.path.exists(path): return
    
    with open(path, 'r', encoding='utf-8') as f:
        raw = json.load(f)
        
    df = pd.DataFrame([{
        "nom": item.get("name"),
        "capacite": item.get("capacity"),
        "lat": item.get("coordonnees_geo", {}).get("lat"),
        "lon": item.get("coordonnees_geo", {}).get("lon")
    } for item in raw])
    
    df = assign_arrondissement(df, "lat", "lon", arr_gdf)
    # Filtrer uniquement Paris (arr > 0)
    df = df[df['arrondissement'] > 0]
    clean_and_save(df.to_dict(orient="records"), "velib")

def transform_common_points(dataset_name, name_field, lat_field, lon_field, arr_gdf, extra_fields=None):
    """Fonction générique pour nettoyer les datasets de points."""
    path = os.path.join(BRONZE_DIR, f"{dataset_name}.json")
    if not os.path.exists(path): return
    
    with open(path, 'r', encoding='utf-8') as f:
        raw = json.load(f)
        
    records = []
    for item in raw:
        # Naviguer dans le dict si lat/lon sont imbriqués
        lat = item
        for k in lat_field.split('.'): lat = lat.get(k, {}) if isinstance(lat, dict) else None
        
        lon = item
        for k in lon_field.split('.'): lon = lon.get(k, {}) if isinstance(lon, dict) else None
        
        if lat is None or lon is None: continue
        
        record = {
            "nom": item.get(name_field, "Inconnu"),
            "lat": float(lat),
            "lon": float(lon)
        }
        
        if extra_fields:
            for ex in extra_fields:
                record[ex] = item.get(ex)
                
        # Chercher l'arrondissement si déjà présent
        arr = item.get("arrondissement") or item.get("arrdt")
        if arr:
            if isinstance(arr, str):
                import re
                match = re.search(r'\d+', arr)
                if match: arr = int(match.group())
        record["arrondissement_source"] = arr
        
        records.append(record)
        
    df = pd.DataFrame(records)
    if df.empty: return
    
    df = assign_arrondissement(df, "lat", "lon", arr_gdf)
    df = df[df['arrondissement'] > 0] # Keep only Paris
    
    # Nettoyer les clés temporaires
    if 'arrondissement_source' in df.columns:
        df = df.drop(columns=['arrondissement_source'])
        
    clean_and_save(df.where(pd.notnull(df), None).to_dict(orient="records"), dataset_name)

def transform_data_gouv():
    # 1. Monuments historiques
    path = os.path.join(BRONZE_DIR, "monuments_historiques.csv")
    if os.path.exists(path):
        df = pd.read_csv(path, sep=';', on_bad_lines='skip', low_memory=False)
        # Filtrer pour Paris (code insee 75101 à 75120)
        df_paris = df[df['Commune forme index'] == 'Paris'].copy()
        
        records = []
        for _, row in df_paris.iterrows():
            # Extraire les coords
            coords = str(row.get('coordonnées au format WGS84', ''))
            lat, lon = None, None
            if ',' in coords:
                lat, lon = coords.split(',')
                try:
                    lat, lon = float(lat), float(lon)
                except:
                    lat, lon = None, None
            
            records.append({
                "nom": row.get('Dénomination de l’édifice', ''),
                "adresse": row.get('Adresse forme éditoriale', ''),
                "lat": lat,
                "lon": lon
            })
        
        # We process this just to get the list, then we assign arrondissements via geopandas
        df_clean = pd.DataFrame(records)
        arr_gdf = load_arrondissements()
        df_clean = assign_arrondissement(df_clean, "lat", "lon", arr_gdf)
        df_clean = df_clean[df_clean['arrondissement'] > 0]
        
        clean_and_save(df_clean.where(pd.notnull(df_clean), None).to_dict(orient="records"), "monuments_historiques")


def process_all():
    ensure_silver_dir()
    print("\n🔨 Démarrage de la Phase Silver (Transformation)")
    print("=" * 50)
    
    arr_gdf = load_arrondissements()
    
    transform_logements_sociaux()
    transform_espaces_verts()
    transform_velib(arr_gdf)
    
    # Generic point datasets
    transform_common_points("belib", "adresse_station", "coordonneesxy.lat", "coordonneesxy.lon", arr_gdf)
    transform_common_points("stationnement_emplacements", "typsta", "locsta.lat", "locsta.lon", arr_gdf, ["typsta", "parite"])
    transform_common_points("toilettes", "type", "geo_point_2d.lat", "geo_point_2d.lon", arr_gdf, ["acces_pmr"])
    transform_common_points("ecoles", "nom_etablissement", "geo_point_2d.lat", "geo_point_2d.lon", arr_gdf)
    transform_common_points("colleges", "nom_etablissement", "geo_point_2d.lat", "geo_point_2d.lon", arr_gdf)
    transform_common_points("marches", "nom", "geo_point_2d.lat", "geo_point_2d.lon", arr_gdf, ["jours_tenue"])
    
    # Que faire à paris
    # (Titre est "title", coords dans "url" ou géoloc)
    # L'API a changé, regardons plutôt "lat_lon" ou "geometry" -> On va s'adapter
    transform_data_gouv()
    
    print("\n✨ Transformation Silver terminée!")

if __name__ == "__main__":
    process_all()
