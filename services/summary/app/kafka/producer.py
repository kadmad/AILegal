from confluent_kafka import Producer
import json
from config import KAFKA_BROKER, SUMMARY_TOPIC

producer = Producer({'bootstrap.servers': KAFKA_BROKER})

def send_summary_to_kafka(payload):
    producer.produce(SUMMARY_TOPIC, json.dumps(payload).encode("utf-8"))
    producer.flush()
