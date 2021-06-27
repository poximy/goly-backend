from typing import List

from data import models
from data.mongo import UrlDB
from fastapi import APIRouter, Request

router = APIRouter(
    tags=["metadata"]
)


@router.get("/user/{user_name}", response_model=List[models.UrlMetadata])
async def metadata(request: Request, user_name: str):
    database: UrlDB = request.state.db
    user_urls = await database.get_user_urls("user", user_name)
    data = await database.get_metadata("metadata", user_urls)
    return data
