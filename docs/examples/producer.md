# Producer Example

This example demonstrates how to set up a Kafka Producer within a FastAPI application using Kafkify.

## Structure

The example consists of:
-   **Main Application (`main.py`)**: Sets up the FastAPI app, configures the producer, and manages the producer lifecycle.
-   **Service (`person_notifier_service.py`)**: Uses the producer to send messages via an API endpoint.

## Application Setup

In your `main.py`, you initialize the producer and store it in the app state so it can be accessed by dependencies.

```python title="src/examples/producer_example/main.py" hl_lines="10-14 17 20"
# ... imports ...

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Load Configuration
    kafka_config = config_manager.get_property("kafka")
    producer_config = KafkaProducerConfig(...)

    # 2. Create Producer Adapter
    producer = KafkaBaseProducerAdapter(
        config=producer_config,
        key_serializer=default_serializer,
        value_serializer=default_serializer,
    )

    # 3. Start Producer
    await producer.start()

    # 4. Store in App State
    app.state.producer = producer

    yield

    # 5. Stop Producer
    await producer.stop()

app = FastAPI(lifespan=lifespan)
```

## Sending Messages

You can inject the producer into your API routes (e.g., using `Request.app.state.producer` or a dependency) and use the `send` method.

```python title="src/examples/producer_example/entrypoints/api/routers/person_notifier_service.py" hl_lines="13 16-23"
# ... imports ...
from fastapi import APIRouter, Depends
from starlette.requests import Request

router = APIRouter()

@router.post("/person/notify")
async def notify_person(
    request: Request,
    person_data: dict
):
    producer = request.app.state.producer
    
    # Send message
    await producer.send(
        topic="people-events",
        value={
            "code": "PERSON_CREATED",
            "data": person_data
        },
        key=person_data.get("id")
    )
    
    return {"status": "Message sent"}
```

## Running the Example

Make sure you have a Kafka broker running.

```bash
uvicorn src.examples.producer_example.main:app --reload --port 8000
```
