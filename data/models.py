from pydantic import BaseModel, Field


class Url(BaseModel):
    id: str = Field(alias='_id')
    url: str
