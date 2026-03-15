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

# MinIO / S3-compatible object storage settings
# TODO (production): S3_ENDPOINT should be omitted for AWS S3 (boto3 resolves it automatically).
#                    Only set this for local MinIO or custom S3-compatible stores.
S3_ENDPOINT = os.getenv("S3_ENDPOINT")          # e.g. "http://minio:9000"

# TODO (production): Replace S3_ACCESS_KEY / S3_SECRET_KEY with IAM Role-based auth
#                    (instance profile or ECS task role). Never put real credentials in .env.
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")      # MinIO root user
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")      # MinIO root password

# TODO (production): S3_BUCKET must be a pre-provisioned bucket (Terraform/CDK).
#                    Enable versioning, SSE-S3 encryption, and block all public access.
S3_BUCKET = os.getenv("S3_BUCKET")              # Target bucket name (e.g. "ailegal-docs")

# Kafka broker and topic for uploaded-file events
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")  # e.g. "kafka:9092"
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC")                          # e.g. "uploaded-files"
