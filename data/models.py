from typing import Optional

from pydantic import BaseModel, Field


class Url(BaseModel):
    id: Optional[str] = Field(alias='_id')
    url: str
