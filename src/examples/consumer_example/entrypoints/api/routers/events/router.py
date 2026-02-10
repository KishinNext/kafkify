from src.consumers.router import ConsumerRouter
from src.examples.consumer_example.entrypoints.api.routers.events import (
    people_event,
    purchase_event,
)

main_event_router = ConsumerRouter()

# Register all domain event routers here
main_event_router.include_router(people_event.router)
main_event_router.include_router(purchase_event.router)
