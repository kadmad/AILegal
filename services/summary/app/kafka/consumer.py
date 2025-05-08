from confluent_kafka import Consumer
from config import KAFKA_BROKER, EXTRACTED_TOPIC

def listen(callback):
    c = Consumer({
        'bootstrap.servers': KAFKA_BROKER,
        'group.id': 'analysis-group',
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
