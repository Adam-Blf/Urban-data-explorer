# Schémas de Données

## 1. Structure du Dataset `arrondissements_stats.geojson` (Gold Layer)
C'est le fichier principal servi par le backend, contenant les limites des arrondissements et les statistiques complètes.

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": { ... },
      "properties": {
        "arrondissement": 11,
        "ev_surface": 150000,
        "nb_toilettes": 12,
        "nb_ecoles": 24,
        "nb_marches": 3,
        "velib_stations": 45,
        "velib_capacite": 1200,
        "nb_belib": 8,
        "nb_parking": 150,
        "nb_monuments": 42,
        "logements_sociaux": 1500,
        "prix_m2": 9500,
        
        // Indicateurs composites (0-100)
        "indice_qdv": 65.4,
        "indice_mobilite": 82.1,
        "indice_culture": 50.0,
        "indice_tension": 78.5
      }
    }
  ]
}
```

## 2. Structure des Datasets de Points (Silver Layer)
Les endpoints comme `/api/dataset/velib` ou `/api/dataset/ecoles` peuvent être exposés sous forme brute (liste JSON) ou GeoJSON si le paramètre `?geojson=true` est passé.

### Format JSON interne:
```json
[
  {
    "nom": "Station République",
    "lat": 48.8675,
    "lon": 2.3638,
    "arrondissement": 11,
    // Champs optionnels selon le dataset
    "capacite": 30,
    "jours_tenue": "Mardi, Jeudi"
  }
]
```

### Format GeoJSON exposé:
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [2.3638, 48.8675]
      },
      "properties": {
        "nom": "Station République",
        "arrondissement": 11,
        "capacite": 30
      }
    }
  ]
}
```
