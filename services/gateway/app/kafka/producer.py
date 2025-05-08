from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaConnectionError
import asyncio
import json
from app import config

producer = None

async def init_kafka():
    global producer
    producer = AIOKafkaProducer(bootstrap_servers='kafka:9092')

    for attempt in range(10):  # Retry up to 10 times
        try:
            await producer.start()
            print("Kafka producer started.")
            return
        except KafkaConnectionError as e:
            print(f"Kafka not ready yet, retrying ({attempt+1}/10)...")
            await asyncio.sleep(5)

    raise RuntimeError("Kafka is not available after 10 retries.")

async def send_to_kafka(data: dict):
    await producer.send_and_wait(config.KAFKA_TOPIC, json.dumps(data).encode('utf-8'))

async def close_kafka():
    await producer.stop()
