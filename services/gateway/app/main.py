from fastapi import FastAPI
from app.routes.upload import router
from app.kafka.producer import init_kafka, close_kafka

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    await init_kafka()

@app.on_event("shutdown")
async def shutdown_event():
    await close_kafka()

app.include_router(router)
