from __future__ import annotations

import argparse
from datetime import date
from io import StringIO

import polars as pl
import psycopg2
from pyspark.sql import SparkSession

from etl.catalog import ALL_SOURCES
from etl.processing import build_gold_dashboard, build_gold_timeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build gold mart in PostgreSQL.")
    parser.add_argument("--snapshot-date", default=str(date.today()))
    return parser.parse_args()


def _write_copy(conn, table: str, frame: pl.DataFrame) -> None:
    """Load a dataframe into PostgreSQL with a COPY operation."""

    buffer = StringIO()
    frame.write_csv(buffer)
    buffer.seek(0)
    with conn.cursor() as cursor:
        cursor.execute(f"TRUNCATE TABLE {table}")
        cursor.copy_expert(f"COPY {table} FROM STDIN WITH CSV HEADER", buffer)
    conn.commit()


def _arrondissement_label(code: str) -> str:
    """Generate a human-readable arrondissement label."""

    number = int(code[-2:])
    suffix = "er" if number == 1 else "e"
    return f"Paris {number}{suffix} arrondissement"


def main() -> None:
    """Build Gold marts in PostgreSQL and export parquet snapshots."""

    args = parse_args()
    spark = SparkSession.builder.appName("ude-gold-build").getOrCreate()

    silver_path = "hdfs://namenode:8020/data/silver/sources"
    silver_df = spark.read.parquet(silver_path).filter(f"snapshot_date = '{args.snapshot_date}'")
    silver_rows = [row.asDict(recursive=True) for row in silver_df.collect()]
    silver_frame = pl.DataFrame(silver_rows) if silver_rows else pl.DataFrame()

    dashboard = build_gold_dashboard(silver_frame)
    timeline = build_gold_timeline(silver_frame)
    source_dim = pl.DataFrame(
        [
            {
                "source_id": spec.source_id,
                "title": spec.title,
                "family": spec.family,
                "catalog_url": spec.catalog_url,
                "provider": spec.provider,
                "metadata_only": spec.metadata_only,
            }
            for spec in ALL_SOURCES
        ]
    )
    arrondissement_dim = pl.DataFrame(
        [
            {"code_arrondissement": f"751{i:02d}", "label": _arrondissement_label(f"751{i:02d}")}
            for i in range(1, 21)
        ]
    )

    conn = psycopg2.connect(
        host="postgres",
        port=5432,
        dbname="ude",
        user="ude",
        password="ude",
    )
    try:
        _write_copy(conn, "dim_source", source_dim)
        _write_copy(conn, "dim_arrondissement", arrondissement_dim)
        if not dashboard.is_empty():
            _write_copy(conn, "fact_arrondissement_dashboard", dashboard)
            spark.createDataFrame(dashboard.to_dicts()).write.mode("overwrite").parquet(
                "hdfs://namenode:8020/data/gold/dashboard"
            )
        if not timeline.is_empty():
            _write_copy(conn, "fact_arrondissement_timeline", timeline)
            spark.createDataFrame(timeline.to_dicts()).write.mode("overwrite").parquet(
                "hdfs://namenode:8020/data/gold/timeline"
            )
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO pipeline_runs (run_date, stage, status, row_count) VALUES (%s, %s, %s, %s) "
                "ON CONFLICT (run_date, stage) DO UPDATE SET status = EXCLUDED.status, row_count = EXCLUDED.row_count",
                (args.snapshot_date, "gold", "done", int(dashboard.height + timeline.height)),
            )
        conn.commit()
    finally:
        conn.close()

    spark.stop()


if __name__ == "__main__":
    main()
