import logging
import os
from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from kafka import KafkaAdminClient
from kafka.admin import NewTopic
from kafka.errors import TopicAlreadyExistsError

from producers.basic_producer import router as basic_producer_router
from utils.logging import get_logging_config, setup_logging

setup_logging()
log = logging.getLogger(__name__)
load_dotenv(verbose=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    admin_client = KafkaAdminClient(bootstrap_servers=os.getenv("PRODUCER_BOOSTRAP_SERVERS"))

    try:
        admin_client.create_topics(
            [
                NewTopic(
                    name=os.getenv("PRODUCER_TOPICS_PEOBLE_BASIC_NAME"),
                    num_partitions=int(os.getenv("PRODUCER_TOPICS_PEOPLE_BASIC_PARTITIONS")),
                    replication_factor=int(os.getenv("PRODUCER_TOPICS_PEOPLE_BASIC_REPLICAS")),
                    topic_configs={
                        "cleanup.policy": "compact",
                        "retention.ms": "10000",
                    },
                )
            ]
        )
    except TopicAlreadyExistsError as e:
        log.warning(f"Topic already exists: {e}")
    except Exception as e:
        log.error(f"Error creating topics: {e}")
    finally:
        admin_client.close()

    log.info("Producer server started on http://localhost:8000")
    yield
    log.info("Producer server shutting down")


app = FastAPI(
    title="Kafka Producer API",
    description="API para producir mensajes a Kafka",
    lifespan=lifespan,
)
app.include_router(basic_producer_router)


@app.get("/health-check")
async def health_check():
    return {"message": "Producer OK", "port": 8000}


if __name__ == "__main__":
    uvicorn.run(
        app, host="0.0.0.0", port=8000, log_config=get_logging_config()["logging"]
    )
