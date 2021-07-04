from typing import Set

from pydantic import BaseModel, Field


class UrlID(BaseModel):
    id: str = Field(alias='_id')


class User(BaseModel):
    user_name: str
    password: str
    urls: Set[UrlID] = set()


class UrlMetadata(BaseModel):
    id: str = Field(alias="_id")
    created: str
    clicks: int
