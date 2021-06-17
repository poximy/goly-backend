from typing import Set

from pydantic import BaseModel, Field


class Url_ID(BaseModel):
    id: str = Field(alias='_id')


class User(BaseModel):
    user_name: str
    password: str
    urls: Set[Url_ID]


class Url_Metadata(BaseModel):
    id: str = Field(alias="_id")
    created: str
    clicks: int
