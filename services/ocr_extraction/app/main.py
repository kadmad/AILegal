"""
OCR Extraction Service — entry point.

This service is a long-running Kafka consumer worker.  It listens on the
"uploaded-files" topic, fetches each file from MinIO, runs OCR to extract
text, and publishes the result to the "extracted-texts" topic for the
summary service to consume.

Pipeline per message:
    Kafka (uploaded-files) → MinIO fetch → OCR → Kafka (extracted-texts)

Run directly:
    python main.py
"""

import os
import boto3
from dotenv import load_dotenv
from botocore.client import Config
from kafka.consumer import listen
from kafka.producer import send_to_topic
from ocr.extractor import extract_text_from_file

load_dotenv()

# Initialise the S3 client.
# Config(signature_version='s3v4') is required for MinIO and is also safe for
# real AWS S3.  S3_ENDPOINT is optional: set it for local MinIO dev (e.g.
# "http://minio:9000"); leave it unset in production to connect to AWS S3.
_s3_kwargs = dict(
    aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("S3_SECRET_KEY"),
    config=Config(signature_version='s3v4')
)
_s3_endpoint = os.getenv("S3_ENDPOINT")
if _s3_endpoint:
    _s3_kwargs["endpoint_url"] = _s3_endpoint

s3 = boto3.client('s3', **_s3_kwargs)


def handle_uploaded_file(data: dict) -> None:
    """
    Process a single "uploaded-files" Kafka message.

    Steps:
        1. Parse the S3 URL and bucket name to derive the object key.
        2. Download the raw file bytes from MinIO.
        3. Run OCR (PDF → page images → Tesseract, or image → Tesseract directly).
        4. Publish ``{"filename": ..., "text": ...}`` to the "extracted-texts" topic.

    Args:
        data: Decoded Kafka message payload with keys:
              - ``file_url`` (str): Full MinIO URL of the uploaded file.
              - ``type`` (str): File extension — ``"pdf"`` or an image type
                (``"png"``, ``"jpg"``, etc.).
              - ``filename`` (str): Original filename, forwarded downstream.
    """
    print('data: ', data)
    s3_url = data["file_url"]
    file_type = data["type"]  # "pdf" or an image extension

    bucket = os.getenv("S3_BUCKET")
    # Extract the object key by stripping the bucket prefix from the full URL
    key = s3_url.split(f"{bucket}/")[-1]

    print('bucket: ', bucket)
    print('key: ', key)
    obj = s3.get_object(Bucket=bucket, Key=key)
    file_bytes = obj['Body'].read()

    extracted_text = extract_text_from_file(file_bytes, file_type)
    print('extracted_text: ', extracted_text)

    send_to_topic("extracted-texts", {
        "filename": data["filename"],
        "text": extracted_text
    })


if __name__ == "__main__":
    print("=== OCR Extraction Service ===")
    print("Listening for uploaded files...")
    listen(handle_uploaded_file)
