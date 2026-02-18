import logging
from typing import Any, Callable, Dict, Optional

from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError

from src.producers.domain.ports.base_producer import (
    BaseProducer,
    SerializableKey,
    SerializableValue,
)

log = logging.getLogger(__name__)


class KafkaBaseProducerAdapter(BaseProducer):
    def __init__(
        self,
        config: Dict[str, Any],
        key_serializer: Optional[Callable] = None,
        value_serializer: Optional[Callable] = None,
    ):
        super().__init__(config, key_serializer, value_serializer)

        self._producer: Optional[AIOKafkaProducer] = None

    async def start(self) -> None:
        if self._producer:
            return

        log.debug("Starting Kafka Producer...")
        self._producer = AIOKafkaProducer(
            **self.config,
            value_serializer=self._value_deserializer,
            key_serializer=self._key_deserializer,
        )
        await self._producer.start()
        log.debug("Kafka Producer started successfully.")

    async def stop(self) -> None:
        if self._producer:
            log.debug("Stopping Kafka Producer...")
            await self._producer.stop()
            self._producer = None
            log.debug("Kafka Producer stopped.")

    async def send(
        self,
        topic: str,
        value: SerializableValue,
        key: SerializableKey = None,
    ) -> None:
        if not self._producer:
            raise RuntimeError(
                "The producer is not started. Call 'start()' before sending messages."
            )

        try:
            await self._producer.send_and_wait(
                topic=topic,
                value=value,
                key=key,
            )

            log.debug(
                "Message sent successfully.",
                extra={
                    "topic": topic,
                },
            )
            return True

        except KafkaError as e:
            log.error(
                f"Kafka error fatal: {e._get_error_name()}",
                exc_info=True,
                extra={"topic": topic, "key": key},
            )
            raise Exception("Failed to send message to Kafka")
        except Exception:
            log.error(
                "Unexpected error when sending message to Kafka",
                exc_info=True,
                extra={"topic": topic, "key": key},
            )
            raise Exception("Unexpected error when sending message to Kafka")

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()
