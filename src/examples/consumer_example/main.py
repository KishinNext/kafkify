import logging
import asyncio
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from src.consumers.infrastructure.adapters.base_consumer_adapter import (
    KafkaBaseConsumerAdapter,
)
from src.consumers.infrastructure.config.consumer_settings import KafkaConsumerConfig
from src.examples.consumer_example.entrypoints.api.routers.events.router import (
    main_event_router,
)
from src.utils.access_config import config_manager
from src.utils.deserializers import default_deserializer
from src.utils.logging import setup_logging

setup_logging()
log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    kafka_config = config_manager.get_property("kafka")
    consumer_config = kafka_config.get("consumer", {}).get("config", {})

    if not kafka_config:
        log.error("Kafka consumer configuration is missing.")
        raise RuntimeError("Kafka consumer configuration is missing.")

    consumer_config = KafkaConsumerConfig(
        bootstrap_servers=kafka_config.get("bootstrap_servers", "localhost:9092"),
        group_id=consumer_config.get("group_id", "example-consumer-group"),
        enable_auto_commit=consumer_config.get("enable_auto_commit", False),
        auto_offset_reset=consumer_config.get("auto_offset_reset", "earliest"),
        isolation_level=consumer_config.get("isolation_level", "read_committed"),
        max_poll_interval_ms=consumer_config.get("max_poll_interval_ms", 300000),
    )

    consumer = KafkaBaseConsumerAdapter(
        config=consumer_config,
        key_deserializer=default_deserializer,
        value_deserializer=default_deserializer,
    )

    # Register all handlers from the main domain router
    main_event_router.register_handlers(consumer)

    await consumer.start()
    app.state.consumer = consumer

    consumer_task = asyncio.create_task(consumer.listen())

    yield

    await consumer.stop()
    
    try:
        await consumer_task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="Kafka Consumer API",
    lifespan=lifespan,
)


@app.get("/health-check")
async def health_check():
    return {"message": "Consumer OK", "port": 8000}


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_config=config_manager.get_property("logging"),
    )
