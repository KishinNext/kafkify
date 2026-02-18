import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from src.producers.infrastructure.adapters.base_producer_adapter import (
    KafkaBaseProducerAdapter,
)
from src.examples.producer_example.entrypoints.api.routers.person_notifier_service import (
    router as person_notifier_router,
)
from src.utils.access_config import config_manager
from src.utils.logging import setup_logging
from src.utils.serializers import default_serializer

setup_logging()
log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    kafka_config = config_manager.get_property("kafka")

    if not kafka_config:
        log.error("Kafka producer configuration is missing.")
        raise RuntimeError("Kafka producer configuration is missing.")

    producer_config_data = kafka_config.get("producer", {}).get("config", {})

    # Defaults
    producer_config = {
        "bootstrap_servers": kafka_config.get("bootstrap_servers", "localhost:9092"),
        "client_id": "example-producer",
        "acks": "all",
        "request_timeout_ms": 40000,
        "max_batch_size": 16384,
        "linger_ms": 5,
        "enable_idempotence": True,
        "retry_backoff_ms": 100,
        "metadata_max_age_ms": 30000,
    }

    producer_config.update(producer_config_data)

    producer = KafkaBaseProducerAdapter(
        config=producer_config,
        key_serializer=default_serializer,
        value_serializer=default_serializer,
    )
    await producer.start()

    app.state.producer = producer

    yield

    await producer.stop()


app = FastAPI(
    title="Kafka Producer API",
    lifespan=lifespan,
)

app.include_router(person_notifier_router)


@app.get("/health-check")
async def health_check():
    return {"message": "Producer OK", "port": 8000}


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_config=config_manager.get_property("logging"),
    )
