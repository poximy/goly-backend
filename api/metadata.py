from typing import List

from data import models, mongo
from fastapi import APIRouter
from motor.motor_asyncio import AsyncIOMotorClient

router = APIRouter()


@router.on_event("startup")
async def startup_event():
    uri = await mongo.get_uri()
    router.client = AsyncIOMotorClient(uri)
    router.db = router.client.url


@router.on_event("shutdown")
def shutdown_event():
    router.client.close()


@router.get("/user/{user_name}", response_model=List[models.Url_Metadata])
async def metadata(user_name: str):
    user_urls = await mongo.get_user_urls(router.db.user, user_name)
    data = await mongo.get_metadata(router.db.metadata, user_urls)
    return data
