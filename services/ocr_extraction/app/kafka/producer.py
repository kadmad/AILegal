from confluent_kafka import Producer
import json
import os

producer = Producer({'bootstrap.servers': os.getenv("KAFKA_BOOTSTRAP_SERVERS")})

def send_to_topic(topic, message: dict):
    producer.produce(topic, json.dumps(message).encode('utf-8'))
    producer.flush()
