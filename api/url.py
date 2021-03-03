from data import mongo
from fastapi import APIRouter
from motor.motor_asyncio import AsyncIOMotorClient

router = APIRouter()


@router.on_event("startup")
async def startup_event():
    URI = await mongo.get_uri()
    router.client = AsyncIOMotorClient(URI)
    router.db = router.client.url


@router.on_event("shutdown")
def shutdown_event():
    router.client.close()