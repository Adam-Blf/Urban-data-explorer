#!/usr/bin/env bash
set -euo pipefail

kafka-topics.sh --bootstrap-server kafka:9092 --create --if-not-exists \
  --topic urban-events --replication-factor 1 --partitions 3

