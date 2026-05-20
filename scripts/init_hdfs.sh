#!/usr/bin/env bash
set -euo pipefail

hdfs dfs -mkdir -p /data/bronze
hdfs dfs -mkdir -p /data/silver
hdfs dfs -mkdir -p /data/gold/checkpoints
hdfs dfs -mkdir -p /data/gold/dashboard
hdfs dfs -mkdir -p /data/gold/timeline
hdfs dfs -mkdir -p /data/bronze/sources
hdfs dfs -mkdir -p /data/bronze/events
hdfs dfs -mkdir -p /data/silver/sources
hdfs dfs -chmod -R 755 /data

echo "HDFS zones created."
