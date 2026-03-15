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

# Config(signature_version='s3v4') is required for MinIO compatibility.
# MinIO does not accept the legacy SigV2 signing algorithm used by some
# AWS-default boto3 configurations.
s3_client = session.client(
    service_name='s3',
    # TODO (production): Remove `endpoint_url` for AWS S3. It is only needed for MinIO.
    #                    When omitted, boto3 resolves the correct regional AWS endpoint automatically.
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
    # TODO (production): This constructs a MinIO-style URL. For AWS S3, use one of:
    #   - Virtual-hosted style: f"https://{config.S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{filename}"
    #   - Presigned URL (preferred for secure access): s3_client.generate_presigned_url(...)
    #   Store only the object key in Kafka messages; generate URLs on demand.
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
        # TODO (production): Never auto-create S3 buckets at runtime. Bucket creation must be
        #                    handled by IaC (Terraform/CDK) with proper policies, CORS rules,
        #                    lifecycle configuration, and logging. Remove this block for production.
        if error_code == 404:
            print(f"Bucket {bucket_name} not found, creating...")
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            raise


# TODO (production): Remove this call. Bucket existence should be guaranteed by IaC before
#                    the application starts. This call will fail if IAM role lacks s3:CreateBucket.
ensure_bucket_exists(config.S3_BUCKET)
