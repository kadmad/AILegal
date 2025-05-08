# AI Legal Document Processing Platform

This project is a microservices-based platform for uploading, extracting, and summarizing legal and medical documents using OCR and LLMs. It uses FastAPI, Kafka, MinIO (S3-compatible), and OpenAI.

## Architecture

- **gateway**: FastAPI service for file upload, S3 storage, and Kafka publishing.
- **ocr_extraction**: Extracts text from uploaded PDFs/images using OCR and publishes to Kafka.
- **summary**: Consumes extracted text, summarizes it using OpenAI, and publishes the summary.

## Directory Structure

```
services/
  gateway/         # FastAPI upload API, S3 client, Kafka producer
  ocr_extraction/  # OCR extraction, S3 client, Kafka consumer/producer
  summary/         # Summarization service, Kafka consumer/producer, OpenAI client
shared/            # (for shared code, if any)
k8s/               # (for Kubernetes manifests, if any)
docker-compose.yml # Multi-service orchestration
Makefile           # Dev utility commands
```

## Getting Started

### Prerequisites

- Docker & Docker Compose
- Python 3.12 (for local dev)
- OpenAI API Key

### Environment Variables

Each service has its own `.env` file. Example variables:

- `S3_ENDPOINT`, `S3_ACCESS_KEY`, `S3_SECRET_KEY`, `S3_BUCKET`
- `KAFKA_BOOTSTRAP_SERVERS`, `KAFKA_TOPIC`
- `OPENAI_API_KEY` (for summary service)

### Running with Docker Compose

```sh
docker compose up --build
```

This will start all services, Kafka, Zookeeper, MinIO, and Kafka UI.

### Development

- To restart a service after code changes:
  ```sh
  make gateway-refresh
  make ocr-refresh
  make summary-refresh
  ```

- To run the gateway locally:
  ```sh
  cd services/gateway
  uvicorn app.main:app --reload
  ```

## API

### File Upload

- `POST /upload` (gateway): Upload a PDF/image file.

### Flow

1. User uploads a file via gateway.
2. File is stored in MinIO (S3).
3. Kafka message triggers OCR extraction.
4. Extracted text is sent to summary service.
5. Summary is generated and published.

## Monitoring

- Kafka UI: [http://localhost:8080](http://localhost:8080)
- MinIO Console: [http://localhost:9001](http://localhost:9001)

## License

MIT License

---

**Note:** Update `.env` files with your credentials and API keys before running.
