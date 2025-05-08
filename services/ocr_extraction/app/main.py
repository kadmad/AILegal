import os
import boto3
from dotenv import load_dotenv
from botocore.client import Config
from kafka.consumer import listen
from kafka.producer import send_to_topic
from ocr.extractor import extract_text_from_file

load_dotenv()

s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("S3_SECRET_KEY"),
    endpoint_url=os.getenv("S3_ENDPOINT"),  # key line for MinIO!
    config=Config(signature_version='s3v4')  # required for MinIO
)

def handle_uploaded_file(data):
    print('data: ', data)
    s3_url = data["file_url"]
    file_type = data["type"]  # "pdf" or "image"

    bucket = os.getenv("S3_BUCKET")
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
