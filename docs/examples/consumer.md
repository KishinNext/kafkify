# Consumer Example

This example demonstrates how to set up a Kafka Consumer within a FastAPI application using Kafkify.

## Structure

The example consists of:
-   **Main Application (`main.py`)**: Sets up the FastAPI app, configures the consumer, and manages the consumer lifecycle.
-   **Router (`router.py`)**: Defines the message handlers using `ConsumerRouter`.

## Defining Handlers

You can define handlers using the `ConsumerRouter`. This allows you to group related event handlers.

```python title="src/examples/consumer_example/entrypoints/api/routers/events/router.py" hl_lines="6 12-14"
# ... imports ...
from src.consumers.router import ConsumerRouter

main_event_router = ConsumerRouter()

@main_event_router.get({"topic": "people-events", "codes": ["PERSON_CREATED"]})
async def handle_person_created(msg: ConsumerRecord):
    data = msg.value
    # Process the message
    print(f"Person created: {data}")

@main_event_router.get({"topic": "purchase-events"})
async def handle_purchase(msg: ConsumerRecord):
    # Handles all messages on 'purchase-events' regardless of code
    print(f"Purchase received: {msg.value}")
```

## Organizing Handlers

For larger applications, it is recommended to split your handlers into multiple files (e.g., by domain or topic) and use a main router to aggregate them. This main router acts as a central registry or factory.

**Example of an aggregating router:**

```python title="src/examples/consumer_example/entrypoints/api/routers/events/router.py"
from src.consumers.router import ConsumerRouter
from src.examples.consumer_example.entrypoints.api.routers.events import (
    people_event,
    purchase_event,
)

main_event_router = ConsumerRouter()

# Register all domain event routers here
main_event_router.include_router(people_event.router)
main_event_router.include_router(purchase_event.router)
```

## Application Setup

In your `main.py`, you initialize the consumer and register the router.

```python title="src/examples/consumer_example/main.py" hl_lines="10-14 17 20 23"
# ... imports ...

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Load Configuration
    kafka_config = config_manager.get_property("kafka")
    consumer_config = KafkaConsumerConfig(...)

    # 2. Create Consumer Adapter
    consumer = KafkaBaseConsumerAdapter(
        config=consumer_config,
        key_deserializer=default_deserializer,
        value_deserializer=default_deserializer,
    )

    # 3. Register Handlers
    main_event_router.register_handlers(consumer)

    # 4. Start Consumer
    await consumer.start()
    
    # 5. Start Listening Loop (in background)
    consumer_task = asyncio.create_task(consumer.listen())

    yield

    # 6. Stop Consumer (graceful shutdown)
    await consumer.stop()
    try:
        await consumer_task
    except asyncio.CancelledError:
        pass

app = FastAPI(lifespan=lifespan)
```

## Running the Example

Make sure you have a Kafka broker running (e.g., via `docker-compose`).

```bash
uvicorn src.examples.consumer_example.main:app --reload --port 8001
```
