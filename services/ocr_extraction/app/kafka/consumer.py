from confluent_kafka import Consumer
import json
import os

from dotenv import load_dotenv
load_dotenv()
consumer = Consumer({
    'bootstrap.servers': os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
    'group.id': 'ocr_group',
    'auto.offset.reset': 'earliest'
})
print("----os.environ.get('KAFKA_TOPIC')",os.environ.get('KAFKA_TOPIC'))
consumer.subscribe([os.environ.get('KAFKA_TOPIC')])

def listen(callback):

    while True:
        msg = consumer.poll(1.0)
        print("msg=0", msg)
        if msg is None or msg.error():
            continue
        data = json.loads(msg.value().decode('utf-8'))
        callback(data)
