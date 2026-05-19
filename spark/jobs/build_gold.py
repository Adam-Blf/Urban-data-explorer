from __future__ import annotations

import argparse
from datetime import date

from pyspark.sql import SparkSession, functions as F


def parse_args():
    p = argparse.ArgumentParser(description="Gold build (Postgres datamarts).")
    p.add_argument("--ingestion-date", default=str(date.today()))
    return p.parse_args()


def main():
    args = parse_args()
    spark = (
        SparkSession.builder.appName("ude-gold-build")
        .getOrCreate()
    )

    silver = "hdfs://namenode:8020/data/silver"

    tx = spark.read.parquet(
        f"{silver}/transactions/ingestion_date={args.ingestion_date}"
    )
    social = spark.read.parquet(
        f"{silver}/social_housing/ingestion_date={args.ingestion_date}"
    )

    kpi = (
        tx.groupBy("code_arrondissement")
        .agg(
            F.avg("prix_m2").alias("prix_m2"),
        )
        .join(social, on="code_arrondissement", how="left")
        .withColumn("idx_accessibilite", F.lit(None).cast("double"))
        .withColumn("idx_tension", F.lit(None).cast("double"))
        .withColumn("idx_effort_social", F.lit(None).cast("double"))
        .withColumn("idx_attractivite", F.lit(None).cast("double"))
        .withColumn("label", F.col("code_arrondissement"))
    )

    timeline = (
        tx.groupBy("code_arrondissement", "year", "month")
        .agg(F.avg("prix_m2").alias("prix_m2_median"))
    )

    jdbc_url = "jdbc:postgresql://postgres:5432/ude"
    props = {"user": "ude", "password": "ude", "driver": "org.postgresql.Driver"}

    kpi.write.mode("overwrite").jdbc(jdbc_url, "datamart_kpi", properties=props)
    timeline.write.mode("overwrite").jdbc(jdbc_url, "datamart_timeline", properties=props)

    spark.stop()


if __name__ == "__main__":
    main()

