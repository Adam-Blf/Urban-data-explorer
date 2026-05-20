from __future__ import annotations

import json
import os
import uuid
from datetime import datetime

from kafka import KafkaProducer


def main():
    broker = os.getenv("KAFKA_BROKER", "localhost:9092")
    topic = os.getenv("KAFKA_TOPIC", "urban-events")

    producer = KafkaProducer(bootstrap_servers=broker)

    events = [
        {
            "event_id": str(uuid.uuid4()),
            "event_type": "service_snapshot",
            "source_id": "velib_disponibilite",
            "arrondissement_code": "75108",
            "payload": {"is_renting": "true", "is_installed": "true", "name": "Parc Monceau"},
            "event_time": datetime.utcnow().isoformat() + "Z",
        },
        {
            "event_id": str(uuid.uuid4()),
            "event_type": "service_snapshot",
            "source_id": "sanisettesparis",
            "arrondissement_code": "75101",
            "payload": {"statut": "Ouverte", "acces_pmr": "Oui"},
            "event_time": datetime.utcnow().isoformat() + "Z",
        },
    ]

    for payload in events:
        producer.send(topic, json.dumps(payload).encode("utf-8"))
    producer.flush()
    producer.close()


if __name__ == "__main__":
    main()
