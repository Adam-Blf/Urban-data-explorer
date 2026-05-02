# ADRs · Architectural Decision Records

## ADR-001 · Polars + DuckDB plutôt que Spark Standalone

**Contexte** · Le sujet autorise Spark mais ne l'impose pas. Le volume cible (Paris, ~250k mutations DVF + ~100k POI) tient en RAM et n'a pas besoin de cluster.

**Décision** · Pipeline Bronze/Silver en **Polars** (Rust, multithread, lazy), Gold en **DuckDB** (analytique colonnaire, intégration Parquet native, lecture directe sans import). Spark UI remplacée par des métriques Polars/DuckDB dans les logs.

**Conséquences**
- Démarrage 0 seconde (pas de JVM).
- Empreinte mémoire ~5x plus basse que PySpark.
- Bonus Spark/YARN du sujet non couvert. Acceptable car volume hors zone Spark utile.
- Pour scaler à France entière, migration Polars → PySpark triviale (mêmes verbes).

## ADR-002 · Médaillon avec partitionnement `year/month/day` par date d'ingestion

**Contexte** · Le sujet impose un partitionnement par date d'ingestion sur Bronze + Silver.

**Décision** · `RAW_DIR/<source>/year=YYYY/month=MM/day=DD/<source>.parquet`, idem Silver. Date calculée en UTC à l'ingestion (idempotence stricte par jour).

**Conséquences**
- Pruning naturel par date (même si Polars/DuckDB ne pushent pas le predicate, on lit la dernière partition explicitement via `rglob`).
- Replays sans pollution · rejouer le même jour écrase, pas de doublon.
- Ne capture pas la date métier (`date_mutation`) côté répertoire · cette dimension reste dans les colonnes pour les agrégations.

## ADR-003 · Indicateurs composites en z-score plutôt qu'index 0-100

**Contexte** · 4 indicateurs custom à inventer · accessibilité, tension, effort social, attractivité.

**Décision** · Pour les 3 premiers, formule métier explicite (ratio direct interprétable). Pour `idx_attractivite`, **moyenne pondérée de z-scores** (centrage/réduction par les 20 arrondissements).

**Conséquences**
- L'indice attractivité est comparable et lisible (0 = arrondissement moyen, +1 = un écart-type au-dessus).
- Il évolue mois après mois sans bricolage de bornes.
- Il faut au moins ~10 arrondissements pour que le z soit pertinent (OK avec 20).

## ADR-004 · DuckDB read-only par requête plutôt qu'une connexion partagée

**Contexte** · L'API doit servir le Gold avec faible latence et concurrence.

**Décision** · `gold_connection()` ouvre une connexion DuckDB **read-only** par requête (context manager). DuckDB est thread-safe en lecture concurrente sur le même fichier.

**Conséquences**
- Pas de pool à gérer, pas d'état partagé.
- Latence négligeable (DuckDB s'attache en quelques ms).
- Si le pipeline Gold tourne pendant que l'API sert, la lecture reste cohérente sur la version snapshot du fichier.

## ADR-005 · Frontend statique CDN-only

**Contexte** · Le sujet veut un dashboard JS interactif. Pas d'obligation de framework.

**Décision** · HTML + ESM via CDN (MapLibre + Chart.js), pas de bundler. Code dans `frontend/app.js`, styles dans `frontend/styles.css`.

**Conséquences**
- Démo déployable en 5 min sur n'importe quel static host (Vercel, Netlify, S3, GH Pages).
- Pas de pipeline JS à maintenir.
- Pas de TypeScript · risque limité car surface d'API < 300 lignes.
- Si l'app croît, migration vers Vite/Vue/React reste possible (les modules ESM sont déjà découpés).
