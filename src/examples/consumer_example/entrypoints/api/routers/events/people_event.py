import logging

from src.consumers.router import ConsumerRouter

log = logging.getLogger(__name__)

router = ConsumerRouter()


@router.get({"topic": "people"})
async def handle_all_people_events(msg):
    log.info(
        f"Processing a people event: {msg.value}, partition: {msg.partition}, offset: {msg.offset}, key: {msg.key}, headers: {msg.headers}"
    )
