import logging
import uuid
from typing import List

from faker import Faker
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

from src.producers.infrastructure.adapters.base_producer_adapter import (
    KafkaBaseProducerAdapter,
)
from src.examples.producer_example.domain.person import Person
from src.examples.producer_example.entrypoints.api.dependencies import (
    get_kafka_producer,
)

log = logging.getLogger(__name__)

router = APIRouter(prefix="/producers", tags=["producers"])


@router.post("/person", response_model=List[Person], status_code=201)
async def basic_producer(
    number_of_people: int = Query(default=10),
    kafka_producer: KafkaBaseProducerAdapter = Depends(get_kafka_producer),
):
    people: List[Person] = []
    try:
        fake = Faker()
        for _ in range(number_of_people):
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
            await kafka_producer.send(
                topic="people",
                key=person.id,
                value=person.model_dump(),
            )
            people.append(person)
        return JSONResponse(
            status_code=201, content=[person.model_dump() for person in people]
        )
    except Exception as e:
        log.error(
            "An error occurred while producing messages",
            exc_info=True,
            extra={"number_of_people": number_of_people},
        )
        raise HTTPException(status_code=500, detail=str(e))
