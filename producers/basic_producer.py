import asyncio
import json
import logging
import os
import random
import uuid
from typing import List

from dotenv import load_dotenv
from faker import Faker
from fastapi import APIRouter, HTTPException, Query
from kafka.producer import KafkaProducer

from producers.types.person import Person

load_dotenv(verbose=True)
log = logging.getLogger(__name__)

router = APIRouter(prefix="/producers", tags=["producers"])


class SuccessHandler:
    def __init__(self, person):
        self.person = person

    def __call__(self, record):
        log.info(
            f"Message sent successfully: {record.topic} [{record.partition}] at offset {record.offset}"
        )


class ErrorHandler:
    def __init__(self, person):
        self.person = person

    def __call__(self, record):
        log.error(
            f"Error sending message: {record.topic} [{record.partition}] at offset {record.offset}",
            exc_info=record,
        )


def make_producer():
    return KafkaProducer(
        bootstrap_servers=os.getenv("PRODUCER_BOOSTRAP_SERVERS"),
        linger_ms=int(os.getenv("PRODUCER_TOPICS_PEOPLE_LINGER_MS")),
        retries=int(os.getenv("PRODUCER_TOPICS_PEOPLE_RETRIES")),
        max_in_flight_requests_per_connection=int(
            os.getenv("PRODUCER_TOPICS_PEOPLE_INFLIGHT_REQS")
        ),
        acks=os.getenv("PRODUCER_TOPICS_PEOPLE_ACKS"),
        enable_idempotence=True,
    )


@router.post("/basic_producer", response_model=List[Person], status_code=201)
async def basic_producer(number_of_people: int = Query(default=10)):
    people: List[Person] = []
    try:
        producer = make_producer()
        fake = Faker()
        for _ in range(number_of_people):
            await asyncio.sleep(random.uniform(0.1, 0.5))
            person = Person(
                id=str(uuid.uuid4()),
                name=fake.name(),
                age=fake.random_int(min=18, max=100),
                email=fake.email(),
                phone=fake.phone_number(),
                address=fake.address(),
                city=fake.city(),
                state=fake.state_abbr(),
                zip=fake.zipcode(),
                country=fake.country(),
            )
            people.append(person)
            producer.send(
                topic=os.getenv("PRODUCER_TOPICS_PEOBLE_BASIC_NAME"),
                key=person.id.encode("utf-8"),
                value=json.dumps(person.model_dump()).encode("utf-8"),
            ).add_callback(SuccessHandler(person)).add_errback(ErrorHandler(person))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        log.info("Flushing producer")
        producer.flush()
        log.info("Closing producer")
        producer.close()

    return people
