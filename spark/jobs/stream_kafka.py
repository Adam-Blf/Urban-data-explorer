from __future__ import annotations

import json
import os

from pyspark.sql import SparkSession, functions as F, types as T


def write_to_cassandra(df, _batch_id):
    from cassandra.cluster import Cluster

    host = os.getenv("CASSANDRA_HOST", "cassandra")
    keyspace = os.getenv("CASSANDRA_KEYSPACE", "ude")
    cluster = Cluster([host])
    session = cluster.connect(keyspace)

    rows = df.select("event_id", "event_type", "payload", "event_time").collect()
    for r in rows:
        session.execute(
            """
            INSERT INTO events_by_type (event_type, event_time, event_id, payload)
            VALUES (%s, %s, %s, %s)
            """,
            (r.event_type, r.event_time, r.event_id, json.dumps(r.payload)),
        )

    session.cluster.shutdown()


def main():
    spark = (
        SparkSession.builder.appName("ude-stream-kafka")
        .getOrCreate()
    )

    topic = os.getenv("KAFKA_TOPIC", "urban-events")
    broker = os.getenv("KAFKA_BROKER", "kafka:9092")

    schema = T.StructType(
        [
            T.StructField("event_id", T.StringType(), False),
            T.StructField("event_type", T.StringType(), False),
            T.StructField("payload", T.MapType(T.StringType(), T.StringType()), False),
            T.StructField("event_time", T.TimestampType(), False),
        ]
    )

    raw = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", broker)
        .option("subscribe", topic)
        .option("startingOffsets", "latest")
        .load()
    )

    parsed = raw.select(
        F.from_json(F.col("value").cast("string"), schema).alias("data")
    ).select("data.*")

    hdfs_path = "hdfs://namenode:8020/data/bronze/events"
    checkpoint = "hdfs://namenode:8020/data/gold/checkpoints/events"

    hdfs_query = (
        parsed.writeStream.format("json")
        .option("path", hdfs_path)
        .option("checkpointLocation", checkpoint)
        .outputMode("append")
        .start()
    )

    cassandra_query = (
        parsed.writeStream.foreachBatch(write_to_cassandra)
        .outputMode("append")
        .start()
    )

    hdfs_query.awaitTermination()
    cassandra_query.awaitTermination()


if __name__ == "__main__":
    main()

