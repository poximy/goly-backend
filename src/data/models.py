from typing import List

from pydantic import BaseModel, Field


class User(BaseModel):
    user_name: str
    password: str
    urls: List[str] = list()


class Url(BaseModel):
    id: str = Field(alias="_id")
    url: str
    created: str
    clicks: int = 0
