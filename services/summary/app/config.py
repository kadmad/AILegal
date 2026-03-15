"""
Summary Generation Service — configuration.

Loads all environment variables from a .env file (or the host environment)
at import time.  Centralising configuration here avoids scattered os.getenv()
calls across the codebase.

NOTE — API key discrepancy:
    This config file exposes ``GEMINI_API_KEY`` (intended for a future Google
    Gemini integration), but ``openai_client.py`` reads ``OPENAI_API_KEY``
    directly from the environment.  Both keys may need to be set in .env
    until the AI provider is unified.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# NOTE: GEMINI_API_KEY is defined here for a planned Gemini integration.
# The current summarisation implementation in openai_client.py uses
# OPENAI_API_KEY instead — ensure that variable is also set in your .env.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Kafka broker address (defaults to the docker-compose service name)
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")

# Topic this service consumes OCR-extracted text from
EXTRACTED_TOPIC = os.getenv("EXTRACTED_TOPIC", "extracted-texts")

# Topic this service publishes finished summaries to
SUMMARY_TOPIC = os.getenv("SUMMARY_TOPIC", "summary-texts")
