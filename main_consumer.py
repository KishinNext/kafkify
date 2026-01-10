import logging
from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI

from consumers.basic_consumer import router as basic_consumer_router
from consumers.basic_consumer import stop_background_consumer
from utils.logging import get_logging_config, setup_logging

setup_logging()
log = logging.getLogger(__name__)
load_dotenv(verbose=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Consumer server started on http://localhost:8001")

    yield

    log.info("Consumer server shutting down")
    await stop_background_consumer()


app = FastAPI(
    title="Kafka Consumer API",
    description="API to consume messages from Kafka in background",
    lifespan=lifespan,
)
app.include_router(basic_consumer_router)


@app.get("/health-check")
async def health_check():
    return {"message": "Consumer OK", "port": 8001}


if __name__ == "__main__":
    uvicorn.run(
        app, host="0.0.0.0", port=8001, log_config=get_logging_config()["logging"]
    )
