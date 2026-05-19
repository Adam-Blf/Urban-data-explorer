# Copilot instructions (Urban Data Explorer v2)

## Build, run, test
- **Infra:** `docker compose up -d`
- **Init HDFS:** `docker compose exec namenode bash /scripts/init_hdfs.sh`
- **Topic Kafka:** `docker compose exec kafka bash /scripts/create_topic.sh`
- **Schema Cassandra:** `docker compose exec cassandra bash /scripts/init_cassandra.sh`
- **DDL Hive:** `docker compose exec hive-server bash -lc "hive -f /hive/ddl/bronze.hql"`
- **Spark batch:** `docker compose exec spark-master spark-submit --master spark://spark-master:7077 /opt/spark/jobs/batch_ingest.py`
- **Spark streaming:** `docker compose exec spark-master spark-submit --master spark://spark-master:7077 --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1 /opt/spark/jobs/stream_kafka.py`
- **API:** `docker compose up -d api` (docs: `http://localhost:8000/docs`)
- **Frontend:** `docker compose up -d frontend` (UI: `http://localhost:8080`)
- **Test unitaire:** aucun pour le moment

## Architecture (big picture)
- **Data Lake HDFS** en Bronze/Silver/Gold; tables Hive externes pour SQL.
- **Spark** gere batch + streaming Kafka.
- **PostgreSQL** pour Gold relationnel; **Cassandra** pour events semi-structures.
- **FastAPI** expose les datamarts et les events.

## Conventions
- **Tous les chemins** sont sous HDFS (`/data/bronze`, `/data/silver`, `/data/gold`).
- **DDL Hive** aligne sur les sorties Spark (parquet en Silver).
- **Streaming** ecrit HDFS (append) + Cassandra (events).
- **Config env** via `.env` uniquement.
