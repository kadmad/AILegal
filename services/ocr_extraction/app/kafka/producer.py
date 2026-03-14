"""
OCR Extraction Service — Kafka producer.

A thin wrapper around confluent-kafka's synchronous Producer.
The producer is shared as a module-level singleton across all calls so we
avoid the overhead of creating a new connection for every message.
"""

from confluent_kafka import Producer
import json
import os

# Module-level producer singleton — connects to the broker at import time.
producer = Producer({'bootstrap.servers': os.getenv("KAFKA_BOOTSTRAP_SERVERS")})


def send_to_topic(topic: str, message: dict) -> None:
    """
    Serialize ``message`` to JSON and publish it to the given Kafka topic.

    ``producer.flush()`` is called immediately after ``produce()`` to ensure
    the message is delivered before the function returns (synchronous send).

    Args:
        topic: The Kafka topic name to publish to (e.g. ``"extracted-texts"``).
        message: A JSON-serialisable dictionary to send as the message value.
    """
    producer.produce(topic, json.dumps(message).encode('utf-8'))
    producer.flush()
