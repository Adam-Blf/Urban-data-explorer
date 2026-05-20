from __future__ import annotations

import argparse
from datetime import date

import polars as pl
from pyspark.sql import SparkSession

from etl.catalog import ALL_SOURCES
from etl.processing import build_silver_records


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Normalize bronze snapshots into silver.")
    parser.add_argument("--snapshot-date", default=str(date.today()))
    return parser.parse_args()


def main() -> None:
    """Normalize the Bronze snapshot into a shared Silver schema."""

    args = parse_args()
    spark = SparkSession.builder.appName("ude-silver-transform").getOrCreate()

    bronze_path = "hdfs://namenode:8020/data/bronze/sources"
    silver_path = "hdfs://namenode:8020/data/silver/sources"

    bronze_df = spark.read.parquet(bronze_path).filter(f"snapshot_date = '{args.snapshot_date}'")
    bronze_rows = [row.asDict(recursive=True) for row in bronze_df.collect()]
    by_source: dict[str, list[dict[str, object]]] = {}
    for row in bronze_rows:
        by_source.setdefault(str(row["source_id"]), []).append(row)

    silver_rows: list[dict[str, object]] = []
    for spec in ALL_SOURCES:
        source_rows = by_source.get(spec.source_id, [])
        if not source_rows:
            continue
        silver_rows.extend(build_silver_records(spec, source_rows))

    if silver_rows:
        silver_frame = pl.DataFrame(silver_rows)
        spark.createDataFrame(silver_frame.to_dicts()).write.mode("append").partitionBy(
            "source_id", "snapshot_date"
        ).parquet(silver_path)

    spark.stop()


if __name__ == "__main__":
    main()
