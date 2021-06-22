from data import models
from data.mongo import UrlDB
from fastapi import APIRouter, Body, HTTPException, Request
from fastapi.responses import RedirectResponse

router = APIRouter()


@router.get('/{url_id}', status_code=301)
async def get_url(request: Request, url_id: str):
    database: UrlDB = request.state.db
    result = await database.get_url("links", url_id)
    if result:
        return RedirectResponse(result["url"])
    detail = {"error": f"{url_id} does not exist"}
    raise HTTPException(status_code=404, detail=detail)


@router.post('/', response_model=models.UrlID, status_code=201)
async def post_url(request: Request, url: str = Body(..., embed=True)):
    database: UrlDB = request.state.db
    result = await database.post_url("links", url)
    return result
