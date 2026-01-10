from pydantic import BaseModel


class Person(BaseModel):
    id: str
    name: str
    age: int
    email: str
    phone: str
    address: str
    city: str
    state: str
    zip: str
    country: str
