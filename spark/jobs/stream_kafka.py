from __future__ import annotations

import json
import os

from pyspark.sql import SparkSession, functions as F, types as T


def write_to_cassandra(df, _batch_id):
    """Persist each micro-batch into Cassandra for fast event access."""

    from cassandra.cluster import Cluster

    host = os.getenv("CASSANDRA_HOST", "cassandra")
    keyspace = os.getenv("CASSANDRA_KEYSPACE", "ude")
    cluster = Cluster([host])
    session = cluster.connect(keyspace)

    rows = df.select(
        "event_type",
        "event_time",
        "event_id",
        "source_id",
        "arrondissement_code",
        "payload",
    ).collect()
    for row in rows:
        session.execute(
            """
            INSERT INTO events_by_type (event_type, event_time, event_id, source_id, arrondissement_code, payload)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                row.event_type,
                row.event_time,
                row.event_id,
                row.source_id,
                row.arrondissement_code,
                json.dumps(row.payload),
            ),
        )

    session.cluster.shutdown()


def main():
    """Consume Kafka events and mirror them to HDFS and Cassandra."""

    spark = SparkSession.builder.appName("ude-stream-kafka").getOrCreate()

    topic = os.getenv("KAFKA_TOPIC", "urban-events")
    broker = os.getenv("KAFKA_BROKER", "kafka:9092")

    schema = T.StructType(
        [
            T.StructField("event_id", T.StringType(), False),
            T.StructField("event_type", T.StringType(), False),
            T.StructField("source_id", T.StringType(), False),
            T.StructField("arrondissement_code", T.StringType(), True),
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

    parsed = raw.select(F.from_json(F.col("value").cast("string"), schema).alias("data")).select("data.*")

    hdfs_query = (
        parsed.writeStream.format("json")
        .option("path", "hdfs://namenode:8020/data/bronze/events")
        .option("checkpointLocation", "hdfs://namenode:8020/data/gold/checkpoints/events")
        .outputMode("append")
        .start()
    )

    cassandra_query = parsed.writeStream.foreachBatch(write_to_cassandra).outputMode("append").start()

    spark.streams.awaitAnyTermination()
    hdfs_query.stop()
    cassandra_query.stop()


if __name__ == "__main__":
    main()
