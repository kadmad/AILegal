"""
OCR Extraction Service — Kafka consumer.

Creates a module-level confluent-kafka Consumer that subscribes to the
"uploaded-files" topic (read from KAFKA_TOPIC env var).

Consumer configuration notes:
  - ``group.id: ocr_group``          — all OCR worker replicas share this group
    so each message is processed by exactly one worker.
  - ``auto.offset.reset: earliest``  — on first start (or after an offset reset)
    consume from the beginning of the topic so no messages are missed.
"""

from confluent_kafka import Consumer
import json
import os

from dotenv import load_dotenv

load_dotenv()

# Initialise the consumer at import time so it is ready when listen() is called.
consumer = Consumer({
    'bootstrap.servers': os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
    # Consumer group: all OCR service instances share this group id so
    # Kafka distributes partitions among them (each message processed once).
    'group.id': 'ocr_group',
    # Start from the earliest available offset when no committed offset exists.
    'auto.offset.reset': 'earliest'
})
print("----os.environ.get('KAFKA_TOPIC')", os.environ.get('KAFKA_TOPIC'))
consumer.subscribe([os.environ.get('KAFKA_TOPIC')])


def listen(callback) -> None:
    """
    Blocking poll loop — continuously reads messages from the subscribed topic.

    Deserialises each message value from JSON and passes the resulting dict to
    ``callback``.  Messages with errors or empty payloads are silently skipped.

    Args:
        callback: A callable that accepts a single ``dict`` argument.  Called
                  once for every successfully decoded Kafka message.
    """
    while True:
        msg = consumer.poll(1.0)
        print("msg=0", msg)
        if msg is None or msg.error():
            continue
        data = json.loads(msg.value().decode('utf-8'))
        callback(data)
