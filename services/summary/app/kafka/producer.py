"""
Summary Generation Service — Kafka producer.

A thin wrapper around confluent-kafka's synchronous Producer that publishes
completed document summaries to the "summary-texts" topic.

The producer is held as a module-level singleton to avoid the overhead of
creating a new broker connection for every message.
"""

from confluent_kafka import Producer
import json
from config import KAFKA_BROKER, SUMMARY_TOPIC

# Module-level producer singleton — connects to the broker at import time.
producer = Producer({'bootstrap.servers': KAFKA_BROKER})


def send_summary_to_kafka(payload: dict) -> None:
    """
    Serialize ``payload`` to JSON and publish it to the summary-texts topic.

    ``producer.flush()`` is called immediately after ``produce()`` to ensure
    the message is delivered before the function returns (synchronous send).

    Args:
        payload: A JSON-serialisable dictionary to publish as the message value.
                 Expected to contain at least ``filename`` and ``summary`` keys.
    """
    producer.produce(SUMMARY_TOPIC, json.dumps(payload).encode("utf-8"))
    producer.flush()
