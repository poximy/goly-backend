from pydantic import BaseModel, Field


class Url_ID(BaseModel):
    id: str = Field(alias='_id')


class Url_Metadata(BaseModel):
    id: str = Field(alias="_id")
    created: str
    clicks: int
