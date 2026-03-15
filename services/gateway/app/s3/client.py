"""
Gateway Service — S3 / MinIO client.

Creates a module-level boto3 S3 client configured to talk to either a MinIO
instance (local dev) or real AWS S3 (production).  The client is shared across
requests for efficiency (boto3 clients are thread-safe for read operations and
most upload operations).

``Config(signature_version='s3v4')`` is required for MinIO compatibility.
It is also safe and recommended for real AWS S3.

``S3_ENDPOINT`` is optional.  Set it to your MinIO URL (e.g.
``http://minio:9000``) for local development.  Leave it unset (or empty) in
production so boto3 connects directly to AWS S3.
"""

import boto3
from botocore.client import Config
import botocore.exceptions
from app import config

session = boto3.session.Session()

s3_kwargs = dict(
    aws_access_key_id=config.S3_ACCESS_KEY,
    aws_secret_access_key=config.S3_SECRET_KEY,
    config=Config(signature_version='s3v4')
)
if config.S3_ENDPOINT:
    s3_kwargs["endpoint_url"] = config.S3_ENDPOINT

s3_client = session.client(service_name='s3', **s3_kwargs)


def upload_file_to_s3(file, filename: str) -> str:
    """
    Upload a file-like object to the configured S3 bucket.

    Args:
        file: A file-like object (e.g. ``UploadFile.file`` from FastAPI).
        filename: The object key / filename to use inside the bucket.

    Returns:
        str: The full URL of the stored object.  For MinIO/local dev this is
             ``<S3_ENDPOINT>/<S3_BUCKET>/<filename>``; for real AWS S3 this is
             ``https://<S3_BUCKET>.s3.amazonaws.com/<filename>``.
    """
    s3_client.upload_fileobj(file, config.S3_BUCKET, filename)
    print(filename.encode('utf-8'))
    if config.S3_ENDPOINT:
        return f"{config.S3_ENDPOINT}/{config.S3_BUCKET}/{filename}"
    return f"https://{config.S3_BUCKET}.s3.amazonaws.com/{filename}"


def ensure_bucket_exists(bucket_name: str) -> None:
    """
    Check whether the given bucket exists; create it if it does not.

    This is called once at module import time so the bucket is always ready
    before the first upload request arrives.

    Args:
        bucket_name: The name of the S3/MinIO bucket to check or create.

    Raises:
        botocore.exceptions.ClientError: Re-raised for any error other than
            a 404 "bucket not found" response.
    """
    try:
        s3_client.head_bucket(Bucket=bucket_name)
    except botocore.exceptions.ClientError as e:
        error_code = int(e.response['Error']['Code'])
        if error_code == 404:
            print(f"Bucket {bucket_name} not found, creating...")
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            raise


# Ensure the bucket exists before the application starts serving requests.
ensure_bucket_exists(config.S3_BUCKET)
