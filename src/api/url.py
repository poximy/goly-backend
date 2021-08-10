from fastapi import APIRouter, BackgroundTasks, Body, HTTPException, Request
from fastapi.responses import RedirectResponse

from src.data import models
from src.data.mongo import Database

router = APIRouter(tags=["url"])


@router.get("/{url_id}", response_class=RedirectResponse, status_code=301)
async def get_url(background_tasks: BackgroundTasks, request: Request,
                  url_id: str):
    url_collection: Database.Url = request.state.url

    result = await url_collection.get(url_id)
    if result is not None:
        background_tasks.add_task(url_collection.click, url_id)
        return result["url"]
    detail = {"error": f"{url_id} does not exist"}
    raise HTTPException(status_code=404, detail=detail)


@router.post("/", response_model=models.Url, status_code=201)
async def post_url(request: Request, url: str = Body(..., embed=True)):
    url_collection: Database.Url = request.state.url
    return await url_collection.post(url)
