from __future__ import annotations

import argparse
from datetime import date

from pyspark.sql import SparkSession


def parse_args():
    p = argparse.ArgumentParser(description="Bronze ingest (synthetic seed).")
    p.add_argument("--ingestion-date", default=str(date.today()))
    return p.parse_args()


def main():
    args = parse_args()
    spark = (
        SparkSession.builder.appName("ude-bronze-ingest")
        .getOrCreate()
    )

    base = "hdfs://namenode:8020/data/bronze"

    transactions = spark.createDataFrame(
        [
            ("75101", "2024-01-15", 12500.0, 48.86, 2.35),
            ("75108", "2024-01-20", 14200.0, 48.87, 2.32),
            ("75115", "2024-02-02", 11000.0, 48.84, 2.30),
        ],
        ["code_arrondissement", "date_mutation", "prix_m2", "lat", "lon"],
    )

    social = spark.createDataFrame(
        [
            ("75101", 2024, 120),
            ("75108", 2024, 210),
            ("75115", 2024, 180),
        ],
        ["code_arrondissement", "year", "nb_logements_finances"],
    )

    air = spark.createDataFrame(
        [
            ("2024-01-15", 32.5),
            ("2024-01-16", 28.1),
        ],
        ["date_obs", "aqi_mean_paris"],
    )

    transactions.write.mode("overwrite").json(
        f"{base}/transactions/ingestion_date={args.ingestion_date}"
    )
    social.write.mode("overwrite").json(
        f"{base}/social_housing/ingestion_date={args.ingestion_date}"
    )
    air.write.mode("overwrite").json(
        f"{base}/air_quality/ingestion_date={args.ingestion_date}"
    )

    spark.stop()


if __name__ == "__main__":
    main()

