from __future__ import annotations

import argparse
from datetime import date

from pyspark.sql import SparkSession, functions as F


def parse_args():
    p = argparse.ArgumentParser(description="Silver transform (clean + normalize).")
    p.add_argument("--ingestion-date", default=str(date.today()))
    return p.parse_args()


def main():
    args = parse_args()
    spark = (
        SparkSession.builder.appName("ude-silver-transform")
        .getOrCreate()
    )

    bronze = "hdfs://namenode:8020/data/bronze"
    silver = "hdfs://namenode:8020/data/silver"

    tx = spark.read.json(
        f"{bronze}/transactions/ingestion_date={args.ingestion_date}"
    )
    tx = tx.withColumn("year", F.year("date_mutation")).withColumn(
        "month", F.month("date_mutation")
    )

    tx.write.mode("overwrite").parquet(
        f"{silver}/transactions/ingestion_date={args.ingestion_date}"
    )

    social = spark.read.json(
        f"{bronze}/social_housing/ingestion_date={args.ingestion_date}"
    )
    social.write.mode("overwrite").parquet(
        f"{silver}/social_housing/ingestion_date={args.ingestion_date}"
    )

    air = spark.read.json(
        f"{bronze}/air_quality/ingestion_date={args.ingestion_date}"
    )
    air.write.mode("overwrite").parquet(
        f"{silver}/air_quality/ingestion_date={args.ingestion_date}"
    )

    spark.stop()


if __name__ == "__main__":
    main()

