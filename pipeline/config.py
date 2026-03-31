import os

# Chemins des dossiers (relatifs a la racine du projet)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
BRONZE_DIR = os.path.join(DATA_DIR, "bronze")
SILVER_DIR = os.path.join(DATA_DIR, "silver")
GOLD_DIR = os.path.join(DATA_DIR, "gold")

# 1. API OpenData Paris (Export complet dynamique au format JSON)
PARIS_OPENDATA_BASE = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/{dataset}/exports/json"
PARIS_OPENDATA_GEOJSON_BASE = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/{dataset}/exports/geojson"

PARIS_DATASETS = {
    "logements_sociaux": {
        "id": "logements-sociaux-finances-a-paris",
        "format": "json"
    },
    "espaces_verts": {
        "id": "espaces_verts",
        "format": "json"
    },
    "velib": {
        "id": "velib-emplacement-des-stations",
        "format": "json"
    },
    "belib": {
        "id": "belib-points-de-recharge-pour-vehicules-electriques-disponibilite-temps-reel",
        "format": "json"
    },
    "stationnement_emplacements": {
        "id": "stationnement-voie-publique-emplacements",
        "format": "json"
    },
    "toilettes": {
        "id": "sanisettesparis",
        "format": "json"
    },
    "ecoles": {
        "id": "etablissements-scolaires-ecoles-elementaires",
        "format": "json"
    },
    "colleges": {
        "id": "etablissements-scolaires-colleges",
        "format": "json"
    },
    "marches": {
        "id": "marches-decouverts",
        "format": "json"
    },
    "culture_events": {
        "id": "que-faire-a-paris-",
        "format": "json"
    },
    "pistes_cyclables": {
        "id": "amenagements-cyclables",
        "format": "json"
    },
    "chantiers": {
        "id": "chantiers-perturbants",
        "format": "json"
    },
    "arrondissements": { # Pour le fond de carte de base
        "id": "arrondissements",
        "format": "geojson"
    }
}

# 2. Data.gouv.fr (téléchargement direct de CSV)
DATA_GOUV_DATASETS = {
    "monuments_historiques": {
        # URL vers la derniere version du CSV (culture.gouv.fr)
        "url": "https://www.data.gouv.fr/api/1/datasets/r/3a52af4a-f9da-4dcc-8110-b07774dfb3bc",
        "format": "csv"
    },
    "musees_france": {
        "url": "https://www.data.gouv.fr/api/1/datasets/r/29406189-15e9-4f2f-9e9d-d18649762198",
        "format": "csv"
    }
}
