from __future__ import annotations

import argparse
from datetime import date

import polars as pl
from pyspark.sql import SparkSession

from etl.catalog import ALL_SOURCES
from etl.processing import build_bronze_records, read_source_frame


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bronze ingest for all catalog sources.")
    parser.add_argument("--snapshot-date", default=str(date.today()))
    return parser.parse_args()


def main() -> None:
    """Fetch every downloadable source and persist Bronze snapshots."""

    args = parse_args()
    spark = SparkSession.builder.appName("ude-bronze-ingest").getOrCreate()
    bronze_path = "hdfs://namenode:8020/data/bronze/sources"

    for spec in ALL_SOURCES:
        if spec.metadata_only:
            continue
        source_frame = read_source_frame(spec)
        bronze_records = build_bronze_records(spec, source_frame, args.snapshot_date)
        if not bronze_records:
            continue
        bronze_polars = pl.DataFrame(bronze_records)
        spark_frame = spark.createDataFrame(bronze_polars.to_dicts())
        spark_frame.write.mode("append").partitionBy("source_id", "snapshot_date").parquet(
            bronze_path
        )

    spark.stop()


if __name__ == "__main__":
    main()
