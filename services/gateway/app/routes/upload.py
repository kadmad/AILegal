"""
Gateway Service — upload route.

Exposes the POST /upload endpoint that:
  1. Streams the uploaded file to MinIO via the S3 client.
  2. Publishes a JSON message to the Kafka "uploaded-files" topic so the
     OCR extraction service can pick it up asynchronously.
"""

from fastapi import APIRouter, File, UploadFile
from app.s3.client import upload_file_to_s3
from app.kafka.producer import send_to_kafka

router = APIRouter()

@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    """
    Accept a multipart file upload, store it in MinIO, and notify Kafka.

    Args:
        file: The uploaded file provided via multipart/form-data.

    Returns:
        dict: ``{"file_url": str}`` — the full MinIO URL of the stored object.

    Side effects:
        - Writes the file to the configured S3 bucket.
        - Sends a Kafka message to ``KAFKA_TOPIC`` containing the filename,
          the MinIO URL, and the file extension (used as ``type`` by the OCR
          service to choose the correct extraction strategy).
    """
    file_url = upload_file_to_s3(file.file, file.filename)
    await send_to_kafka({
        "filename": file.filename,
        "file_url": file_url,
        "type": file.filename.split(".")[-1]  # "pdf" or image extension
    })
    return {"file_url": file_url}
