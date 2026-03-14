"""
Gateway Service — async Kafka producer.

Wraps aiokafka's AIOKafkaProducer with startup retry logic so the service
can come up before Kafka is fully ready (common in docker-compose environments
where containers start concurrently).

The producer instance is held as a module-level singleton and managed via
the FastAPI lifespan events defined in ``main.py``.
"""

from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaConnectionError
import asyncio
import json
from app import config

# Module-level producer singleton; initialised by init_kafka() at startup.
producer = None


async def init_kafka() -> None:
    """
    Initialise and start the global Kafka producer.

    Retries the connection up to 10 times with a 5-second delay between
    attempts.  This is necessary in docker-compose deployments where the
    Kafka broker may not be ready immediately when the gateway container
    starts.

    Raises:
        RuntimeError: If Kafka cannot be reached after all 10 retries.
    """
    global producer
    producer = AIOKafkaProducer(bootstrap_servers='kafka:9092')

    # Retry loop: Kafka may still be initialising when this service starts.
    # 10 attempts × 5 s = up to 50 s of grace time before giving up.
    for attempt in range(10):
        try:
            await producer.start()
            print("Kafka producer started.")
            return
        except KafkaConnectionError as e:
            print(f"Kafka not ready yet, retrying ({attempt+1}/10)...")
            await asyncio.sleep(5)

    raise RuntimeError("Kafka is not available after 10 retries.")


async def send_to_kafka(data: dict) -> None:
    """
    Serialize ``data`` to JSON and publish it to the configured Kafka topic.

    Args:
        data: A dictionary that will be JSON-encoded and sent as the message
              value.  Must be JSON-serialisable.
    """
    await producer.send_and_wait(config.KAFKA_TOPIC, json.dumps(data).encode('utf-8'))


async def close_kafka() -> None:
    """
    Gracefully stop the Kafka producer.

    Flushes any buffered messages and closes the underlying network connection.
    Should be called during application shutdown.
    """
    await producer.stop()
