import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
EXTRACTED_TOPIC = os.getenv("EXTRACTED_TOPIC", "extracted-texts")
SUMMARY_TOPIC = os.getenv("SUMMARY_TOPIC", "summary-texts")
