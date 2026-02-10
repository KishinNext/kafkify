import logging

from src.consumers.router import ConsumerRouter

log = logging.getLogger(__name__)

router = ConsumerRouter()


@router.get({"topic": "purchase-events", "codes": ["purchase_event"]})
async def handle_purchase_events(msg):
    log.info(
        f"Processing purchase event: {msg.value}, partition: {msg.partition}, offset: {msg.offset}, key: {msg.key}, headers: {msg.headers}"
    )
