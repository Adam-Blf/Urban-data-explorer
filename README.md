# Urban Data Explorer

Architecture data de démonstration pour le bloc RNCP40875 :
HDFS, Hive, Spark, Kafka, PostgreSQL, Cassandra, FastAPI et frontend statique.

## Objectif

Centraliser des jeux de données Paris / data.gouv autour de 20 arrondissements :
espaces verts, stationnement, Belib, Velib, sanisettes, aménagements cyclables,
chantiers, écoles, marchés, loisirs, logements sociaux, musées, hôpitaux et médecins.

## Points clés

- **Bronze** : snapshots bruts par source dans HDFS.
- **Silver** : normalisation et typage des champs communs avec **Polars**.
- **Gold** : datamarts arrondissements dans PostgreSQL.
- **Streaming** : Kafka -> Spark Structured Streaming -> HDFS + Cassandra.
- **API** : FastAPI expose le catalogue, les datamarts et les événements.

## Lancer l’infra

```bash
copy .env.example .env
docker compose up -d
docker compose exec namenode bash /scripts/init_hdfs.sh
docker compose exec kafka bash /scripts/create_topic.sh
docker compose exec cassandra bash /scripts/init_cassandra.sh
docker compose exec hive-server bash -lc "hive -f /hive/ddl/bronze.hql"
docker compose exec hive-server bash -lc "hive -f /hive/ddl/silver.hql"
docker compose exec hive-server bash -lc "hive -f /hive/ddl/gold.hql"
```

## Exécuter les pipelines

```bash
docker compose exec spark-master spark-submit --master spark://spark-master:7077 /opt/spark/jobs/batch_ingest.py
docker compose exec spark-master spark-submit --master spark://spark-master:7077 /opt/spark/jobs/transform_silver.py
docker compose exec spark-master spark-submit --master spark://spark-master:7077 /opt/spark/jobs/build_gold.py
docker compose exec spark-master spark-submit --master spark://spark-master:7077 --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1 /opt/spark/jobs/stream_kafka.py
python scripts/seed_kafka.py
docker compose exec hive-server bash -lc "hive -e 'MSCK REPAIR TABLE ude.bronze_sources; MSCK REPAIR TABLE ude.silver_sources;'"
```

## API

- `GET /health`
- `GET /catalog/sources`
- `GET /datamarts/dashboard`
- `GET /datamarts/timeline`
- `GET /events/recent`
- `GET /pipeline/latest`
- OpenAPI: `http://localhost:8000/openapi.json`
- Swagger: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Notes

- `API_TOKEN` dans `.env` active une clé API optionnelle sur les routes métier.
- Les tables PostgreSQL et Cassandra sont initialisées au démarrage via leurs scripts dédiés.
- Le frontend est servi sur `http://localhost:8080`.
- Le rapport de soutenance est généré en `rapport.pdf` avec `python scripts/generate_report_pdf.py`.
