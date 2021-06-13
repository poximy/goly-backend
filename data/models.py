from pydantic import BaseModel, Field


class Url_ID(BaseModel):
    id: str = Field(alias='_id')
