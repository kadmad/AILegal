"""
Gateway Service — FastAPI entry point.

This service acts as the HTTP-facing front door for the AI Document Analysis platform.
It accepts file uploads from clients, stores them in MinIO (S3-compatible),
and publishes a message to Kafka so downstream services can begin processing.

Lifecycle:
    startup  → initialises the Kafka producer (with retry logic)
    shutdown → gracefully stops the Kafka producer
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routes.upload import router
from app.kafka.producer import init_kafka, close_kafka


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_kafka()
    yield
    await close_kafka()


app = FastAPI(lifespan=lifespan)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
