from abc import ABC, abstractmethod
from typing import Any, Callable, Coroutine, Dict, Optional

from aiokafka import ConsumerRecord

from src.consumers.infrastructure.config.consumer_settings import KafkaConsumerConfig


class BaseConsumer(ABC):
    """
    Abstract base class for a message bus that can consume from multiple topics
    and register handlers for message processing.
    """

    def __init__(
        self,
        config: KafkaConsumerConfig,
        key_deserializer: Optional[Callable] = None,
        value_deserializer: Optional[Callable] = None,
    ):
        """
        Initializes the BaseConsumer with configuration and deserializers.

        Args:
            config: The Kafka consumer configuration.
            key_deserializer: Optional function to deserialize message keys.
            value_deserializer: Optional function to deserialize message values.
        """
        self.config = config
        self._key_deserializer = key_deserializer
        self._value_deserializer = value_deserializer

    @abstractmethod
    def get(
        self,
        config: Dict[str, Any],
    ) -> Callable[[Callable[[ConsumerRecord], Coroutine]], None]:
        """
        A decorator factory for registering message handlers.

        The decorated function will be called to process messages that match
        the criteria specified in the config.

        Args:
            config: A dictionary with configuration for the handler,
                    e.g., {'topic': 'my-topic', 'codes': ['code1', 'code2']}.
        Returns:
            A decorator that registers the processing function.
        """
        raise NotImplementedError

    @abstractmethod
    async def listen(self):
        """
        Starts the consumer to listen for messages and dispatch them to the
        registered handlers.
        """
        raise NotImplementedError

    @abstractmethod
    async def start(self) -> None:
        """Initializes and starts the underlying Kafka consumer."""
        raise NotImplementedError

    @abstractmethod
    async def stop(self) -> None:
        """Stops the underlying Kafka consumer."""
        raise NotImplementedError
