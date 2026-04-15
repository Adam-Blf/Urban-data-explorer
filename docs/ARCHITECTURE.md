# Architecture

## Pipeline data · Medallion

### Bronze · raw landing
Ingestion brute, aucune transformation. Un fichier par source, horodaté.
`data/bronze/<source>/<YYYY-MM-DD>.json|.geojson|.csv`

### Silver · cleaned + typed
Nettoyage (dédup, null, types), normalisation des clés (code_insee, code_arrondissement), géocodage si nécessaire, stockage parquet.
`data/silver/<entity>.parquet`

### Gold · aggregated + joined
Jointures multi-sources par arrondissement + calcul des 4 indicateurs composites. Prêt à être consommé par l'API.
`data/gold/arrondissements.parquet`, `data/gold/timeseries.parquet`

## API

FastAPI expose :

- `GET /health`
- `GET /arrondissements` · GeoJSON enrichi avec indicateurs courants
- `GET /arrondissements/{code}` · détail d'un arrondissement
- `GET /timeseries/{code}?indicator=prix_m2` · série temporelle
- `GET /compare?a={code}&b={code}` · comparaison deux arrondissements
- `GET /indicators` · liste des indicateurs disponibles

## Frontend

- Carte choroplèthe MapLibre (fond Carto Voyager)
- Sélecteur d'indicateur (prix m², logements sociaux, AQI, délits, 4 composites)
- Timeline scrubber (année)
- Panneau détail on click
- Mode comparaison (2 panneaux côte à côte)
- Accessibilité · contraste AA, navigation clavier, lecture alt des couches

## Qualité / CI

- Tests unitaires pipeline (`pytest pipeline/tests`)
- Lint · ruff
- CI GitHub Actions · `.github/workflows/ci.yml`
- Pipeline planifié quotidien · `.github/workflows/pipeline.yml` (cron 03:00 UTC)
