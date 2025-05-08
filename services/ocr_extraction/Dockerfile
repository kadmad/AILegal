FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libglib2.0-0 libsm6 libxext6 libxrender-dev \
    poppler-utils

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "app/main.py"]
