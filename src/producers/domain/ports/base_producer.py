from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, TypeAlias, Union

from src.producers.infrastructure.config.producer_settings import KafkaProducerConfig

SerializableKey: TypeAlias = Optional[Union[str, int, float, bytes]]
SerializableValue: TypeAlias = Union[
    str, int, float, bytes, Dict[str, Any], List[Dict[str, Any]]
]


class BaseProducer(ABC):
    """
    Abstract base class for a message bus producer.
    """

    def __init__(
        self,
        config: KafkaProducerConfig,
        key_deserializer: Optional[Callable] = None,
        value_deserializer: Optional[Callable] = None,
    ):
        """
        Initializes the BaseProducer with configuration and deserializers.

        Args:
            config: The Kafka producer configuration.
            key_deserializer: Optional function to deserialize message keys.
            value_deserializer: Optional function to deserialize message values.
        """
        self.config = config
        self._key_deserializer = key_deserializer
        self._value_deserializer = value_deserializer

    @abstractmethod
    async def start(self) -> None:
        """Initializes and starts the underlying Kafka producer."""
        raise NotImplementedError

    @abstractmethod
    async def stop(self) -> None:
        """Stops the underlying Kafka producer."""
        raise NotImplementedError

    @abstractmethod
    async def send(
        self,
        topic: str,
        key: SerializableKey,
        value: SerializableValue,
    ) -> None:
        """Sends a message to the specified topic.
        Args:
            topic: The Kafka topic to send the message to.
            key: The key of the message, either as a string, bytes, or a JSON-serializable object.
            value: The value of the message, either as a string, bytes, or a JSON-serializable object.
        """
        raise NotImplementedError
