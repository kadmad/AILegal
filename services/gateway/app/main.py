"""
Gateway Service — FastAPI entry point.

This service acts as the HTTP-facing front door for the AI Document Analysis platform.
It accepts file uploads from clients, stores them in MinIO (S3-compatible),
and publishes a message to Kafka so downstream services can begin processing.

Lifecycle:
    startup  → initialises the Kafka producer (with retry logic)
    shutdown → gracefully stops the Kafka producer
"""

from fastapi import FastAPI
from app.routes.upload import router
from app.kafka.producer import init_kafka, close_kafka

app = FastAPI(title="AI Document Analysis")

@app.on_event("startup")
async def startup_event():
    """
    Called automatically when the FastAPI application starts.

    Initialises the async Kafka producer and waits until a connection
    is established (up to 10 retries with 5-second intervals).
    Raises RuntimeError if Kafka remains unreachable after all retries.
    """
    await init_kafka()

@app.on_event("shutdown")
async def shutdown_event():
    """
    Called automatically when the FastAPI application shuts down.

    Gracefully stops the Kafka producer, flushing any pending messages
    and releasing the underlying network connection.
    """
    await close_kafka()

app.include_router(router)
