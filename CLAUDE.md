# AILegal — CLAUDE.md

Developer guide for Claude Code and human contributors working on this codebase.

---

## Architecture Overview

AILegal is an event-driven, microservices platform for ingesting, OCR-extracting,
and AI-summarising legal and medical documents.

```
Client
  │
  │  POST /upload (multipart)
  ▼
┌─────────────────┐       uploaded-files topic
│  gateway        │ ─────────────────────────────► Kafka
│  (FastAPI :8000)│                                  │
└─────────────────┘                                  │
         │                                           ▼
         │ upload file                  ┌──────────────────────┐
         ▼                              │  ocr_extraction      │
      MinIO :9000                       │  (Python worker)     │
      (S3-compatible)                   │  Tesseract OCR       │
                                        └──────────┬───────────┘
                                                   │ extracted-texts topic
                                                   ▼
                                        ┌──────────────────────┐
                                        │  summary             │
                                        │  (Python worker)     │
                                        │  OpenAI gpt-3.5-turbo│
                                        └──────────┬───────────┘
                                                   │ summary-texts topic
                                                   ▼
                                                Kafka
```

---

## Services

| Service          | Path                        | Port  | Description                                    |
|------------------|-----------------------------|-------|------------------------------------------------|
| `gateway`        | `services/gateway/`         | 8000  | FastAPI HTTP entry point; handles uploads      |
| `ocr_extraction` | `services/ocr_extraction/`  | —     | Kafka worker; OCRs files from MinIO            |
| `summary`        | `services/summary/`         | —     | Kafka worker; summarises text via OpenAI       |
| `kafka`          | (docker image)              | 9092  | Event bus                                      |
| `minio`          | (docker image)              | 9000  | S3-compatible object storage                   |
| `kafka-ui`       | (docker image)              | 8080  | Kafka UI for topic inspection                  |

---

## Kafka Topic Flow

```
uploaded-files  →  extracted-texts  →  summary-texts
     ▲                   ▲                   ▲
  gateway           ocr_extraction         summary
  (producer)          (consumer             (consumer
                       + producer)           + producer)
```

| Topic              | Producer         | Consumer         | Payload fields                          |
|--------------------|------------------|------------------|-----------------------------------------|
| `uploaded-files`   | gateway          | ocr_extraction   | `filename`, `file_url`, `type`          |
| `extracted-texts`  | ocr_extraction   | summary          | `filename`, `text`                      |
| `summary-texts`    | summary          | (downstream TBD) | `filename`, `summary`                   |

---

## Running Locally

### Full stack (recommended)

```bash
docker compose up --build
```

This starts all services: gateway, ocr_extraction, summary, kafka, zookeeper,
minio, and kafka-ui.

### Gateway only (hot-reload)

```bash
cd services/gateway
make run
# or directly:
uvicorn app.main:app --reload
```

### Rebuild individual services without restarting the full stack

```bash
make dev-refresh      # rebuild + restart gateway
make ocr-refresh      # rebuild + restart ocr_extraction
make summary-refresh  # rebuild + restart summary
```

---

## Environment Variables

Each service reads from its own `.env` file at `services/<name>/.env`.

### Gateway (`services/gateway/.env`)

| Variable                  | Example                  | Description                        |
|---------------------------|--------------------------|------------------------------------|
| `S3_ENDPOINT`             | `http://minio:9000`      | MinIO endpoint URL                 |
| `S3_ACCESS_KEY`           | `minioadmin`             | MinIO access key                   |
| `S3_SECRET_KEY`           | `minioadmin`             | MinIO secret key                   |
| `S3_BUCKET`               | `legal-docs`             | Target bucket name                 |
| `KAFKA_BOOTSTRAP_SERVERS` | `kafka:9092`             | Kafka broker address               |
| `KAFKA_TOPIC`             | `uploaded-files`         | Topic to publish upload events to  |

### OCR Extraction (`services/ocr_extraction/.env`)

| Variable                  | Example                  | Description                        |
|---------------------------|--------------------------|------------------------------------|
| `S3_ENDPOINT`             | `http://minio:9000`      | MinIO endpoint URL                 |
| `S3_ACCESS_KEY`           | `minioadmin`             | MinIO access key                   |
| `S3_SECRET_KEY`           | `minioadmin`             | MinIO secret key                   |
| `S3_BUCKET`               | `legal-docs`             | Bucket to fetch uploaded files from|
| `KAFKA_BOOTSTRAP_SERVERS` | `kafka:9092`             | Kafka broker address               |
| `KAFKA_TOPIC`             | `uploaded-files`         | Topic to consume from              |

### Summary (`services/summary/.env`)

| Variable          | Example          | Description                                                   |
|-------------------|------------------|---------------------------------------------------------------|
| `OPENAI_API_KEY`  | `sk-...`         | OpenAI API key (used by `openai_client.py`)                  |
| `GEMINI_API_KEY`  | `AIza...`        | Reserved for a planned Gemini integration (unused currently)  |
| `KAFKA_BROKER`    | `kafka:9092`     | Kafka broker address (defaults to `kafka:9092`)               |
| `EXTRACTED_TOPIC` | `extracted-texts`| Topic to consume OCR results from                             |
| `SUMMARY_TOPIC`   | `summary-texts`  | Topic to publish summaries to                                 |

> **Note:** `GEMINI_API_KEY` is defined in `config.py` but the active
> summarisation code in `openai_client.py` uses `OPENAI_API_KEY`.  Both may
> need to be present in `.env` until the AI provider is unified.

---

## Ports Reference

| Service   | Host port | Container port | Purpose                |
|-----------|-----------|----------------|------------------------|
| gateway   | 8000      | 8000           | REST API               |
| kafka     | 9092      | 9092           | Kafka broker           |
| minio     | 9000      | 9000           | S3 API                 |
| minio     | 9001      | 9001           | MinIO web console      |
| kafka-ui  | 8080      | 8080           | Kafka topic browser    |

---

## Key Dependencies

| Service          | Notable packages                                  |
|------------------|---------------------------------------------------|
| gateway          | `fastapi`, `aiokafka`, `boto3`                    |
| ocr_extraction   | `confluent-kafka`, `pytesseract`, `pdf2image`, `Pillow`, `boto3` |
| summary          | `confluent-kafka`, `openai`                       |

Tesseract and Poppler must be installed on the `ocr_extraction` container OS
(handled in its `Dockerfile`).

---

## Notes for Claude Code

- All Python services follow the same config pattern: import from `config.py`
  rather than calling `os.getenv()` directly in business logic.
- MinIO requires `Config(signature_version='s3v4')` in every boto3 client —
  do not remove this.
- The gateway Kafka producer uses `aiokafka` (async); the worker services use
  `confluent-kafka` (sync/blocking). Keep this distinction when adding code.
- There is no frontend in this repository yet.
