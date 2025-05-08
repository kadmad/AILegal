import boto3
from botocore.client import Config
import botocore.exceptions
from app import config

session = boto3.session.Session()
s3_client = session.client(
    service_name='s3',
    endpoint_url=config.S3_ENDPOINT,
    aws_access_key_id=config.S3_ACCESS_KEY,
    aws_secret_access_key=config.S3_SECRET_KEY,
    config=Config(signature_version='s3v4')
)

def upload_file_to_s3(file, filename):
    s3_client.upload_fileobj(file, config.S3_BUCKET, filename)
    print(filename.encode('utf-8'))
    return f"{config.S3_ENDPOINT}/{config.S3_BUCKET}/{filename}"

def ensure_bucket_exists(bucket_name: str):
    try:
        s3_client.head_bucket(Bucket=bucket_name)
    except botocore.exceptions.ClientError as e:
        error_code = int(e.response['Error']['Code'])
        if error_code == 404:
            print(f"Bucket {bucket_name} not found, creating...")
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            raise

# Ensure bucket exists before upload
ensure_bucket_exists(config.S3_BUCKET)