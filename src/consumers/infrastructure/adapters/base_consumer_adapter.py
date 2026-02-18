import asyncio
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable, Coroutine, Dict, List, Optional, Set

from aiokafka import AIOKafkaConsumer, ConsumerRecord, TopicPartition
from aiokafka.errors import (
    CommitFailedError,
    IllegalGenerationError,
    UnknownMemberIdError,
)

from src.consumers.domain.ports.base_consumer import BaseConsumer
from src.consumers.infrastructure.adapters.base_rebalance_listener import (
    RebalanceHandler,
)

log = logging.getLogger(__name__)


@dataclass
class Handler:
    """Represents a registered message handler and its filters."""

    func: Callable[[ConsumerRecord], Coroutine]
    topic: str
    codes: Optional[List[str]] = field(default_factory=list)


class KafkaBaseConsumerAdapter(BaseConsumer):
    """
    Manages Kafka consumption, handling multiple topics and dynamically
    dispatching messages to registered handlers.
    """

    def __init__(
        self,
        config: Dict[str, Any],
        key_deserializer: Optional[Callable] = None,
        value_deserializer: Optional[Callable] = None,
    ):
        super().__init__(config, key_deserializer, value_deserializer)

        self._consumer: Optional[AIOKafkaConsumer] = None
        self._running = False
        self._rebalance_in_progress = False
        self._handlers: Dict[str, Dict[str, Handler]] = defaultdict(dict)
        self._topics: Set[str] = set()

    def get(
        self, config: Dict[str, str | list[str]]
    ) -> Callable[[Callable[..., Coroutine]], Callable[..., Coroutine]]:
        """
        Decorator factory to register a function as a message handler.

        Args:
            config: A dictionary containing 'topic' and optional 'codes' to filter messages.

        Returns:
            A decorator that registers the function.
        """
        topic = config.get("topic")
        codes = config.get("codes", [])

        if topic:
            self._topics.add(topic)

        def decorator(func: Callable[..., Coroutine]):

            if isinstance(codes, str):
                codes_list = [codes]
            elif isinstance(codes, list):
                codes_list = codes
            else:
                codes_list = []

            handler = Handler(func=func, topic=topic, codes=codes_list)

            if not codes:
                """ Default case: No specific codes, register for all messages on the topic """
                self._handlers[topic]["__default__"] = handler
            else:
                """ Case: Index the same handler for each code it handles """
                for code in codes:
                    self._handlers[topic][code] = handler

            log.debug(
                f"Handler registered for topic '{topic}' with codes {codes or 'ALL'}"
            )

            return func

        return decorator

    async def start(self) -> None:
        """Initializes the Kafka consumer and subscribes to registered topics."""
        if self._consumer:
            return

        if not self._topics:
            log.warning("No topics registered. The consumer will not start.")
            return

        log.debug("Starting Kafka Consumer Manager...")
        self._consumer = AIOKafkaConsumer(
            **self.config,
            key_deserializer=self._key_deserializer,
            value_deserializer=self._value_deserializer,
        )
        await self._consumer.start()

        listener = RebalanceHandler(self)
        self._consumer.subscribe(topics=list(self._topics), listener=listener)

        self._running = True
        log.info("Consumer Manager started successfully for topics: %s", self._topics)

    async def _commit_offset(self, msg):
        try:
            tp = TopicPartition(msg.topic, msg.partition)
            await self._consumer.commit({tp: msg.offset + 1})
        except (CommitFailedError, UnknownMemberIdError, IllegalGenerationError):
            log.error(
                "Commit failed, rebalance likely in progress.",
                exc_info=True,
                extra={"partition": msg.partition, "offset": msg.offset},
            )
            self._rebalance_in_progress = True

    async def _process_message(self, msg: ConsumerRecord, **kwargs):
        """Processes a single message by dispatching it to relevant handlers."""

        if self._rebalance_in_progress:
            log.warning("Rebalance in progress, skipping message processing.")
            return

        msg_code = "__default__"
        if isinstance(msg.value, dict) and "code" in msg.value:
            msg_code = msg.value.get("code")

        topic_handlers = self._handlers.get(msg.topic, {})
        handler = topic_handlers.get(msg_code)
        if not handler:
            log.warning(
                f"No handler found for topic {msg.topic} code {msg_code}. Skipping."
            )
            await self._commit_offset(msg)
            return

        try:
            await handler.func(msg, **kwargs)
            await self._commit_offset(msg)
        except (
            CommitFailedError,
            UnknownMemberIdError,
            IllegalGenerationError,
        ) as e:
            log.error(
                "Commit failed, rebalance might be in progress: %s",
                e,
                extra={"partition": msg.partition, "offset": msg.offset},
            )
            self._rebalance_in_progress = True  # Signal rebalance
            return
        except Exception as e:
            log.error(
                "Unexpected error during message processing by '%s': %s",
                handler.func.__name__,
                e,
                exc_info=True,
                extra={"partition": msg.partition, "offset": msg.offset},
            )
            return

    async def listen(self, **kwargs):
        """The main consumer loop that fetches and processes messages."""
        if not self._running or not self._consumer:
            log.error("Consumer is not running. Call start() before listening.")
            return

        log.info("Consumer is now listening for messages...")
        try:
            while self._running:
                if self._rebalance_in_progress:
                    log.warning("Rebalance in progress, pausing message fetching.")
                    await asyncio.sleep(1)
                    continue

                try:
                    result = await self._consumer.getmany(timeout_ms=1000)
                    for tp, messages in result.items():
                        if tp not in self._consumer.assignment():
                            continue
                        for msg in messages:
                            await self._process_message(msg, **kwargs)
                            if self._rebalance_in_progress:
                                break
                        if self._rebalance_in_progress:
                            break

                except Exception:
                    log.error("Critical error in consumer loop.", exc_info=True)
                    # Simple backoff
                    await asyncio.sleep(2)

        finally:
            await self.stop()

    async def stop(self):
        """Stops the consumer and cleans up resources."""
        self._running = False
        if self._consumer:
            log.info("Stopping consumer manager...")
            await self._consumer.stop()
            self._consumer = None
            log.info("Consumer manager stopped.")

    async def __aenter__(self):
        """Enables usage with 'async with' statement."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleans up resources upon exiting 'async with' block."""
        await self.stop()
