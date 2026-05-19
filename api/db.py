from __future__ import annotations

import os
from contextlib import contextmanager

import psycopg2
from cassandra.cluster import Cluster


@contextmanager
def pg_conn():
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "postgres"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        dbname=os.getenv("POSTGRES_DB", "ude"),
        user=os.getenv("POSTGRES_USER", "ude"),
        password=os.getenv("POSTGRES_PASSWORD", "ude"),
    )
    try:
        yield conn
    finally:
        conn.close()


def cassandra_session():
    host = os.getenv("CASSANDRA_HOST", "cassandra")
    port = int(os.getenv("CASSANDRA_PORT", "9042"))
    keyspace = os.getenv("CASSANDRA_KEYSPACE", "ude")
    cluster = Cluster([host], port=port)
    session = cluster.connect()
    session.set_keyspace(keyspace)
    return session

