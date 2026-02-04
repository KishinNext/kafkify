from abc import ABC, abstractmethod
from typing import Any, Callable, Coroutine, Dict

from aiokafka import ConsumerRecord


class BaseConsumer(ABC):
    """
    Abstract base class for a message bus that can consume from multiple topics
    and register handlers for message processing.
    """

    @abstractmethod
    def get(
        self, config: Dict[str, Any]
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
