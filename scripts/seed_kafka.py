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

    payload = {
        "event_id": str(uuid.uuid4()),
        "event_type": "transaction",
        "payload": {"code_arrondissement": "75108", "prix_m2": "14200"},
        "event_time": datetime.utcnow().isoformat() + "Z",
    }

    producer.send(topic, json.dumps(payload).encode("utf-8"))
    producer.flush()
    producer.close()


if __name__ == "__main__":
    main()
