from fastapi import HTTPException, Request

from producers.infrastructure.adapters.base_producer_adapter import (
    KafkaProducerImpl,
)


async def get_kafka_producer(request: Request) -> KafkaProducerImpl:
    producer = getattr(request.app.state, "producer", None)
    if not producer:
        raise HTTPException(status_code=500, detail="Kafka Producer not initialized")
    return producer
