"""
Gateway Service — configuration.

Loads all environment variables from a .env file (or the host environment)
at import time.  Every downstream module should import settings from here
rather than calling os.getenv() directly, so configuration is centralised
and easy to override in tests.
"""

from dotenv import load_dotenv
import os

load_dotenv()

# TODO: convert to AWS S3 for production — S3_ENDPOINT, S3_ACCESS_KEY, and
# S3_SECRET_KEY are MinIO-only. On AWS, remove these and use IAM instance role.
S3_ENDPOINT = os.getenv("S3_ENDPOINT")          # e.g. "http://minio:9000"
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")      # MinIO root user
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")      # MinIO root password
S3_BUCKET = os.getenv("S3_BUCKET")              # Target bucket name (e.g. "ailegal-docs")

# Kafka broker and topic for uploaded-file events
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")  # e.g. "kafka:9092"
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC")                          # e.g. "uploaded-files"
