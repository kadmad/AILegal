from fastapi import APIRouter, File, UploadFile
from app.s3.client import upload_file_to_s3
from app.kafka.producer import send_to_kafka

router = APIRouter()

@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    file_url = upload_file_to_s3(file.file, file.filename)
    await send_to_kafka({
        "filename": file.filename,
        "file_url": file_url,
        "type": file.filename.split(".")[-1]  # "pdf" or "image"
    })
    return {"file_url": file_url}
