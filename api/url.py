from data import models, mongo
from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import RedirectResponse
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


@router.get('/{url_id}')
async def get_url(url_id: str):
    collection = router.db.links
    result = await mongo.get_url(collection, url_id)
    if result:
        return RedirectResponse(result["url"])
    detail = {"error": f"{url_id} does not exist"}
    raise HTTPException(status_code=404, detail=detail)


@router.post('/', response_model=models.Url_ID)
async def post_url(url: str = Body(..., embed=True)):
    collection = router.db.links
    result = await mongo.post_url(collection, url)
    return result
