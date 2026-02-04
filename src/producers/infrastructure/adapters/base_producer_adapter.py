import json
import logging
from typing import Any, Dict, Optional, Union

from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError

from src.producers.domain.ports.producer import BaseProducer as PortProducer
from producers.infrastructure.config.producer_settings import KafkaProducerConfig

log = logging.getLogger(__name__)


class KafkaProducerImpl(PortProducer):
    def __init__(self, config: KafkaProducerConfig):
        self.config = config
        self._producer: Optional[AIOKafkaProducer] = None

    async def start(self) -> None:
        if self._producer:
            return

        log.debug("Starting Kafka Producer...")
        self._producer = AIOKafkaProducer(
            bootstrap_servers=self.config.bootstrap_servers,
            client_id=self.config.client_id,
            acks=self.config.acks,
            request_timeout_ms=self.config.request_timeout_ms,
            max_batch_size=self.config.max_batch_size,
            linger_ms=self.config.linger_ms,
            enable_idempotence=self.config.enable_idempotence,
            value_serializer=self._default_serializer,
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
        value: Union[Dict[str, Any], str, bytes],
        key: Optional[str] = None,
    ) -> None:
        if not self._producer:
            raise RuntimeError(
                "The producer is not started. Call 'start()' before sending messages."
            )

        key_bytes = key.encode("utf-8") if key else None

        try:
            await self._producer.send_and_wait(
                topic=topic,
                value=value,
                key=key_bytes,
            )

            log.debug(
                "Message sent successfully.",
                extra={
                    "topic": topic,
                },
            )
            return True

        except KafkaError:
            log.error(
                "Errot to send message to Kafka",
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

    def _default_serializer(self, value: Any) -> bytes:
        if isinstance(value, dict):
            return json.dumps(value).encode("utf-8")
        elif isinstance(value, str):
            return value.encode("utf-8")
        elif isinstance(value, bytes):
            return value
        return str(value).encode("utf-8")

    def status(self):
        return "started" if self._producer else "stopped"

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()
