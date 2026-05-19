#!/usr/bin/env bash
set -euo pipefail

hdfs dfs -mkdir -p /data/bronze
hdfs dfs -mkdir -p /data/silver
hdfs dfs -mkdir -p /data/gold/checkpoints
hdfs dfs -chmod -R 755 /data

echo "HDFS zones created."

