from fastapi import HTTPException, Request

from src.producers.infrastructure.adapters.base_producer_adapter import (
    KafkaBaseProducerAdapter,
)


async def get_kafka_producer(request: Request) -> KafkaBaseProducerAdapter:
    """
    Dependency to get the Kafka producer from the FastAPI app state.
    Args:
        request: The FastAPI request object.
    """
    producer = getattr(request.app.state, "producer", None)
    if not producer:
        raise HTTPException(status_code=500, detail="Kafka Producer not initialized")
    return producer
