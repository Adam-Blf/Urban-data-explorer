# Urban Data Explorer v2 (HDFS + Hive + Spark)

Une architecture data complete pour le logement a Paris :
data lake HDFS, Hive SQL, Spark batch + streaming, Kafka, PostgreSQL, Cassandra,
et une API FastAPI + frontend statique pour l acces universel.

## Architecture (vue d ensemble)
1. **Bronze** : ingestion brute HDFS (CSV/JSON) partitionnee par ingestion_date.
2. **Silver** : nettoyage + normalisation en parquet HDFS, catalogue Hive.
3. **Gold** : data marts dans PostgreSQL + acces rapide Cassandra.
4. **Streaming** : Kafka -> Spark Structured Streaming -> HDFS + Cassandra.
5. **API** : FastAPI lit Postgres (analytics) et Cassandra (events).

## Stack
- HDFS + Hive (data lake + SQL)
- Spark (batch + streaming)
- Kafka (event streaming)
- PostgreSQL (marts relationnels)
- Cassandra (NoSQL / semi-structure)
- FastAPI (API)
- Frontend statique (MapLibre + Chart.js)

## Demarrage rapide (local, Docker Compose)
1. Copier env :
   - `copy .env.example .env` (Windows) ou `cp .env.example .env`
2. Lancer infra :
   - `docker compose up -d`
3. Creer les zones HDFS :
   - `docker compose exec namenode bash /scripts/init_hdfs.sh`
4. Creer le topic Kafka :
   - `docker compose exec kafka bash /scripts/create_topic.sh`
5. Init Cassandra :
   - `docker compose exec cassandra bash /scripts/init_cassandra.sh`
6. DDL Hive :
   - `docker compose exec hive-server bash -lc "hive -f /hive/ddl/bronze.hql"`
   - `docker compose exec hive-server bash -lc "hive -f /hive/ddl/silver.hql"`
7. Batch ingest (Bronze -> Silver) :
   - `docker compose exec spark-master spark-submit --master spark://spark-master:7077 /opt/spark/jobs/batch_ingest.py`
   - `docker compose exec spark-master spark-submit --master spark://spark-master:7077 /opt/spark/jobs/transform_silver.py`
8. Gold (Postgres) :
   - `docker compose exec spark-master spark-submit --master spark://spark-master:7077 --packages org.postgresql:postgresql:42.7.3 /opt/spark/jobs/build_gold.py`
9. Streaming (Kafka -> HDFS + Cassandra) :
   - `docker compose exec spark-master spark-submit --master spark://spark-master:7077 --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1 /opt/spark/jobs/stream_kafka.py`
   - `python scripts/seed_kafka.py`
10. API + frontend :
   - `docker compose up -d api frontend`
   - API : `http://localhost:8000/docs`
   - Frontend : `http://localhost:8080`

## Data layout (HDFS)
```
/data/bronze/<source>/ingestion_date=YYYY-MM-DD/*.json
/data/silver/<domain>/ingestion_date=YYYY-MM-DD/*.parquet
/data/gold/ (checkpoints + refs Hive)
```

## Securite + gouvernance (local)
- Permissions HDFS actives (service user ingestion).
- Tables Hive externes en lecture sur Silver.
- API expose uniquement Gold.

## Scalabilite
- Spark workers scalable : `docker compose up -d --scale spark-worker=2`
- Kafka partitions ajustables pour le debit.
- Cassandra pret pour multi-noeuds (non active en local).

## Structure
```
api/                  FastAPI
frontend/             Front statique
spark/jobs/           Jobs Spark batch + streaming
hive/ddl/             DDL Hive
postgres/init.sql     Schema relationnel
cassandra/schema.cql  Schema NoSQL
scripts/              Ops (HDFS init, Kafka seed)
```

## Auteurs
- Emilien Morice
- Adam Beloucif
