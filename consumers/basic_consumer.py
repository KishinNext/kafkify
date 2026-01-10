import asyncio
import json
import logging
import os
from typing import Dict, List

from dotenv import load_dotenv
from fastapi import APIRouter
from kafka.consumer import KafkaConsumer
from kafka.structs import TopicPartition, OffsetAndMetadata


load_dotenv(verbose=True)
log = logging.getLogger(__name__)


router = APIRouter(prefix="/consumers", tags=["consumers"])

# Variable global para controlar el consumidor
_consumer_running = False
_consumer_instance = None
_messages_consumed: List[Dict] = []
_max_messages_in_memory = 100  # Límite de mensajes en memoria


def people_key_deserializer(key):
    return key.decode("utf-8") if key else None


def people_value_deserializer(value):
    return json.loads(value.decode("utf-8"))


async def start_background_consumer():
    global _consumer_running, _consumer_instance, _messages_consumed

    if _consumer_running:
        log.warning("Consumer already running")
        return

    _consumer_running = True
    log.info(
        f"Starting background consumer for topic: {os.getenv('CONSUMER_TOPICS_PEOBLE_BASIC_NAME')}"
    )

    _consumer_instance = KafkaConsumer(
        bootstrap_servers=os.getenv("CONSUMER_BOOSTRAP_SERVERS"),
        group_id=os.getenv("CONSUMER_GROUP_ID"),
        key_deserializer=people_key_deserializer,
        value_deserializer=people_value_deserializer,
        # auto_offset_reset="earliest",
        enable_auto_commit=False,
        consumer_timeout_ms=1000,  # Timeout para no bloquear indefinidamente
    )

    _consumer_instance.subscribe([os.getenv("CONSUMER_TOPICS_PEOBLE_BASIC_NAME")])

    try:
        while _consumer_running:
            for message in _consumer_instance:
                try:
                    log.info(
                        f"Received message - Key: {message.key}, "
                        f"Value: {message.value}, "
                        f"Partition: {message.partition}, "
                        f"Offset: {message.offset}"
                    )

                    topic_partition = TopicPartition(message.topic, message.partition)

                    # Obtener leader_epoch del mensaje, usar -1 como valor por defecto
                    leader_epoch = getattr(message, "leader_epoch", -1)

                    offset = OffsetAndMetadata(
                        message.offset + 1, metadata=None, leader_epoch=leader_epoch
                    )

                    _consumer_instance.commit({topic_partition: offset})

                except Exception as e:
                    log.error(f"Error processing message: {e}")

                await asyncio.sleep(0.1)
            await asyncio.sleep(0.1)
    except Exception as e:
        log.error(f"Error in background consumer: {e}")
    finally:
        if _consumer_instance:
            log.info("Closing consumer")
            _consumer_instance.close()


async def stop_background_consumer():
    global _consumer_running
    _consumer_running = False
    log.info("Stopping background consumer")


@router.get("/status")
async def get_consumer_status():
    return {
        "running": _consumer_running,
        "messages_consumed_count": len(_messages_consumed),
        "topic": os.getenv("CONSUMER_TOPICS_PEOBLE_BASIC_NAME"),
        "group_id": os.getenv("CONSUMER_GROUP_ID"),
    }


@router.get("/messages")
async def get_consumed_messages(limit: int = 10):
    return {
        "total": len(_messages_consumed),
        "messages": _messages_consumed[-limit:] if _messages_consumed else [],
    }


@router.post("/stop")
async def stop_consumer():
    await stop_background_consumer()
    return {"message": "Consumer stop signal sent"}


@router.post("/start")
async def start_consumer():
    global _consumer_running

    if _consumer_running:
        return {"message": "Consumer already running"}

    asyncio.create_task(start_background_consumer())
    return {"message": "Consumer started"}
