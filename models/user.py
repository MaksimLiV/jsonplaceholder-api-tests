from models.base import ApiModel


class Geo(ApiModel):
    lat: str
    lng: str


class Address(ApiModel):
    street: str
    suite: str
    city: str
    zipcode: str
    geo: Geo


class Company(ApiModel):
    name: str
    catch_phrase: str
    bs: str


class User(ApiModel):
    id: int
    name: str
    username: str
    email: str
    address: Address
    phone: str
    website: str
    company: Company
