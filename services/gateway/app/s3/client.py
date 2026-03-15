"""
Gateway Service — S3 / MinIO client.

Creates a module-level boto3 S3 client configured to talk to a MinIO instance.
The client is shared across requests for efficiency (boto3 clients are
thread-safe for read operations and most upload operations).

MinIO requires the ``s3v4`` signature version — standard AWS clients default
to ``s3`` (v2) which MinIO rejects, so ``Config(signature_version='s3v4')``
is mandatory here.
"""

import boto3
from botocore.client import Config
import botocore.exceptions
from app import config

session = boto3.session.Session()

<<<<<<< Updated upstream
# Config(signature_version='s3v4') is required for MinIO compatibility.
# MinIO does not accept the legacy SigV2 signing algorithm used by some
# AWS-default boto3 configurations.
=======
# TODO: convert to AWS S3 for production — remove S3_ENDPOINT and switch to
# IAM-role-based auth (no access key / secret key needed). Also update the
# URL returned by upload_file_to_s3() to use a pre-signed URL or CloudFront.
>>>>>>> Stashed changes
s3_client = session.client(
    service_name='s3',
    endpoint_url=config.S3_ENDPOINT,
    aws_access_key_id=config.S3_ACCESS_KEY,
    aws_secret_access_key=config.S3_SECRET_KEY,
    config=Config(signature_version='s3v4')
)


def upload_file_to_s3(file, filename: str) -> str:
    """
    Upload a file-like object to the configured S3 bucket.

    Args:
        file: A file-like object (e.g. ``UploadFile.file`` from FastAPI).
        filename: The object key / filename to use inside the bucket.

    Returns:
        str: The full URL of the stored object in the format
             ``<S3_ENDPOINT>/<S3_BUCKET>/<filename>``.
    """
    s3_client.upload_fileobj(file, config.S3_BUCKET, filename)
    print(filename.encode('utf-8'))
    return f"{config.S3_ENDPOINT}/{config.S3_BUCKET}/{filename}"


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
