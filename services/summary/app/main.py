"""
Summary Generation Service — entry point.

This service is a long-running Kafka consumer worker.  It listens on the
"extracted-texts" topic, sends each document's text to the OpenAI API for
summarisation, and publishes the result to the "summary-texts" topic.

Pipeline per message:
    Kafka (extracted-texts) → OpenAI summarise → Kafka (summary-texts)

Run directly:
    python main.py
"""

import json
from kafka.consumer import listen
from kafka.producer import send_summary_to_kafka
from openai_client import summarize_text


def process_message(data) -> None:
    """
    Process a single "extracted-texts" Kafka message.

    Steps:
        1. JSON-decode the raw message string received from the consumer.
        2. Send the extracted text to OpenAI for summarisation.
        3. Publish ``{"filename": ..., "summary": ...}`` to "summary-texts".

    Args:
        data: Raw UTF-8 string (JSON) from the Kafka message value, containing:
              - ``filename`` (str): Original filename, forwarded downstream.
              - ``text`` (str): OCR-extracted text to be summarised.
    """
    print("Received:", data)
    data = json.loads(data)
    summary = summarize_text(data['text'])

    payload = {
        "filename": data["filename"],
        "summary": summary
    }
    print("Sending summary:", payload)
    send_summary_to_kafka(payload)


if __name__ == "__main__":
    print("=== Summary Generation Service ===")
    listen(process_message)
