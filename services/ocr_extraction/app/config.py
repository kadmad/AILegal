"""
OCR Extraction Service — configuration.

Loads all environment variables from a .env file (or the host environment)
at import time.  Centralising configuration here avoids scattered os.getenv()
calls across the codebase and makes it easy to mock settings in tests.
"""

from dotenv import load_dotenv
import os

load_dotenv()

# MinIO / S3-compatible object storage settings
# TODO (production): S3_ENDPOINT should be omitted for AWS S3 (boto3 auto-resolves endpoint).
S3_ENDPOINT = os.getenv("S3_ENDPOINT")          # e.g. "http://minio:9000"

# TODO (production): Use IAM Role / ECS Task Role instead of static access keys.
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")      # MinIO root user
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")      # MinIO root password

# TODO (production): Must reference a pre-provisioned production bucket (via IaC).
S3_BUCKET = os.getenv("S3_BUCKET")              # Bucket where uploaded files are stored

# Kafka broker and the input topic this service consumes from
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")  # e.g. "kafka:9092"
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC")                          # e.g. "uploaded-files"
