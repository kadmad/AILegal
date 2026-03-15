"""
Summary Generation Service — Kafka consumer.

Creates a new confluent-kafka Consumer inside ``listen()`` so the connection
is established lazily when the worker starts, rather than at import time.

Consumer configuration notes:
  - ``group.id: analysis-group``     — all summary worker replicas share this
    group so each extracted-text message is summarised exactly once.
  - ``auto.offset.reset: earliest``  — process from the start of the topic on
    first launch so no documents are missed during initial deployment.
"""

from confluent_kafka import Consumer
from config import KAFKA_BROKER, EXTRACTED_TOPIC


def listen(callback) -> None:
    """
    Create a Kafka consumer, subscribe to the extracted-texts topic, and
    enter a blocking poll loop.

    The consumer is created inside this function (not at module level) so
    that multiple workers can be launched in separate processes without
    sharing a single connection.

    Messages are passed to ``callback`` as raw UTF-8 strings (not yet
    JSON-decoded) — decoding is intentionally deferred to the caller so this
    module stays decoupled from the message schema.

    Args:
        callback: A callable that accepts a single ``str`` argument (the raw
                  JSON message value).  Called once per successfully received
                  Kafka message.
    """
    c = Consumer({
        'bootstrap.servers': KAFKA_BROKER,
        # Consumer group: share partitions among all running summary workers
        'group.id': 'analysis-group',
        # Start from the earliest offset when no prior commit exists
        'auto.offset.reset': 'earliest',
    })
    c.subscribe([EXTRACTED_TOPIC])

    print("Listening to extracted-texts...")
    while True:
        msg = c.poll(1.0)
        if msg is None or msg.error():
            continue
        data = msg.value().decode('utf-8')
        callback(data)
